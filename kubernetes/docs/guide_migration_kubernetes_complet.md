# Migration du data lake vers Kubernetes — guide complet

Copie locale du guide écrit le 9 octobre 2026 (3 parties : Guide, Aide-mémoire, Continuer sans assistance).
Le schéma d'architecture n'existe que dans le PDF : `guide_migration_kubernetes_complet.pdf`.

---

# Partie 1 — Guide

## Objectif et principes

Le data lake passe de Docker Compose à Kubernetes (k3s), avec un objectif de production : sécurisé, reproductible, prêt pour plusieurs nœuds. Au 9 octobre 2026, la plateforme, Swift, memcached et la zone access tournent dans k3s ; Keystone, MariaDB, Keycloak, Horizon et JupyterHub restent dans le Compose.

Les principes qui guident chaque choix :

- **Toujours l'option production**, même sur une seule machine. Quand le matériel manque, on assume une « production dégradée » (exemple : disque Swift en fichier `fallocate`).
- **Réécrire, pas convertir.** Kompose traduit la syntaxe Compose, pas son modèle : IP fixes, `depends_on`, bind mounts et scripts multi-processus n'existent pas dans Kubernetes.
- **Un Pod = une instance, un conteneur = un processus.** Le processus est le PID 1 : le kubelet le surveille, le redémarre, et lui envoie SIGTERM.
- **Ni root, ni `privileged`.** Le profil Pod Security `restricted` est visé pour tous les services.
- **La conf est générée depuis `conf.env`.** Rien de généré ni de secret n'est versionné dans git.
- **Le Compose reste intact jusqu'à l'intégration.** Les Dockerfiles et images Kubernetes sont séparés quand ceux du Compose ne conviennent pas.

*(Schéma : architecture cible, 3 zones, 1 point d'entrée — voir le PDF.)* Le navigateur n'entre que par `nginx-proxy` ; les boîtes en pointillés sont encore dans le Compose.

## Informations à réunir

Ces informations décident de la forme du déploiement de production ; la plupart sont encore à définir.

| Information | Ce qu'elle décide | Situation actuelle |
| --- | --- | --- |
| Machines : nombre, CPU, RAM | Nombre de nœuds k3s, répartition des pods, haute disponibilité | 1 machine (WSL en dev) ; production à définir |
| Disques disponibles pour Swift | Type de stockage : disque dédié, partition, LVM ou fichier | Pas de disque dédié ni de LVM : fichier `fallocate` |
| Nombre et taille des storage nodes | `NB_STORAGE_NODE`, `NODE_STORAGE_SIZE`, réplicas Swift | 1 × 10 GB, 1 réplica |
| Nom de domaine et certificats TLS | Ingress, URLs publiques (`WEB_GUI_URL`, `KEYCLOAK_PUBLIC_URL`, `KEYSTONE_PUBLIC_URL`) | À définir ; accès actuel par `localhost:7000` |
| Registry d'images | Livraison des images à plusieurs nœuds | Import manuel dans k3s (1 nœud) |
| Accès Internet du cluster | Téléchargement des images publiques (nginx, memcached, Keycloak) | Requis |
| Secrets de production | Mots de passe, hash Swift, clés Keycloak et Flask | Valeurs de dev dans `conf.env` (mots de passe courts) |
| Lieu des sauvegardes hors machine | Snapshots etcd, dumps MariaDB, données Swift | À définir |
| Utilisateurs et projets | Tenants de la zone de consommation, quotas | À définir |

## Concepts Kubernetes utilisés

Chaque objet ci-dessous remplace un mécanisme du Compose ; la définition est celle de la documentation Kubernetes.

| Concept | Définition | Dans le projet / équivalent Compose |
| --- | --- | --- |
| Pod | Plus petite unité déployable : un ou plusieurs conteneurs qui partagent réseau et stockage | Un storage node Swift = 1 pod de 12 conteneurs |
| Deployment | Maintient N pods identiques et interchangeables, mis à jour progressivement | `swift-proxy`, `memcached`, `flask-app`, `web-gui`, `nginx-proxy` |
| StatefulSet | Pods à identité stable : nom, ordre, disque | `swift-storage-0`, `-1`… |
| Job | Pods exécutés jusqu'à réussite | Ex-`initswift` ; `keystone_bootstrap` (à venir) |
| Service ClusterIP | Nom DNS et IP stables vers les pods prêts | Le nom d'un service Compose |
| Service headless | DNS sans IP virtuelle : un nom par pod | Noms des storage nodes dans les rings |
| Service LoadBalancer | Ouvre un port sur le nœud (ServiceLB de k3s) | `ports: "7000:80"` |
| Ingress | Accès HTTP(S) externe par nom ou chemin, avec TLS | À venir (Traefik, inclus dans k3s) |
| ConfigMap / Secret | Données de configuration, montées en fichiers ou en variables | Bind mounts `./conf`, fichiers `.env` |
| PV / PVC / StorageClass | Disque réel / demande de disque / classe de disque | Volumes Compose |
| Namespace | Isolation de ressources : portée des noms, droits, quotas | Réseau `swift-cluster` (en partie) |
| Labels et sélecteurs | Étiquettes clé/valeur, et requêtes qui relient les objets entre eux | Aucun |
| NetworkPolicy | Définit quels pods peuvent en joindre d'autres | Aucun : réseau ouvert |
| Pod Security Admission | Niveau de sécurité imposé aux pods d'un namespace | `privileged: true` |
| Probes | Tests du kubelet : prêt (readiness), vivant (liveness) | `healthcheck` |

## Méthode : migrer un service

Chaque service suit les mêmes onze étapes ; Swift et la zone access ont été migrés ainsi.

1. **Inventaire.** Partir du Compose (`create_docker.sh`), pas de la sortie Kompose : image, commande, variables, ports, volumes, dépendances, healthcheck.
2. **Type d'objet.** Deployment si le service est sans état, StatefulSet s'il a une identité ou un disque, Job pour une tâche ponctuelle.
3. **Image.** Dockerfile Kubernetes séparé si celui du Compose ne convient pas. UID numérique fixe, tag explicite (jamais `latest`), build et import par `start.sh -b`.
4. **Configuration.** Le `create_conf.sh` de la zone génère ConfigMaps et Secrets dans `volumes/` à partir de `conf.env`. Aucun secret dans l'image.
5. **Stockage.** PVC (ou `volumeClaimTemplates` pour un StatefulSet) pour les données ; `emptyDir` pour les fichiers temporaires.
6. **Réseau.** Un Service par point d'accès. Remplacer toutes les IP `10.5.x.x` des confs par des noms de Services.
7. **Sécurité.** `securityContext` non-root, `readOnlyRootFilesystem`, `capabilities: drop: [ALL]`, seccomp `RuntimeDefault` ; NetworkPolicy d'entrée.
8. **Santé et ressources.** Readiness et liveness probes, `requests` et `limits` mémoire, arrêt propre (signal et délai de grâce).
9. **Labels.** `app.kubernetes.io/name`, `component`, `part-of` (la zone), `version`. Le `selector` n'utilise que `name` (et `component`) : il est immuable.
10. **Intégration.** Ajouter le build et l'`apply` dans `kubernetes/start.sh`, puis l'attente du rollout.
11. **Test et nettoyage.** Pods `Running`, logs, `curl` via `port-forward` ; puis suppression des fichiers Kompose du service.

## Organisation du dépôt et de start.sh

Tout le Kubernetes vit dans `kubernetes/`, une zone par dossier, avec les mêmes sous-dossiers partout ; `start.sh` construit (`-b`) puis déploie (`-r`).

```
kubernetes/
├── start.sh                    -b build, -r déploiement
├── namespace_datalake.yml
├── kubernetes_config/          plateforme, une fois par cluster
│   ├── storage_class_swift_disk.yml
│   ├── local_static_provisioner.yml
│   └── disk_creation.sh, disks.env
├── memcached/                  pods/ services/ network/
├── rawdata_zone/openstackSwift/
│   ├── create_conf.sh, create_rings.sh
│   ├── pods/ services/ network/
│   └── volumes/                généré, ignoré par git
├── access_zone/
│   ├── create_conf.sh
│   ├── flask/Dockerfile, web_gui/Dockerfile
│   ├── pods/ services/ network/
│   └── volumes/                généré, ignoré par git
└── docs/                       ce guide (PDF et Markdown)
```

| Dossier | Contenu | Versionné |
| --- | --- | --- |
| `pods/` | Deployments et StatefulSets, avec des variables `${...}` remplies par `start.sh` (`envsubst`) | Oui |
| `services/` | Services : noms DNS et ports | Oui |
| `network/` | NetworkPolicies d'entrée | Oui |
| `volumes/` | ConfigMaps, Secrets, rings, générés par les scripts | Non (`.gitignore`) |

| Option | Étapes |
| --- | --- |
| `-b` | Disques locaux (`NB_STORAGE_NODE` × `NODE_STORAGE_SIZE`), images Swift, Flask et web GUI importées dans k3s, `create_conf.sh` des zones, `create_rings.sh` |
| `-r` | Namespace, memcached, Swift, zone access (`apply --server-side`), redémarrage des Deployments après un build, attente des rollouts |

Les images construites depuis le dépôt ont pour tag le commit git (`APP_TAG`). `-r` refuse de déployer si les images de ce commit ne sont pas dans k3s. `start.sh` sera fusionné dans le `start.sh` racine à l'intégration.

## Plateforme

La plateforme est en place : k3s, stockage local pour Swift, namespace `datalake` et memcached partagé. Il ne manque que le script des disques physiques pour la production.

| Brique | Choix | Fichier |
| --- | --- | --- |
| Cluster | k3s avec etcd embarqué, Secrets chiffrés au repos, Traefik, ServiceLB, metrics-server ; Headlamp en interface web | `kubernetes/installK3S.sh` |
| Classe de disque Swift | StorageClass `swift-disks` : `no-provisioner`, `WaitForFirstConsumer`, `reclaimPolicy: Retain` | `kubernetes_config/storage_class_swift_disk.yml` |
| Création des PV | Local static provisioner v2.9.0 (`kube-system`) : un PV par point de montage sous `/mnt/disks/<classe>/` | `kubernetes_config/local_static_provisioner.yml` |
| Disques | Fichier `fallocate` (espace réservé), loop en `direct-io`, XFS ou ext4, monté par une unité systemd avant k3s | `kubernetes_config/disk_creation.sh` (`-c -g -a -i --remove`) |
| Namespace | `datalake` ; Pod Security `enforce: baseline`, `warn` et `audit: restricted` | `namespace_datalake.yml` |
| Cache | Un memcached central pour toute l'architecture (1 réplica), joignable par le proxy Swift et Keystone | `memcached/` |

Ce qu'il faut savoir :

- **Un PV local est lié à son nœud.** Si le nœud tombe, le pod storage attend au lieu de redémarrer ailleurs sur un disque vide ; Swift sert les autres réplicas.
- **Une PVC demande 90 % de `NODE_STORAGE_SIZE`.** Le système de fichiers garde une partie du disque et le provisioner arrondit la capacité vers le bas.
- **Agrandir un disque se fait à chaud** (`disk_creation.sh -g`), sans toucher à Kubernetes ; le PV affiche toujours l'ancienne capacité.
- **En production sur de vrais disques**, seul le script de préparation change (disque, partition ou volume LVM) : la StorageClass, le provisioner et les pods restent identiques.

## Zone rawdata

Swift tourne et répond ; il attend Keystone pour authentifier les requêtes. La prochaine migration est donc MariaDB + Keystone, puis Keycloak.

### Swift (fait)

- **Storage** : StatefulSet `swift-storage`, un pod par disque, 12 conteneurs (3 serveurs, 3 replicators, 3 auditors, 2 updaters, 1 reaper), UID 55555.
- **Proxy** : Deployment `swift-proxy`, conf en dossier (`proxy-server.conf.d/`) pour séparer le mot de passe Keystone, Service `swift-proxy:8080`.
- **Rings** : noms DNS du headless Service, créés une seule fois puis modifiés ; builders gardés dans la ConfigMap `swift-ring-builders`.
- **Sécurité** : NetworkPolicy (seuls le proxy et les storage pods joignent le storage et rsync), arrêt propre par SIGHUP.
- **Reste à décider** : le tag de l'image. Debian installe Swift 2.30.1, le tag dit 2.30.0 ; option A = tag lu après le build, option B = version figée dans le Dockerfile.

### MariaDB et Keystone (à faire)

1. **MariaDB** : StatefulSet avec PVC et Secret pour les mots de passe, NetworkPolicy ouverte à Keystone seul, sauvegarde par `mariadb-dump` (CronJob).
2. **Base Keystone** : `keystone-manage db_sync` dans un Job exécuté avant le Deployment.
3. **Keystone** : Deployment sans état, label `app.kubernetes.io/name: keystone` (attendu par la NetworkPolicy de memcached). `keystone.conf` et les confs Apache en ConfigMap ; connexion à la base et passphrase OIDC en Secret.
4. **Clés fernet et credential** : un Secret monté dans tous les pods, pour qu'un token émis par un pod soit valide sur les autres.
5. **Image** : construite par LOCI (`rawdata_zone/openstackKeystone/build.sh`), à ajouter à `start.sh -b`.
6. **Bootstrap** : `keystone_bootstrap` devient un Job. Il crée l'utilisateur `swift`, les endpoints et la fédération Keycloak. L'endpoint `object-store` interne pointe vers `http://swift-proxy:8080/v1/AUTH_%(project_id)s`.
7. **Ensuite, côté Swift** : URL publique de Keystone dans `www_authenticate_uri`, `service_token_roles_required = true`, puis un vrai test d'écriture et de lecture d'objet.

Décisions à prendre : MariaDB écrit à la main ou par un opérateur ; classe de disque de la base ; rotation des clés fernet (CronJob ou manuelle) ; `wsgi.py` modifié intégré à une image dérivée ou monté depuis une ConfigMap.

### Keycloak (à faire)

- **Mode** : le Compose lance `start-dev`, avec une base embarquée qui n'est pas faite pour la production. En production : `start` avec une base externe (MariaDB ou PostgreSQL) et `KC_HOSTNAME` = l'URL publique en HTTPS.
- **Realm** : le JSON généré par `create_conf.sh` devient une ConfigMap importée au démarrage.
- **Exposition** : le navigateur doit joindre Keycloak directement. Il faut donc une URL publique (Ingress ou LoadBalancer), cohérente avec `KEYCLOAK_PUBLIC_URL` et l'émetteur des tokens.

### Horizon (à décider)

Horizon est l'interface d'administration OpenStack. À garder seulement s'il est utilisé en dehors de la web GUI : Deployment, `local_settings.py` en ConfigMap, exposition réservée aux administrateurs.

## Zone access

L'API, la web GUI et nginx tournent dans k3s, derrière un seul point d'entrée sur le port 7000 ; la connexion SSO attend Keycloak et Keystone.

| Service | Ce qui change par rapport au Compose | Image |
| --- | --- | --- |
| `flask-app` | gunicorn (3 workers), variables depuis la ConfigMap et le Secret `flask-env`, aucun `.env` dans l'image, UID 55556 | `datalake-flask:<commit>`, Dockerfile dans `kubernetes/access_zone/flask/` |
| `web-gui` | Build React de production servi par nginx, au lieu du serveur de dev `npm start` | `datalake-web-gui:<commit>`, Dockerfile dans `kubernetes/access_zone/web_gui/` |
| `nginx-proxy` | Noms de Services au lieu des IP `10.5.x.x` ; route `/hub/` retirée jusqu'à JupyterHub | `nginxinc/nginx-unprivileged:1.28-alpine`, conf en ConfigMap |

Les NetworkPolicies limitent `flask-app` et `web-gui` à `nginx-proxy` (et JupyterHub pour l'API, une fois migré). `nginx-proxy` est un Service LoadBalancer sur le port 7000, comme le `7000:80` du Compose.

Décisions et points ouverts :

- **`REACT_APP_FLASK_APP_URL="/api"`** (URL relative) : la GUI appelle l'API sur la même adresse que la page, quelle qu'elle soit. La valeur est compilée dans le build.
- **Exposition de production** : un nom de domaine et du TLS par un Ingress Traefik devant `nginx-proxy`. `WEB_GUI_URL` devient alors cette URL publique.
- **Flask** : `app.config['DEBUG'] = True` est écrit dans `app.py`, à passer à `False` ; passer à plusieurs réplicas une fois vérifié que l'API ne garde aucun état en mémoire.
- **Route `/hub/`** : à remettre dans la conf nginx avec la migration de JupyterHub.

## Zone process et zone de consommation

Les deux zones exécutent du code d'utilisateurs : leurs pods ne doivent jamais tourner dans le périmètre de confiance du namespace `datalake`.

### JupyterHub (à faire)

- **Spawner** : le Compose utilise DockerSpawner via le socket Docker, impossible dans Kubernetes. Il faut **KubeSpawner**, qui crée un pod par utilisateur.
- **Déploiement** : le chart Helm officiel *Zero to JupyterHub*, ou des manifests écrits à la main comme le reste. Choisir Helm ouvre la question du packaging pour tout le projet.
- **Pods utilisateurs** : dans un namespace séparé (un par utilisateur, ou un commun avec NetworkPolicy et limites par pod), jamais dans `datalake`.
- **Image** : `cors_base-notebook` à construire et importer comme les autres ; un disque par utilisateur si les notebooks doivent survivre au pod.
- **Authentification** : par l'API Flask (`http://flask-app:5000`) ; la NetworkPolicy de Flask accepte déjà le label `jupyterhub`.
- **Accès** : route `/hub/` dans nginx, avec les en-têtes WebSocket.

### Zone de consommation (à concevoir)

Un namespace par tenant, tous étiquetés `datalake/zone: consumption`, forme la zone. Sur chacun :

- **NetworkPolicy** : tout refusé par défaut ; sortie autorisée seulement vers les points d'entrée authentifiés (`swift-proxy`, `flask-app`, Keycloak).
- **Pod Security `restricted`**, **ResourceQuota** pour le budget du tenant, `automountServiceAccountToken: false`.
- **Accès aux applications** : authentification Keycloak à l'entrée (Ingress), le partage passant par les droits Keycloak et Keystone.

Décisions à prendre : un tenant = un utilisateur ou un projet (à aligner sur les projets Keystone ou les groupes Keycloak) ; quel composant lance les applications, avec quels droits RBAC ; règle de conversion des identifiants en noms de namespace (63 caractères, minuscules) ; runtime isolé (gVisor, Kata) pour le code non fiable.

## Sécurité, exploitation et plusieurs nœuds

Ces chantiers concernent toute l'architecture ; la plupart se font une fois les services migrés.

| Sujet | Mesure | Quand |
| --- | --- | --- |
| Pod Security | Passer `datalake` en `enforce: restricted` | Quand tous les services du namespace sont conformes |
| NetworkPolicy | Une policy d'entrée par service (proxy Swift, Keystone, MariaDB, Keycloak), puis un refus par défaut du namespace | À chaque migration |
| Secrets | Mots de passe longs et aléatoires en production ; déjà chiffrés au repos par k3s | Avant la production |
| Sauvegardes | Snapshots etcd de k3s (toutes les 12 h, 5 gardés) copiés hors machine ; dumps MariaDB ; données Swift | Avant la production |
| Logs et métriques | Collecteur pour tout le cluster (Fluent Bit, Loki) ; `kubectl top` pour ajuster `requests` et `limits` | Après stabilisation |
| Images | Tag = version réellement installée ; nettoyage de `Dockerfile.base` (memcached, rsyslog, xfsprogs, `USER 55555`) | Quand le Compose n'en dépend plus |
| Registry | Images servies à tous les nœuds au lieu de l'import manuel | Dès le 2e nœud |
| Swift multi-nœuds | Conteneur rsync dans le pod storage (ajouté par le script), `podAntiAffinity`, une zone Swift par nœud, PodDisruptionBudget, poids du ring = capacité | Dès 2 storage nodes |
| Disques de production | Script de préparation pour disque, partition ou volume LVM | Quand une machine a des disques |
| Mises à jour | Rollouts sans coupure (`maxUnavailable: 0`), mises à jour de k3s, rotation des clés | En continu |

## Registre des décisions

18 décisions sont prises et 11 restent ouvertes.

| Décision | Choix ou options | Statut |
| --- | --- | --- |
| Cible | k3s, objectif production ; « production dégradée » assumée sur une machine | Prise |
| Méthode | Kompose abandonné, réécriture service par service | Prise |
| Compose | Inchangé jusqu'à l'intégration ; Dockerfiles Kubernetes séparés | Prise |
| Namespace | Un seul, `datalake` ; les zones sont un label `part-of` | Prise |
| Labels | `app.kubernetes.io/*` ; `selector` = `name` (+ `component`) | Prise |
| Swift : objets | Storage = StatefulSet + headless Service ; proxy = Deployment | Prise |
| Swift : processus | Un conteneur par processus, 12 dans le pod storage | Prise |
| Swift : rings | Noms DNS ; créés une fois puis modifiés ; builders gardés dans le cluster | Prise |
| Stockage Swift | Local PV, local static provisioner, StorageClass `swift-disks` en `Retain` | Prise |
| Disque | Fichier `fallocate` + loop `direct-io`, XFS par défaut | Prise |
| UID | Swift 55555, Flask 55556 | Prise |
| Livraison des images | Import manuel dans k3s (1 nœud) | Prise |
| Cache | Un memcached central pour toute l'architecture | Prise |
| rsync | Ajouté par le script dès 2 storage nodes | Prise |
| Configuration | `create_conf.sh` par zone, sortie dans `volumes/`, ignorée par git | Prise |
| Zone access | GUI en build statique, Flask sous gunicorn, entrée unique `nginx-proxy` | Prise |
| Exposition actuelle | LoadBalancer sur le port 7000 (ServiceLB) | Prise |
| Pod Security | `enforce: baseline`, `warn` et `audit: restricted` | Prise |
| Tag de l'image Swift | A : tag lu après le build ; B : version figée dans le Dockerfile | Ouverte |
| Exposition de production | Nom de domaine, TLS, Ingress Traefik | Ouverte |
| URL de l'API dans la GUI | Relative `/api` recommandée | Ouverte |
| MariaDB | Écrite à la main ou opérateur ; classe de disque | Ouverte |
| Clés fernet Keystone | Secret partagé ; rotation par CronJob ou manuelle | Ouverte |
| Keycloak | Mode dev, ou production avec base externe | Ouverte |
| Horizon | Garder ou retirer | Ouverte |
| JupyterHub et packaging | Chart Helm ou manifests ; Kustomize ou Helm pour tout le projet | Ouverte |
| Tenants | Utilisateur ou projet ; composant qui lance les applications | Ouverte |
| Registry | Lequel, pour plusieurs nœuds | Ouverte |
| Sauvegardes hors machine | Lieu et fréquence | Ouverte |

## Ordre recommandé et checklist

Keystone vient en premier parce qu'il débloque l'authentification de Swift et de l'API ; Keycloak débloque ensuite le SSO, dont JupyterHub dépend.

- [x] Installer k3s et Headlamp
- [x] Plateforme de stockage : StorageClass, provisioner, disques
- [x] Swift (storage et proxy) et memcached
- [x] Zone access : API Flask, web GUI, nginx
- [ ] Corriger le tag de l'image Swift (2.30.1)
- [ ] MariaDB et Keystone, avec le Job de bootstrap ; test d'un objet Swift avec un token
- [ ] Keycloak ; SSO de bout en bout depuis la web GUI
- [ ] Horizon, s'il est conservé
- [ ] JupyterHub avec KubeSpawner, et la route `/hub/`
- [ ] Exposition de production : domaine, TLS, Ingress
- [ ] NetworkPolicies restantes, puis Pod Security `restricted`
- [ ] Sauvegardes hors machine, logs et métriques
- [ ] Intégration dans le `start.sh` racine, puis retrait du Compose
- [ ] Zone de consommation
- [ ] Passage à plusieurs nœuds : registry, rsync, anti-affinité

---

# Partie 2 — Aide-mémoire : commandes et modèles

Les commandes et modèles utiles pendant la migration, à lancer depuis WSL dans `kubernetes/`.

## Déployer et suivre

```bash
./start.sh -br                                   # reconstruire puis déployer
./start.sh -r                                    # redéployer sans rebuild (même commit)

kubectl -n datalake get pods,svc,pvc             # vue d'ensemble
kubectl -n datalake get pods -w                  # suivre en direct (Ctrl+C pour sortir)
kubectl -n datalake get pods -l app.kubernetes.io/part-of=raw-data-zone   # filtrer par zone

kubectl -n datalake rollout status deployment/flask-app     # attendre la fin d'un déploiement
kubectl -n datalake rollout restart deployment/flask-app    # recréer les pods (nouvelle image, nouvelle conf)
kubectl -n datalake rollout undo deployment/flask-app       # revenir à la version précédente

kubectl -n datalake top pod --containers         # CPU et mémoire réellement consommés
```

## Diagnostiquer un pod

| Statut | Première commande | Cause fréquente |
| --- | --- | --- |
| `Pending` | `describe pod`, section Events | Aucun PV assez grand pour la PVC, ressources insuffisantes |
| `ImagePullBackOff` | `sudo k3s ctr images ls \| grep datalake` | Image pas importée dans k3s, ou tag `latest` |
| `CreateContainerConfigError` | `describe pod` | ConfigMap, Secret ou clé manquante |
| `CrashLoopBackOff` | `logs --previous` | Erreur de conf, droits (UID, système de fichiers en lecture seule) |
| `Running` mais pas `Ready` | `describe pod`, puis `logs` | Probe sur un mauvais chemin ou port, service lent à démarrer |

```bash
kubectl -n datalake describe pod <pod>                       # section Events en bas
kubectl -n datalake logs <pod> -c <conteneur> --tail=50
kubectl -n datalake logs <pod> -c <conteneur> --previous     # logs d'avant le dernier redémarrage
kubectl -n datalake logs swift-storage-0 --all-containers --prefix --tail=20
kubectl -n datalake get events --sort-by=.lastTimestamp | tail -20
kubectl -n datalake exec -it <pod> -c <conteneur> -- sh      # shell dans un conteneur

# pod jetable avec curl, supprimé à la sortie ; sans label, les NetworkPolicies le bloquent
kubectl -n datalake run tmp --rm -it --image=curlimages/curl --restart=Never -- sh
#   curl -s http://swift-proxy:8080/healthcheck             -> OK (pas de policy sur le proxy)
#   curl -s -m 3 http://flask-app:5000/flask-health-check    -> timeout (réservé à nginx-proxy)
```

## Tester Swift

```bash
kubectl -n datalake port-forward svc/swift-proxy 8081:8080 &        # tunnel vers le proxy (8080 est pris par Headlamp)
curl -i http://localhost:8081/healthcheck                            # 200 OK
curl -s http://localhost:8081/info                                   # version et middlewares chargés
curl -i http://localhost:8081/v1/AUTH_test                           # 401 tant que Keystone n'est pas migré

kubectl -n datalake port-forward pod/swift-storage-0 6202:6202 &     # tunnel vers un storage node
curl -s http://localhost:6202/recon/diskusage                        # d1 monté et sa taille

kill %1 %2                                                           # arrêter les tunnels

bash rawdata_zone/openstackSwift/create_rings.sh                     # rings : modifiés, jamais recréés s'ils existent
kubectl -n datalake get configmap swift-ring-builders                # les builders gardés dans le cluster
```

## Disques et stockage

```bash
bash kubernetes_config/disk_creation.sh -i                          # disques : taille, utilisation, montage, direct-io
bash kubernetes_config/disk_creation.sh -cai -n swift-1 -s 10GB     # créer, appliquer le provisioner, attendre le PV
bash kubernetes_config/disk_creation.sh -g -n swift-0 -s 20GB       # agrandir à chaud (jamais réduire)
bash kubernetes_config/disk_creation.sh --remove -n swift-1         # supprimer (le nom est redemandé)

kubectl get pv                                                      # Available, Bound ou Released
kubectl -n datalake get pvc

# PV Released (PVC supprimée, policy Retain) : les données restent sur le disque,
# le provisioner recrée un PV Available pour ce même disque
kubectl delete pv <nom-du-pv>

# changer volumeClaimTemplates : retirer le StatefulSet en gardant ses pods et ses PVC, puis le réappliquer
kubectl -n datalake delete statefulset swift-storage --cascade=orphan
./start.sh -r
```

## Configs, secrets et templates

```bash
bash rawdata_zone/openstackSwift/create_conf.sh                     # régénère volumes/ de Swift depuis conf.env
bash access_zone/create_conf.sh                                     # idem pour la zone access

# voir un template tel que start.sh l'applique
APP_TAG=$(git rev-parse --short HEAD) envsubst '${APP_TAG}' < access_zone/pods/deployment_flask_app.yml

# valider sur le serveur sans rien modifier, puis voir ce qui changerait
kubectl apply --server-side --dry-run=server -f access_zone/services/
kubectl diff --server-side -f access_zone/services/

# lire une valeur d'un Secret
kubectl -n datalake get secret flask-env -o jsonpath='{.data.FLASK_SECRET}' | base64 -d

# la conf réellement vue par un pod
kubectl -n datalake exec deploy/swift-proxy -- cat /etc/swift/proxy-server.conf.d/00-proxy.conf

# la documentation d'un champ, depuis le cluster
kubectl explain deployment.spec.template.spec.containers.securityContext
```

## Modèle pour un nouveau service

Les trois objets d'un service sans état, aux conventions du projet. Dans le dépôt, chacun va dans son dossier : `pods/`, `services/`, `network/`. Remplace chaque `<...>`.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: <service>
  namespace: datalake
  labels:
    app.kubernetes.io/name: <service>
    app.kubernetes.io/component: <role>
    app.kubernetes.io/part-of: <zone>-zone
    app.kubernetes.io/version: "<version>"
spec:
  replicas: 1
  strategy:
    type: RollingUpdate
    rollingUpdate: {maxUnavailable: 0, maxSurge: 1}
  selector:
    matchLabels:
      app.kubernetes.io/name: <service>          # immuable : jamais la version ici
  template:
    metadata:
      labels:
        app.kubernetes.io/name: <service>
        app.kubernetes.io/component: <role>
        app.kubernetes.io/part-of: <zone>-zone
        app.kubernetes.io/version: "<version>"
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: <uid>                          # UID numérique fixe de l'image
        runAsGroup: <gid>
        seccompProfile: {type: RuntimeDefault}
      containers:
        - name: <service>
          image: <image>:<tag>                    # jamais latest
          imagePullPolicy: IfNotPresent
          envFrom:
            - configMapRef: {name: <service>-env}
            - secretRef: {name: <service>-env}
          ports:
            - {name: http, containerPort: <port>}
          volumeMounts:
            - {name: tmp, mountPath: /tmp}
          resources:
            requests: {cpu: 100m, memory: 128Mi}
            limits: {memory: 512Mi}               # pas de limite CPU : elle bride même quand la machine est libre
          readinessProbe:
            httpGet: {path: <chemin-sante>, port: http}
            periodSeconds: 10
          livenessProbe:
            httpGet: {path: <chemin-sante>, port: http}
            periodSeconds: 20
            failureThreshold: 3
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities: {drop: ["ALL"]}
      volumes:
        - name: tmp
          emptyDir: {sizeLimit: 128Mi}
---
apiVersion: v1
kind: Service
metadata:
  name: <service>                                 # joignable par http://<service>:<port>
  namespace: datalake
  labels:
    app.kubernetes.io/name: <service>
    app.kubernetes.io/component: <role>
    app.kubernetes.io/part-of: <zone>-zone
spec:
  selector:
    app.kubernetes.io/name: <service>
  ports:
    - {name: http, port: <port>, targetPort: http}
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: <service>-ingress
  namespace: datalake
spec:
  podSelector:
    matchLabels: {app.kubernetes.io/name: <service>}
  policyTypes: [Ingress]                          # toute entrée non listée est refusée
  ingress:
    - from:
        - podSelector:
            matchLabels: {app.kubernetes.io/name: <client-autorise>}
      ports:
        - {port: <port>}
```

## Modèle de create_conf.sh

Le schéma des `create_conf.sh` existants : lire `conf.env`, écrire ConfigMap et Secret dans `volumes/`. Ajoute `volumes/` au `.gitignore` de la zone.

```bash
#!/bin/bash
# Generates the configuration of <service> from conf.env into volumes/
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONF_ENV="${CONF_ENV:-$SCRIPT_DIR/../../conf.env}"
VOLUMES_PATH="$SCRIPT_DIR/volumes"
NAMESPACE="datalake"

export $(grep -v '^#' "$CONF_ENV" | sed 's/\r$//' | xargs)
mkdir -p "$VOLUMES_PATH"

# kv <VAR...> : one '  VAR: "value"' line per variable, value escaped for YAML
kv() {
  local var value
  for var in "$@"; do
    value="${!var:-}"
    value="${value//\\/\\\\}"
    value="${value//\"/\\\"}"
    echo "  $var: \"$value\""
  done
}

# indent <n> : shifts stdin by n spaces, to embed a file in a YAML block scalar
indent() {
  sed "s/^/$(printf '%*s' "$1" '')/"
}

# a conf file : quoted heredoc ('EOF') keeps its $ as is, unquoted (EOF) fills the variables
APP_CONF=$(cat << EOF
[section]
key = $SOME_VAR
EOF
)

cat << EOF > "$VOLUMES_PATH/configmap_<service>_env.yml"
# Generated by create_conf.sh from conf.env : edit create_conf.sh, not this file
apiVersion: v1
kind: ConfigMap
metadata:
  name: <service>-env
  namespace: $NAMESPACE
data:
$(kv VAR_1 VAR_2)
  app.conf: |
$(echo "$APP_CONF" | indent 4)
EOF

# stringData : plain values, Kubernetes encodes them itself
cat << EOF > "$VOLUMES_PATH/secret_<service>_env.yml"
# Generated by create_conf.sh from conf.env : edit create_conf.sh, not this file
apiVersion: v1
kind: Secret
metadata:
  name: <service>-env
  namespace: $NAMESPACE
type: Opaque
stringData:
$(kv PASSWORD_VAR)
EOF
chmod 600 "$VOLUMES_PATH/secret_<service>_env.yml"
```

---

# Partie 3 — Continuer sans assistance

Tout ce qu'il faut pour terminer la migration seul : les procédures des services restants, les pièges déjà rencontrés et où trouver la documentation.

## Mettre son travail à l'abri

Trois choses à sauvegarder : le code dans git, une copie locale de ce guide, et l'état du cluster (rings Swift, etcd).

**1. Committer le code Kubernetes.** Les dossiers `volumes/` sont ignorés par git (secrets) ; `kubernetes/docker-compose.yml` et les brouillons `pod_*.yml` à la racine ne sont pas à committer.

```bash
git add kubernetes/start.sh kubernetes/namespace_datalake.yml kubernetes/kubernetes_config \
        kubernetes/memcached kubernetes/rawdata_zone kubernetes/access_zone kubernetes/docs \
        rawdata_zone/openstackSwift/Dockerfile.base
git status                          # vérifier : aucun fichier volumes/ ni secret_*
git commit -m "Kubernetes : plateforme, Swift, memcached et zone access"
```

**2. Garder ce guide en local.** Une copie PDF et Markdown est dans `kubernetes/docs/` du dépôt. Pour une copie à jour depuis claude.ai : clic sur le nom du doc, puis **Export**, onglet par onglet.

**3. Sauvegarder l'état du cluster.** Les builders des rings n'existent que dans le cluster : sans eux, il faudrait recréer les rings.

```bash
kubectl -n datalake get configmap swift-ring-builders -o yaml > ~/swift-ring-builders.yml   # pas de secret dedans
sudo k3s etcd-snapshot save                                                                 # snapshot complet du cluster
sudo ls /var/lib/rancher/k3s/server/db/snapshots/                                           # à copier hors de la machine
```

## Procédure : MariaDB et Keystone

Keystone débloque l'authentification de Swift et de l'API. Son `init-keystone.sh` fait tout au démarrage ; dans Kubernetes, il se découpe en Jobs (une fois) et en Deployment (en continu).

Dossier à créer : `kubernetes/rawdata_zone/openstackKeystone/` avec `create_conf.sh`, `pods/`, `services/`, `network/`, `.gitignore` (`volumes/`). Supprimer les fichiers Kompose de ce dossier.

1. **MariaDB**
    - StatefulSet `mariadb`, 1 réplica, image `mariadb` (10.9 comme le Compose, ou une version LTS plus récente : à décider).
    - `volumeClaimTemplates` : une classe de disque pour la base (`local-path` de k3s pour commencer, ou une classe dédiée créée comme `swift-disks`).
    - Secret `mariadb-env` : `MYSQL_ROOT_PASSWORD`, `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD` depuis `conf.env`.
    - Probe : `exec` de `healthcheck.sh --connect --innodb_initialized`, comme le healthcheck du Compose.
    - Service `mariadb:3306` ; NetworkPolicy ouverte à Keystone seul (et Keycloak s'il utilise cette base).
2. **Image Keystone** : `rawdata_zone/openstackKeystone/build.sh` (LOCI) produit `keystone:2026.1-ubuntu_noble`. L'ajouter à `start.sh -b`, suivie de `docker save | sudo k3s ctr images import -`.
3. **Configuration** (`create_conf.sh`) :
    - Secret `keystone-conf` : `keystone.conf`, qui contient le mot de passe de la base dans `[database] connection`.
    - ConfigMap : `ports.conf`, `sites-available/keystone.conf`, `wsgi.py`, `policy.yaml`, `init-keystone.sh`.
    - Variables OIDC (`FEDERATION_ENABLED`, `KEYCLOAK_ISSUER`, `KEYCLOAK_JWKS_URI`, `KEYSTONE_PUBLIC_URL`…) en ConfigMap ; `OIDC_CRYPTO_PASSPHRASE` et `KEYCLOAK_CLIENT_SECRET` en Secret.
4. **Clés fernet et credential** : reprendre celles déjà générées dans `rawdata_zone/openstackKeystone/conf/etc/keystone/` et les mettre en Secrets, montés dans tous les pods Keystone :

    ```bash
    kubectl -n datalake create secret generic keystone-fernet-keys \
      --from-file=rawdata_zone/openstackKeystone/conf/etc/keystone/fernet-keys/ \
      --dry-run=client -o yaml > kubernetes/rawdata_zone/openstackKeystone/volumes/secret_keystone_fernet.yml
    ```

    Idem pour `credential-keys`. Les clés credential chiffrent des données de la base : ne jamais les changer sur une base existante.
5. **Job `keystone-db-sync`** : `keystone-manage db_sync`, puis `keystone-manage bootstrap` (admin, région `RegionOne`, endpoints Keystone). Un Job ne se modifie pas : `kubectl delete job keystone-db-sync --ignore-not-found` avant chaque `apply`.
6. **Deployment `keystone`** : `init-keystone.sh` sans les lignes `keystone-manage` (partie OIDC + `exec apache2ctl -D FOREGROUND`). Label `app.kubernetes.io/name: keystone` (la NetworkPolicy de memcached l'attend). Probe `GET /healthcheck` sur le port 5000. Le script modifie `/etc/apache2` au démarrage : système de fichiers en lecture seule impossible au début, et peut-être root (accepté par `baseline`).
7. **Job `keystone-bootstrap`** : l'image de `Dockerfile.openstackClientBootstrap` avec `bootstrap_keystone.sh` (utilisateur `swift`, endpoints, fédération Keycloak).
8. **Service `keystone:5000`** et NetworkPolicy : depuis `flask-app`, `swift-proxy`, les Jobs, Horizon. Le navigateur doit aussi joindre Keystone pour la fédération (redirection OIDC vers `KEYSTONE_PUBLIC_URL`) : il faut donc une exposition publique.
9. **Ordre dans `start.sh -r`** : MariaDB → attendre ; Job db-sync → `kubectl wait --for=condition=complete job/keystone-db-sync --timeout=300s` ; Deployment Keystone → attendre ; Job bootstrap.
10. **Côté Swift** : URL publique de Keystone dans `www_authenticate_uri` (`create_conf.sh` de Swift), `service_token_roles_required = true`.

Valeurs à changer par rapport au Compose :

| Où | Compose | Kubernetes |
| --- | --- | --- |
| `bootstrap_keystone.sh`, `SWIFT_INTERNAL` | `http://management-1:8080/v1/AUTH_$(tenant_id)s` | `http://swift-proxy:8080/v1/AUTH_$(tenant_id)s` |
| `bootstrap_keystone.sh`, `SWIFT_ADMIN` | `http://management-1:8080` | `http://swift-proxy:8080` |
| `bootstrap_keystone.sh`, `SWIFT_PUBLIC` | `http://management-1:8080/v1/AUTH_$(tenant_id)s` | URL publique du proxy si exposé, sinon l'interne |
| `init-keystone.sh`, admin URL du bootstrap | `http://keystone:35357/v3` | `http://keystone:5000/v3` |
| `keystone.conf`, `[database]` et `[cache]` | `mariadb`, `memcached:11211` | Inchangés, si les Services portent ces noms |
| `KEYCLOAK_JWKS_URI` | `http://keycloak:8080/realms/…` | Inchangé, si le Service s'appelle `keycloak` |

Test : `kubectl -n datalake port-forward svc/keystone 5000:5000`, puis `openstack --os-auth-url http://localhost:5000/v3 --os-username admin --os-project-name admin --os-user-domain-name Default --os-project-domain-name Default token issue`. Avec ce token, créer un container et un objet Swift par le proxy (`curl -X PUT -H "X-Auth-Token: <token>" …`).

## Procédure : Keycloak

Keycloak est le seul service, avec nginx, que le navigateur joint directement : son URL publique doit être fixée avant de le déployer.

1. **Choisir le mode.**
    - *Dev* : `start-dev --import-realm`, comme le Compose, avec une base embarquée dans `/opt/keycloak/data` (sur un PVC pour qu'elle survive).
    - *Production* : `start --import-realm`, avec une base externe (`KC_DB`, `KC_DB_URL`, `KC_DB_USERNAME`, `KC_DB_PASSWORD`), `KC_HOSTNAME` = l'URL publique, `KC_PROXY_HEADERS=xforwarded` derrière un proxy TLS.
2. **Realm** : le JSON généré par le `create_conf.sh` racine (`rawdata_zone/openstackKeycloak/realm/`) devient une ConfigMap montée dans `/opt/keycloak/data/import`. `--import-realm` ne l'importe que si le realm n'existe pas encore.
3. **Variables** : `KC_BOOTSTRAP_ADMIN_USERNAME` et `KC_BOOTSTRAP_ADMIN_PASSWORD` en Secret ; `KC_HOSTNAME`, `KC_HTTP_ENABLED`, `KC_HOSTNAME_BACKCHANNEL_DYNAMIC`, `KC_HEALTH_ENABLED` en ConfigMap, avec les valeurs du Compose.
4. **Deployment `keycloak`**, 1 réplica (plusieurs réplicas demandent une config de cache partagé). Probes sur `/health/ready` et `/health/live` : dans les versions récentes, elles sont servies sur le port de management 9000, pas sur 8080 (à vérifier dans les logs au démarrage).
5. **Exposition** : Service `keycloak:8080` en interne ; pour le navigateur, un LoadBalancer sur 8088 (comme le `8088:8080` du Compose) ou un Ingress. L'URL publique doit être identique partout : `KC_HOSTNAME`, `KEYCLOAK_PUBLIC_URL`, `KEYCLOAK_ISSUER`.
6. **NetworkPolicy** : entrée depuis `flask-app` et `keystone` (récupération des clés et échange de tokens), plus le trafic public.
7. **Test** : console d'administration ouverte, realm importé, puis connexion SSO depuis la web GUI de bout en bout.

## Procédure : JupyterHub

JupyterHub change le plus : DockerSpawner (qui pilote Docker par son socket) est remplacé par KubeSpawner, qui crée un pod par utilisateur.

1. **Choisir l'outil.** Le chart Helm officiel *Zero to JupyterHub* fournit déjà KubeSpawner, le proxy, les droits RBAC, un disque par utilisateur et des NetworkPolicies. Il s'installe sans le client `helm`, par un objet `HelmChart` de k3s, comme Headlamp dans `installK3S.sh`. L'alternative est d'écrire les manifests à la main.
2. **Namespace séparé** (par exemple `jupyter`, zone process) : les notebooks exécutent du code utilisateur et ne doivent pas tourner dans `datalake`.
3. **Image du hub** : `FROM` l'image hub du chart + `COPY datalake_authenticator.py` (l'authentificateur `FlaskLocalAuthenticator`), construite et importée comme les autres.
4. **Image des notebooks** : `cors_base-notebook`, construite depuis `process_zone/jupyter/Dockerfile.jupyterserver` et importée dans k3s.
5. **Ce qui disparaît de `jupyterhub_config.py`** : les réglages `DockerSpawner`, `network_name`, `hub_connect_ip = '10.5.100.1'`, les volumes Docker. La base SQLite et le cookie secret sont gérés par le chart.
6. **Ce qui reste** : `base_url = '/hub/'`, l'authentificateur, les templates, l'image des notebooks, le dossier `/home/jovyan/work` (disque par utilisateur, classe `local-path` ou dédiée).
7. **Liens avec le reste** :
    - `JUPYTERHUB_FLASK_URL` = `http://flask-app.datalake.svc.cluster.local:5000` (nom complet, d'un namespace à l'autre).
    - NetworkPolicy de `flask-app` : ajouter un `namespaceSelector` vers `jupyter`, puisque son `podSelector` actuel ne vise que `datalake`.
    - nginx : remettre la route `/hub/` dans `access_zone/create_conf.sh`, vers le Service `proxy-public` du namespace `jupyter`, avec les en-têtes WebSocket.
8. **Test** : `/hub/` par nginx, connexion, lancement d'un notebook, et un pod `jupyter-<utilisateur>` doit apparaître dans le namespace.

## Pièges déjà rencontrés

Chaque ligne vient d'un problème réel de cette migration ; les trois premières sont propres à WSL.

| Symptôme | Cause | Solution |
| --- | --- | --- |
| Le provisioner ne démarre pas : `path "/mnt/disks" is mounted on "/mnt/d" but it is not a shared or slave mount` | WSL : `/mnt/disks` commence par `/mnt/d` (disque D:), et containerd compare les chemins comme du texte | `sudo mount --rbind /mnt/disks /mnt/disks` puis `sudo mount --make-rshared /mnt/disks`, à refaire après chaque redémarrage de WSL |
| `localhost:7000` refusé depuis Windows alors que le Service a une `EXTERNAL-IP` | WSL ne relaie vers Windows que les ports où un programme écoute ; le LoadBalancer de k3s passe par des règles iptables | `kubectl -n datalake port-forward svc/nginx-proxy 7000:7000`, ou l'IP WSL (elle change à chaque redémarrage) |
| `curl localhost:8081` refusé | Le `port-forward` s'est arrêté | Le relancer et laisser son terminal ouvert |
| Pod storage `Pending` : `didn't find available persistent volumes to bind` | Aucun PV assez grand : la PVC demande 90 % de `NODE_STORAGE_SIZE` | Un disque de cette taille (`start.sh -b` les crée) ; vérifier avec `kubectl get pv` |
| `create_rings.sh` dit l'image absente alors qu'elle existe | L'utilisateur n'a pas accès à Docker sans `sudo` | Les scripts passent par `sudo docker` tout seuls ; les lancer sans `sudo` |
| Swift annonce 2.30.1, le tag dit 2.30.0 | `apt-get install` sans version : Debian installe la dernière de bookworm | Décision A ou B (registre des décisions) |
| nginx ne démarre pas : `host not found in upstream` | Un `proxy_pass` vise un Service qui n'existe pas encore | Créer le Service avant, ou retirer la route (cas de `/hub/`) |
| Une ConfigMap modifiée reste sans effet | Variables d'environnement et confs nginx sont lues au démarrage | `kubectl rollout restart` ; `start.sh -br` le fait après un build |
| `field is immutable` en réappliquant un Job | Un Job ne se modifie pas | `kubectl delete job <nom>` puis réappliquer |
| `volumeClaimTemplates` refusé en mise à jour | Champ immuable du StatefulSet | `kubectl delete statefulset <nom> --cascade=orphan`, puis réappliquer |
| `metadata.annotations: Too long` | L'`apply` classique copie l'objet dans une annotation limitée à 256 Ko | `kubectl apply --server-side` |
| PV `Released` après suppression d'une PVC | `reclaimPolicy: Retain` | `kubectl delete pv <nom>` : le disque et ses données restent, un nouveau PV apparaît |
| `ImagePullBackOff` sur une image maison | Image pas importée dans k3s, ou tag `latest` (téléchargement forcé) | `start.sh -b` ; toujours un tag explicite |
| Avertissements `would violate PodSecurity "restricted"` | Le namespace signale (`warn`) ce qui n'est pas encore `restricted` | Normal pour un service pas encore durci ; à corriger avant `enforce: restricted` |
| Logs du proxy : `The option "…" is not known to keystonemiddleware` | keystonemiddleware reçoit toute la section de conf | Aucune action |
| Port 7000 déjà pris | La stack Compose tourne encore | L'arrêter avant de tester Kubernetes |

## Comment décider seul

Huit questions couvrent presque tous les choix de cette migration ; réponds-y pour chaque service avant d'écrire son YAML.

| Question | Si oui | Si non |
| --- | --- | --- |
| Le service garde-t-il des données ou une identité ? | StatefulSet + PVC | Deployment |
| Ses données doivent-elles survivre au pod ? | PVC | `emptyDir` |
| Le navigateur doit-il le joindre ? | LoadBalancer ou Ingress, et une URL publique fixée | Service ClusterIP seulement |
| Contient-il un mot de passe, une clé, un token ? | Secret, généré dans `volumes/` | ConfigMap |
| Peut-il tourner sans root et sans écrire dans son image ? | `restricted` : non-root, lecture seule, `drop: [ALL]` | Noter l'exception, rester en `baseline`, prévoir de la retirer |
| Exécute-t-il du code d'utilisateurs ? | Hors du namespace `datalake`, NetworkPolicy fermante, quotas | Dans `datalake` |
| Ses données sont-elles déjà répliquées (Swift) ? | Disque local suffisant | Sauvegarde à prévoir (dump, snapshot) |
| Le choix est-il difficile à défaire ? | Prendre le temps (voir ci-dessous) | Choisir le plus simple et avancer |

Ce qui est difficile ou impossible à changer après coup :

- **`SWIFT_HASH_PREFIX` et `SWIFT_HASH_SUFFIX`** : jamais, sous peine de rendre toutes les données introuvables.
- **`SWIFT_PART_POWER`** : très difficile une fois des données écrites.
- **Les UID** d'un service qui a déjà écrit des fichiers : `chown` de tout le disque.
- **Le `selector` et les `volumeClaimTemplates`** : suppression et recréation de l'objet.
- **Les noms** de namespace, de Service et de StorageClass : tout ce qui les référence est à refaire.
- **Les clés credential de Keystone** sur une base existante.

## Documentation officielle

En cas de doute, la documentation officielle fait foi ; `kubectl explain <objet>.<champ>` donne la même définition depuis le cluster.

| Sujet | Lien |
| --- | --- |
| Concepts Kubernetes (Pods, workloads, Services, stockage) | [kubernetes.io/docs/concepts](https://kubernetes.io/docs/concepts/) |
| Aide-mémoire `kubectl` | [kubectl quick reference](https://kubernetes.io/docs/reference/kubectl/quick-reference/) |
| StatefulSet | [StatefulSets](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/) |
| Volumes persistants et classes | [Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/) |
| NetworkPolicy | [Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/) |
| Niveaux de sécurité des pods | [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/) |
| Labels recommandés | [Recommended Labels](https://kubernetes.io/docs/concepts/overview/working-with-objects/common-labels/) |
| k3s (installation, ServiceLB, etcd, Helm intégré) | [docs.k3s.io](https://docs.k3s.io/) |
| Local static provisioner | [sig-storage-local-static-provisioner](https://github.com/kubernetes-sigs/sig-storage-local-static-provisioner) |
| OpenStack Swift | [docs.openstack.org/swift](https://docs.openstack.org/swift/latest/) |
| OpenStack Keystone | [docs.openstack.org/keystone](https://docs.openstack.org/keystone/latest/) |
| Keycloak en production | [Configuring Keycloak for production](https://www.keycloak.org/server/configuration-production) |
| JupyterHub sur Kubernetes | [Zero to JupyterHub](https://z2jh.jupyter.org/) |
| Image MariaDB | [mariadb sur Docker Hub](https://hub.docker.com/_/mariadb) |

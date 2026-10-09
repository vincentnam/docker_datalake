#!/usr/bin/env bash
# k3s-lab.sh — installation, test et désinstallation propre de k3s
#
# Usage : ./k3s-lab.sh install     inventaire avant + config + install + attente + test + GUI
#         ./k3s-lab.sh test        test de bout en bout (nginx exposé par Traefik)
#         ./k3s-lab.sh gui         jeton + accès à Headlamp sur http://localhost:8080
#         ./k3s-lab.sh uninstall   désinstallation + nettoyage des résidus + vérification
#         ./k3s-lab.sh verifier    inventaire après + traces réseau / iptables / montages
#
# Variables surchargeables : K3S_VERSION, INV_DIR, INSTALL_GUI (1/0), GUI_PORT
#   ex. : K3S_VERSION=v1.36.5+k3s1 INSTALL_GUI=0 ./k3s-lab.sh install
set -euo pipefail

K3S_VERSION="${K3S_VERSION:-v1.36.4+k3s1}"
INV_DIR="${INV_DIR:-$HOME/k3s-inventaires}"
INSTALL_GUI="${INSTALL_GUI:-1}"
GUI_PORT="${GUI_PORT:-8080}"
CONFIG_FILE=/etc/rancher/k3s/config.yaml
K3S_KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# Résidus connus que k3s-uninstall.sh ne supprime pas
RESIDUS_CONNUS=(/var/log/pods /var/log/containers /usr/libexec/kubernetes)

# ---------------------------------------------------------------- utilitaires
info() { printf '\033[1;34m[i]\033[0m %s\n' "$*"; }
ok()   { printf '\033[1;32m[ok]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[!]\033[0m %s\n' "$*"; }
die()  { printf '\033[1;31m[x]\033[0m %s\n' "$*" >&2; exit 1; }

K() { kubectl --kubeconfig "$K3S_KUBECONFIG" "$@"; }

# attendre <description> <timeout_s> <commande...>
attendre() {
  local desc=$1 timeout=$2; shift 2
  local fin=$((SECONDS + timeout))
  until "$@" >/dev/null 2>&1; do
    (( SECONDS < fin )) || die "Timeout ($timeout s) : $desc"
    sleep 2
  done
}

# inventaire <fichier> : liste triée de tout le système de fichiers racine
inventaire() {
  { sudo find / -xdev \
      -path /proc -prune -o -path /home -prune -o -path /mnt -prune -o \
      -path /var/log/journal -prune -o -path '*systemd-private*' -prune -o \
      -print 2>/dev/null || true; } | sort > "$1"
}

# ---------------------------------------------------------------- vérifications
preflight() {
  [[ $EUID -ne 0 ]] || die "Lance le script avec ton utilisateur : il appelle sudo lui-même."
  command -v curl >/dev/null || die "curl manquant : sudo apt install curl"

  if grep -qi microsoft /proc/version && ! grep -qi wsl2 /proc/version; then
    die "WSL1 détecté : k3s nécessite WSL2."
  fi
  [[ "$(ps -p 1 -o comm=)" == systemd ]] \
    || die "systemd n'est pas actif (voir [boot] systemd=true dans /etc/wsl.conf, puis wsl --shutdown)."

  if command -v k3s >/dev/null || [[ -e /usr/local/bin/k3s-uninstall.sh ]]; then
    die "k3s semble déjà installé : lance d'abord './k3s-lab.sh uninstall'."
  fi

  if sudo ss -ltnH 'sport = :80 or sport = :443' | grep -q .; then
    warn "Les ports 80/443 sont déjà utilisés : Traefik ne pourra pas les prendre."
    sudo ss -ltnp 'sport = :80 or sport = :443' || true
  fi
}

# ---------------------------------------------------------------- commandes
cmd_install() {
  preflight
  mkdir -p "$INV_DIR"

  info "Inventaire du système avant installation (une à deux minutes)…"
  inventaire "$INV_DIR/avant.txt"
  ok "Inventaire : $INV_DIR/avant.txt ($(wc -l < "$INV_DIR/avant.txt") entrées)"

  info "Écriture de $CONFIG_FILE"
  sudo mkdir -p "$(dirname "$CONFIG_FILE")"
  sudo tee "$CONFIG_FILE" >/dev/null <<'EOF'
write-kubeconfig-mode: "0644"   # pratique en test, à retirer en prod
cluster-init: true              # etcd embarqué, comme en prod
secrets-encryption: true        # Secrets chiffrés au repos
EOF

  info "Installation de k3s $K3S_VERSION…"
  curl -sfL https://get.k3s.io | sudo INSTALL_K3S_VERSION="$K3S_VERSION" sh -

  info "Attente de l'API et du nœud…"
  attendre "API k3s joignable" 180 test -r "$K3S_KUBECONFIG"
  attendre "API k3s joignable" 180 K get nodes
  K wait --for=condition=Ready node --all --timeout=180s >/dev/null
  ok "Nœud prêt"

  info "Attente des composants intégrés…"
  for d in coredns local-path-provisioner metrics-server traefik; do
    attendre "déploiement $d créé" 300 K -n kube-system get deploy "$d"
    K -n kube-system rollout status deploy/"$d" --timeout=300s >/dev/null
    ok "$d disponible"
  done

  # Kubeconfig utilisateur, sans écraser une config existante
  mkdir -p ~/.kube
  if [[ -e ~/.kube/config ]]; then
    cp "$K3S_KUBECONFIG" ~/.kube/k3s.yaml && chmod 600 ~/.kube/k3s.yaml
    echo ~/.kube/k3s.yaml > "$INV_DIR/kubeconfig-copie"
    warn "~/.kube/config existe déjà : kubeconfig copié dans ~/.kube/k3s.yaml"
    warn "Utilise : export KUBECONFIG=~/.kube/k3s.yaml"
  else
    cp "$K3S_KUBECONFIG" ~/.kube/config && chmod 600 ~/.kube/config
    echo ~/.kube/config > "$INV_DIR/kubeconfig-copie"
    ok "Kubeconfig copié dans ~/.kube/config"
  fi

  cmd_test
  ok "k3s $K3S_VERSION installé et fonctionnel"

  if [[ "$INSTALL_GUI" == 1 ]]; then
    installer_gui
    info "Pour ouvrir l'interface : ./k3s-lab.sh gui"
  fi
}

installer_gui() {
  info "Installation de Headlamp (web GUI) via le contrôleur Helm de k3s…"
  # Le chart crée lui-même le compte 'headlamp' et sa ClusterRoleBinding 'headlamp-admin'
  # (cluster-admin) : ne pas créer d'objets portant ces noms à la main.
  # En prod : clusterRoleBinding.create: false dans valuesContent + OIDC Keycloak.
  K apply -f - >/dev/null <<'EOF'
apiVersion: helm.cattle.io/v1
kind: HelmChart
metadata:
  name: headlamp
  namespace: kube-system
spec:
  repo: https://kubernetes-sigs.github.io/headlamp/
  chart: headlamp
  targetNamespace: kube-system
EOF

  attendre "job helm-install-headlamp créé" 120 K -n kube-system get job helm-install-headlamp
  if ! K -n kube-system wait --for=condition=complete job/helm-install-headlamp \
         --timeout=300s >/dev/null 2>&1; then
    K -n kube-system logs job/helm-install-headlamp --tail=20 || true
    die "Installation de Headlamp échouée (logs ci-dessus)"
  fi
  attendre "déploiement headlamp créé" 120 K -n kube-system get deploy headlamp
  K -n kube-system rollout status deploy/headlamp --timeout=300s >/dev/null
  ok "Headlamp disponible"
}

cmd_gui() {
  K -n kube-system get deploy headlamp >/dev/null 2>&1 \
    || die "Headlamp n'est pas installé (INSTALL_GUI=1 ./k3s-lab.sh install)"

  info "Jeton de connexion (valable 1 h) :"
  echo
  K -n kube-system create token headlamp
  echo
  info "Interface : http://localhost:$GUI_PORT  (Ctrl+C pour arrêter)"
  exec kubectl --kubeconfig "$K3S_KUBECONFIG" -n kube-system \
    port-forward svc/headlamp "$GUI_PORT":80
}

cmd_test() {
  info "Test : nginx exposé par Traefik…"
  K create deployment web-test --image=nginx --dry-run=client -o yaml | K apply -f - >/dev/null
  K expose deployment web-test --port=80 --dry-run=client -o yaml | K apply -f - >/dev/null
  K create ingress web-test --rule="web-test.localhost/*=web-test:80" \
    --dry-run=client -o yaml | K apply -f - >/dev/null
  K rollout status deploy/web-test --timeout=180s >/dev/null

  local reussi=0
  for _ in $(seq 1 30); do
    if curl -sf -H "Host: web-test.localhost" http://localhost | grep -q "Welcome to nginx"; then
      reussi=1; break
    fi
    sleep 2
  done

  K delete ingress,service,deployment web-test --ignore-not-found >/dev/null
  (( reussi )) || die "nginx injoignable via Traefik (vérifie : K -n kube-system get svc traefik)"
  ok "Chemin complet OK : curl → Traefik → Service → Pod"
}

cmd_uninstall() {
  [[ -x /usr/local/bin/k3s-uninstall.sh ]] || die "k3s-uninstall.sh introuvable : k3s n'est pas installé ?"

  info "Désinstallation de k3s…"
  sudo /usr/local/bin/k3s-uninstall.sh

  info "Nettoyage des résidus connus…"
  for p in "${RESIDUS_CONNUS[@]}"; do
    [[ -e $p ]] || continue
    if [[ -f "$INV_DIR/avant.txt" ]] && grep -qx "$p" "$INV_DIR/avant.txt"; then
      warn "$p existait avant k3s : conservé"
    else
      sudo rm -rf "$p" && ok "Supprimé : $p"
    fi
  done

  if [[ -f "$INV_DIR/kubeconfig-copie" ]]; then
    rm -f "$(cat "$INV_DIR/kubeconfig-copie")" "$INV_DIR/kubeconfig-copie"
    ok "Kubeconfig utilisateur supprimé"
  fi

  cmd_verifier
}

cmd_verifier() {
  local propre=1

  if [[ -f "$INV_DIR/avant.txt" ]]; then
    info "Inventaire après désinstallation…"
    inventaire "$INV_DIR/apres.txt"
    comm -13 "$INV_DIR/avant.txt" "$INV_DIR/apres.txt" > "$INV_DIR/residus.txt"
    if [[ -s "$INV_DIR/residus.txt" ]]; then
      propre=0
      warn "$(wc -l < "$INV_DIR/residus.txt") nouveaux chemins (liste : $INV_DIR/residus.txt) :"
      head -n 30 "$INV_DIR/residus.txt"
    else
      ok "Aucun fichier ni dossier résiduel"
    fi
  else
    warn "Pas d'inventaire 'avant' : comparaison des fichiers impossible"
  fi

  if ip -o link | grep -qE 'cni0|flannel'; then
    propre=0; warn "Interfaces réseau restantes :"; ip -o link | grep -E 'cni0|flannel'
  else
    ok "Aucune interface cni0/flannel"
  fi

  local n
  n=$(sudo iptables-save 2>/dev/null | grep -ciE 'kube|cni|flannel' || true)
  if (( n > 0 )); then
    propre=0; warn "$n règles iptables liées à k3s restantes"
  else
    ok "Aucune règle iptables k3s"
  fi

  if mount | grep -qE 'kubelet|k3s'; then
    propre=0; warn "Montages restants :"; mount | grep -E 'kubelet|k3s'
  else
    ok "Aucun montage kubelet/k3s"
  fi

  (( propre )) && ok "Système revenu à l'état initial" || warn "Des traces subsistent (voir ci-dessus)"
}

# ---------------------------------------------------------------- point d'entrée
case "${1:-}" in
  install)   cmd_install ;;
  test)      cmd_test ;;
  gui)       cmd_gui ;;
  uninstall) cmd_uninstall ;;
  verifier)  cmd_verifier ;;
  *) sed -n '2,11p' "$0" | sed 's/^# \{0,1\}//'; exit 1 ;;
esac
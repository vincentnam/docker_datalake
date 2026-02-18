script.sh : build + docker compose

#TODO : finish config (connection Horizon to keystone test + Swift connection)
#TODO : Refactor folders (keystone = python wsgi.py lib ; horizon = apache2 conf ; etc/apache2 = keystone apache 2 conf ; etc/horizon = horizon python conf -> unmaintanable, not logic, need refactor)



Refactored : 2 folder : 
- Apache : for apache configuration
- etc : for all configuration, both in /etc/ folder or other location 













# POUR PASSER A LA FEDERATION :

keystone.conf
[auth]
methods = password,token,openid

[federation]
remote_id_attribute = HTTP_OIDC_ISS
trusted_dashboard = https://<VOTRE_HORIZON_URL>/auth/websso/



apache2/sites-available/keystone.conf


<VirtualHost *:5000>
    # ... (config WSGI existante) ...

    OIDCProviderMetadataURL https://<KEYCLOAK_URL>/auth/realms/<REALM>/.well-known/openid-configuration
    OIDCClientID keystone-client
    OIDCClientSecret <VOTRE_SECRET>
    OIDCRedirectURI https://<KEYSTONE_URL>:5000/v3/OS-FEDERATION/identity_providers/keycloak/protocols/openid/auth/redirect
    OIDCCryptoPassphrase une_phrase_secrete_aleatoire

    # On protège l'endpoint de fédération
    <Location ~ "/v3/OS-FEDERATION/identity_providers/keycloak/protocols/openid/auth">
        AuthType openid-connect
        Require valid-user
    </Location>
</VirtualHost>



mapping.json :


[
    {
        "local": [
            {
                "group": {
                    "name": "{0}",
                    "domain": { "name": "Default" }
                }
            }
        ],
        "remote": [
            {
                "type": "HTTP_OIDC_GROUPS"
            }
        ]
    }
]


Keycloak, les opérations à faire :

# 1. Créer le mapping
openstack mapping create --rules mapping_rules.json keycloak_mapping

# 2. Créer l'Identity Provider (IdP)
openstack identity provider create --remote-id https://<KEYCLOAK_URL>/auth/realms/<REALM> keycloak

# 3. Lier le protocole, l'IdP et le mapping
openstack federation protocol create openid --mapping keycloak_mapping --identity-provider keycloak











# Le script pour synchroniser les groupes Keycloak avec Keystone

import openstack
from keycloak import KeycloakAdmin

# --- CONFIGURATION ---
KEYCLOAK_URL = "https://keycloak.example.com/auth/"
KEYCLOAK_REALM = "mon-realm"
KEYCLOAK_USER = "admin-keycloak"
KEYCLOAK_PASS = "password"
OPENSTACK_CLOUD = "admin-openstack" # Nom dans votre clouds.yaml

# 1. Connexion à Keycloak
keycloak_admin = KeycloakAdmin(server_url=KEYCLOAK_URL,
                               username=KEYCLOAK_USER,
                               password=KEYCLOAK_PASS,
                               realm_name=KEYCLOAK_REALM,
                               verify=True)

# 2. Connexion à OpenStack
conn = openstack.connect(cloud=OPENSTACK_CLOUD)

# 3. Récupérer tous les groupes de Keycloak
kc_groups = keycloak_admin.get_groups()

print("Synchronisation en cours...")

for group in kc_groups:
    group_name = group['name']
    
    # On filtre (optionnel) : ne traiter que les groupes qui commencent par "projet-"
    if not group_name.startswith("projet-"):
        continue

    # 4. Vérifier si le projet existe déjà dans OpenStack
    os_project = conn.identity.find_project(group_name)

    if os_project:
        print(f"[OK] Le projet '{group_name}' existe déjà.")
    else:
        # 5. Créer le projet s'il n'existe pas
        print(f"[CRÉATION] Projet '{group_name}' introuvable. Création en cours...")
        try:
            new_project = conn.identity.create_project(name=group_name, domain_id="default")
            print(f" -> Projet '{group_name}' créé avec l'ID {new_project.id}")
        except Exception as e:
            print(f" -> Erreur lors de la création de '{group_name}': {e}")

print("Synchronisation terminée.")
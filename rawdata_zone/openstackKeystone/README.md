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
trusted_dashboard = https://horizon/auth/websso/



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
        "user": {
          "name": "{0}",
          "email": "{1}"
        }
      },
      {
        "group": {
          "name": "{2}",
          "domain": { "name": "Default" }
        }
      }
    ],
    "remote": [
      { "type": "HTTP_OIDC_PREFERRED_USERNAME" },
      { "type": "HTTP_OIDC_EMAIL" },
      { "type": "HTTP_OIDC_GROUPS" }
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

# CONFIG
KEYCLOAK_URL = "https://VOTRE_IP:7000/keycloak/"
REALM = "mon-realm"
KC_USER = "admin"
KC_PASS = "adminpassword"
OPENSTACK_CLOUD = "admin"

keycloak_admin = KeycloakAdmin(server_url=KEYCLOAK_URL,
                               username=KC_USER,
                               password=KC_PASS,
                               realm_name=REALM,
                               verify=False)  # ou True avec cert

conn = openstack.connect(cloud=OPENSTACK_CLOUD)

print("🔄 Synchronisation Keycloak → OpenStack...")

for group in keycloak_admin.get_groups():
    name = group['name']
    if not name.startswith("projet-"):
        continue

    # Projet
    project = conn.identity.find_project(name)
    if not project:
        project = conn.identity.create_project(name=name, domain_id="default")
        print(f" Projet créé : {name}")

    # Groupe Keystone (même nom)
    keystone_group = conn.identity.find_group(name, domain_id="default")
    if not keystone_group:
        keystone_group = conn.identity.create_group(name=name, domain_id="default")
        print(f" Groupe Keystone créé : {name}")

    # Rôle member sur le projet
    role = conn.identity.find_role("member")
    conn.identity.assign_role_to_group_on_project(
        role.id, keystone_group.id, project.id
    )
    print(f" Rôle member assigné à {name}")

print(" Synchronisation terminée !")
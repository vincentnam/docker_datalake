#!/bin/bash


export $(grep -v '^#' ./conf.env | sed 's/\r$//' | xargs)
OPENSTACKSWIFT_PATH="./rawdata_zone/openstackSwift"
OPENSTACKKEYSTONE_PATH="./rawdata_zone/openstackKeystone"
OPENSTACKKEYCLOAK_PATH="./rawdata_zone/openstackKeycloak"


JUPYTER_PATH="./process_zone/jupyter"
WEBGUI_PATH="./access_zone/web_gui"
REST_API_PATH="./access_zone/flask"
NGINX_PATH="./access_zone/nginx"

# Derive the OIDC issuer from the *public* Keycloak URL + realm unless the user
# pinned an explicit one (e.g. legacy /auth/realms/<realm> layout). The issuer
# must match the URL the browser logs in through (KC_HOSTNAME is pinned to it).
KEYCLOAK_ISSUER="${KEYCLOAK_ISSUER:-${KEYCLOAK_PUBLIC_URL%/}/realms/${KEYCLOAK_REALM}}"

# Browser-reachable OIDC redirect URI : Keycloak sends the user back here after
# login. It targets the Flask SSO callback through the nginx proxy (/api).
KEYCLOAK_REDIRECT_URI="${WEB_GUI_URL%/}/api/auth/callback"



###################################
# OPENSTACK SWIFT
###################################

cat << EOF > $OPENSTACKSWIFT_PATH/config_cluster.env
NB_MANAGEMENT_NODE=$NB_MANAGEMENT_NODE
NB_STORAGE_NODE=$NB_STORAGE_NODE
NODE_STORAGE_SIZE="$NODE_STORAGE_SIZE"
SWIFT_PASSWORD="$SWIFT_PASSWORD"
SWIFT_HASH_PREFIX="$SWIFT_HASH_PREFIX"
SWIFT_HASH_SUFFIX="$SWIFT_HASH_SUFFIX"
SWIFT_PART_POWER=$SWIFT_PART_POWER
SWIFT_MIN_PART_HOURS=$SWIFT_MIN_PART_HOURS
EOF


####################################
## WEB GUI SECTION
####################################
cat << EOF > $WEBGUI_PATH/.env

REACT_APP_JUPYTERHUB_URL="$REACT_APP_JUPYTERHUB_URL"
REACT_APP_JUPYTERHUB_TOKEN="$REACT_APP_JUPYTERHUB_TOKEN"
REACT_APP_FLASK_APP_URL="$REACT_APP_FLASK_APP_URL"


EOF
####################################
## REST API SECTION / ACCESS TO SERVICES
####################################

cat << EOF > $REST_API_PATH/.env


# AUTH CONF
FEDERATION_ENABLED="$FEDERATION_ENABLED"
KEYCLOAK_URL="$KEYCLOAK_URL"
KEYCLOAK_PUBLIC_URL="$KEYCLOAK_PUBLIC_URL"
KEYCLOAK_ISSUER="$KEYCLOAK_ISSUER"
KEYCLOAK_REALM="$KEYCLOAK_REALM"
KEYCLOAK_CLIENT_ID="$KEYCLOAK_CLIENT_ID"
KEYCLOAK_CLIENT_SECRET="$KEYCLOAK_CLIENT_SECRET"
KEYCLOAK_REDIRECT_URI="$KEYCLOAK_REDIRECT_URI"
KEYCLOAK_IDP_ID="$KEYCLOAK_IDP_ID"
KEYCLOAK_PROTOCOL_ID="$KEYCLOAK_PROTOCOL_ID"
FEDERATED_PROJECT="$FEDERATED_PROJECT"
FEDERATED_DOMAIN="$FEDERATED_DOMAIN"
IDP_READER_USER="$IDP_READER_USER"
IDP_READER_PASSWORD="$IDP_READER_PASSWORD"
IDP_READER_PROJECT="service"
KEYSTONE_URL="$KEYSTONE_URL"
WEB_GUI_URL="$WEB_GUI_URL"
FLASK_SECRET="$FLASK_SECRET"
EOF

####################################
## KEYCLOAK REALM SECTION
####################################
# Render the realm imported by the bundled Keycloak container so that the
# Keystone OIDC client (id/secret/redirect URIs) and a sample user/group match
# the values configured in conf.env. Skipped when reusing an external Keycloak.
if [ "${DEPLOY_KEYCLOAK,,}" = "true" ]; then
  mkdir -p "$OPENSTACKKEYCLOAK_PATH/realm"
  cat << EOF > "$OPENSTACKKEYCLOAK_PATH/realm/datalake-realm.json"
{
  "realm": "$KEYCLOAK_REALM",
  "enabled": true,
  "sslRequired": "none",
  "loginWithEmailAllowed": true,
  "groups": [
    { "name": "$FEDERATED_GROUP" }
  ],
  "users": [
    {
      "username": "$KEYCLOAK_SAMPLE_USER",
      "enabled": true,
      "emailVerified": true,
      "email": "$KEYCLOAK_SAMPLE_USER@datalake.local",
      "firstName": "Datalake",
      "lastName": "User",
      "credentials": [
        { "type": "password", "value": "$KEYCLOAK_SAMPLE_PASSWORD", "temporary": false }
      ],
      "groups": [ "/$FEDERATED_GROUP" ]
    }
  ],
  "clients": [
    {
      "clientId": "$KEYCLOAK_CLIENT_ID",
      "enabled": true,
      "protocol": "openid-connect",
      "publicClient": false,
      "secret": "$KEYCLOAK_CLIENT_SECRET",
      "standardFlowEnabled": true,
      "directAccessGrantsEnabled": true,
      "serviceAccountsEnabled": false,
      "redirectUris": [ "$KEYCLOAK_REDIRECT_URI", "${WEB_GUI_URL%/}/*", "${KEYSTONE_PUBLIC_URL%/}/*" ],
      "webOrigins": [ "+" ],
      "attributes": { "post.logout.redirect.uris": "+" },
      "defaultClientScopes": [ "openid", "profile", "email", "roles" ],
      "protocolMappers": [
        {
          "name": "groups",
          "protocol": "openid-connect",
          "protocolMapper": "oidc-group-membership-mapper",
          "consentRequired": false,
          "config": {
            "full.path": "false",
            "id.token.claim": "true",
            "access.token.claim": "true",
            "userinfo.token.claim": "true",
            "claim.name": "groups",
            "multivalued": "true"
          }
        }
      ]
    }
  ]
}
EOF
fi

####################################
## NETWORK SECTION
####################################

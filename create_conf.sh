#!/bin/bash
###################################
# OPENSTACK SWIFT
###################################

export $(grep -v '^#' ./conf.env | sed 's/\r$//' | xargs)


####################################
## WEB GUI SECTION
####################################
cat << EOF > frontend/web_gui/.env

REACT_APP_JUPYTERHUB_URL="$REACT_APP_JUPYTERHUB_URL"
REACT_APP_JUPYTERHUB_TOKEN=f918425567cc42c28c7ab3c55ee90000
REACT_APP_FLASK_APP_URL="$REACT_APP_FLASK_APP_URL"


EOF
####################################
## REST API SECTION / ACCESS TO SERVICES
####################################

cat << EOF > RESTapi/flask/.env


# AUTH CONF
KEYCLOAK_ISSUER="$KEYCLOAK_ISSUER"
KEYCLOAK_REALM="$KEYCLOAK_REALM"
KEYCLOAK_CLIENT_ID="$KEYCLOAK_CLIENT_ID"
KEYCLOAK_CLIENT_SECRET="$KEYCLOAK_CLIENT_SECRET"

EOF

####################################
## NETWORK SECTION
####################################

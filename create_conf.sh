#!/bin/bash


export $(grep -v '^#' ./conf.env | sed 's/\r$//' | xargs)
OPENSTACKSWIFT_PATH="./rawdata_zone/openstackSwift"
OPENSTACKKEYSTONE_PATH="./rawdata_zone/openstackKeystone"


JUPYTER_PATH="./process_zone/jupyter"
WEBGUI_PATH="./access_zone/web_gui"
REST_API_PATH="./access_zone/flask"
NGINX_PATH="./access_zone/nginx"



###################################
# OPENSTACK SWIFT
###################################

cat << EOF > $OPENSTACKSWIFT_PATH/config_cluster.env
NB_MANAGEMENT_NODE=$NB_MANAGEMENT_NODE
NB_STORAGE_NODE=$NB_STORAGE_NODE
NODE_STORAGE_SIZE="$NODE_STORAGE_SIZE"
EOF


####################################
## WEB GUI SECTION
####################################
cat << EOF > $WEBGUI_PATH/.env

REACT_APP_JUPYTERHUB_URL="$REACT_APP_JUPYTERHUB_URL"
REACT_APP_JUPYTERHUB_TOKEN=f918425567cc42c28c7ab3c55ee90000
REACT_APP_FLASK_APP_URL="$REACT_APP_FLASK_APP_URL"


EOF
####################################
## REST API SECTION / ACCESS TO SERVICES
####################################

cat << EOF > $REST_API_PATH/.env


# AUTH CONF
KEYCLOAK_ISSUER="$KEYCLOAK_ISSUER"
KEYCLOAK_REALM="$KEYCLOAK_REALM"
KEYCLOAK_CLIENT_ID="$KEYCLOAK_CLIENT_ID"
KEYCLOAK_CLIENT_SECRET="$KEYCLOAK_CLIENT_SECRET"
KEYSTONE_URL="$KEYSTONE_URL"
EOF

####################################
## NETWORK SECTION
####################################

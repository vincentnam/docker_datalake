#!/bin/bash
###################################
# OPENSTACK SWIFT
###################################

export $(grep -v '^#' ./conf.env | sed 's/\r$//' | xargs)


####################################
## WEB GUI SECTION
####################################
cat << EOF > frontend/web_gui/.env

REACT_APP_JUPYTERHUB_URL=http://localhost:8000
REACT_APP_JUPYTERHUB_TOKEN=f918425567cc42c28c7ab3c55ee90000
REACT_APP_FLASK_APP_URL=http://localhost:7000


EOF
####################################
## REST API SECTION / ACCESS TO SERVICES
####################################

cat << EOF > RESTapi/flask/.env

FLASK_PORT=7000

# AUTH CONF
KEYCLOAK_ISSUER="https://neosso.univ-tlse3.fr/"
KEYCLOAK_REALM="MIDOC"
KEYCLOAK_CLIENT_ID="REST_API"
KEYCLOAK_CLIENT_SECRET="JDlkD6DktrbirbiclJPksQ4wlAabEknT"

EOF

####################################
## NETWORK SECTION
####################################

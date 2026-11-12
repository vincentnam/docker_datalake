#!/bin/bash
set -euo pipefail

export $(grep -v '^#' ./conf.env | sed 's/\r$//' | xargs)
KUBE_ROOT_FOLDER="./kubernetes"
MEMCACHED_KUBE_PATH="$KUBE_ROOT_FOLDER/memcached"
OPENSTACKSWIFT_KUBE_PATH="$KUBE_ROOT_FOLDER/rawdata_zone/openstackSwift"
OPENSTACKKEYSTONE_KUBE_PATH="$KUBE_ROOT_FOLDER/rawdata_zone/openstackKeystone"
OPENSTACKKEYCLOAK_KUBE_PATH="$KUBE_ROOT_FOLDER/rawdata_zone/openstackKeycloak"
ACCESS_ZONE_KUBE_PATH="$KUBE_ROOT_FOLDER/access_zone"

export KUBECONFIG="$PWD/k3s.yaml"

# Values of the ${...} placeholders of the pods/ files.
# The storage requests are 90 % of the disk sizes : the filesystem keeps a part of the disk.
export SWIFT_STORAGE_REPLICAS="$NB_STORAGE_NODE"
export SWIFT_PROXY_REPLICAS="$NB_MANAGEMENT_NODE"
export SWIFT_STORAGE_REQUEST="$(( $(numfmt --from=auto "${NODE_STORAGE_SIZE%B}") * 9 / 10 / 1048576 ))Mi"
export MARIADB_STORAGE_REQUEST="$(( $(numfmt --from=auto "${MARIADB_STORAGE_SIZE%B}") * 9 / 10 / 1048576 ))Mi"
export KEYCLOAK_STORAGE_REQUEST="$(( $(numfmt --from=auto "${KEYCLOAK_STORAGE_SIZE%B}") * 9 / 10 / 1048576 ))Mi"
# Same tag as rawdata_zone/openstackKeystone/build.sh and create_docker.sh
export KEYSTONE_TAG="${OPENSTACK_RELEASE_VAR//stable\//}-${BASE_TAG_VAR}"
export APP_TAG="$(git rev-parse --short HEAD)"

# Checksum of the generated conf of each service (volumes/ files), written in its pod template (checksum/config).
# Conf changed = pod template changed = Kubernetes replaces the pods of that service only.
export SWIFT_CONF_HASH="$(cat $OPENSTACKSWIFT_KUBE_PATH/volumes/*.yml | sha256sum | cut -c1-16)"
export MARIADB_CONF_HASH="$(cat $OPENSTACKKEYSTONE_KUBE_PATH/volumes/secret_mariadb_env.yml | sha256sum | cut -c1-16)"
export KEYSTONE_CONF_HASH="$(cat $OPENSTACKKEYSTONE_KUBE_PATH/volumes/*keystone*.yml | sha256sum | cut -c1-16)"
export FLASK_CONF_HASH="$(cat $ACCESS_ZONE_KUBE_PATH/volumes/*flask_env.yml | sha256sum | cut -c1-16)"
export WEB_GUI_CONF_HASH="$(cat $ACCESS_ZONE_KUBE_PATH/volumes/configmap_web_gui_nginx.yml | sha256sum | cut -c1-16)"
export NGINX_PROXY_CONF_HASH="$(cat $ACCESS_ZONE_KUBE_PATH/volumes/configmap_nginx_proxy.yml | sha256sum | cut -c1-16)"
if [ "${DEPLOY_KEYCLOAK,,}" = "true" ]; then
  export KEYCLOAK_CONF_HASH="$(cat $OPENSTACKKEYCLOAK_KUBE_PATH/volumes/*.yml | sha256sum | cut -c1-16)"
fi

VARS='${SWIFT_STORAGE_REPLICAS} ${SWIFT_PROXY_REPLICAS} ${SWIFT_STORAGE_REQUEST} ${MARIADB_VERSION} ${MARIADB_STORAGE_REQUEST} ${KEYSTONE_TAG} ${KEYCLOAK_VERSION} ${KEYCLOAK_STORAGE_REQUEST} ${KEYCLOAK_HOST_PORT} ${APP_TAG}'
VARS="$VARS"' ${SWIFT_CONF_HASH} ${MARIADB_CONF_HASH} ${KEYSTONE_CONF_HASH} ${KEYCLOAK_CONF_HASH} ${FLASK_CONF_HASH} ${WEB_GUI_CONF_HASH} ${NGINX_PROXY_CONF_HASH}'


###################################
# NAMESPACE
###################################
kubectl apply --server-side -f $KUBE_ROOT_FOLDER/namespace_datalake.yml

###################################
# MEMCACHED
###################################
kubectl apply --server-side -f $MEMCACHED_KUBE_PATH/services/ -f $MEMCACHED_KUBE_PATH/network/ -f $MEMCACHED_KUBE_PATH/pods/

###################################
# KEYCLOAK (optional)
###################################
# Only when DEPLOY_KEYCLOAK=true, like create_docker.sh. Before Keystone : Keystone fetches its certificates at start.
if [ "${DEPLOY_KEYCLOAK,,}" = "true" ]; then
  kubectl apply --server-side -f $OPENSTACKKEYCLOAK_KUBE_PATH/volumes/
  kubectl apply --server-side -f $OPENSTACKKEYCLOAK_KUBE_PATH/services/service_keycloak.yml
  envsubst "$VARS" < $OPENSTACKKEYCLOAK_KUBE_PATH/services/service_keycloak_public.yml | kubectl apply --server-side -f -
  envsubst "$VARS" < $OPENSTACKKEYCLOAK_KUBE_PATH/pods/statefulset_keycloak.yml | kubectl apply --server-side -f -
fi

###################################
# OPENSTACK KEYSTONE (MariaDB + Keystone)
###################################
kubectl apply --server-side -f $OPENSTACKKEYSTONE_KUBE_PATH/volumes/
kubectl apply --server-side -f $OPENSTACKKEYSTONE_KUBE_PATH/services/ -f $OPENSTACKKEYSTONE_KUBE_PATH/network/
envsubst "$VARS" < $OPENSTACKKEYSTONE_KUBE_PATH/pods/statefulset_mariadb.yml | kubectl apply --server-side -f -
envsubst "$VARS" < $OPENSTACKKEYSTONE_KUBE_PATH/pods/deployment_keystone.yml | kubectl apply --server-side -f -
# The pod template of a Job cannot be changed : the bootstrap Job is deleted, then created again (the script can run again)
kubectl -n datalake delete job keystone-bootstrap --ignore-not-found
envsubst "$VARS" < $OPENSTACKKEYSTONE_KUBE_PATH/pods/job_keystone_bootstrap.yml | kubectl apply --server-side -f -

###################################
# OPENSTACK SWIFT
###################################
kubectl apply --server-side -f $OPENSTACKSWIFT_KUBE_PATH/volumes/
kubectl apply --server-side -f $OPENSTACKSWIFT_KUBE_PATH/services/ -f $OPENSTACKSWIFT_KUBE_PATH/network/
envsubst "$VARS" < $OPENSTACKSWIFT_KUBE_PATH/pods/statefulset_swift_storage.yml | kubectl apply --server-side -f -
envsubst "$VARS" < $OPENSTACKSWIFT_KUBE_PATH/pods/deployment_swift_proxy.yml | kubectl apply --server-side -f -

###################################
# REST API + WEB GUI + NGINX PROXY
###################################
kubectl apply --server-side -f $ACCESS_ZONE_KUBE_PATH/volumes/
kubectl apply --server-side -f $ACCESS_ZONE_KUBE_PATH/services/ -f $ACCESS_ZONE_KUBE_PATH/network/
envsubst "$VARS" < $ACCESS_ZONE_KUBE_PATH/pods/deployment_flask_app.yml | kubectl apply --server-side -f -
envsubst "$VARS" < $ACCESS_ZONE_KUBE_PATH/pods/deployment_web_gui.yml | kubectl apply --server-side -f -
envsubst "$VARS" < $ACCESS_ZONE_KUBE_PATH/pods/deployment_nginx_proxy.yml | kubectl apply --server-side -f -

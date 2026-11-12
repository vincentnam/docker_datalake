#!/bin/bash
set -euo pipefail

export $(grep -v '^#' ./conf.env | sed 's/\r$//' | xargs)
KUBE_ROOT_FOLDER="./kubernetes"
MEMCACHED_KUBE_PATH="$KUBE_ROOT_FOLDER/memcached"
OPENSTACKSWIFT_KUBE_PATH="$KUBE_ROOT_FOLDER/rawdata_zone/openstackSwift"
ACCESS_ZONE_KUBE_PATH="$KUBE_ROOT_FOLDER/access_zone"

export KUBECONFIG="$PWD/k3s.yaml"

# Values of the ${...} placeholders of the pods/ files.
# The storage request is 90 % of NODE_STORAGE_SIZE : the filesystem keeps a part of the disk.
export SWIFT_STORAGE_REPLICAS="$NB_STORAGE_NODE"
export SWIFT_PROXY_REPLICAS="$NB_MANAGEMENT_NODE"
export SWIFT_STORAGE_REQUEST="$(( $(numfmt --from=auto "${NODE_STORAGE_SIZE%B}") * 9 / 10 / 1048576 ))Mi"
export APP_TAG="$(git rev-parse --short HEAD)"
VARS='${SWIFT_STORAGE_REPLICAS} ${SWIFT_PROXY_REPLICAS} ${SWIFT_STORAGE_REQUEST} ${APP_TAG}'


###################################
# NAMESPACE
###################################
kubectl apply --server-side -f $KUBE_ROOT_FOLDER/namespace_datalake.yml

###################################
# MEMCACHED
###################################
kubectl apply --server-side -f $MEMCACHED_KUBE_PATH/services/ -f $MEMCACHED_KUBE_PATH/network/ -f $MEMCACHED_KUBE_PATH/pods/

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
kubectl apply --server-side -f $ACCESS_ZONE_KUBE_PATH/pods/deployment_nginx_proxy.yml

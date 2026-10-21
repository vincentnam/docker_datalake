#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"

export KUBECONFIG="${KUBECONFIG:-$(cd .. && pwd)/k3s.yaml}"

# Values of the ${...} placeholders in the pods/ templates
export $(grep -v '^#' ../conf.env | sed 's/\r$//' | xargs)
export SWIFT_STORAGE_REPLICAS="$NB_STORAGE_NODE"
export SWIFT_PROXY_REPLICAS="$NB_MANAGEMENT_NODE"
export SWIFT_STORAGE_REQUEST="$(( $(numfmt --from=auto "${NODE_STORAGE_SIZE%B}") * 9 / 10 / 1048576 ))Mi"
export APP_TAG="$(git rev-parse --short HEAD)"
VARS='${SWIFT_STORAGE_REPLICAS} ${SWIFT_PROXY_REPLICAS} ${SWIFT_STORAGE_REQUEST} ${APP_TAG}'

# Namespace
kubectl apply --server-side -f namespace_datalake.yml

# memcached
kubectl apply --server-side -f memcached/services/ -f memcached/network/ -f memcached/pods/

# Swift
kubectl apply --server-side -f rawdata_zone/openstackSwift/volumes/
kubectl apply --server-side -f rawdata_zone/openstackSwift/services/ -f rawdata_zone/openstackSwift/network/
envsubst "$VARS" < rawdata_zone/openstackSwift/pods/statefulset_swift_storage.yml | kubectl apply --server-side -f -
envsubst "$VARS" < rawdata_zone/openstackSwift/pods/deployment_swift_proxy.yml   | kubectl apply --server-side -f -

# Access zone
kubectl apply --server-side -f access_zone/volumes/
kubectl apply --server-side -f access_zone/services/ -f access_zone/network/
envsubst "$VARS" < access_zone/pods/deployment_flask_app.yml | kubectl apply --server-side -f -
envsubst "$VARS" < access_zone/pods/deployment_web_gui.yml   | kubectl apply --server-side -f -
kubectl apply --server-side -f access_zone/pods/deployment_nginx_proxy.yml
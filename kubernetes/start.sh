#!/bin/bash
# Kubernetes (k3s) deployment of the data lake : will be merged into the root start.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONF_ENV="$SCRIPT_DIR/../conf.env"

if [ ! -f "$CONF_ENV" ]; then
  echo "Error: $CONF_ENV not found."
  exit 1
fi
export $(grep -v '^#' "$CONF_ENV" | sed 's/\r$//' | xargs)

if [ -z "${SWIFT_PASSWORD:-}" ]; then
  echo "Set the Swift account password in conf.env file."
  exit 1
else
  PASSWORD_LENGTH=${#SWIFT_PASSWORD}
  if [ "$PASSWORD_LENGTH" -lt 12 ]; then
    echo "WARNING : Swift password is short (<12 char)."
  fi
fi

# ==================== CONFIGURATION PATHS ====================
NAMESPACE="datalake"
NAMESPACE_FILE="$SCRIPT_DIR/namespace_datalake.yml"
MEMCACHED_PATH="$SCRIPT_DIR/memcached"
DISK_SCRIPT="$SCRIPT_DIR/kubernetes_config/disk_creation.sh"
OPENSTACKSWIFT_PATH="$SCRIPT_DIR/rawdata_zone/openstackSwift"
SWIFT_BUILD_PATH="$SCRIPT_DIR/../rawdata_zone/openstackSwift"    # Dockerfile.base, shared with Compose
SWIFT_IMAGE="swift-base:2.30.0"
ACCESS_ZONE_PATH="$SCRIPT_DIR/access_zone"
ACCESS_ZONE_SRC="$SCRIPT_DIR/../access_zone"                   # sources of the REST API and the web GUI
KUBECONFIG_FILE="${KUBECONFIG_FILE:-/etc/rancher/k3s/k3s.yaml}"

# Tag of the images built from this repository : the git commit (same commit = same tag for -b and -r)
APP_TAG="$(git -C "$SCRIPT_DIR" rev-parse --short HEAD 2>/dev/null || echo dev)"
export APP_TAG
FLASK_IMAGE="datalake-flask:$APP_TAG"
WEB_GUI_IMAGE="datalake-web-gui:$APP_TAG"

K() { kubectl --kubeconfig "$KUBECONFIG_FILE" "$@"; }

# apply_rendered <dir> : applies every *.yml of dir, with the ${...} placeholders replaced
apply_rendered() {
  local file
  for file in "$1"/*.yml; do
    envsubst '${SWIFT_STORAGE_REPLICAS} ${SWIFT_PROXY_REPLICAS} ${SWIFT_STORAGE_REQUEST} ${APP_TAG}' < "$file" \
      | K apply --server-side -f -
  done
}

# build_image <image> <dockerfile> <context> [docker build options...] : builds, then imports into k3s
build_image() {
  local image=$1 dockerfile=$2 context=$3
  shift 3
  echo "Building $image..."
  "${DOCKER[@]}" build -t "$image" -f "$dockerfile" "$@" "$context"
  # k3s runs containerd, not Docker : the image has to be imported to be seen by the pods
  echo "Importing $image into k3s..."
  "${DOCKER[@]}" save "$image" | sudo k3s ctr images import -
}

# wait_rollout <kind/name> : waits until the pods are ready
wait_rollout() {
  if ! K -n "$NAMESPACE" rollout status "$1" --timeout=300s; then
    echo "Error: $1 is not ready. See : kubectl -n $NAMESPACE get pods,pvc ; kubectl -n $NAMESPACE describe $1"
    exit 1
  fi
}

# ==================== HELP ====================
help_message() {
  echo "Usage: $0 [OPTIONS]"
  echo "Options:"
  echo "  -b, --build        Run build steps (local disks, images imported into k3s, configs, rings)"
  echo "  -r, --run          Deploy to the cluster : namespace, memcached, Swift, access zone (REST API, web GUI, nginx)"
  echo "  -h, --help         Show this help"
  echo ""
  echo "Examples:"
  echo "  $0 -b              # Build only"
  echo "  $0 -br             # Build + Run"
}

# No args → help
if [ $# -eq 0 ]; then
  help_message
  exit 0
fi

# Parse arguments
if ! command -v getopt >/dev/null 2>&1; then
  echo "Error: getopt is not installed."
  exit 1
fi

if ! PARSED=$(getopt -o brh -l build,run,help --name "$0" -- "$@"); then
  echo "Error: Invalid arguments."
  exit 1
fi

eval set -- "$PARSED"

BUILD=false
RUN=false

while true; do
  case "$1" in
    -b|--build) BUILD=true; shift ;;
    -r|--run)   RUN=true;   shift ;;
    -h|--help) help_message; exit 0 ;;
    --) shift; break ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# At least one action
if [ "$BUILD" = false ] && [ "$RUN" = false ]; then
  echo "Error: You must specify at least one action (-b, -r)"
  help_message
  exit 1
fi

# Both steps need the cluster : the rings are read from it, the configs are applied to it
if ! K get nodes >/dev/null 2>&1; then
  echo "Error: cluster unreachable with $KUBECONFIG_FILE (sudo systemctl status k3s)."
  exit 1
fi

# ==================== BUILD ====================
if [ "$BUILD" = true ]; then
  echo "Running build steps..."

  # One local disk per storage pod (fallocate image, see kubernetes_config/disk_creation.sh), from conf.env.
  # Idempotent : existing disks are kept, grown if NODE_STORAGE_SIZE increased, never removed.
  echo "Creating the local disks of the storage pods ($NB_STORAGE_NODE x $NODE_STORAGE_SIZE)..."
  for i in $(seq 0 $((NB_STORAGE_NODE - 1))); do
    bash "$DISK_SCRIPT" --create --grow --apply --name "swift-$i" --size "$NODE_STORAGE_SIZE"
  done

  # Docker through sudo when the user is not allowed to reach the daemon
  DOCKER=(docker)
  if ! docker info >/dev/null 2>&1; then
    DOCKER=(sudo docker)
  fi

  build_image "$SWIFT_IMAGE" "$SWIFT_BUILD_PATH/Dockerfile.base" "$SWIFT_BUILD_PATH"
  build_image "$FLASK_IMAGE" "$ACCESS_ZONE_PATH/flask/Dockerfile" "$ACCESS_ZONE_SRC/flask"
  # REACT_APP_* are compiled into the web GUI : they come from conf.env, like the web_gui/.env of Compose
  build_image "$WEB_GUI_IMAGE" "$ACCESS_ZONE_PATH/web_gui/Dockerfile" "$ACCESS_ZONE_SRC/web_gui" \
    --build-arg "REACT_APP_FLASK_APP_URL=${REACT_APP_FLASK_APP_URL:-/api}" \
    --build-arg "REACT_APP_JUPYTERHUB_URL=${REACT_APP_JUPYTERHUB_URL:-}"

  echo "Generating Swift configs..."
  bash "$OPENSTACKSWIFT_PATH/create_conf.sh"

  echo "Generating Swift rings..."
  bash "$OPENSTACKSWIFT_PATH/create_rings.sh"

  echo "Generating access zone configs..."
  bash "$ACCESS_ZONE_PATH/create_conf.sh"
fi

# ==================== RUN ====================
if [ "$RUN" = true ]; then
  for dir in "$OPENSTACKSWIFT_PATH/volumes" "$ACCESS_ZONE_PATH/volumes"; do
    if [ ! -d "$dir" ]; then
      echo "Error: $dir not found. Please run with -b first."
      exit 1
    fi
  done

  # The images of this commit must already be in k3s (built and imported by -b)
  IMAGES_IN_K3S="$(sudo k3s ctr images ls -q)"
  for image in "$FLASK_IMAGE" "$WEB_GUI_IMAGE"; do
    if ! grep -qx "docker.io/library/$image" <<< "$IMAGES_IN_K3S"; then
      echo "Error: $image is not in k3s (new commit since the last build ?). Please run with -b first."
      exit 1
    fi
  done

  if ! command -v envsubst >/dev/null 2>&1; then
    echo "Error: envsubst is not installed (sudo apt install gettext-base)."
    exit 1
  fi

  # Values injected in the templates of pods/ ( ${...} placeholders ), from conf.env
  export SWIFT_STORAGE_REPLICAS="$NB_STORAGE_NODE"
  export SWIFT_PROXY_REPLICAS="$NB_MANAGEMENT_NODE"
  # PVC request = 90 % of NODE_STORAGE_SIZE : the filesystem keeps part of the disk and the PV capacity is rounded down
  STORAGE_BYTES=$(numfmt --from=auto "${NODE_STORAGE_SIZE%B}")
  export SWIFT_STORAGE_REQUEST="$(( STORAGE_BYTES * 9 / 10 / 1048576 ))Mi"

  # --server-side : no last-applied annotation, which is capped at 256 KiB (ring builders can grow past it)
  echo "Applying the datalake namespace..."
  K apply --server-side -f "$NAMESPACE_FILE"

  echo "Applying memcached (shared by the whole architecture)..."
  K apply --server-side -f "$MEMCACHED_PATH/services/" -f "$MEMCACHED_PATH/network/" -f "$MEMCACHED_PATH/pods/"

  echo "Applying Swift (configs, rings, services, network policies, pods)..."
  K apply --server-side -f "$OPENSTACKSWIFT_PATH/volumes/"
  K apply --server-side -f "$OPENSTACKSWIFT_PATH/services/" -f "$OPENSTACKSWIFT_PATH/network/"
  apply_rendered "$OPENSTACKSWIFT_PATH/pods"

  echo "Applying the access zone (REST API, web GUI, nginx)..."
  K apply --server-side -f "$ACCESS_ZONE_PATH/volumes/"
  K apply --server-side -f "$ACCESS_ZONE_PATH/services/" -f "$ACCESS_ZONE_PATH/network/"
  apply_rendered "$ACCESS_ZONE_PATH/pods"

  # After a build : same tag rebuilt (uncommitted changes) and regenerated configs (env, nginx confs)
  # do not change the Deployments by themselves, so their pods are restarted to take them
  if [ "$BUILD" = true ]; then
    K -n "$NAMESPACE" rollout restart deployment/flask-app deployment/web-gui deployment/nginx-proxy
  fi

  echo "Waiting for the pods (storage request : $SWIFT_STORAGE_REQUEST per storage pod)..."
  wait_rollout deployment/memcached
  wait_rollout statefulset/swift-storage
  wait_rollout deployment/swift-proxy
  wait_rollout deployment/flask-app
  wait_rollout deployment/web-gui
  wait_rollout deployment/nginx-proxy

  echo "Data lake entry point : http://localhost:7000"
fi

echo "Script completed successfully."

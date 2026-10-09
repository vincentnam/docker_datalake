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
NAMESPACE_FILE="$SCRIPT_DIR/namespace_datalake.yml"
OPENSTACKSWIFT_PATH="$SCRIPT_DIR/rawdata_zone/openstackSwift"
SWIFT_BUILD_PATH="$SCRIPT_DIR/../rawdata_zone/openstackSwift"    # Dockerfile.base, shared with Compose
SWIFT_IMAGE="swift-base:2.30.0"
KUBECONFIG_FILE="${KUBECONFIG_FILE:-/etc/rancher/k3s/k3s.yaml}"

K() { kubectl --kubeconfig "$KUBECONFIG_FILE" "$@"; }

# ==================== HELP ====================
help_message() {
  echo "Usage: $0 [OPTIONS]"
  echo "Options:"
  echo "  -b, --build        Run build steps (Swift image imported into k3s, configs, rings)"
  echo "  -r, --run          Apply the namespace and the generated configs to the cluster"
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

  # Docker through sudo when the user is not allowed to reach the daemon
  DOCKER=(docker)
  if ! docker info >/dev/null 2>&1; then
    DOCKER=(sudo docker)
  fi

  echo "Building $SWIFT_IMAGE..."
  "${DOCKER[@]}" build -t "$SWIFT_IMAGE" -f "$SWIFT_BUILD_PATH/Dockerfile.base" "$SWIFT_BUILD_PATH"

  # k3s runs containerd, not Docker : the image has to be imported to be seen by the pods
  echo "Importing $SWIFT_IMAGE into k3s..."
  "${DOCKER[@]}" save "$SWIFT_IMAGE" | sudo k3s ctr images import -

  echo "Generating Swift configs..."
  bash "$OPENSTACKSWIFT_PATH/create_conf.sh"

  echo "Generating Swift rings..."
  bash "$OPENSTACKSWIFT_PATH/create_rings.sh"
fi

# ==================== RUN ====================
if [ "$RUN" = true ]; then
  if [ ! -d "$OPENSTACKSWIFT_PATH/volumes" ]; then
    echo "Error: $OPENSTACKSWIFT_PATH/volumes not found. Please run with -b first."
    exit 1
  fi

  # --server-side : no last-applied annotation, which is capped at 256 KiB (ring builders can grow past it)
  echo "Applying the datalake namespace..."
  K apply --server-side -f "$NAMESPACE_FILE"

  echo "Applying the Swift configs and rings..."
  K apply --server-side -f "$OPENSTACKSWIFT_PATH/volumes/"
fi

echo "Script completed successfully."

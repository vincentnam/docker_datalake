#!/bin/bash
set -euo pipefail
export $(grep -v '^#' ./conf.env | sed 's/\r$//' | xargs)

if [ -z "$OS_PASSWORD" ]; then
  echo "Set the Admin account password in conf.env file."
  exit 1;
else
  PASSWORD_LENGTH=${#OS_PASSWORD}
  if [ "$PASSWORD_LENGTH" -lt 12 ]; then
    echo "WARNING : Admin password is short (<12 char)."
  fi
fi



if [ -z "$SWIFT_PASSWORD" ]; then
  echo "Set the Swift account password in conf.env file."
  exit 1;
else
  PASSWORD_LENGTH=${#SWIFT_PASSWORD}
  if [ "$PASSWORD_LENGTH" -lt 12 ]; then
    echo "WARNING : Swift password is short (<12 char)."
  fi
fi








# ==================== CONFIGURATION PATHS ====================
OPENSTACKSWIFT_PATH="./rawdata_zone/openstackSwift"
OPENSTACKKEYSTONE_PATH="./rawdata_zone/openstackKeystone"
JUPYTER_PATH="./process_zone/jupyter"
WEBGUI_PATH="./access_zone/web_gui"
REST_API_PATH="./access_zone/flask"
NGINX_PATH="./access_zone/nginx"

COMPOSE_FILE="docker-compose_datalake.yml"

# ==================== CLEANUP FUNCTIONS ====================
cleanup_function() {
  echo "Cleaning up containers before exiting..."
  sudo docker compose -f "$COMPOSE_FILE" down --remove-orphans 2>/dev/null || true
  # TODO: ADD LOSETUP CLEAN (Multiple deployment create multiple loop dev even if truncate file are deleted)
  exit 0
}

hard_clean() {
  echo "Performing hard clean (full reset)..."
  sudo docker compose -f "$COMPOSE_FILE" down --remove-orphans -v 2>/dev/null || true
  sudo rm -rf ./rawdata_zone/openstackSwift/data \
             ./process_zone/jupyter/jupyterhub-data \
             "$COMPOSE_FILE" .env
  echo "Hard clean completed. Ready for fresh start."
  exit 0
}

# Trap signals
trap cleanup_function SIGINT SIGTERM

# ==================== HELP ====================
help_message() {
  echo "Usage: $0 [OPTIONS]"
  echo "Options:"
  echo "  -b, --build        Run build steps (configs, init, builds)"
  echo "  -r, --run          Start the data lake services"
  echo "  -t, --test         Test mode: automatically add Caddy reverse proxy"
  echo "  -c, --clean        Clean stopped containers and orphans"
  echo "  --platform         Choose the platform : docker-compose OR kubernetes"
  echo "  --clean-hard       Full reset (delete volumes, configs, data)"

  echo "  -h, --help         Show this help"
  echo ""
  echo "Examples:"
  echo "  $0 -b                  # Build only"
  echo "  $0 -br                 # Build + Run"
  echo "  $0 -bt                 # Build + Test mode"
  echo "  $0 -brt                # Build + Run + Test mode (recommandé en dev)"
  echo "  $0 --clean-hard        # Full wipe"
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

PARSED=$(getopt -o brtch -l build,run,test,clean,clean-hard,help,platform: --name "$0" -- "$@")
if [ $? -ne 0 ]; then
  echo "Error: Invalid arguments."
  exit 1
fi

eval set -- "$PARSED"

BUILD=false
RUN=false
TEST=false
CLEAN=false
PLATFORM=false

while true; do
  case "$1" in
    -b|--build) BUILD=true; shift ;;
    -r|--run)   RUN=true;   shift ;;
    -t|--test)  TEST=true;  shift ;;
    -c|--clean) CLEAN=true; shift ;;
    --platform) PLATFORM="$2"; shift 2;;
    --clean-hard) hard_clean ;;
    -h|--help) help_message; exit 0 ;;
    --) shift; break ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# At least one action
if [ "$BUILD" = false ] && [ "$RUN" = false ] && [ "$TEST" = false ] && [ "$CLEAN" = false ]; then
  echo "Error: You must specify at least one action (-b, -r, -t, -c)"
  help_message
  exit 1
fi

case "$PLATFORM" in
  docker-compose|kubernetes) ;;
  false)
    echo "Error: You must specify a platform to deploy on (--platform docker-compose OR kubernetes)"
    help_message
    exit 1 ;;
  *)
    echo "Error: unknown platform « $PLATFORM » (docker-compose OR kubernetes)"
    help_message
    exit 1 ;;
esac


if [ "$PLATFORM" = "docker-compose" ]; then
  # Clean
  if [ "$CLEAN" = true ]; then
    echo "Cleaning containers..."
    sudo docker compose -f "$COMPOSE_FILE" down --remove-orphans 2>/dev/null || true
  fi




  # ==================== BUILD ====================
  if [ "$BUILD" = true ]; then



    echo "Running build steps..."

    # Update paths
    sed -i 's#OPENSTACKSWIFT_PATH=".*"#OPENSTACKSWIFT_PATH="'"$OPENSTACKSWIFT_PATH"'"#g' create_docker.sh create_conf.sh
    sed -i 's#JUPYTER_PATH=".*"#JUPYTER_PATH="'"$JUPYTER_PATH"'"#g' create_docker.sh create_conf.sh
    sed -i 's#WEBGUI_PATH=".*"#WEBGUI_PATH="'"$WEBGUI_PATH"'"#g' create_docker.sh create_conf.sh
    sed -i 's#REST_API_PATH=".*"#REST_API_PATH="'"$REST_API_PATH"'"#g' create_docker.sh create_conf.sh
    sed -i 's#NGINX_PATH=".*"#NGINX_PATH="'"$NGINX_PATH"'"#g' create_docker.sh create_conf.sh

    chmod +x create_docker.sh create_conf.sh
    chmod +x "$OPENSTACKSWIFT_PATH"/{init.sh,create_conf.sh}
    chmod +x "$OPENSTACKKEYSTONE_PATH/build.sh"

    (cd "$OPENSTACKKEYSTONE_PATH" && ./build.sh)

    ./create_conf.sh
    ./create_docker.sh

    echo "Initializing Swift in background..."
    (cd "$OPENSTACKSWIFT_PATH" && ./init.sh) &

    # Build Jupyter base image
    sudo docker build -t cors_base-notebook:latest -f "$JUPYTER_PATH/Dockerfile.jupyterserver" "$JUPYTER_PATH"
  fi

  # ==================== TEST MODE (Caddy) ====================
  if [ "$TEST" = true ]; then
    if [ ! -f "$COMPOSE_FILE" ]; then
      echo "Error: $COMPOSE_FILE not found. Please run with -b first."
      exit 1
    fi

    echo "Adding Caddy for test mode..."

    if ! grep -q "^  caddy:" "$COMPOSE_FILE"; then
  #sed -i 's?#END SERVICE SECTION?  caddy:\n    image: caddy:2-alpine\n    container_name: caddy_temp_proxy\n    restart: unless-stopped\n    profiles:\n      - debug\n    ports:\n      - \"2015:80\"\n    volumes:\n      - ./Caddyfile:/et
  #c/caddy/Caddyfile:ro\n    networks:\n      - swift-cluster\n    depends_on:\n      - web_gui\n      - flask-app\n      - horizon\n      - management-1\n#END SERVICE SECTION?g' docker-compose_datalake.yml -i
    sed -i 's/#END SERVICE SECTION/\
  caddy:\
    image: caddy:2-alpine\
    container_name: caddy_temp_proxy\
    restart: unless-stopped\
    profiles:\
      - debug\
    ports:\
      - "2015:80"    # Web GUI\
      - "5000:5000"  # Keystone\
      - "5001:5001"  # flask\
      - "8081:8080"  # Swift - Horizon\
    volumes:\
      - .\/debug\/Caddyfile:\/etc\/caddy\/Caddyfile:ro\
    networks:\
      - swift-cluster\
#END SERVICE SECTION/g' docker-compose_datalake.yml
    fi


    echo "Caddy ready → http://localhost:2015"
  fi

  # ==================== RUN ====================
  if [ "$RUN" = true ]; then
    echo "Starting data lake services..."
    # 42424 is ID of Keystone user in container / check and change id if not working
    chown -R 42424:42424 rawdata_zone/openstackKeystone/conf/etc/keystone/credential-keys
    chown -R 42424:42424 rawdata_zone/openstackKeystone/conf/etc/keystone/fernet-keys
    chmod -R 770 rawdata_zone/openstackKeystone/conf/etc/keystone/credential-keys
    chmod -R 770 rawdata_zone/openstackKeystone/conf/etc/keystone/fernet-keys
    if [ "$TEST" = true ]; then
      export DOCKER_BUILDKIT=1
      sudo docker compose -f "$COMPOSE_FILE" --profile datalake --profile debug up --build
    else
      sudo docker compose -f "$COMPOSE_FILE" --profile datalake up --build
    fi
  fi

  echo "Script completed successfully."
elif [ "$PLATFORM" = "kubernetes" ]; then
  KUBE_ROOT_FOLDER="./kubernetes"
  OPENSTACKSWIFT_KUBE_PATH="$KUBE_ROOT_FOLDER/rawdata_zone/openstackSwift"
  OPENSTACKKEYSTONE_KUBE_PATH="$KUBE_ROOT_FOLDER/rawdata_zone/openstackKeystone"
  ACCESS_ZONE_KUBE_PATH="$KUBE_ROOT_FOLDER/access_zone"
  DISK_CONFIG_PATH="$KUBE_ROOT_FOLDER/kubernetes_config"

  # kubeconfig of the cluster, used by every kubectl of the scripts below
  export KUBECONFIG="$PWD/k3s.yaml"

  # ==================== BUILD ====================
  if [ "$BUILD" = true ]; then
    echo "Running build steps..."

    if ! kubectl get nodes >/dev/null 2>&1; then
      echo "Error: no reachable cluster with KUBECONFIG=$KUBECONFIG (local install : $KUBE_ROOT_FOLDER/runK3S.sh install)"
      exit 1
    fi

    chmod +x "$DISK_CONFIG_PATH/disk_creation.sh"
    chmod +x "$OPENSTACKSWIFT_KUBE_PATH"/{create_conf.sh,create_rings.sh}
    chmod +x "$ACCESS_ZONE_KUBE_PATH/create_conf.sh"
    chmod +x "$OPENSTACKKEYSTONE_KUBE_PATH/create_conf.sh"

    if [ -z "$MARIADB_VERSION" ]; then
      echo "Set the MariaDB version in conf.env file."
      exit 1
    fi

    if [ -z "$MARIADB_STORAGE_SIZE" ]; then
      echo "Set the MariaDB disk size in conf.env file."
      exit 1
    fi
    # One local disk per storage node (swift-0, swift-1... like the storage pods)
    for i in $(seq 0 $((NB_STORAGE_NODE - 1))); do
      "$DISK_CONFIG_PATH/disk_creation.sh" --create --grow --apply --name "swift-$i" --size "$NODE_STORAGE_SIZE"
    done

    # One local disk for the MariaDB of Keystone (mariadb-0, like its pod)
    "$DISK_CONFIG_PATH/disk_creation.sh" --create --grow --apply --class mariadb-disks --name mariadb-0 --size "$MARIADB_STORAGE_SIZE"
    # Flask and web GUI images are tagged with the git commit (same tag in deploy.sh)
    APP_TAG="$(git rev-parse --short HEAD)"

    # k3s does not see the Docker images : each image is imported after its build
    sudo docker build -t swift-base:2.30.0 -f "$OPENSTACKSWIFT_PATH/Dockerfile.base" "$OPENSTACKSWIFT_PATH"
    sudo docker save swift-base:2.30.0 | sudo k3s ctr images import -

    # Keystone image built by LOCI, like the docker-compose platform (same tag as create_docker.sh)
    # build.sh calls docker without sudo : run with sudo, like the other docker commands of this block
    chmod +x "$OPENSTACKKEYSTONE_PATH/build.sh"
    (cd "$OPENSTACKKEYSTONE_PATH" && sudo ./build.sh)
    KEYSTONE_TAG="${OPENSTACK_RELEASE_VAR//stable\//}-${BASE_TAG_VAR}"
    sudo docker save "keystone:$KEYSTONE_TAG" | sudo k3s ctr images import -

    # openstack client image of the bootstrap Job, tagged with the git commit (same tag in deploy.sh)
    sudo docker build -t "keystone-bootstrap:$APP_TAG" -f "$OPENSTACKKEYSTONE_PATH/Dockerfile.openstackClientBootstrap" "$OPENSTACKKEYSTONE_PATH"
    sudo docker save "keystone-bootstrap:$APP_TAG" | sudo k3s ctr images import -

    sudo docker build -t "datalake-flask:$APP_TAG" -f "$ACCESS_ZONE_KUBE_PATH/flask/Dockerfile" "$REST_API_PATH"
    sudo docker save "datalake-flask:$APP_TAG" | sudo k3s ctr images import -

    sudo docker build -t "datalake-web-gui:$APP_TAG" -f "$ACCESS_ZONE_KUBE_PATH/web_gui/Dockerfile" \
      --build-arg "REACT_APP_FLASK_APP_URL=${REACT_APP_FLASK_APP_URL:-/api}" \
      --build-arg "REACT_APP_JUPYTERHUB_URL=${REACT_APP_JUPYTERHUB_URL:-}" \
      "$WEBGUI_PATH"
    sudo docker save "datalake-web-gui:$APP_TAG" | sudo k3s ctr images import -

    "$OPENSTACKSWIFT_KUBE_PATH/create_conf.sh"
    "$OPENSTACKSWIFT_KUBE_PATH/create_rings.sh"
    "$OPENSTACKKEYSTONE_KUBE_PATH/create_conf.sh"
    "$ACCESS_ZONE_KUBE_PATH/create_conf.sh"

#    $KUBE_ROOT_FOLDER/runK3S.sh install
#    $KUBE_ROOT_FOLDER/runK3S.sh gui &
  fi

  # ==================== TEST MODE (Caddy) ====================
  if [ "$TEST" = true ]; then
    echo "Pas de test"
  fi

  # ==================== RUN ====================
  if [ "$RUN" = true ]; then
    chmod +x $KUBE_ROOT_FOLDER/deploy.sh
    $KUBE_ROOT_FOLDER/deploy.sh
  fi
fi
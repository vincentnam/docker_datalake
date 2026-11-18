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
  echo "  --force-restart    Restart every service, even unchanged ones (image rebuilt with the same tag)"

  echo "  -h, --help         Show this help"
  echo ""
  echo "Examples:"
  echo "  $0 -b                  # Build only"
  echo "  $0 -br                 # Build + Run"
  echo "  $0 -bt                 # Build + Test mode"
  echo "  $0 -brt                # Build + Run + Test mode (recommandé en dev)"
  echo "  $0 --clean-hard        # Full wipe"
  echo "  $0 --platform kubernetes --force-restart   # Restart every pod"
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

PARSED=$(getopt -o brtch -l build,run,test,clean,clean-hard,force-restart,help,platform: --name "$0" -- "$@")
if [ $? -ne 0 ]; then
  echo "Error: Invalid arguments."
  exit 1
fi

eval set -- "$PARSED"

BUILD=false
RUN=false
TEST=false
CLEAN=false
FORCE_RESTART=false
PLATFORM=false

while true; do
  case "$1" in
    -b|--build) BUILD=true; shift ;;
    -r|--run)   RUN=true;   shift ;;
    -t|--test)  TEST=true;  shift ;;
    -c|--clean) CLEAN=true; shift ;;
    --platform) PLATFORM="$2"; shift 2;;
    --clean-hard) hard_clean ;;
    --force-restart) FORCE_RESTART=true; shift ;;
    -h|--help) help_message; exit 0 ;;
    --) shift; break ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# At least one action
if [ "$BUILD" = false ] && [ "$RUN" = false ] && [ "$TEST" = false ] && [ "$CLEAN" = false ] && [ "$FORCE_RESTART" = false ]; then
  echo "Error: You must specify at least one action (-b, -r, -t, -c, --force-restart)"
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

  # Force restart : every container of the data lake is restarted.
  # Same profiles as -r (and -t) : without them, compose ignores every service that belongs to a profile.
  if [ "$FORCE_RESTART" = true ]; then
    echo "Restarting containers..."
    sudo docker compose -f "$COMPOSE_FILE" --profile datalake --profile debug restart
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
  MEMCACHED_KUBE_PATH="$KUBE_ROOT_FOLDER/memcached"
  OPENSTACKSWIFT_KUBE_PATH="$KUBE_ROOT_FOLDER/rawdata_zone/openstackSwift"
  OPENSTACKKEYSTONE_KUBE_PATH="$KUBE_ROOT_FOLDER/rawdata_zone/openstackKeystone"
  OPENSTACKKEYCLOAK_KUBE_PATH="$KUBE_ROOT_FOLDER/rawdata_zone/openstackKeycloak"
  JUPYTER_KUBE_PATH="$KUBE_ROOT_FOLDER/process_zone/jupyter"
  ACCESS_ZONE_KUBE_PATH="$KUBE_ROOT_FOLDER/access_zone"
  DISK_CONFIG_PATH="$KUBE_ROOT_FOLDER/kubernetes_config"

  # kubeconfig of the cluster, used by every kubectl of the scripts below
  export KUBECONFIG="$PWD/k3s.yaml"

  # ==================== CONF.ENV VALUES (build and run) ====================
  # ${X:-} : with set -u, a variable missing from conf.env would stop the script before its message
  if [ -z "${MARIADB_VERSION:-}" ]; then
    echo "Set the MariaDB version in conf.env file."
    exit 1
  fi

  if [ -z "${MARIADB_STORAGE_SIZE:-}" ]; then
    echo "Set the MariaDB disk size in conf.env file."
    exit 1
  fi

  if [ -z "${JUPYTERHUB_STORAGE_SIZE:-}" ]; then
    echo "Set the JupyterHub disk size in conf.env file."
    exit 1
  fi

  if [ -z "${KUBE_PUBLIC_PORT:-}" ]; then
    echo "Set the public port of Traefik in conf.env file."
    exit 1
  fi

  if [ "${DEPLOY_KEYCLOAK,,}" = "true" ]; then
    if [ -z "${KEYCLOAK_VERSION:-}" ]; then
      echo "Set the Keycloak version in conf.env file."
      exit 1
    fi

    if [ -z "${KEYCLOAK_STORAGE_SIZE:-}" ]; then
      echo "Set the Keycloak disk size in conf.env file."
      exit 1
    fi
  fi

  # Image tags : Keystone, same tag as rawdata_zone/openstackKeystone/build.sh and create_docker.sh ;
  # Flask, web GUI and bootstrap Job, the git commit
  export KEYSTONE_TAG="${OPENSTACK_RELEASE_VAR//stable\//}-${BASE_TAG_VAR}"
  export APP_TAG="$(git rev-parse --short HEAD)"

  # Requests of the disks : 90 % of the disk size, the filesystem keeps a part of the disk
  export SWIFT_STORAGE_REQUEST="$(( $(numfmt --from=auto "${NODE_STORAGE_SIZE%B}") * 9 / 10 / 1048576 ))Mi"
  export MARIADB_STORAGE_REQUEST="$(( $(numfmt --from=auto "${MARIADB_STORAGE_SIZE%B}") * 9 / 10 / 1048576 ))Mi"
  if [ "${DEPLOY_KEYCLOAK,,}" = "true" ]; then
    export KEYCLOAK_STORAGE_REQUEST="$(( $(numfmt --from=auto "${KEYCLOAK_STORAGE_SIZE%B}") * 9 / 10 / 1048576 ))Mi"
  fi

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
    chmod +x "$OPENSTACKKEYCLOAK_KUBE_PATH/create_conf.sh"
    chmod +x "$JUPYTER_KUBE_PATH/create_conf.sh"
    chmod +x create_conf.sh

    # One local disk per storage node (swift-0, swift-1... like the storage pods)
    for i in $(seq 0 $((NB_STORAGE_NODE - 1))); do
      "$DISK_CONFIG_PATH/disk_creation.sh" --create --grow --apply --name "swift-$i" --size "$NODE_STORAGE_SIZE"
    done

    # One local disk for the MariaDB of Keystone (mariadb-0, like its pod)
    "$DISK_CONFIG_PATH/disk_creation.sh" --create --grow --apply --class mariadb-disks --name mariadb-0 --size "$MARIADB_STORAGE_SIZE"

    # One local disk for the bundled Keycloak (keycloak-0, like its pod), only when it is deployed
    if [ "${DEPLOY_KEYCLOAK,,}" = "true" ]; then
      "$DISK_CONFIG_PATH/disk_creation.sh" --create --grow --apply --class keycloak-disks --name keycloak-0 --size "$KEYCLOAK_STORAGE_SIZE"
    fi

    # One local disk for the JupyterHub hub (database, cookie secret)
    "$DISK_CONFIG_PATH/disk_creation.sh" --create --grow --apply --class jupyterhub-disks --name jupyterhub-0 --size "$JUPYTERHUB_STORAGE_SIZE"

    # k3s does not see the Docker images : each image is imported after its build
    sudo docker build -t swift-base:2.30.0 -f "$OPENSTACKSWIFT_PATH/Dockerfile.base" "$OPENSTACKSWIFT_PATH"
    sudo docker save swift-base:2.30.0 | sudo k3s ctr images import -

    # Keystone image built by LOCI, like the docker-compose platform (KEYSTONE_TAG, see CONF.ENV VALUES)
    # build.sh calls docker without sudo : run with sudo, like the other docker commands of this block
    chmod +x "$OPENSTACKKEYSTONE_PATH/build.sh"
    (cd "$OPENSTACKKEYSTONE_PATH" && sudo ./build.sh)
    sudo docker save "keystone:$KEYSTONE_TAG" | sudo k3s ctr images import -

    # openstack client image of the bootstrap Job, tagged with the git commit (APP_TAG, like Flask and the web GUI)
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
    "$JUPYTER_KUBE_PATH/create_conf.sh"

    # The Keycloak realm is the file of the docker-compose platform, generated by the root create_conf.sh
    if [ "${DEPLOY_KEYCLOAK,,}" = "true" ]; then
      ./create_conf.sh
      "$OPENSTACKKEYCLOAK_KUBE_PATH/create_conf.sh"
    fi

#    $KUBE_ROOT_FOLDER/runK3S.sh install
#    $KUBE_ROOT_FOLDER/runK3S.sh gui &
  fi

  # ==================== TEST MODE (Caddy) ====================
  if [ "$TEST" = true ]; then
    echo "Pas de test"
  fi

  # ==================== RUN ====================
  if [ "$RUN" = true ]; then
    # Values of the ${...} placeholders of the pods/ files (tags and disk requests : see CONF.ENV VALUES)
    export SWIFT_STORAGE_REPLICAS="$NB_STORAGE_NODE"
    export SWIFT_PROXY_REPLICAS="$NB_MANAGEMENT_NODE"

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
    VARS="$VARS"' ${KUBE_PUBLIC_PORT}'


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
    # JUPYTERHUB (Zero to JupyterHub chart)
    ###################################
    # k3s installs or upgrades the chart by itself, in the background (Job helm-install-jupyterhub in kube-system).
    # No wait : nginx-proxy resolves /hub/ at each request, the rest of the data lake does not depend on JupyterHub.
    # Install problem : kubectl -n kube-system logs job/helm-install-jupyterhub
    kubectl apply --server-side -f $JUPYTER_KUBE_PATH/namespace_datalake_jupyter.yml
    kubectl apply --server-side -f $DISK_CONFIG_PATH/storage_class_jupyter_users.yml
    kubectl apply --server-side -f $JUPYTER_KUBE_PATH/volumes/

    ###################################
    # REST API + WEB GUI + NGINX PROXY
    ###################################
    kubectl apply --server-side -f $ACCESS_ZONE_KUBE_PATH/volumes/
    kubectl apply --server-side -f $ACCESS_ZONE_KUBE_PATH/services/ -f $ACCESS_ZONE_KUBE_PATH/network/
    envsubst "$VARS" < $ACCESS_ZONE_KUBE_PATH/pods/deployment_flask_app.yml | kubectl apply --server-side -f -
    envsubst "$VARS" < $ACCESS_ZONE_KUBE_PATH/pods/deployment_web_gui.yml | kubectl apply --server-side -f -
    envsubst "$VARS" < $ACCESS_ZONE_KUBE_PATH/pods/deployment_nginx_proxy.yml | kubectl apply --server-side -f -

    ###################################
    # TRAEFIK (only entry point)
    ###################################
    # After the access zone : nginx-proxy is ClusterIP, the port of the machine is free for Traefik.
    # k3s redeploys Traefik with the new port (a few seconds), then the Ingress sends everything to nginx-proxy.
    envsubst "$VARS" < $DISK_CONFIG_PATH/traefik_config.yml | kubectl apply --server-side -f -
    kubectl apply --server-side -f $ACCESS_ZONE_KUBE_PATH/ingress/
  fi

  # ==================== FORCE RESTART ====================
  # -r already restarts the services whose conf changed (checksum/config annotation, see RUN above).
  # This restarts every service of the data lake : needed when an image is rebuilt with the same tag (swift-base, keystone, mariadb...).
  # datalake-jupyter : hub and proxy of JupyterHub. The notebooks already started by the users are not restarted.
  if [ "$FORCE_RESTART" = true ]; then
    kubectl -n datalake rollout restart deployment,statefulset
    kubectl -n datalake-jupyter rollout restart deployment,statefulset
  fi
fi
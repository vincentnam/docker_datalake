#!/bin/bash
set -euo pipefail

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

PARSED=$(getopt -o brtch -l build,run,test,clean,clean-hard,help --name "$0" -- "$@")
if [ $? -ne 0 ]; then
  echo "Error: Invalid arguments."
  exit 1
fi

eval set -- "$PARSED"

BUILD=false
RUN=false
TEST=false
CLEAN=false

while true; do
  case "$1" in
    -b|--build) BUILD=true; shift ;;
    -r|--run)   RUN=true;   shift ;;
    -t|--test)  TEST=true;  shift ;;
    -c|--clean) CLEAN=true; shift ;;
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

  if [ "$TEST" = true ]; then
    sudo docker compose -f "$COMPOSE_FILE" --profile datalake --profile debug up --build
  else
    sudo docker compose -f "$COMPOSE_FILE" --profile datalake up --build
  fi
fi

echo "Script completed successfully."

##!/bin/bash
#
#OPENSTACKSWIFT_PATH="./rawdata_zone/openstackSwift"
#OPENSTACKKEYSTONE_PATH="./rawdata_zone/openstackKeystone"
#
#JUPYTER_PATH="./process_zone/jupyter"
#WEBGUI_PATH="./access_zone/web_gui"
#REST_API_PATH="./access_zone/flask"
#NGINX_PATH="./access_zone/nginx"
#
#
#
#sed -i 's#OPENSTACKSWIFT_PATH=".*"#OPENSTACKSWIFT_PATH="'"$OPENSTACKSWIFT_PATH"'"#g' create_docker.sh create_conf.sh
#sed -i 's#JUPYTER_PATH=".*"#JUPYTER_PATH="'"$JUPYTER_PATH"'"#g' create_docker.sh create_conf.sh
#sed -i 's#WEBGUI_PATH=".*"#WEBGUI_PATH="'"$WEBGUI_PATH"'"#g' create_docker.sh create_conf.sh
#sed -i 's#REST_API_PATH=".*"#REST_API_PATH="'"$REST_API_PATH"'"#g' create_docker.sh create_conf.sh
#sed -i 's#NGINX_PATH=".*"#NGINX_PATH="'"$NGINX_PATH"'"#g' create_docker.sh create_conf.sh
#
#
#
#
#
##set -x
#
#chmod +x create_docker.sh
#chmod +x $OPENSTACKSWIFT_PATH/init.sh
#chmod +x $OPENSTACKSWIFT_PATH/create_conf.sh
#chmod +x $OPENSTACKKEYSTONE_PATH/build.sh
#(cd $OPENSTACKKEYSTONE_PATH/ && ./build.sh)
#
#
#chmod +x create_conf.sh
#./create_conf.sh
#./create_docker.sh
#
#
#
#
#(cd $OPENSTACKSWIFT_PATH/; ./init.sh) &
##(cd ./frontend/; sh ./start.sh -br ) &
#
#docker build -t cors_base-notebook:latest -f $JUPYTER_PATH/Dockerfile.jupyterserver $JUPYTER_PATH
#docker compose -f docker-compose_datalake.yml --profile datalake up --build

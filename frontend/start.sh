#!/bin/bash

## Cleanup function
cleanup_function() {
  echo "Cleaning up containersjupyter labextension listec before exiting..."
  sudo docker compose down --remove-orphans
  exit 0
}

hard_clean(){
  sudo rm -rf ./dags ./logs ./plugins ./config ./jupyterhub-data
  sudo rm .env
  sudo docker compose down --remove-orphans
}

## Trap signals
trap cleanup_function SIGINT SIGTERM
help_message() {
  echo "Usage: $0 [OPTIONS]"
  echo "Options:"
  echo "  -b, --build    Run build steps (create directories, .env, initialize Airflow)"
  echo "  -r, --run      Run data lake services with docker compose up"
  echo "  -h, --help     Display this help message"
  echo "  -c, --clean    Remove docker orphans and delete .env file"
  echo "  --hard-clean   Same as clean but also remove all data and every folders created"

  echo "Examples:"
  echo "  $0 --build           # Launch build steps"
  echo "  $0 --run             # Run data lake services"
  echo "  $0 -br               # Run build steps followed by Airflow services"
  echo "  $0 -rb               # Same as -br"
  echo "  $0 --build --run     # Same as -br"
}
# Display help message if no arguments are provided
if [ $# -eq 0 ]; then

  help_message
  exit 0
fi

# Check if getopt is available
if ! command -v getopt >/dev/null 2>&1; then
  echo "Error: getopt is not installed. Please install it."
  exit 1
fi

# Parse arguments using getopt
PARSED_OPTIONS=$(getopt -o b,r,h,c -l build,run,help,clean,hard-clean --name "$0" -- "$@")
if [ $? -ne 0 ]; then
  echo "Error: Invalid argument format."
  exit 1
fi

eval set -- "$PARSED_OPTIONS"

# Variables to track arguments
BUILD=false
RUN=false
CLEAN=false
# Process arguments
while true; do
  case "$1" in
    -b|--build)
      BUILD=true
      shift
      ;;
    -r|--run)
      RUN=true
      shift
      ;;
    -c|--clean)
      CLEAN=true
      shift
      ;;
    -h|--help)
      help_message
      exit 0
      ;;
    --hard-clean)
      hard_clean
      exit 0
      ;;
    --)
      shift
      break
      ;;
    *)
      echo "Warning: Unknown option '$1' ignored"
      shift
      ;;
  esac
done

# Check if at least one action is specified
if [ "$BUILD" = false ] && [ "$RUN" = false ] && [ "$CLEAN" = false ]; then
  echo "Error: At least one of --build, --run or --clean must be specified."
  echo "Use --help for usage information."
  exit 1
fi

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
  echo "Error: docker-compose.yml not found in the current directory."
  exit 1
fi

if [ "$CLEAN" = true ]; then
   sudo docker compose down --remove-orphans
   rm .env
fi

# Execute build steps if build argument is provided
if [ "$BUILD" = true ]; then
  echo "Running build steps..."

  # Create .env file
  touch .env


  #############AIRFLOW###################
  # Create Airflow directories
  mkdir -p ./dags ./logs ./plugins ./config

  # Set Airflow UID in .env
  echo "AIRFLOW_UID=$(id -u)" >> .env

  # Check Airflow configuration
  if ! sudo -E docker compose run airflow-cli airflow config list; then
    echo "Error: Failed to check Airflow configuration."
    cleanup_function
  fi

  # Initialize Airflow
  if ! sudo -E docker compose up airflow-init; then
    echo "Error: Failed to initialize Airflow."
    cleanup_function
  fi
  #######################################

  #############JUPYTERHUB################

  [ -d ./jupyterhub-data ] || mkdir ./jupyterhub-data



  #######################################
  # Build jupyter base container
  sudo docker build -f Dockerfile.jupyterserver -t cors_jupyter-base:latest .
  # Build containers

  sudo docker compose down --remove-orphans
  sudo docker compose build

fi

# Start Airflow services if run argument is provided
if [ "$RUN" = true ]; then
  echo "Starting datalake..."
  if ! sudo docker compose up; then
    echo "Error: Failed to start data lake services."
    echo "Try to use -b / --build argument."
    cleanup_function
  fi
fi
#!/bin/bash


#set -x

chmod +x create_docker.sh
chmod +x ./openstackSwift/init.sh
chmod +x ./openstackSwift/create_conf.sh
chmod +x create_conf.sh
./create_conf.sh
./create_docker.sh

(cd ./openstackSwift/; ./init.sh) &
#(cd ./frontend/; sh ./start.sh -br ) &

docker build -t cors_base-notebook:latest -f ./jupyter/Dockerfile.jupyterserver ./jupyter/
docker compose -f docker-compose_datalake.yml --profile datalake up --build

#!/bin/bash

OPENSTACKSWIFT_PATH="./rawdata_zone/openstackSwift"
JUPYTER_PATH="./process_zone/jupyter"
WEBGUI_PATH="./access_zone/web_gui"
REST_API_PATH="./access_zone/flask"
NGINX_PATH="./access_zone/nginx"



sed -i 's#OPENSTACKSWIFT_PATH=".*"#OPENSTACKSWIFT_PATH="'"$OPENSTACKSWIFT_PATH"'"#g' create_docker.sh create_conf.sh
sed -i 's#JUPYTER_PATH=".*"#JUPYTER_PATH="'"$JUPYTER_PATH"'"#g' create_docker.sh create_conf.sh
sed -i 's#WEBGUI_PATH=".*"#WEBGUI_PATH="'"$WEBGUI_PATH"'"#g' create_docker.sh create_conf.sh
sed -i 's#REST_API_PATH=".*"#REST_API_PATH="'"$REST_API_PATH"'"#g' create_docker.sh create_conf.sh
sed -i 's#NGINX_PATH=".*"#NGINX_PATH="'"$NGINX_PATH"'"#g' create_docker.sh create_conf.sh





#set -x

chmod +x create_docker.sh
chmod +x $OPENSTACKSWIFT_PATH/init.sh
chmod +x $OPENSTACKSWIFT_PATH/create_conf.sh
chmod +x create_conf.sh
./create_conf.sh
./create_docker.sh

(cd $OPENSTACKSWIFT_PATH/; ./init.sh) &
#(cd ./frontend/; sh ./start.sh -br ) &

docker build -t cors_base-notebook:latest -f $JUPYTER_PATH/Dockerfile.jupyterserver $JUPYTER_PATH
docker compose -f docker-compose_datalake.yml --profile datalake up --build

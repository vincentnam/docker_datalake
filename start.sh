
set -x

chmod +x create_docker.sh
chmod +x ./openstackSwift/init.sh
chmod +x ./openstackSwift/create_conf.sh
./create_docker.sh

(cd ./openstackSwift/; ./init.sh) &
#(cd ./frontend/; sh ./start.sh -br ) &

sudo docker build -t cors_base-notebook:latest -f ./jupyter/Dockerfile.jupyterserver ./jupyter/
sudo docker compose -f docker-compose_datalake.yml --profile datalake up

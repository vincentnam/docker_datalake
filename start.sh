
set -x
./create_docker.sh

(cd ./openstackSwift/; ./init.sh) &
#(cd ./frontend/; sh ./start.sh -br ) &


sudo docker compose -f docker-compose_datalake.yml up

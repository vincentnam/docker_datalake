###################################
# Be careful to spaces in docker compose sections when modified
###################################


#!/bin/bash
###################################
# FILE CREATION
###################################
cat <<EOF > docker-compose_datalake.yml
services:
EOF

###################################
# OPENSTACK SWIFT
###################################
cat <<EOF >> docker-compose_datalake.yml
  initswift:
    profiles:
      - backend
      - storage
      - datalake
    build:
      context: ./openstackSwift/
      dockerfile: Dockerfile.base
    volumes:
      - ./openstackSwift/conf/:/etc/swift
      - ./openstackSwift/data/:/srv/
      - ./openstackSwift/scripts:/scripts/
    command: sh /scripts/init.sh
    #user: "\${UID:-1000}:\${GID:-1000}"
    privileged: true
    networks:
      - swift-cluster

EOF
export $(grep -v '^#' ./conf.env | sed 's/\r$//' | xargs)



for i in $(seq $NB_MANAGEMENT_NODE); do


  cat << EOF >> docker-compose_datalake.yml
  management-$i:
    profiles:
      - backend
      - storage
      - datalake
    hostname: management-$i
    build:
      context: ./openstackSwift/
      dockerfile: Dockerfile.base
    entrypoint: ["sh","/scripts/management/management-$i.sh"]
    volumes:
        - ./openstackSwift/conf/:/etc/swift
        - ./openstackSwift/scripts:/scripts/
    privileged: true
    #user: "\${UID:-1000}:\${GID:-1000}"
#    ports:
#      - "8080:8080"
    restart: always
    networks:
      swift-cluster:
        ipv4_address: 10.5.10.$i
    depends_on:
      initswift:
        condition: service_completed_successfully
EOF

done

for i in $(seq $NB_STORAGE_NODE); do
  cat << EOF >> docker-compose_datalake.yml
  storage-$i:
    profiles:
      - backend
      - storage
      - datalake
    hostname: storage-$i
    build:
      context: openstackSwift/
      dockerfile: Dockerfile.base
    entrypoint: ["sh","/scripts/storage/storage-$i.sh"]
    #user: "\${UID:-1000}:\${GID:-1000}"
    volumes:
        - ./openstackSwift/conf/:/etc/swift
        - ./openstackSwift/data/:/internal_dev/
        - ./openstackSwift/scripts:/scripts/
        - ./openstackSwift/rsyncd/rsyncd-$i.conf:/etc/rsyncd.conf
    privileged: true
    restart: always
    networks:
      swift-cluster:
        ipv4_address: 10.5.1.$i
    depends_on:
      initswift:
        condition: service_completed_successfully
EOF

done

###################################
# JUPYTER HUB SECTION
###################################

cat << EOF >> docker-compose_datalake.yml
  hub:
    build:
      context: ./jupyter/
      dockerfile: Dockerfile.jupyterhub
      args:
        JUPYTERHUB_VERSION: 5.3.0
    profiles:
      - datalake
      - frontend
      - process
    #user: "\${UID:-1000}:\${GID:-1000}"
    restart: always
    image: jupyterhub
    container_name: jupyterhub
    networks:
      swift-cluster:
          ipv4_address: 10.5.100.1

    volumes:
      # The JupyterHub configuration file
      - ./jupyter/jupyterhub_config.py:/srv/jupyterhub/jupyterhub_config.py:ro
      # Bind Docker socket on the host so we can connect to the daemon from
      # within the container
      - /var/run/docker.sock:/var/run/docker.sock:rw
      # Bind Docker volume on host for JupyterHub database and cookie secrets
      - ./jupyter/jupyterhub-data:/data
#    ports:
#      - 8000:8000
    environment:
      # This username will be a JupyterHub admin
      JUPYTERHUB_ADMIN: admin
      # All containers will join this network
      DOCKER_NETWORK_NAME: swift-cluster
      # JupyterHub will spawn this Notebook image for users
      DOCKER_NOTEBOOK_IMAGE: cors_base-notebook:latest
      #DOCKER_NOTEBOOK_IMAGE: quay.io/jupyter/base-notebook:latest
      # Notebook directory inside user image
      DOCKER_NOTEBOOK_DIR: /home/jovyan/work
EOF


###################################
# WEB GUI SECTION
###################################



cat << EOF >> docker-compose_datalake.yml


  web_gui:
    profiles:
      - frontend
      - webgui
      - datalake
    build:
      context: ./frontend/
      dockerfile: Dockerfile.web_gui
    image: web_gui
    container_name: web_gui
    #user: "\${UID:-1000}:\${GID:-1000}"
    volumes:
      - ./frontend/web_gui:/opt/app/web_gui/
#    ports :
#      - $REACT_APP_PORT:3000
    networks:
        swift-cluster:
          ipv4_address: 10.5.255.1
EOF


###################################
# REST API SECTION / ACCESS TO SERVICES
###################################
cat <<EOF >> docker-compose_datalake.yml
#  nginx-proxy:
#    profiles:
#      - frontend
#      - datalake
#    build:
#      context: ./RESTapi/
#      dockerfile: Dockerfile.nginx
#    restart: always
#    #user: "\${UID:-1000}:\${GID:-1000}"
#    volumes:
#      - ./RESTapi/nginx/default.conf:/tmp/default.conf
#    environment:
#      - FLASK_SERVER_ADDR=flask-app:8000
#    ports:
#      - "80:80"
#    depends_on:
#      - flask-app
#    healthcheck:
#      test: ["CMD-SHELL", "curl --silent --fail localhost:80/health-check || exit 1"]
#      interval: 10s
#      timeout: 10s
#      retries: 3
#    command: /app/start.sh
#    networks:
#      swift-cluster:
#        ipv4_address: 10.5.255.254

  nginx-proxy:
    build:
      context: ./RESTapi/
      dockerfile: Dockerfile.nginx
    container_name: nginx_proxy
    restart: unless-stopped
    profiles:
      - frontend
      - datalake
    ports:
      - "7000:80"
    depends_on:
      - web_gui
      - flask-app
    networks:
      swift-cluster:
        ipv4_address: 10.5.255.254


  flask-app:
    build:
      context: ./RESTapi/
      dockerfile: Dockerfile.flask
    restart: always
    #user: "\${UID:-1000}:\${GID:-1000}"
    profiles:
      - frontend
      - RESTApi
      - datalake
    volumes:
      - "./RESTapi/flask/app.py:/home/app/app.py"
#    ports:
#      - '$FLASK_PORT:5000'
    healthcheck:
      test: ["CMD-SHELL", "curl --silent --fail localhost:8000/flask-health-check || exit 1"]
      interval: 10s
      timeout: 10s
      retries: 3
    command: gunicorn -w 3 -t 60 -b 0.0.0.0:5000 app:app
    networks:
      swift-cluster:
        ipv4_address: 10.5.255.2

EOF

###################################
# VOLUME SECTION
###################################
cat <<EOF >> docker-compose_datalake.yml


volumes:
  OpenstackSwiftData:
    name: OpenstackSwiftData

EOF
###################################
# NETWORK SECTION
###################################
cat <<EOF >> docker-compose_datalake.yml


networks:
#  jupyterhub-network:
#    name: jupyterhub-network
  swift-cluster:
    name: swift-cluster
    driver: bridge
    ipam:
      config:
        - subnet: 10.5.0.0/16
          gateway: 10.5.0.1
EOF
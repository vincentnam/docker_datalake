#!/bin/bash
###################################
# Be careful to spaces in docker compose sections when modified
###################################

export $(grep -v '^#' ./conf.env | sed 's/\r$//' | xargs)



OPENSTACKSWIFT_PATH="./rawdata_zone/openstackSwift"
OPENSTACKKEYSTONE_PATH="./rawdata_zone/openstackKeystone"

JUPYTER_PATH="./process_zone/jupyter"
WEBGUI_PATH="./access_zone/web_gui"
REST_API_PATH="./access_zone/flask"
NGINX_PATH="./access_zone/nginx"


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
      context: $OPENSTACKSWIFT_PATH
      dockerfile: Dockerfile.base
    volumes:
      - $OPENSTACKSWIFT_PATH/conf/:/etc/swift
      - $OPENSTACKSWIFT_PATH/data/:/srv/
      - $OPENSTACKSWIFT_PATH/scripts:/scripts/
    command: sh /scripts/init.sh
    #user: "\${UID:-1000}:\${GID:-1000}"
    privileged: true
    depends_on:
      keystone:
        condition: service_healthy
    networks:
      - swift-cluster

EOF




for i in $(seq $NB_MANAGEMENT_NODE); do


  cat << EOF >> docker-compose_datalake.yml
  management-$i:
    profiles:
      - backend
      - storage
      - datalake
    hostname: management-$i
    build:
      context: $OPENSTACKSWIFT_PATH
      dockerfile: Dockerfile.base
    entrypoint: ["sh","/scripts/management/management-$i.sh"]
    volumes:
        - $OPENSTACKSWIFT_PATH/conf/:/etc/swift
        - $OPENSTACKSWIFT_PATH/scripts:/scripts/
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
      context: $OPENSTACKSWIFT_PATH
      dockerfile: Dockerfile.base
    entrypoint: ["sh","/scripts/storage/storage-$i.sh"]
    #user: "\${UID:-1000}:\${GID:-1000}"
    volumes:
        - $OPENSTACKSWIFT_PATH/conf/:/etc/swift
        - $OPENSTACKSWIFT_PATH/data/:/internal_dev/
        - $OPENSTACKSWIFT_PATH/scripts:/scripts/
        - $OPENSTACKSWIFT_PATH/rsyncd/rsyncd-$i.conf:/etc/rsyncd.conf
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
# OPENSTACK KEYSTONE SECTION
###################################
#TODO: Config var for Keystone


cat << EOF >> docker-compose_datalake.yml

  mariadb:
    image: mariadb:10.9
    container_name: mariadb
    hostname: mariadb
    environment:
      - MYSQL_ROOT_PASSWORD=secret
      - MYSQL_DATABASE=keystone
      - MYSQL_USER=keystone
      - MYSQL_PASSWORD=keystone_db_pass
    volumes:
      - mariadb_data:/var/lib/mysql
    networks:
      swift-cluster:
        ipv4_address: 10.5.3.3
    healthcheck:
      test: [ "CMD", "healthcheck.sh", "--connect", "--innodb_initialized" ]
      start_period: 10s
      interval: 10s
      timeout: 5s
      retries: 3

  memcached:
    image: memcached:alpine
    networks:
      swift-cluster:
        ipv4_address: 10.5.3.4

  keystone:
    image: keystone:${OPENSTACK_RELEASE_VAR//stable\//}-${BASE_TAG_VAR}
    container_name: keystone
    restart: always
    profiles:
      - datalake
      - authentication
#    ports:
#      - "5000:5000"
#      - "35357:35357"   # Admin endpoint
    volumes:
      - $OPENSTACKKEYSTONE_PATH/conf/etc/keystone:/etc/keystone:rw
      - $OPENSTACKKEYSTONE_PATH/conf/apache2/keystone/ports.conf:/etc/apache2/ports.conf:ro
      - $OPENSTACKKEYSTONE_PATH/conf/apache2/keystone/sites-available/keystone.conf:/etc/apache2/sites-available/keystone.conf:ro
      - $OPENSTACKKEYSTONE_PATH/conf/python/keystone/wsgi/wsgi.py:/var/lib/openstack/lib/python3.10/site-packages/keystone/server/wsgi.py
      - $OPENSTACKKEYSTONE_PATH/scripts/init-keystone.sh:/entrypoint.sh:ro
      - keystone_data:/var/lib/keystone
    command: /entrypoint.sh
    depends_on:
        mariadb:
          condition: service_healthy
        memcached:
          condition: service_started   # memcached est prêt quasi immédiatement
    networks:
      swift-cluster:
        ipv4_address: 10.5.3.1
    healthcheck:
      test: ["CMD", "curl", "--fail", "--silent", "http://localhost:5000/healthcheck"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
      start_interval: 2s
  keystone_bootstrap:
    build:
      context: $OPENSTACKKEYSTONE_PATH
      dockerfile: Dockerfile.openstackClientBootstrap
    environment:
      - OS_AUTH_URL=http://keystone:5000/v3
      - OS_USERNAME=admin
      - OS_PASSWORD=$OS_PASSWORD
      - OS_PROJECT_NAME=admin
      - OS_USER_DOMAIN_NAME=Default
      - OS_PROJECT_DOMAIN_NAME=Default
      - SWIFT_PASSWORD=$SWIFT_PASSWORD           # change si besoin
    profiles:
      - datalake
      - frontend
      - process
      - authentication
    container_name: keystone_bootstrap
    networks:
      swift-cluster:
          ipv4_address: 10.5.3.30
    command: sh /bootstrap_keystone.sh
    depends_on:
      keystone:
        condition: service_healthy


  horizon:
    image: horizon:${OPENSTACK_RELEASE_VAR//stable\//}-${BASE_TAG_VAR}
    container_name: horizon
    restart: always
    profiles:
      - authentication
      - datalake
    ports:
      - "8080:80"
    volumes:
      - $OPENSTACKKEYSTONE_PATH/conf/etc/horizon/local_settings.py:/local_settings.py:ro
      - $OPENSTACKKEYSTONE_PATH/conf/apache2/horizon/000-default.conf:/etc/apache2/sites-available/000-default.conf:ro
      - $OPENSTACKKEYSTONE_PATH/scripts/init-horizon.sh:/entrypoint.sh:ro
    command: /entrypoint.sh
    depends_on:
      - keystone
    networks:
      swift-cluster:
        ipv4_address: 10.5.3.2

EOF

###################################
# JUPYTER HUB SECTION
###################################

cat << EOF >> docker-compose_datalake.yml
  hub:
    build:
      context: $JUPYTER_PATH
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
      - $JUPYTER_PATH/jupyterhub_config.py:/srv/jupyterhub/jupyterhub_config.py:ro
      # Bind Docker socket on the host so we can connect to the daemon from
      # within the container
      - /var/run/docker.sock:/var/run/docker.sock:rw
      # Bind Docker volume on host for JupyterHub database and cookie secrets
      - $JUPYTER_PATH/jupyterhub-data:/data
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
      - authentication
    build:
      context: $WEBGUI_PATH
      dockerfile: Dockerfile.web_gui
    image: web_gui
    container_name: web_gui
    volumes:
      - $WEBGUI_PATH:/opt/app/web_gui/
    networks:
        swift-cluster:
          ipv4_address: 10.5.255.1
EOF


###################################
# REST API SECTION / ACCESS TO SERVICES
###################################
cat <<EOF >> docker-compose_datalake.yml
  nginx-proxy:
    build:
      context: $NGINX_PATH
      dockerfile: Dockerfile.nginx
    container_name: nginx_proxy
    restart: unless-stopped
    profiles:
      - frontend
      - datalake
      - authentication
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
      context: $REST_API_PATH
      dockerfile: Dockerfile.flask
    restart: always
    #user: "\${UID:-1000}:\${GID:-1000}"
    profiles:
      - frontend
      - RESTApi
      - datalake
      - authentication
    volumes:
      - "$REST_API_PATH/app.py:/home/app/app.py"
    healthcheck:
      test: ["CMD-SHELL", "curl --silent --fail localhost:5000/flask-health-check || exit 1"]
      interval: 10s
      timeout: 10s
      retries: 3
      #for tests
#    command: gunicorn -w 3 -t 60 -b 0.0.0.0:5000 app:app
    command: python /home/app/app.py
    networks:
      swift-cluster:
        ipv4_address: 10.5.255.2

EOF




###################################
# VOLUME SECTION
###################################
cat <<EOF >> docker-compose_datalake.yml

#END SERVICE SECTION
######################

volumes:
  OpenstackSwiftData:
    name: OpenstackSwiftData
  mariadb_data:
  keystone_data:


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
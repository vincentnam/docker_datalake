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
    build:
      context: ./openstackSwift/
      dockerfile: Dockerfile.base
    volumes:
      - ./openstackSwift/conf/:/etc/swift
      - ./openstackSwift/data/:/srv/
      - ./openstackSwift/scripts:/scripts/
    command: sh /scripts/init.sh
    privileged: true
    networks:
      - swift_cluster

EOF
export $(grep -v '^#' ./conf.env | sed 's/\r$//' | xargs)



for i in $(seq $NB_MANAGEMENT_NODE); do


  cat << EOF >> docker-compose_datalake.yml
  management-$i:
    hostname: management-$i
    build:
      context: ./openstackSwift/
      dockerfile: Dockerfile.base
    entrypoint: ["sh","/scripts/management/management-$i.sh"]
    volumes:
        - ./openstackSwift/conf/:/etc/swift
        - ./openstackSwift/scripts:/scripts/
    privileged: true
#    ports:
#      - "8080:8080"
    restart: always
    networks:
      swift_cluster:
        ipv4_address: 10.5.10.$i
    depends_on:
      initswift:
        condition: service_completed_successfully
EOF

done

for i in $(seq $NB_STORAGE_NODE); do
  cat << EOF >> docker-compose_datalake.yml
  storage-$i:
    hostname: storage-$i
    build:
      context: openstackSwift/
      dockerfile: Dockerfile.base
    entrypoint: ["sh","/scripts/storage/storage-$i.sh"]
    volumes:
        - ./openstackSwift/conf/:/etc/swift
        - ./openstackSwift/data/:/internal_dev/
        - ./openstackSwift/scripts:/scripts/
        - ./openstackSwift/rsyncd/rsyncd-$i.conf:/etc/rsyncd.conf
    privileged: true
    restart: always
    networks:
      swift_cluster:
        ipv4_address: 10.5.1.$i
    depends_on:
      initswift:
        condition: service_completed_successfully
EOF

done

###################################
# WEB GUI SECTION
###################################



cat << EOF >> docker-compose_datalake.yml


  web_gui:
    build:
      context: ./frontend/
      dockerfile: Dockerfile.web_gui
    image: web_gui
    container_name: web_gui
    volumes:
      - ./frontend/web_gui:/opt/app/web_gui
    ports :
      - 3000:3000
    networks:
        swift_cluster:
          ipv4_address: 10.5.255.1
EOF


###################################
# REST API SECTION / ACCESS TO SERVICES
###################################
cat <<EOF >> docker-compose_datalake.yml
  nginx-proxy:
    build:
      context: ./RESTapi/
      dockerfile: Dockerfile.nginx
    restart: always
    volumes:
      - ./RESTapi/nginx/default.conf:/tmp/default.conf
    environment:
      - FLASK_SERVER_ADDR=flask-app:8000
    ports:
      - "80:80"
    depends_on:
      - flask-app
    healthcheck:
      test: ["CMD-SHELL", "curl --silent --fail localhost:80/health-check || exit 1"]
      interval: 10s
      timeout: 10s
      retries: 3
    command: /app/start.sh
  flask-app:
    build:
      context: ./RESTapi/
      dockerfile: Dockerfile.flask
    restart: always
    ports:
      - '8000:8000'
    healthcheck:
      test: ["CMD-SHELL", "curl --silent --fail localhost:8000/flask-health-check || exit 1"]
      interval: 10s
      timeout: 10s
      retries: 3
    command: gunicorn -w 3 -t 60 -b 0.0.0.0:8000 app:app
EOF
###################################
# NETWORK SECTION
###################################
cat <<EOF >> docker-compose_datalake.yml


networks:
  swift_cluster:
    driver: bridge
    ipam:
      config:
        - subnet: 10.5.0.0/16
          gateway: 10.5.0.1
EOF
#!/usr/bin/env bash

docker run -d --rm \
  --name mariadb \
  --env-file .env \
  -p 3306:3306 \
  -v "$(pwd)"/data:/var/lib/mysql \
  mariadb:10.6

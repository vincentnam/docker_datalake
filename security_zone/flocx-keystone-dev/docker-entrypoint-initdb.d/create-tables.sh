#!/bin/sh

mysql -u root -p${MYSQL_ROOT_PASSWORD} mysql <<EOF
CREATE DATABASE IF NOT EXISTS keystone;
GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'localhost' \
IDENTIFIED BY '${KEYSTONE_ADMIN_PASSWORD}';
GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'%' \
IDENTIFIED BY '${KEYSTONE_ADMIN_PASSWORD}';
EOF

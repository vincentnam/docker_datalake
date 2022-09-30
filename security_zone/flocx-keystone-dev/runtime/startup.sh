#!/bin/sh

set -e

RUNTIME=/runtime
DTU="python3.6 $RUNTIME/dtu.py"

: ${KEYSTONE_DB_HOST:=database}
export KEYSTONE_DB_HOST

echo "* generating config files from templates"
$DTU -o /etc/keystone/keystone.conf $RUNTIME/keystone.j2.conf
$DTU -o clouds.yaml $RUNTIME/clouds.j2.yaml

echo "* initializing fernet tokens"
install -d -o root -g keystone -m 770 /etc/keystone/fernet-keys
runuser -u keystone -- keystone-manage fernet_setup \
	--keystone-user keystone \
	--keystone-group keystone

echo "* initializing database schema"
while ! keystone-manage db_sync; do
	echo "! database schema initialization failed; retrying in 5 seconds..."
	sleep 5
done

echo "* initializing service catalog"
runuser -u keystone -- keystone-manage bootstrap \
	--bootstrap-password ${KEYSTONE_ADMIN_PASSWORD} \
	--bootstrap-internal-url http://localhost:5000 \
	--bootstrap-public-url ${KEYSTONE_PUBLIC_URL:-http://localhost:5000} \
	--bootstrap-region-id ${KEYSTONE_REGION:-RegionOne}

echo "* starting httpd"
exec /usr/sbin/httpd -DFOREGROUND

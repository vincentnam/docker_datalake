#!/bin/bash
set -e
: "${OS_PASSWORD:=admin}" # change in production
echo OS_PASSWORD

# Configuration Apache (toujours, idempotent)
a2enmod wsgi
a2dissite 000-default || true
a2ensite keystone
apache2ctl configtest

# Initialisation unique
if [ ! -f /var/lib/keystone/.initialized ]; then
    echo "Initialisation de Keystone..."
    keystone-manage db_sync
    keystone-manage fernet_setup --keystone-user keystone --keystone-group keystone
    keystone-manage credential_setup --keystone-user keystone --keystone-group keystone

    # Sécurise les clés
    chmod 700 /etc/keystone/fernet-keys /etc/keystone/credential-keys

    keystone-manage bootstrap \
        --bootstrap-password $OS_PASSWORD \
        --bootstrap-username admin \
        --bootstrap-project-name admin \
        --bootstrap-role-name admin \
        --bootstrap-service-name keystone \
        --bootstrap-region-id RegionOne \
        --bootstrap-admin-url http://keystone:35357/v3 \
        --bootstrap-internal-url http://keystone:5000/v3 \
        --bootstrap-public-url http://keystone:5000/v3

    touch /var/lib/keystone/.initialized
fi
#echo "application = initialize_public_application()" >> /var/lib/openstack/lib/python3.10/site-packages/keystone/server/wsgi.py
exec apache2ctl -D FOREGROUND
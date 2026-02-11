#!/bin/bash
set -euo pipefail
#TODO : Add verification if already exists in Keystone to not try to recreate

# Variables (surchargeables via env dans docker-compose)
: "${OS_AUTH_URL:=http://keystone:5000/v3}"
: "${OS_USERNAME:=admin}"
: "${OS_PASSWORD:=admin}"                  # change en prod !
: "${OS_PROJECT_NAME:=admin}"
: "${OS_USER_DOMAIN_NAME:=Default}"
: "${OS_PROJECT_DOMAIN_NAME:=Default}"

: "${SWIFT_USER:=swift}"
: "${SWIFT_PASSWORD:=swift}"
: "${SWIFT_PROJECT:=service}"
: "${SWIFT_ROLE:=admin}"
: "${REGION:=RegionOne}"

# URLs Swift (adaptées à ton compose)
SWIFT_PUBLIC="http://swift-proxy:8080/v1/AUTH_\$(tenant_id)s"
SWIFT_INTERNAL="http://swift-proxy:8080/v1/AUTH_\$(tenant_id)s"
SWIFT_ADMIN="http://swift-proxy:8080"

# ─── Attente Keystone prêt ───────────────────────────────────────────────────
echo "Attente que Keystone soit prêt..."
until openstack token issue >/dev/null 2>&1; do
    echo "Keystone pas encore disponible... (attente 5s)"
    sleep 5
done
echo "Keystone OK !"

# ─── Création idempotente ────────────────────────────────────────────────────
echo "Création projet service"
openstack project create --domain Default --description "Service Project" "$SWIFT_PROJECT"

echo "Création utilisateur swift"
openstack user create --domain Default --password "$SWIFT_PASSWORD" "$SWIFT_USER"

echo "Ajout rôle $SWIFT_ROLE"
openstack role add --project "$SWIFT_PROJECT" --user "$SWIFT_USER" "$SWIFT_ROLE" || true

echo "Création service object-store"
#openstack service create - --name swift --description "Swift Object Storage" object-store
openstack service create \
    --name swift \
    --description "Swift Object Storage" \
    object-store || true   # ignore si déjà existe


echo "Création endpoints Swift"
openstack endpoint create --region "$REGION" object-store public   "$SWIFT_PUBLIC"
openstack endpoint create --region "$REGION" object-store internal "$SWIFT_INTERNAL"
openstack endpoint create --region "$REGION" object-store admin    "$SWIFT_ADMIN"

# ─── Vérification rapide ─────────────────────────────────────────────────────
echo -e "\nRésultat final :"
openstack endpoint list --service object-store
openstack user show "$SWIFT_USER"

echo -e "\nPrêt pour proxy-server.conf [filter:authtoken] :"
cat <<EOF

username             = $SWIFT_USER
password             = $SWIFT_PASSWORD
project_name         = $SWIFT_PROJECT
user_domain_name     = Default
project_domain_name  = Default
auth_url             = $OS_AUTH_URL
www_authenticate_uri = $OS_AUTH_URL
auth_type            = password
EOF

echo "Initialisation terminée."
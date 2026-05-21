#!/bin/bash
set -euo pipefail

# Keystone admin credentials
: "${OS_AUTH_URL:=http://keystone:5000/v3}"
: "${OS_USERNAME:=admin}"
: "${OS_PASSWORD:=admin}" # change in production
: "${OS_PROJECT_NAME:=admin}"
: "${OS_USER_DOMAIN_NAME:=Default}"
: "${OS_PROJECT_DOMAIN_NAME:=Default}"

# Swift service account
: "${SWIFT_USER:=swift}"
: "${SWIFT_PASSWORD:=testing}"
: "${SWIFT_PROJECT:=service}"
: "${SWIFT_ROLE:=admin}"
: "${REGION:=RegionOne}"
echo "SWIFT_PASSWORD : $SWIFT_PASSWORD"
echo "OS_PASSWORD : $OS_PASSWORD"
# RBAC model (default roles reused as much as possible)
: "${GLOBAL_ADMIN_ROLE:=admin}"   # Global admin
: "${WRITER_ROLE:=member}"        # Writer
: "${READER_ROLE:=reader}"        # Reader
: "${BUCKET_ADMIN_ROLE:=bucket_admin}"
: "${BUCKET_OWNER_ROLE:=bucket_owner}"

# Swift endpoints
SWIFT_PUBLIC="http://management-1:8080/v1/AUTH_\$(tenant_id)s"
SWIFT_INTERNAL="http://management-1:8080/v1/AUTH_\$(tenant_id)s"
SWIFT_ADMIN="http://management-1:8080"

ensure_role() {
    role_name="$1"
    if ! openstack role show "$role_name" >/dev/null 2>&1; then
        echo "Creating role: $role_name"
        openstack role create "$role_name" >/dev/null
    fi
}

ensure_project() {
    project_name="$1"
    if ! openstack project show "$project_name" >/dev/null 2>&1; then
        echo "Creating project: $project_name"
        openstack project create --domain Default --description "Service Project" "$project_name" >/dev/null
    fi
}

ensure_user() {
    user_name="$1"
    user_password="$2"
    if ! openstack user show "$user_name" >/dev/null 2>&1; then
        echo "Creating user: $user_name"
        openstack user create --domain Default --password "$user_password" "$user_name" >/dev/null
    fi
}

ensure_endpoint() {
    endpoint_interface="$1"
    endpoint_url="$2"
    existing_url=""

    existing_url="$(openstack endpoint list --service object-store --interface "$endpoint_interface" -f value -c URL | head -n 1 || true)"
    if [ -z "$existing_url" ]; then
        echo "Creating $endpoint_interface endpoint: $endpoint_url"
        openstack endpoint create --region "$REGION" object-store "$endpoint_interface" "$endpoint_url" >/dev/null
    elif [ "$existing_url" != "$endpoint_url" ]; then
        echo "WARNING: $endpoint_interface endpoint already exists with URL: $existing_url"
        echo "         expected URL in this deployment: $endpoint_url"
    fi
}

echo "Waiting for Keystone..."
until openstack token issue >/dev/null 2>&1; do
    echo "Keystone unavailable, retrying in 5s..."
    sleep 5
done
echo "Keystone ready."

# Default Keystone roles + minimal custom roles for bucket governance.
ensure_role "$GLOBAL_ADMIN_ROLE"
ensure_role "$WRITER_ROLE"
ensure_role "$READER_ROLE"
ensure_role "$BUCKET_ADMIN_ROLE"
ensure_role "$BUCKET_OWNER_ROLE"
ensure_role "user" # useful for Horizon UX

# Service project and user
ensure_project "$SWIFT_PROJECT"
ensure_user "$SWIFT_USER" "$SWIFT_PASSWORD"

echo "Ensuring role '$SWIFT_ROLE' on project '$SWIFT_PROJECT' for user '$SWIFT_USER'"
openstack role add --project "$SWIFT_PROJECT" --user "$SWIFT_USER" "$SWIFT_ROLE" || true

echo "Ensuring object-store service exists"
openstack service create \
    --name swift \
    --description "Swift Object Storage" \
    object-store >/dev/null 2>&1 || true

echo "Ensuring Swift endpoints exist"
ensure_endpoint public "$SWIFT_PUBLIC"
ensure_endpoint internal "$SWIFT_INTERNAL"
ensure_endpoint admin "$SWIFT_ADMIN"

echo
echo "Final checks:"
openstack endpoint list --service object-store
openstack user show "$SWIFT_USER"

echo
echo "Proxy [filter:authtoken] values:"
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

echo "Bootstrap complete."

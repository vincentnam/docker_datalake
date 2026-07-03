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

# OIDC federation with Keycloak (identity provider / mapping / protocol)
: "${FEDERATION_ENABLED:=false}"
: "${KEYCLOAK_IDP_ID:=keycloak}"
# Read-only service account used by the Flask API to list the identity
# providers (dynamic login buttons in the web GUI).
: "${IDP_READER_USER:=idp-reader}"
: "${IDP_READER_PASSWORD:=ChangeMe_idp_reader}"
: "${KEYCLOAK_PROTOCOL_ID:=openid}"
: "${KEYCLOAK_ISSUER:=}"
: "${FEDERATED_DOMAIN:=Default}"
: "${FEDERATED_GROUP:=datalake_users}"
: "${FEDERATED_PROJECT:=federated}"
: "${FEDERATED_ROLE:=member}"

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

ensure_domain() {
    domain_name="$1"
    if ! openstack domain show "$domain_name" >/dev/null 2>&1; then
        echo "Creating domain: $domain_name"
        openstack domain create --description "Federated (Keycloak) users and their auto-provisioned projects" "$domain_name" >/dev/null
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

# ---------------------------------------------------------------------------
# OIDC federation with Keycloak : identity provider + mapping + protocol.
# Idempotent ; gated by FEDERATION_ENABLED so a pure-password deployment is
# unaffected. (POSIX sh : this script is run with busybox ash, no bash-isms.)
# ---------------------------------------------------------------------------
FEDERATION_ENABLED_LC=$(printf '%s' "$FEDERATION_ENABLED" | tr '[:upper:]' '[:lower:]')
if [ "$FEDERATION_ENABLED_LC" = "true" ]; then
    echo
    echo "Configuring OIDC federation (IdP=$KEYCLOAK_IDP_ID, issuer=$KEYCLOAK_ISSUER)"

    if [ -z "$KEYCLOAK_ISSUER" ]; then
        echo "ERROR: FEDERATION_ENABLED=true but KEYCLOAK_ISSUER is empty." >&2
        exit 1
    fi

    # Per-user model : the mapping below auto-provisions a dedicated project per
    # federated user and grants them FEDERATED_ROLE on it. Just make sure every
    # role referenced by the datalake exists (idempotent).
    ensure_role "$FEDERATED_ROLE"
    ensure_role "$READER_ROLE"
    ensure_role "$WRITER_ROLE"
    ensure_role "$BUCKET_ADMIN_ROLE"
    ensure_role "$BUCKET_OWNER_ROLE"

    # Dedicated domain for the federated users : Keystone attaches the shadow
    # users AND the auto-provisioned projects to the domain of the identity
    # provider, so this is what really isolates them from the local accounts.
    ensure_domain "$FEDERATED_DOMAIN"

    # Read-only service account for the Flask API : lists the registered IdPs
    # (policy.yaml grants identity:list_identity_providers to idp_reader) so
    # the web GUI can build one login button per identity provider.
    # ensure_user never updates the password of an existing user, so re-apply
    # it explicitly : the Flask .env and Keystone must stay in sync even when
    # IDP_READER_PASSWORD changed between two runs.
    ensure_role "idp_reader"
    ensure_user "$IDP_READER_USER" "$IDP_READER_PASSWORD"
    openstack user set --password "$IDP_READER_PASSWORD" "$IDP_READER_USER"
    openstack role add --project "$SWIFT_PROJECT" --user "$IDP_READER_USER" idp_reader || true

    # Identity provider (remote-id MUST equal the Keycloak issuer).
    # NOTE : the domain of an existing IdP is immutable — only remote-id can be
    # updated in place. Changing FEDERATED_DOMAIN requires deleting the IdP
    # first so it gets recreated here in the new domain.
    if ! openstack identity provider show "$KEYCLOAK_IDP_ID" >/dev/null 2>&1; then
        echo "Creating identity provider: $KEYCLOAK_IDP_ID (domain: $FEDERATED_DOMAIN)"
        openstack identity provider create --domain "$FEDERATED_DOMAIN" \
            --remote-id "$KEYCLOAK_ISSUER" \
            --description "Keycloak ($KEYCLOAK_IDP_ID)" \
            "$KEYCLOAK_IDP_ID" >/dev/null
    else
        openstack identity provider set --remote-id "$KEYCLOAK_ISSUER" "$KEYCLOAK_IDP_ID" >/dev/null
    fi

    # Mapping : Keycloak identity -> ephemeral Keystone user, with a dedicated
    # auto-provisioned project named after the username ({0}) on which the user
    # gets FEDERATED_ROLE (bucket_owner). Keystone creates the project on first
    # login (federation auto-provisioning).
    #
    # Every entry listed in "remote" is a *requirement* :
    #  - preferred_username ({0}) : always present, names the user + project.
    #    (email is deliberately NOT required : a hand-created Keycloak account
    #    often has none, and requiring it would silently break provisioning.)
    #  - HTTP_OIDC_groups must contain FEDERATED_GROUP : the Keycloak group is
    #    the datalake ACCESS GATE. Not in the group = authenticated by Keycloak
    #    but refused by Keystone (no token). Removing a user from the group
    #    blocks the NEXT login ; the shadow user / project / data stay intact
    #    and are recovered if the user is added back.
    #    Requires the "groups" protocol mapper on the Keycloak client (present
    #    in the bundled realm ; to create manually on an external Keycloak).
    #    NOTE the claim key case : mod_auth_openidc exposes claims KEEPING their
    #    original (lowercase) name, so it is HTTP_OIDC_groups, NOT _GROUPS, the
    #    same way remote_id_attribute uses HTTP_OIDC_iss (lowercase).
    MAPPING_ID="${KEYCLOAK_IDP_ID}_mapping"
    MAPPING_FILE="$(mktemp)"
    cat > "$MAPPING_FILE" <<MAP
[
  {
    "local": [
      {
        "user": {
          "name": "{0}",
          "domain": { "name": "$FEDERATED_DOMAIN" }
        },
        "projects": [
          {
            "name": "{0}",
            "roles": [
              { "name": "$FEDERATED_ROLE" }
            ]
          }
        ]
      }
    ],
    "remote": [
      { "type": "HTTP_OIDC_preferred_username" },
      {
        "type": "HTTP_OIDC_groups",
        "any_one_of": [ "$FEDERATED_GROUP" ]
      }
    ]
  }
]
MAP
    if ! openstack mapping show "$MAPPING_ID" >/dev/null 2>&1; then
        echo "Creating mapping: $MAPPING_ID"
        openstack mapping create --rules "$MAPPING_FILE" "$MAPPING_ID" >/dev/null
    else
        openstack mapping set --rules "$MAPPING_FILE" "$MAPPING_ID" >/dev/null
    fi
    rm -f "$MAPPING_FILE"

    # Federation protocol linking IdP + mapping.
    # NOTE: `openstack federation protocol create` is unreliable on this client
    # version ("Request requires an ID but none was found"), so we PUT it through
    # the Keystone REST API directly (idempotent: 409 means already present).
    if ! openstack federation protocol show --identity-provider "$KEYCLOAK_IDP_ID" "$KEYCLOAK_PROTOCOL_ID" >/dev/null 2>&1; then
        echo "Creating federation protocol: $KEYCLOAK_PROTOCOL_ID"
        PROTO_TOKEN="$(openstack token issue -f value -c id)"
        python3 - "$PROTO_TOKEN" "$OS_AUTH_URL" "$KEYCLOAK_IDP_ID" "$KEYCLOAK_PROTOCOL_ID" "$MAPPING_ID" <<'PY'
import sys, json, urllib.request, urllib.error
tok, auth_url, idp, proto, mapping = sys.argv[1:6]
url = "%s/OS-FEDERATION/identity_providers/%s/protocols/%s" % (auth_url.rstrip("/"), idp, proto)
body = json.dumps({"protocol": {"mapping_id": mapping}}).encode()
req = urllib.request.Request(url, data=body, method="PUT",
    headers={"X-Auth-Token": tok, "Content-Type": "application/json"})
try:
    resp = urllib.request.urlopen(req)
    print("Protocol '%s' created (HTTP %s)" % (proto, resp.status))
except urllib.error.HTTPError as e:
    if e.code == 409:
        print("Protocol '%s' already exists" % proto)
    else:
        sys.stderr.write("Failed to create protocol: HTTP %s %s\n" % (e.code, e.read().decode()))
        sys.exit(1)
PY
    fi

    echo
    echo "Federation summary:"
    openstack identity provider show "$KEYCLOAK_IDP_ID"
    openstack federation protocol list --identity-provider "$KEYCLOAK_IDP_ID"
fi

echo "Bootstrap complete."

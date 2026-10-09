#!/bin/bash
# Generates the Swift configuration of the Kubernetes deployment from conf.env :
#   volumes/configmap_swift_conf.yml    account / container / object / proxy confs (no secret)
#   volumes/secret_swift_secrets.yml    swift.conf (hash prefix/suffix) + Keystone password of the proxy
#
# Kubernetes counterpart of rawdata_zone/openstackSwift/create_conf.sh :
#  - one common conf per server type : every storage pod uses the same template (no more -$i files)
#  - [container-*] sections in the container conf (they were [object-*])
#  - proxy : memcache_servers on the centralized memcached, explicit workers,
#            Keystone password moved to the Secret (merged through proxy-server.conf.d/)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONF_ENV="${CONF_ENV:-$SCRIPT_DIR/../../../conf.env}"
VOLUMES_PATH="$SCRIPT_DIR/volumes"

NAMESPACE="datalake"
MEMCACHED_SERVERS="memcached:11211"       # centralized memcached of the whole architecture
KEYSTONE_URL_INTERNAL="http://keystone:5000/v3"
STORAGE_WORKERS=2
PROXY_WORKERS=2                           # explicit : unset, Swift forks one worker per core of the whole node

if [ ! -f "$CONF_ENV" ]; then
  echo "Error: $CONF_ENV not found."
  exit 1
fi
export $(grep -v '^#' "$CONF_ENV" | sed 's/\r$//' | xargs)

for var in SWIFT_PASSWORD SWIFT_HASH_PREFIX SWIFT_HASH_SUFFIX; do
  if [ -z "${!var:-}" ]; then
    echo "Set $var in $CONF_ENV."
    exit 1
  fi
done

mkdir -p "$VOLUMES_PATH"

# indent <n> : shifts stdin by n spaces, to embed a file in a YAML block scalar
indent() {
  sed "s/^/$(printf '%*s' "$1" '')/"
}

####################################
## STORAGE SERVERS (storage pods)
####################################
ACCOUNT_CONF=$(cat << EOF
[DEFAULT]
devices = /srv/node/
bind_ip = 0.0.0.0
bind_port = 6200
workers = $STORAGE_WORKERS
log_facility = LOG_LOCAL5

[pipeline:main]
pipeline = healthcheck recon account-server

[app:account-server]
use = egg:swift#account

[filter:recon]
use = egg:swift#recon

[filter:healthcheck]
use = egg:swift#healthcheck

[account-replicator]

[account-auditor]

[account-reaper]
EOF
)

CONTAINER_CONF=$(cat << EOF
[DEFAULT]
devices = /srv/node/
bind_ip = 0.0.0.0
bind_port = 6201
workers = $STORAGE_WORKERS
log_facility = LOG_LOCAL7

[pipeline:main]
pipeline = healthcheck recon container-server

[app:container-server]
use = egg:swift#container

[filter:recon]
use = egg:swift#recon

[filter:healthcheck]
use = egg:swift#healthcheck

[container-replicator]

[container-updater]

[container-auditor]
EOF
)

OBJECT_CONF=$(cat << EOF
[DEFAULT]
devices = /srv/node/
bind_ip = 0.0.0.0
bind_port = 6202
workers = $STORAGE_WORKERS
log_facility = LOG_LOCAL3

[pipeline:main]
pipeline = healthcheck recon object-server

[app:object-server]
use = egg:swift#object

[filter:recon]
use = egg:swift#recon

[filter:healthcheck]
use = egg:swift#healthcheck

[object-replicator]

[object-updater]

[object-auditor]
EOF
)

####################################
## PROXY SERVER (proxy pods)
####################################
PROXY_CONF=$(cat << EOF
[DEFAULT]
bind_ip = 0.0.0.0
bind_port = 8080
workers = $PROXY_WORKERS
log_address = /dev/log
log_facility = LOG_LOCAL2
log_headers = false
log_level = DEBUG
log_name = proxy-server
user = swift

[pipeline:main]
pipeline = catch_errors gatekeeper healthcheck proxy-logging cache listing_formats bulk tempurl ratelimit authtoken keystoneauth staticweb copy container-quotas account-quotas slo dlo versioned_writes symlink proxy-logging proxy-server

[filter:catch_errors]
use = egg:swift#catch_errors

[filter:healthcheck]
use = egg:swift#healthcheck

[filter:proxy-logging]
use = egg:swift#proxy_logging

[filter:bulk]
use = egg:swift#bulk

[filter:ratelimit]
use = egg:swift#ratelimit

[filter:dlo]
use = egg:swift#dlo

[filter:slo]
use = egg:swift#slo

[filter:tempurl]
use = egg:swift#tempurl

[filter:authtoken]
paste.filter_factory = keystonemiddleware.auth_token:filter_factory
www_authenticate_uri = $KEYSTONE_URL_INTERNAL
auth_url = $KEYSTONE_URL_INTERNAL
auth_type = password
project_name = service
username = swift
# password : Secret swift-secrets, mounted as proxy-server.conf.d/10-authtoken.conf
user_domain_name = Default
project_domain_name = Default
memcached_servers = $MEMCACHED_SERVERS
token_cache_time = 3600
include_service_catalog = false
service_type = object-store
delay_auth_decision = true
log_name = authtoken-swift

[filter:keystoneauth]
use = egg:swift#keystoneauth
operator_roles = admin, bucket_owner, bucket_admin, member
project_reader_roles = reader
reseller_admin_role = admin
reseller_prefix = AUTH_

[filter:staticweb]
use = egg:swift#staticweb

[filter:account-quotas]
use = egg:swift#account_quotas

[filter:container-quotas]
use = egg:swift#container_quotas

[filter:cache]
use = egg:swift#memcache
memcache_servers = $MEMCACHED_SERVERS

[filter:gatekeeper]
use = egg:swift#gatekeeper

[filter:versioned_writes]
use = egg:swift#versioned_writes
allow_versioned_writes = true
allow_object_versioning = true

[filter:copy]
use = egg:swift#copy

[filter:listing_formats]
use = egg:swift#listing_formats

[filter:symlink]
use = egg:swift#symlink

[app:proxy-server]
use = egg:swift#proxy
allow_account_management = true
account_autocreate = true
EOF
)

####################################
## SECRETS
####################################
SWIFT_CONF=$(cat << EOF
[swift-hash]
# random unique strings that can never change (DO NOT LOSE)
swift_hash_path_prefix = $SWIFT_HASH_PREFIX
swift_hash_path_suffix = $SWIFT_HASH_SUFFIX

[storage-policy:0]
name = 1replica
default = true
policy_type = replication
EOF
)

PROXY_AUTHTOKEN_CONF=$(cat << EOF
[filter:authtoken]
password = $SWIFT_PASSWORD
EOF
)

####################################
## YAML FILES
####################################
cat << EOF > "$VOLUMES_PATH/configmap_swift_conf.yml"
# Generated by create_conf.sh from conf.env : edit create_conf.sh, not this file
apiVersion: v1
kind: ConfigMap
metadata:
  name: swift-conf
  namespace: $NAMESPACE
  labels:
    app.kubernetes.io/name: swift
    app.kubernetes.io/part-of: raw-data-zone
data:
  account-server.conf: |
$(echo "$ACCOUNT_CONF" | indent 4)
  container-server.conf: |
$(echo "$CONTAINER_CONF" | indent 4)
  object-server.conf: |
$(echo "$OBJECT_CONF" | indent 4)
  proxy-server.conf: |
$(echo "$PROXY_CONF" | indent 4)
EOF

# stringData : plain values, Kubernetes encodes them itself. Holds secrets : never committed (.gitignore)
cat << EOF > "$VOLUMES_PATH/secret_swift_secrets.yml"
# Generated by create_conf.sh from conf.env : edit create_conf.sh, not this file
apiVersion: v1
kind: Secret
metadata:
  name: swift-secrets
  namespace: $NAMESPACE
  labels:
    app.kubernetes.io/name: swift
    app.kubernetes.io/part-of: raw-data-zone
type: Opaque
stringData:
  swift.conf: |
$(echo "$SWIFT_CONF" | indent 4)
  proxy-authtoken.conf: |
$(echo "$PROXY_AUTHTOKEN_CONF" | indent 4)
EOF
chmod 600 "$VOLUMES_PATH/secret_swift_secrets.yml"

echo "Generated :"
echo "  $VOLUMES_PATH/configmap_swift_conf.yml"
echo "  $VOLUMES_PATH/secret_swift_secrets.yml"

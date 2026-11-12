#!/bin/bash


export $(grep -v '^#' ./conf.env | sed 's/\r$//' | xargs)
OPENSTACKSWIFT_KUBE_PATH="./kubernetes/rawdata_zone/openstackSwift"

if [ -z "$SWIFT_PASSWORD" ]; then
  echo "Set the Swift account password in conf.env file."
  exit 1
fi

if [ -z "$SWIFT_HASH_PREFIX" ]; then
  echo "Set the Swift hash prefix in conf.env file."
  exit 1
fi

if [ -z "$SWIFT_HASH_SUFFIX" ]; then
  echo "Set the Swift hash suffix in conf.env file."
  exit 1
fi

mkdir -p $OPENSTACKSWIFT_KUBE_PATH/volumes


###################################
# SWIFT CONF (ConfigMap, no secret)
###################################
# One conf per server type, shared by every storage pod.
# Proxy workers are set : unset, Swift starts one worker per core of the node.
# The Keystone password of the proxy is in the Secret below.
cat << EOF > $OPENSTACKSWIFT_KUBE_PATH/volumes/configmap_swift_conf.yml
apiVersion: v1
kind: ConfigMap
metadata:
  name: swift-conf
  namespace: datalake
  labels:
    app.kubernetes.io/name: swift
    app.kubernetes.io/part-of: raw-data-zone
data:
  account-server.conf: |
    [DEFAULT]
    devices = /srv/node/
    bind_ip = 0.0.0.0
    bind_port = 6200
    workers = 2
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
  container-server.conf: |
    [DEFAULT]
    devices = /srv/node/
    bind_ip = 0.0.0.0
    bind_port = 6201
    workers = 2
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
  object-server.conf: |
    [DEFAULT]
    devices = /srv/node/
    bind_ip = 0.0.0.0
    bind_port = 6202
    workers = 2
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
  proxy-server.conf: |
    [DEFAULT]
    bind_ip = 0.0.0.0
    bind_port = 8080
    workers = 2
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
    www_authenticate_uri = http://keystone:5000/v3
    auth_url = http://keystone:5000/v3
    auth_type = password
    project_name = service
    username = swift
    user_domain_name = Default
    project_domain_name = Default
    memcached_servers = memcached:11211
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
    memcache_servers = memcached:11211

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


###################################
# SWIFT SECRETS (Secret, never committed)
###################################
# proxy-authtoken.conf is mounted as proxy-server.conf.d/10-authtoken.conf :
# Swift merges it with the [filter:authtoken] section of proxy-server.conf.
cat << EOF > $OPENSTACKSWIFT_KUBE_PATH/volumes/secret_swift_secrets.yml
apiVersion: v1
kind: Secret
metadata:
  name: swift-secrets
  namespace: datalake
  labels:
    app.kubernetes.io/name: swift
    app.kubernetes.io/part-of: raw-data-zone
type: Opaque
stringData:
  swift.conf: |
    [swift-hash]
    # random unique strings that can never change (DO NOT LOSE)
    swift_hash_path_prefix = $SWIFT_HASH_PREFIX
    swift_hash_path_suffix = $SWIFT_HASH_SUFFIX

    [storage-policy:0]
    name = 1replica
    default = true
    policy_type = replication
  proxy-authtoken.conf: |
    [filter:authtoken]
    password = $SWIFT_PASSWORD
EOF
chmod 600 $OPENSTACKSWIFT_KUBE_PATH/volumes/secret_swift_secrets.yml

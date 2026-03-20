#!/bin/bash

cat << EOF > conf/swift.conf

[swift-hash]
# random unique strings that can never change (DO NOT LOSE)
swift_hash_path_prefix = bd08f643f5663c4ec607
swift_hash_path_suffix = f423bf7ab663888fe832

[storage-policy:0]
name = 1replica
default = true
policy_type = replication

# [storage-policy:1]
# name = EC42
# policy_type = erasure_coding
# ec_type = liberasurecode_rs_vand
# ec_num_data_fragments = 4
# ec_num_parity_fragments = 2
# ec_object_segment_size = 1048576

EOF


export $(grep -v '^#' ./config_cluster.env | sed 's/\r$//' | xargs)

#NODE_STORAGE_SIZE="1GB"

for i in $(seq $NB_MANAGEMENT_NODE); do


  cat << EOF > scripts/management/management-$i.sh
DEVICE_NAME="swift-account-d-$i"
#
#
#mkdir -p /srv/node/\$DEVICE_NAME
#mount -t xfs -o noatime /internal_dev/\$DEVICE_NAME /srv/node/\$DEVICE_NAME;
chown -R swift:swift /srv/node
su swift
rm /run/rsyslogd.pid
## Start rsync
/etc/init.d/rsync restart

## Start memcached
/etc/init.d/memcached start

## Restart rsyslog
rsyslogd

swift-proxy-server /etc/swift/proxy/proxy-$i.conf verbose
EOF
SWIFT_USER_PASSWORD=$(openssl rand -base64 12)

  cat << EOF > conf/proxy/proxy-$i.conf
[DEFAULT]
bind_ip = 0.0.0.0
bind_port = 8080
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
password = testing
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
operator_roles = admin, bucket_owner, project_admin, swiftoperator, ResellerAdmin
reseller_prefix = AUTH_
is_admin = false

[filter:staticweb]
use = egg:swift#staticweb

[filter:account-quotas]
use = egg:swift#account_quotas

[filter:container-quotas]
use = egg:swift#container_quotas

[filter:cache]
use = egg:swift#memcache

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

#TODO: Version of S3 api + S3 authentication based on Keystone to test
#[DEFAULT]
 #bind_ip = 0.0.0.0
 #bind_port = 8080
 #log_address = /dev/log
 #log_facility = LOG_LOCAL2
 #log_headers = false
 #log_level = DEBUG
 #log_name = proxy-server
 #user = swift
 #
 #[pipeline:main]
 #pipeline = catch_errors gatekeeper healthcheck proxy-logging cache listing_formats bulk tempurl ratelimit s3api s3token authtoken keystoneauth staticweb copy container-quotas account-quotas slo dlo versioned_writes symlink proxy-logging proxy-server
 #
 #[filter:catch_errors]
 #use = egg:swift#catch_errors
 #
 #[filter:healthcheck]
 #use = egg:swift#healthcheck
 #
 #[filter:proxy-logging]
 #use = egg:swift#proxy_logging
 #
 #[filter:bulk]
 #use = egg:swift#bulk
 #
 #[filter:ratelimit]
 #use = egg:swift#ratelimit
 #
 #[filter:dlo]
 #use = egg:swift#dlo
 #
 #[filter:slo]
 #use = egg:swift#slo
 #
 #[filter:tempurl]
 #use = egg:swift#tempurl
 #
 #[filter:authtoken]
 #paste.filter_factory = keystonemiddleware.auth_token:filter_factory
 #www_authenticate_uri = http://keystone:5000/v3
 #auth_url = http://keystone:5000/v3
 #auth_type = password
 #project_name = service
 #username = swift
 #password = testing
 #user_domain_name = Default
 #project_domain_name = Default
 #memcached_servers = memcached:11211
 #token_cache_time = 3600
 #include_service_catalog = false
 #service_type = object-store
 #delay_auth_decision = true
 #log_name = authtoken-swift
 #
 #[filter:s3token]
 #use = egg:swift#s3token
 #auth_uri = http://keystone:5000/v3
 #auth_version = v3
 #admin_user = swift
 #admin_password = testing
 #admin_tenant_name = service
 #admin_user_domain_name = Default
 #admin_project_domain_name = Default
 #memcached_servers = memcached:11211
 #
 #[filter:keystoneauth]
 #use = egg:swift#keystoneauth
 #operator_roles = admin, bucket_owner, project_admin, swiftoperator, ResellerAdmin
 #reseller_prefix = AUTH_
 #is_admin = false
 #
 #[filter:staticweb]
 #use = egg:swift#staticweb
 #
 #[filter:account-quotas]
 #use = egg:swift#account_quotas
 #
 #[filter:container-quotas]
 #use = egg:swift#container_quotas
 #
 #[filter:cache]
 #use = egg:swift#memcache
 #
 #[filter:gatekeeper]
 #use = egg:swift#gatekeeper
 #
 #[filter:versioned_writes]
 #use = egg:swift#versioned_writes
 #allow_versioned_writes = true
 #allow_object_versioning = true
 #
 #[filter:copy]
 #use = egg:swift#copy
 #
 #[filter:listing_formats]
 #use = egg:swift#listing_formats
 #
 #[filter:symlink]
 #use = egg:swift#symlink
 #
 #[filter:s3api]
 #use = egg:swift#s3api
 #cors_preflight_allow_origin = *
 #allow_multipart_uploads = true
 #check_bucket_owner = true
 #
 #[app:proxy-server]
 #use = egg:swift#proxy
 #allow_account_management = true
 #account_autocreate = true




done




# TODO: Mount just created loop dev and not /dev/loop0


for i in $(seq $NB_STORAGE_NODE); do

  cat << EOF > scripts/storage/storage-$i.sh
#!/bin/bash


get_loop_for_device_number() {
  local number="$1"
  local output
  output=$(losetup -l 2>/dev/null | tail -n +2 | awk '{for(i=1; i<=NF; i++) if ($i ~ /swift-storage-d-'"$number"'$/) {print $1; exit}}')
  echo "${output:-null}"
}


ls /internal_dev
mkdir -p /srv/node/swift-storage-d-$i /internal_dev

truncate --size $NODE_STORAGE_SIZE /internal_dev/swift-storage-d-$i
mkfs.xfs -f -L size=512 /internal_dev/swift-storage-d-$i
losetup -f /internal_dev/swift-storage-d-$i -v
losetup

mount -t xfs -o noatime  /dev/loop0 /srv/node/swift-storage-d-1

# TODO: Mount just created loop dev and not /dev/loop0


#truncate -s $NODE_STORAGE_SIZE /internal_dev/$DEVICE_NAME;
#echo "    created storage device /internal_dev/$DEVICE_NAME of $NODE_STORAGE_SIZE";
#export PATH=$PATH:/opt/python/usr/local/bin/

#echo "[[ creating directories ]]"


mkdir -p /srv/node/swift-storage-d-$i

chown -R swift:swift /srv/node


sed -i -e 's/RSYNC_ENABLE=false/RSYNC_ENABLE=true/g' /etc/default/rsync
rm /run/rsyslogd.pid
## Start rsync
/etc/init.d/rsync start

## Start memcached
/etc/init.d/memcached start

## Restart rsyslog
rsyslogd

swift-account-server /etc/swift/account/account-$i.conf verbose &
swift-object-server /etc/swift/object/object-$i.conf verbose &
swift-container-server /etc/swift/container/container-$i.conf &
wait

EOF

  cat << EOF > conf/account/account-$i.conf
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
EOF

  cat << EOF > conf/container/container-$i.conf
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


[object-replicator]

[object-updater]

[object-auditor]
EOF
  cat << EOF > conf/object/object-$i.conf
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
EOF


  cat << EOF > rsyncd/rsyncd-$i.conf
uid = swift
gid = swift
log file = /var/log/rsyncd.log
pid file = /var/run/rsyncd.pid
address = 10.5.1.$i

[account]
max connections = 2
path = /srv/node/
read only = False
lock file = /var/lock/account.lock

[container]
max connections = 2
path = /srv/node/
read only = False
lock file = /var/lock/container.lock

[object]
max connections = 2
path = /srv/node/
read only = False
lock file = /var/lock/object.lock

EOF


done




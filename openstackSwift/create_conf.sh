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

NODE_STORAGE_SIZE="1GB"

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
pipeline = catch_errors gatekeeper healthcheck proxy-logging cache etag-quoter listing_formats bulk tempurl ratelimit s3api tempauth staticweb copy container-quotas account-quotas slo dlo versioned_writes symlink proxy-logging proxy-server

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

[filter:crossdomain]
use = egg:swift#crossdomain

[filter:dlo]
use = egg:swift#dlo

[filter:slo]
use = egg:swift#slo

[filter:tempurl]
use = egg:swift#tempurl

[filter:tempauth]
use = egg:swift#tempauth
user_admin_admin = admin .admin .reseller_admin
user_test_tester = testing .admin
user_test_tester2 = testing2 .admin
user_test_tester3 = testing3
user_test2_tester2 = testing2 .admin

[filter:staticweb]
use = egg:swift#staticweb

[filter:account-quotas]
use = egg:swift#account_quotas

[filter:container-quotas]
use = egg:swift#container_quotas

[filter:cache]
use = egg:swift#memcache

[filter:etag-quoter]
use = egg:swift#etag_quoter
enable_by_default = false

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

# To enable, add the s3api middleware to the pipeline before tempauth
[filter:s3api]
use = egg:swift#s3api
#cors_preflight_allow_origin = http://10.5.255.1:3000,http://localhost:3000
cors_preflight_allow_origin = *

# Example to create root secret: `openssl rand -base64 32`
[filter:keymaster]
use = egg:swift#keymaster
encryption_root_secret = 2dv+rC3v87jdnGwxY+z0jg6xm2BaJM71QXbdMTAOrkQ=

# To enable use of encryption add both middlewares to pipeline, example:
# <other middleware> keymaster encryption proxy-logging proxy-server
[filter:encryption]
use = egg:swift#encryption

[app:proxy-server]
use = egg:swift#proxy
allow_account_management = true
account_autocreate = true
EOF






done







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

truncate --size 1G /internal_dev/swift-storage-d-$i
mkfs.xfs -f -L size=512 /internal_dev/swift-storage-d-$i
losetup -f /internal_dev/swift-storage-d-$i -v
losetup

mount -t xfs -o noatime  /dev/loop0 /srv/node/swift-storage-d-1

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




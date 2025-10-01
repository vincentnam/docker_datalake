cat <<EOF > ../docker-compose_cluster.yml
services:
    init:
      build:
        context: .
        dockerfile: Dockerfile.base
      volumes:
        - ./conf/:/etc/swift
        - ./data/:/internal_dev/
        - ./build_script:/scripts/
      command: sh /scripts/init.sh
      privileged: true
      networks:
        - swift_cluster

EOF
export $(grep -v '^#' ./config_cluster.env | sed 's/\r$//' | xargs)
for i in $(seq $NB_ACCOUNT_SERVER); do
  cat << EOF >> ../docker-compose_cluster.yml
    account-$i:
      hostname: account-$i
      build:
        context: .
        dockerfile: dockerfiles/Dockerfile.base
      entrypoint: ["sh","/scripts/account/account-$i.sh"]
      volumes:
          - ./conf/:/etc/swift
          - ./data/:/internal_dev/
          - ./build_script:/scripts/
      privileged: true
      restart: always
      networks:
        swift_cluster:
          ipv4_address: 10.5.3.$i
      depends_on:
        init:
          condition: service_completed_successfully
EOF
  cat << EOF >> account/account-$i.sh
DEVICE_NAME="swift-account-d-$i"
mount -t xfs -o noatime /internal_dev/\$DEVICE_NAME /srv/node/\$DEVICE_NAME;
su swift
swift-account-server /etc/swift/account/account-$i.conf verbose"
EOF

  cat << EOF >> ../conf/account/account-$i.conf
[DEFAULT]
devices = /srv/node/swift-account-d-$i
bind_ip = 0.0.0.0
bind_port = 6200
workers = 2
mount_check = false
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

done


for i in $(seq $NB_OBJECT_SERVER); do
  cat << EOF >> ../docker-compose_cluster.yml
    object-$i:
      hostname: object-$i
      build:
        context: .
        dockerfile: dockerfiles/Dockerfile.base
      entrypoint: ["sh","/scripts/object/object-$i.sh"]
      volumes:
          - ./conf/:/etc/swift
          - ./data/:/internal_dev/
          - ./build_script:/scripts/
      privileged: true
      restart: always
      networks:
        swift_cluster:
          ipv4_address: 10.5.2.$i
      depends_on:
        init:
          condition: service_completed_successfully
EOF
  cat << EOF >> object/object-$i.sh
DEVICE_NAME="swift-object-d-$i"
mount -t xfs -o noatime /internal_dev/\$DEVICE_NAME /srv/node/\$DEVICE_NAME;
su swift
swift-account-server /etc/swift/object/object-$i.conf verbose"
EOF
  cat << EOF >> ../conf/object/object-$i.conf
[DEFAULT]
devices = /srv/node/swift-object-d-$i
bind_ip = 0.0.0.0
bind_port = 6200
workers = 2
mount_check = false
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


done



for i in $(seq $NB_CONTAINER_SERVER); do
  cat << EOF >> ../docker-compose_cluster.yml
    container-$i:
      hostname: container-$i
      build:
        context: .
        dockerfile: dockerfiles/Dockerfile.base
      entrypoint: ["sh","/scripts/container/container-$i.sh"]
      volumes:
          - ./conf/:/etc/swift
          - ./data/:/internal_dev/
          - ./build_script:/scripts/
      privileged: true
      restart: always
      networks:
        swift_cluster:
          ipv4_address: 10.5.4.$i
      depends_on:
        init:
          condition: service_completed_successfully
EOF
  cat << EOF >> container/container-$i.sh
DEVICE_NAME="swift-container-d-$i"
mount -t xfs -o noatime /internal_dev/\$DEVICE_NAME /srv/node/\$DEVICE_NAME;
su swift
swift-container-server /etc/swift/container/container-$i.conf verbose"
EOF
  cat << EOF >> ../conf/container/container-$i.conf
[DEFAULT]
devices = /srv/node/swift-container-d-$i
bind_ip = 0.0.0.0
bind_port = 6200
workers = 2
mount_check = false
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


done


cat <<EOF >> ../docker-compose_cluster.yml
volumes:
  swift_conf:
  swift_data:
  swift_cache:

networks:
  swift_cluster:
    driver: overlay
    attachable: true
    ipam:
      config:
        - subnet: 10.5.0.0/16
          gateway: 10.5.0.1
EOF
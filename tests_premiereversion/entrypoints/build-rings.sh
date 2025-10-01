##!/bin/sh
#set -e
#
#CONF_DIR=${CONF_DIR:-/etc/swift}
#REPLICAS=${REPLICAS:-3}
#PART_POWER=${PART_POWER:-18}
#PARTITIONS=$(expr 2 \* $(expr 2 \* ${PART_POWER}))
#
## expecting a file devices.json or ENV with device list; simple example: read DEVICES env var like "host1:/srv/node/sdb,host2:/srv/node/sdb"
#if [ -n "${DEVICES}" ]; then
#  IFS=','; set -- ${DEVICES}
#  # build rings with provided device list
#  swift-ring-builder ${CONF_DIR}/account.builder create ${PARTITIONS} ${PART_POWER} ${REPLICAS}
#  for d in "$@"; do
#    IFS=':'; host=${d%%:*}; device=${d#*:}
#    swift-ring-builder ${CONF_DIR}/account.builder add --region 1 --zone 1 --ip ${host} --port 6202 ${device} 100
#  done
#  swift-ring-builder ${CONF_DIR}/account.builder rebalance
#  cp ${CONF_DIR}/account.builder ${CONF_DIR}/account.ring.gz || true
#  # repeat for container and object (simplified)
#  swift-ring-builder ${CONF_DIR}/container.builder create ${PARTITIONS} ${PART_POWER} ${REPLICAS}
#  swift-ring-builder ${CONF_DIR}/object.builder create ${PARTITIONS} ${PART_POWER} ${REPLICAS}
#  swift-ring-builder ${CONF_DIR}/container.builder rebalance
#  swift-ring-builder ${CONF_DIR}/object.builder rebalance
#  cp ${CONF_DIR}/*.builder ${CONF_DIR}/
#else
#  echo "No DEVICES env provided. To create rings, set DEVICES='ip1:/srv/node/sdb,ip2:/srv/node/sdb,...'"
#  exit 1
#fi

#!/bin/bash
set -e

cd /etc/swift

# Build account ring (18 parts, 1 replica, 1 min part hour ; comme SAIO mais multi-node)
swift-ring-builder account.builder create 18 1 1
swift-ring-builder account.builder add r1z1-10.5.3.1:6002/sdb0 100  # account-1
swift-ring-builder account.builder rebalance

# Container ring
swift-ring-builder container.builder create 18 1 1
swift-ring-builder container.builder add r1z1-10.5.4.1:6001/sdb0 100  # container-1
swift-ring-builder container.builder rebalance

# Object ring (3 replicas pour HA)
swift-ring-builder object.builder create 18 3 1
swift-ring-builder object.builder add r1z1-10.5.10.1:6000/sda1 100  # object-1
swift-ring-builder object-builder add r1z1-10.5.10.2:6000/sda1 100  # object-2
swift-ring-builder object.builder add r1z1-10.5.10.3:6000/sda1 100  # object-3
swift-ring-builder object.builder rebalance

chown -R swift:swift *.ring.gz *.builder
echo "Rings built successfully"
#!/bin/sh
set -e

CONF_DIR=${CONF_DIR:-/etc/swift}
REPLICAS=${REPLICAS:-3}
PART_POWER=${PART_POWER:-18}
PARTITIONS=$(expr 2 \* $(expr 2 \* ${PART_POWER}))

# expecting a file devices.json or ENV with device list; simple example: read DEVICES env var like "host1:/srv/node/sdb,host2:/srv/node/sdb"
if [ -n "${DEVICES}" ]; then
  IFS=','; set -- ${DEVICES}
  # build rings with provided device list
  swift-ring-builder ${CONF_DIR}/account.builder create ${PARTITIONS} ${PART_POWER} ${REPLICAS}
  for d in "$@"; do
    IFS=':'; host=${d%%:*}; device=${d#*:}
    swift-ring-builder ${CONF_DIR}/account.builder add --region 1 --zone 1 --ip ${host} --port 6202 ${device} 100
  done
  swift-ring-builder ${CONF_DIR}/account.builder rebalance
  cp ${CONF_DIR}/account.builder ${CONF_DIR}/account.ring.gz || true
  # repeat for container and object (simplified)
  swift-ring-builder ${CONF_DIR}/container.builder create ${PARTITIONS} ${PART_POWER} ${REPLICAS}
  swift-ring-builder ${CONF_DIR}/object.builder create ${PARTITIONS} ${PART_POWER} ${REPLICAS}
  swift-ring-builder ${CONF_DIR}/container.builder rebalance
  swift-ring-builder ${CONF_DIR}/object.builder rebalance
  cp ${CONF_DIR}/*.builder ${CONF_DIR}/
else
  echo "No DEVICES env provided. To create rings, set DEVICES='ip1:/srv/node/sdb,ip2:/srv/node/sdb,...'"
  exit 1
fi
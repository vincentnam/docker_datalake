#!/bin/bash
# A failed step must stop the script : rings written from a half-built builder would lose objects.
set -euo pipefail

export $(grep -v '^#' ./conf.env | sed 's/\r$//' | xargs)
OPENSTACKSWIFT_KUBE_PATH="./kubernetes/rawdata_zone/openstackSwift"
RINGS_WORK_PATH="/tmp/swift_rings"
SWIFT_IMAGE="swift-base:2.30.0"

if [ -z "$NB_STORAGE_NODE" ]; then
  echo "Set the number of storage nodes in conf.env file."
  exit 1
fi

if [ -z "$NODE_STORAGE_SIZE" ]; then
  echo "Set the storage node size in conf.env file."
  exit 1
fi

if [ -z "$SWIFT_PART_POWER" ]; then
  echo "Set the Swift part power in conf.env file."
  exit 1
fi

if [ -z "$SWIFT_MIN_PART_HOURS" ]; then
  echo "Set the Swift min part hours in conf.env file."
  exit 1
fi

if ! sudo docker image inspect $SWIFT_IMAGE >/dev/null 2>&1; then
  echo "Error: image $SWIFT_IMAGE not found. Please run start.sh with -b first."
  exit 1
fi

# 3 replicas at most
REPLICAS=$NB_STORAGE_NODE
if [ "$NB_STORAGE_NODE" -gt 3 ]; then
  REPLICAS=3
fi

# Weight of a device = disk size ("10GB" -> 10)
WEIGHT=$(echo "$NODE_STORAGE_SIZE" | tr -dc '0-9')

# swift-ring-builder runs in the Swift image, on the files of RINGS_WORK_PATH
RING_BUILDER="sudo docker run --rm --user $(id -u):$(id -g) -v $RINGS_WORK_PATH:/rings -w /rings $SWIFT_IMAGE swift-ring-builder"

rm -rf $RINGS_WORK_PATH
mkdir -p $RINGS_WORK_PATH
mkdir -p $OPENSTACKSWIFT_KUBE_PATH/volumes


###################################
# EXISTING RINGS
###################################
# Rings are created once : a new "create" places the partitions at random and
# the objects already stored are no longer found. When the builders are in the
# cluster, they are read back and only modified.
if ! EXISTING=$(kubectl -n datalake get configmap swift-ring-builders --ignore-not-found -o name); then
  echo "Error: cluster unreachable (KUBECONFIG=${KUBECONFIG:-}) : cannot tell whether rings already exist."
  exit 1
fi

if [ -n "$EXISTING" ]; then
  echo "Rings found in the cluster : they are modified, never recreated."
  kubectl -n datalake get configmap swift-ring-builders -o "jsonpath={.binaryData.account\.builder}" | base64 -d > $RINGS_WORK_PATH/account.builder
  kubectl -n datalake get configmap swift-ring-builders -o "jsonpath={.binaryData.container\.builder}" | base64 -d > $RINGS_WORK_PATH/container.builder
  kubectl -n datalake get configmap swift-ring-builders -o "jsonpath={.binaryData.object\.builder}" | base64 -d > $RINGS_WORK_PATH/object.builder
else
  echo "No rings in the cluster : creating them."
  $RING_BUILDER account.builder create $SWIFT_PART_POWER $REPLICAS $SWIFT_MIN_PART_HOURS
  $RING_BUILDER container.builder create $SWIFT_PART_POWER $REPLICAS $SWIFT_MIN_PART_HOURS
  $RING_BUILDER object.builder create $SWIFT_PART_POWER $REPLICAS $SWIFT_MIN_PART_HOURS
fi


###################################
# REPLICAS + DEVICES + REBALANCE
###################################
# One device per storage pod, found by its DNS name (StatefulSet + headless Service) :
# swift-storage-<i>.swift-storage.datalake.svc.cluster.local, device d1
for RING in account container object; do
  if [ "$RING" = "account" ]; then
    PORT=6200
  fi
  if [ "$RING" = "container" ]; then
    PORT=6201
  fi
  if [ "$RING" = "object" ]; then
    PORT=6202
  fi

  if [ ! -s "$RINGS_WORK_PATH/$RING.builder" ]; then
    echo "Error: $RING.builder is missing or empty."
    exit 1
  fi

  CURRENT_REPLICAS=$($RING_BUILDER $RING.builder | grep -o '[0-9.]* replicas' | head -n1 | cut -d' ' -f1)
  if [ "${CURRENT_REPLICAS%%.*}" != "$REPLICAS" ]; then
    $RING_BUILDER $RING.builder set_replicas $REPLICAS
  fi

  for i in $(seq 0 $((NB_STORAGE_NODE - 1))); do
    STORAGE_HOST="swift-storage-$i.swift-storage.datalake.svc.cluster.local"
    # search fails when the device is not in the ring yet
    if ! $RING_BUILDER $RING.builder search --ip $STORAGE_HOST --port $PORT --device d1 >/dev/null 2>&1; then
      $RING_BUILDER $RING.builder add --region 1 --zone 1 --ip $STORAGE_HOST --port $PORT --device d1 --weight $WEIGHT
    fi
  done

  # rebalance returns 1 for a warning (nothing to move, min_part_hours not elapsed), 2 for an error
  REBALANCE_STATUS=0
  $RING_BUILDER $RING.builder rebalance || REBALANCE_STATUS=$?
  if [ "$REBALANCE_STATUS" -ge 2 ]; then
    echo "Error: rebalance of the $RING ring failed."
    exit 1
  fi

  # rebalance only writes the ring when partitions moved
  $RING_BUILDER $RING.builder write_ring
done


###################################
# RINGS + BUILDERS (ConfigMaps)
###################################
# The builders are kept in the cluster : they are the source of the next runs.
kubectl -n datalake create configmap swift-rings \
  --from-file=$RINGS_WORK_PATH/account.ring.gz \
  --from-file=$RINGS_WORK_PATH/container.ring.gz \
  --from-file=$RINGS_WORK_PATH/object.ring.gz \
  --dry-run=client -o yaml \
  | kubectl label --local -f - app.kubernetes.io/name=swift app.kubernetes.io/part-of=raw-data-zone -o yaml \
  > $OPENSTACKSWIFT_KUBE_PATH/volumes/configmap_swift_rings.yml

kubectl -n datalake create configmap swift-ring-builders \
  --from-file=$RINGS_WORK_PATH/account.builder \
  --from-file=$RINGS_WORK_PATH/container.builder \
  --from-file=$RINGS_WORK_PATH/object.builder \
  --dry-run=client -o yaml \
  | kubectl label --local -f - app.kubernetes.io/name=swift app.kubernetes.io/part-of=raw-data-zone -o yaml \
  > $OPENSTACKSWIFT_KUBE_PATH/volumes/configmap_swift_ring_builders.yml

rm -rf $RINGS_WORK_PATH

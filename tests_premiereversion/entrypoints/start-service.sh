#!/bin/bash
set -e

SERVER=${1:-object}  # Par défaut object
CONF=${2:-object-server.conf}

# Wait for rings (comme votre wait-for-files.sh existant)
while [ ! -f "/etc/swift/account.ring.gz" ] || [ ! -f "/etc/swift/object.ring.gz" ]; do
  echo "Waiting for rings..."
  sleep 5
done

# Init devices si pas montés (adapté SAIO ; pour account: sdb0, objects: sda1)
case $SERVER in
  account|container)
    DEV=sdb0
    ;;
  object|replicator)
    DEV=sda1  # Unique par node, mais volume partagé ; adaptez pour multi-dev si scale
    ;;
  *)
    DEV=sda1
    ;;
esac

if [ ! -e "/srv/node/$DEV" ] || ! mountpoint -q "/srv/node/$DEV"; then
  echo "Initializing device $DEV..."
  IMG="/srv/node/${DEV}.img"
  dd if=/dev/zero of="$IMG" bs=1G count=1 status=progress
  mkfs.xfs -f "$IMG"
  LOOP_DEV=$(losetup -fP "$IMG" | cut -d: -f1)
  mkdir -p "/srv/node/$DEV"
  mount "$LOOP_DEV" "/srv/node/$DEV"
  chown -R swift:swift "/srv/node/$DEV"
  echo "Device $DEV mounted"
fi

# Exec le service (wrappe command)
exec gosu swift swift-$SERVER /etc/swift/$CONF "$@"
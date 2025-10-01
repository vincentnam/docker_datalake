#!/bin/bash
set -e
SERVER=${1:-object}
CONF=${2:-object-server.conf}
if [[ $SERVER == "account" ]]; then DEV_PATH="sdb0_account" ; elif [[ $SERVER == "container" ]]; then DEV_PATH="sdb0_container" ; else NUM=${HOSTNAME#object-} ; DEV_PATH="sda1_object$NUM" ; fi
DEV="/srv/node/$DEV_PATH"
while [ ! -f /etc/swift/object.ring.gz ]; do echo "Waiting rings..."; sleep 5; done
if ! mountpoint -q $DEV; then
  IMG="$DEV.img"
  if [ ! -f "$IMG" ]; then
    dd if=/dev/zero of=$IMG bs=1G count=1 status=progress || echo "Skip dd (pre-init)"
    mkfs.xfs -f $IMG || echo "Skip mkfs (pre-init)"
  fi
  if command -v losetup >/dev/null 2>&1; then
    LOOP=$(losetup -fP $IMG 2>/dev/null | cut -d: -f1) || LOOP=""
    if [ -n "$LOOP" ]; then
      mount $LOOP $DEV || echo "Mount fallback"
    fi
  fi
  mkdir -p $DEV
  mount -o remount,rw $DEV 2>/dev/null || true
  chown -R swift:swift $DEV
  echo "Ready $DEV"
fi
rsyslogd -n &
su swift
exec $SERVER $CONF verbose "$@"



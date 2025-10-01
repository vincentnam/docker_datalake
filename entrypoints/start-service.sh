#!/bin/bash
set -x
SERVER=${1:-object}
CONF=${2:-object-server.conf}
if [[ $SERVER == "account" ]]; then DEV_PATH="sdb0_account" ; elif [[ $SERVER == "container" ]]; then DEV_PATH="sdb0_container" ; else NUM=$(echo $HOSTNAME | grep -o '[0-9]\+$') ; DEV_PATH="sda1_object$NUM" ; fi
DEV="/srv/node/$DEV_PATH"

##mount -o remount,rw /dev/loop0/ /src/node/sdb0
#tail -f /dev/null
#
while [ ! -f /etc/swift/object.ring.gz ]; do echo "Waiting rings..."; sleep 5; done
if ! mountpoint -q $DEV; then
  IMG="$DEV.img"
  mkdir -p $DEV

  mount -o remount,rw $DEV 2>/dev/null || true
  chown -R swift:swift $DEV
  echo "Ready $DEV"
fi
rsyslogd -n &
su swift
exec $SERVER $CONF verbose "$@"
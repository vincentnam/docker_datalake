#!/bin/sh
set -e

SWIFT_CONF_DIR=${SWIFT_CONF_DIR:-/etc/swift}
PROXY_CONF=${SWIFT_CONF_DIR}/proxy-server.conf

# wait for rings
/opt/swift-scripts/wait-for-files.sh ${SWIFT_CONF_DIR}/account.ring.gz ${SWIFT_CONF_DIR}/container.ring.gz ${SWIFT_CONF_DIR}/object.ring.gz

# ensure tempauth or keystone conf present
if [ ! -f "${PROXY_CONF}" ]; then
  echo "Missing proxy-server.conf in ${SWIFT_CONF_DIR}" >&2
  exit 1
fi

# run proxy in foreground (gunicorn/eventlet)
exec swift-proxy-server ${PROXY_CONF}
#!/bin/sh
set -e

SWIFT_CONF_DIR=${SWIFT_CONF_DIR:-/etc/swift}
ROLE=${SWIFT_ROLE:-object}  # object, container, account
CONF_FILE=${SWIFT_CONF_DIR}/${ROLE}-server.conf

# wait for config/rings
/opt/swift-scripts/wait-for-files.sh ${CONF_FILE} ${SWIFT_CONF_DIR}/${ROLE}.ring.gz || true

if [ ! -f "${CONF_FILE}" ]; then
  echo "Missing ${CONF_FILE}" >&2
  exit 1
fi

case "${ROLE}" in
  object)
    exec swift-object-server ${CONF_FILE}
    ;;
  container)
    exec swift-container-server ${CONF_FILE}
    ;;
  account)
    exec swift-account-server ${CONF_FILE}
    ;;
  *)
    echo "Unknown SWIFT_ROLE ${ROLE}" >&2
    exit 2
    ;;
esac
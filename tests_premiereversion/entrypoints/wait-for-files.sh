#!/bin/sh
set -e

timeout=${WAIT_TIMEOUT:-60}
start=$(date +%s)
while [ "$#" -gt 0 ]; do
  file="$1"; shift
  while [ ! -f "$file" ]; do
    now=$(date +%s)
    if [ $((now - start)) -gt "$timeout" ]; then
      echo "Timeout waiting for $file" >&2
      exit 1
    fi
    sleep 1
  done
done
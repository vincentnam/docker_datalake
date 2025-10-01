#!/bin/bash
exec memcached -u root -l 0.0.0.0 "$@"
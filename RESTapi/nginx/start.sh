#!/bin/bash
cat /tmp/default.conf > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'

#tail -f /dev/null

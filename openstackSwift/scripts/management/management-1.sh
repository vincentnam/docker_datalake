DEVICE_NAME="swift-account-d-1"
#
#
#mkdir -p /srv/node/$DEVICE_NAME
#mount -t xfs -o noatime /internal_dev/$DEVICE_NAME /srv/node/$DEVICE_NAME;
chown -R swift:swift /srv/node
su swift
rm /run/rsyslogd.pid
## Start rsync
/etc/init.d/rsync restart

## Start memcached
/etc/init.d/memcached start

## Restart rsyslog
rsyslogd

swift-proxy-server /etc/swift/proxy/proxy-1.conf verbose

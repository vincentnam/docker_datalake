#!/bin/sh
/usr/sbin/service rsyslog start
/usr/sbin/service rsync start
/usr/sbin/service memcached start


# set up storage
DATA_DEV=/data_dev/
if [ -d "$DATA_DEV" ]; then
  echo "Docker volume used"
else
  echo "Creating data folder in container /data_dev"
  mkdir /data_dev/
fi
LOOP1=/data_dev/1
LOOP2=/data_dev/2
 #/swift/nodes/3 /swift/nodes/4
if [ -f "$LOOP1" ]; then
  echo "Volume given to container : creating symbolic link"
  ln -s /data_dev/1 /mnt/1
elif [ -d "$LOOP1" ]; then

  echo "Folder given to container"
  ln -s /data_dev/1 /mnt/1
else
  truncate -s 1GB /data_dev/1
  mkfs.xfs /data_dev/1
  mkdir -p /mnt/1
  mount -o loop /data_dev/1 /mnt/1
fi

if [ -f "$LOOP2" ]; then
  echo "Volume given to container : creating symbolic link"

  ln -s /data_dev/2 /mnt/2
elif [ -d "$LOOP2" ]; then
  echo "Folder given to container"
  ln -s /data_dev/2 /mnt/2
else
  truncate -s 1GB /data_dev/2
  mkfs.xfs /data_dev/2
  mkdir -p /mnt/2
  mount -o loop /data_dev/2 /mnt/2
fi

#mkfs.xfs /data_dev/2

ln -s /mnt/1 /srv/1; ln -s /mnt/2 /srv/2; #ln -s /swift/nodes/3 /srv/3; ln -s /swift/nodes/4 /srv/4
sudo mkdir -p /srv/1/node/sdb1 /srv/1/node/sdb5 /srv/2/node/sdb2 /srv/2/node/sdb6 /var/run/swift #/srv/3/node/sdb3 /srv/4/node/sdb4

/usr/bin/sudo /bin/chown -R swift:swift /mnt /etc/swift /srv/1 /srv/2 /var/run/swift /var/cache/swift #/var/cache/swift2 #/srv/3 /srv/4


# set up storage
su swift /swift/bin/remakerings
su swift -c "/usr/local/bin/swift-init main start"
su swift -c "/usr/local/bin/swift-init rest start"
/usr/local/bin/supervisord -n -c /etc/supervisord.conf

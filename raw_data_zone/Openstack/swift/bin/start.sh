##rsync --detach --daemon
##memcached  -vv --daemon && \
##
##echo "----------"
##echo "Constructing rings"
##echo "-----------"
##
####!/bin/bash
###
##set -e
##
##cd /etc/swift
##
##rm -f *.builder *.ring.gz backups/*.builder backups/*.ring.gz
### Create part_power (?) replicas min_part_hour
##swift-ring-builder object.builder create 10 1 1
##swift-ring-builder object.builder add r1z1-127.0.0.1:6210/sdb1 1
##swift-ring-builder object.builder add r1z2-127.0.0.2:6220/sdb2 1
###swift-ring-builder object.builder add r1z3-127.0.0.3:6230/sdb3 1
###swift-ring-builder object.builder add r1z4-127.0.0.4:6240/sdb4 1
##swift-ring-builder object.builder rebalance
##swift-ring-builder object-1.builder create 10 1 1
##swift-ring-builder object-1.builder add r1z1-127.0.0.1:6210/sdb1 1
##swift-ring-builder object-1.builder add r1z2-127.0.0.2:6220/sdb2 1
###swift-ring-builder object-1.builder add r1z3-127.0.0.3:6230/sdb3 1
###swift-ring-builder object-1.builder add r1z4-127.0.0.4:6240/sdb4 1
##swift-ring-builder object-1.builder rebalance
##swift-ring-builder object-2.builder create 10 1 1
##swift-ring-builder object-2.builder add r1z1-127.0.0.1:6210/sdb1 1
##swift-ring-builder object-2.builder add r1z1-127.0.0.1:6210/sdb5 1
##swift-ring-builder object-2.builder add r1z2-127.0.0.2:6220/sdb2 1
##swift-ring-builder object-2.builder add r1z2-127.0.0.2:6220/sdb6 1
###swift-ring-builder object-2.builder add r1z3-127.0.0.3:6230/sdb3 1
###swift-ring-builder object-2.builder add r1z3-127.0.0.3:6230/sdb7 1
###swift-ring-builder object-2.builder add r1z4-127.0.0.4:6240/sdb4 1
###swift-ring-builder object-2.builder add r1z4-127.0.0.4:6240/sdb8 1
##swift-ring-builder object-2.builder rebalance
##swift-ring-builder container.builder create 10 1 1
##swift-ring-builder container.builder add r1z1-127.0.0.1:6211/sdb1 1
##swift-ring-builder container.builder add r1z2-127.0.0.2:6221/sdb2 1
###swift-ring-builder container.builder add r1z3-127.0.0.3:6231/sdb3 1
###swift-ring-builder container.builder add r1z4-127.0.0.4:6241/sdb4 1
##swift-ring-builder container.builder rebalance
##swift-ring-builder account.builder create 10 1 1
##swift-ring-builder account.builder add r1z1-127.0.0.1:6212/sdb1 1
##swift-ring-builder account.builder add r1z2-127.0.0.2:6222/sdb2 1
###swift-ring-builder account.builder add r1z3-127.0.0.3:6232/sdb3 1
###swift-ring-builder account.builder add r1z4-127.0.0.4:6242/sdb4 1
##swift-ring-builder account.builder rebalance
##
##cd /swift_install/swift
##
##echo "----------"
##echo "Starting all"
##echo "-----------"
##swift-init main start
###./.unittests
##ps aux | grep swift
##ls -la /var/log/swift
##tail -f /var/log/*
###
###
####!/bin/bash
###
####
#### Make the rings if they don't exist already
####
###
#### These can be set with docker run -e VARIABLE=X at runtime
###SWIFT_PART_POWER=${SWIFT_PART_POWER:-7}
###SWIFT_PART_HOURS=${SWIFT_PART_HOURS:-1}
###SWIFT_REPLICAS=${SWIFT_REPLICAS:-1}
###
###if [ -e /srv/account.builder ]; then
###	echo "Ring files already exist in /srv, copying them to /etc/swift..."
###	cp /srv/*.builder /etc/swift/
###	cp /srv/*.gz /etc/swift/
###fi
###
#### This comes from a volume, so need to chown it here, not sure of a better way
#### to get it owned by Swift.
###chown -R swift:datalake /srv
###
###if [ ! -e /etc/swift/account.builder ]; then
###
###	cd /etc/swift
###
###	# 2^& = 128 we are assuming just one drive
###	# 1 replica only
###
###	echo "No existing ring files, creating them..."
###
####	swift-ring-builder object.builder create ${SWIFT_PART_POWER} ${SWIFT_REPLICAS} ${SWIFT_PART_HOURS}
####	swift-ring-builder object.builder add r1z1-127.0.0.1:6010/sdb1 1
####	swift-ring-builder object.builder rebalance
####	swift-ring-builder container.builder create ${SWIFT_PART_POWER} ${SWIFT_REPLICAS} ${SWIFT_PART_HOURS}
####	swift-ring-builder container.builder add r1z1-127.0.0.1:6011/sdb1 1
####	swift-ring-builder container.builder rebalance
####	swift-ring-builder account.builder create ${SWIFT_PART_POWER} ${SWIFT_REPLICAS} ${SWIFT_PART_HOURS}
####	swift-ring-builder account.builder add r1z1-127.0.0.1:6012/sdb1 1
####	swift-ring-builder account.builder rebalance
###  set -e
###
###  cd /etc/swift
###
###  rm -f *.builder *.ring.gz backups/*.builder backups/*.ring.gz
###  # Create part_power (?) replicas min_part_hour
###  swift-ring-builder object.builder create 10 1 1
###  swift-ring-builder object.builder add r1z1-127.0.0.1:6210/sdb1 1
###  swift-ring-builder object.builder add r1z2-127.0.0.2:6220/sdb2 1
###  #swift-ring-builder object.builder add r1z3-127.0.0.3:6230/sdb3 1
###  #swift-ring-builder object.builder add r1z4-127.0.0.4:6240/sdb4 1
###  swift-ring-builder object.builder rebalance
###  swift-ring-builder object-1.builder create 10 1 1
###  swift-ring-builder object-1.builder add r1z1-127.0.0.1:6210/sdb1 1
###  swift-ring-builder object-1.builder add r1z2-127.0.0.2:6220/sdb2 1
###  #swift-ring-builder object-1.builder add r1z3-127.0.0.3:6230/sdb3 1
###  #swift-ring-builder object-1.builder add r1z4-127.0.0.4:6240/sdb4 1
###  swift-ring-builder object-1.builder rebalance
###  swift-ring-builder object-2.builder create 10 1 1
###  swift-ring-builder object-2.builder add r1z1-127.0.0.1:6210/sdb1 1
###  swift-ring-builder object-2.builder add r1z1-127.0.0.1:6210/sdb5 1
###  swift-ring-builder object-2.builder add r1z2-127.0.0.2:6220/sdb2 1
###  swift-ring-builder object-2.builder add r1z2-127.0.0.2:6220/sdb6 1
###  #swift-ring-builder object-2.builder add r1z3-127.0.0.3:6230/sdb3 1
###  #swift-ring-builder object-2.builder add r1z3-127.0.0.3:6230/sdb7 1
###  #swift-ring-builder object-2.builder add r1z4-127.0.0.4:6240/sdb4 1
###  #swift-ring-builder object-2.builder add r1z4-127.0.0.4:6240/sdb8 1
###  swift-ring-builder object-2.builder rebalance
###  swift-ring-builder container.builder create 10 1 1
###  swift-ring-builder container.builder add r1z1-127.0.0.1:6211/sdb1 1
###  swift-ring-builder container.builder add r1z2-127.0.0.2:6221/sdb2 1
###  #swift-ring-builder container.builder add r1z3-127.0.0.3:6231/sdb3 1
###  #swift-ring-builder container.builder add r1z4-127.0.0.4:6241/sdb4 1
###  swift-ring-builder container.builder rebalance
###  swift-ring-builder account.builder create 10 1 1
###  swift-ring-builder account.builder add r1z1-127.0.0.1:6212/sdb1 1
###  swift-ring-builder account.builder add r1z2-127.0.0.2:6222/sdb2 1
###  #swift-ring-builder account.builder add r1z3-127.0.0.3:6232/sdb3 1
###  #swift-ring-builder account.builder add r1z4-127.0.0.4:6242/sdb4 1
###  swift-ring-builder account.builder rebalance
###	# Back these up for later use
###	echo "Copying ring files to /srv to save them if it's a docker volume..."
###	cp *.gz /srv
###	cp *.builder /srv
###
###fi
###
#### If you are going to put an ssl terminator in front of the proxy, then I believe
#### the storage_url_scheme should be set to https. So if this var isn't empty, set
#### the default storage url to https.
###if [ ! -z "${SWIFT_STORAGE_URL_SCHEME}" ]; then
###	echo "Setting default_storage_scheme to https in proxy-server.conf..."
###	sed -i -e "s/storage_url_scheme = default/storage_url_scheme = https/g" /etc/swift/proxy-server.conf
###	grep "storage_url_scheme" /etc/swift/proxy-server.conf
###fi
###
###if [ ! -z "${SWIFT_SET_PASSWORDS}" ]; then
###	echo "Setting passwords in /etc/swift/proxy-server.conf..."
###	PASS=`pwgen 12 1`
###	sed -i -e "s/user_admin_admin = admin .admin .reseller_admin/user_admin_admin = $PASS .admin .reseller_admin/g" /etc/swift/proxy-server.conf
###	sed -i -e "s/user_test_tester = testing .admin/user_test_tester = $PASS .admin/g" /etc/swift/proxy-server.conf
###	sed -i -e "s/user_test2_tester2 = testing2 .admin/user_test2_tester2 = $PASS .admin/g" /etc/swift/proxy-server.conf
###	sed -i -e "s/user_test_tester3 = testing3/user_test_tester3 = $PASS/g" /etc/swift/proxy-server.conf
###	grep "user_test" /etc/swift/proxy-server.conf
###fi
###
#### Start supervisord
###echo "Starting supervisord..."
###/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
###
#### Create default container
###if [ ! -z "${SWIFT_DEFAULT_CONTAINER}" ]; then
###	echo "Creating default container..."
###	for container in ${SWIFT_DEFAULT_CONTAINER} ; do
###	    echo "Creating container...${container}"
###	    swift -A http://localhost:8080/auth/v1.0 -U admin:admin -K admin post ${container}
###	done
###fi
###
#### Create meta-url-key to allow temp download url generation
###if [ ! -z "${SWIFT_TEMP_URL_KEY}" ]; then
###  echo "Setting X-Account-Meta-Temp-URL-Key..."
###  swift -A http://localhost:8080/auth/v1.0 -U test:tester -K testing post -m "Temp-URL-Key:${SWIFT_TEMP_URL_KEY}"
###fi
###
####
#### Tail the log file for "docker log $CONTAINER_ID"
####
###
#### sleep waiting for rsyslog to come up under supervisord
###sleep 3
###
###echo "Starting to tail /var/log/syslog...(hit ctrl-c if you are starting the container in a bash shell)"
###
###tail -n 0 -f /var/log/syslog
#export SWIFT_TEST_CONFIG_FILE=/etc/swift/test.conf
#export PATH=${PATH}:$HOME/bin
#service memcached start
#service rsync start
#bash


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

/usr/bin/sudo /bin/chown -R swift:swift /mnt /etc/swift /srv/1 /srv/2 /var/run/swift /var/cache/swift /var/cache/swift2 #/srv/3 /srv/4
/usr/bin/sudo -u swift /swift/bin/remakerings
/usr/bin/sudo -u swift /swift/bin/startmain
/usr/bin/sudo -u swift /swift/bin/startrest
/usr/local/bin/supervisord -n -c /etc/supervisord.conf
#docker run -p 8080:8080 --privileged --device /dev/loop0 --device /dev/loop-control -it ubuntuswift.conf
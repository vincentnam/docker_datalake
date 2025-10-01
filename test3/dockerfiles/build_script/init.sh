#!/usr/bin/with-contenv sh
#set -x
#export $(grep -v '^#' /config_cluster.env | xargs)
export $(grep -v '^#' /scripts/config_cluster.env | sed 's/\r$//' | xargs)
env
POLICIES="object container account"
ACCOUNT_DEV_SIZE="1GB"
OBJECT_DEV_SIZE="1GB"
CONTAINER_DEV_SIZE="1GB"
touch docker-compose.test.yml


cat << EOF >> docker-compose.test.yml

services:

EOF

echo $NB_ACCOUNT_SERVER
cd /etc/swift/
swift-ring-builder object.builder create 10 3 1
swift-ring-builder container.builder create 10 3 1
swift-ring-builder account.builder create 10 3 1

for i in $(seq $NB_OBJECT_SERVER);
  do
    DEVICE_NAME="swift-object-d-$i"

    echo "[[ checking --privileged ]]"
    ip link add dummy0 type dummy >/dev/null
    if [[ $? -eq 0 ]]; then
        PRIVILEGED=true
        # clean the dummy0 link
        ip link delete dummy0 >/dev/null
      else
        PRIVILEGED=false
      fi

    truncate -s $OBJECT_DEV_SIZE /internal_dev/$DEVICE_NAME;
    echo "    created storage device /internal_dev/$DEVICE_NAME of $OBJECT_DEV_SIZE";
    export PATH=$PATH:/opt/python/usr/local/bin/

    echo "[[ creating directories ]]"

    mkdir -p /srv/node/$DEVICE_NAME;
    echo "  created /srv/node/$DEVICE_NAME";
    mkfs.xfs -f -L D$i -i size=512 /internal_dev/$DEVICE_NAME;
    echo "  created XFS file system on device /internal_dev/$DEVICE_NAME";
    mount -t xfs -o noatime /internal_dev/$DEVICE_NAME /srv/node/$DEVICE_NAME;
    echo "  mounted /internal_dev/$DEVICE_NAME as /srv/node/$DEVICE_NAME";
    echo "swift-ring-builder /etc/swift/object.builder add r1z1-10.5.2.$i:6200/$DEVICE_NAME 1" >> /etc/swift/remakerings.object
    echo "pushed command to add r1z1-10.5.2.$i:6200/$DEVICE_NAME to /etc/swift/remakerings.object"

    echo $i;
done

for i in $(seq $NB_ACCOUNT_SERVER);do
    DEVICE_NAME="swift-account-d-$i"
#    MY_STORAGE_TYPE=${STORAGE_TYPE:-"internal_dirs"}
#    MY_DEVICE_COUNT=${DEVICE_COUNT:-6}
    echo "[[ checking --privileged ]]"
    ip link add dummy0 type dummy >/dev/null
    if [[ $? -eq 0 ]]; then
        PRIVILEGED=true
    # clean the dummy0 link
        ip link delete dummy0 >/dev/null
      else
        PRIVILEGED=false
      fi

    truncate -s $ACCOUNT_DEV_SIZE /internal_dev/$DEVICE_NAME;
    echo "    created storage device /internal_dev/$DEVICE_NAME of $ACCOUNT_DEV_SIZE";
    export PATH=$PATH:/opt/python/usr/local/bin/

    echo "[[ creating directories ]]"

    mkdir -p /srv/node/$DEVICE_NAME;
    echo "  created /srv/node/$DEVICE_NAME";
    mkfs.xfs -f -L D$i -i size=512 /internal_dev/$DEVICE_NAME;
    echo "  created XFS file system on device /internal_dev/$DEVICE_NAME";
    mount -t xfs -o noatime /internal_dev/$DEVICE_NAME /srv/node/$DEVICE_NAME;
    echo "  mounted /internal_dev/$DEVICE_NAME as /srv/node/$DEVICE_NAME";
    echo "swift-ring-builder /etc/swift/account.builder add r1z1-10.5.3.$i:6200/$DEVICE_NAME 1" >> /etc/swift/remakerings.account
    echo "pushed command to add r1z1-10.5.3.$i:6200/$DEVICE_NAME to /etc/swift/remakerings.account"
    echo $i;
done





for i in $(seq $NB_CONTAINER_SERVER);
  do
    DEVICE_NAME="swift-container-d-$i"
#    MY_STORAGE_TYPE=${STORAGE_TYPE:-"internal_dirs"}
#    MY_DEVICE_COUNT=${DEVICE_COUNT:-6}
    echo "[[ checking --privileged ]]"
    ip link add dummy0 type dummy >/dev/null
    if [[ $? -eq 0 ]]; then
        PRIVILEGED=true
    # clean the dummy0 link
        ip link delete dummy0 >/dev/null
      else
        PRIVILEGED=false
      fi

    truncate -s $CONTAINER_DEV_SIZE /internal_dev/$DEVICE_NAME;
    echo "    created storage device /internal_dev/$DEVICE_NAME of $CONTAINER_DEV_SIZE";
    export PATH=$PATH:/opt/python/usr/local/bin/
    echo "[[ creating directories ]]"
    mkdir -p /srv/node/$DEVICE_NAME;
    echo "  created /srv/node/$DEVICE_NAME";
    mkfs.xfs -f -L D$i -i size=512 /internal_dev/$DEVICE_NAME;
    echo "  created XFS file system on device /internal_dev/$DEVICE_NAME";
    mount -t xfs -o noatime /internal_dev/$DEVICE_NAME /srv/node/$DEVICE_NAME;
    echo "  mounted /internal_dev/$DEVICE_NAME as /srv/node/$DEVICE_NAME";
    echo "swift-ring-builder /etc/swift/container.builder add r1z1-10.5.4.$i:6200/$DEVICE_NAME 1" >> /etc/swift/remakerings.container
    echo "pushed command to add r1z1-10.5.4.$i:6200/$DEVICE_NAME to /etc/swift/remakerings.container"
    echo $i;
done


touch /etc/swift/remakerings
chmod +x /etc/swift/remakerings



cat /etc/swift/remakerings.account >> /etc/swift/remakerings;
cat /etc/swift/remakerings.container >> /etc/swift/remakerings;
cat /etc/swift/remakerings.object >> /etc/swift/remakerings;
rm /etc/swift/remakerings.account >> /etc/swift/remakerings;
rm /etc/swift/remakerings.container >> /etc/swift/remakerings;
rm /etc/swift/remakerings.object >> /etc/swift/remakerings;
echo $(cat /etc/swift/remakerings.$p >> /etc/swift/remakerings)

#  echo "pushed /etc/swift/remakerings.$p to /etc/swift/remakerings"
#  rm -f /etc/swift/remakerings.$p;
#  echo "deleted /etc/swift/remakerings.$p"

echo $(ls /etc/swift)
echo $(cat /etc/swift/remakerings)

/etc/swift/remakerings




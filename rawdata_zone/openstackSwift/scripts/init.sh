#!/usr/bin/with-contenv sh

#export $(grep -v '^#' /config_cluster.env | xargs)
export $(grep -v '^#' /scripts/config_cluster.env | sed 's/\r$//' | xargs)
env
POLICIES="object container account"
#
#NODE_STORAGE_SIZE="1GB"

touch docker-compose.test.yml


cat << EOF >> docker-compose.test.yml

services:

EOF


cd /etc/swift/

for i in $(seq $NB_STORAGE_NODE);
  do
    DEVICE_NAME="swift-storage-d-$i"
#    echo "swift-ring-builder /etc/swift/account.builder add r1z1-10.5.1.$i:6200/$DEVICE_NAME 1" >> /etc/swift/remakerings.account
    echo "swift-ring-builder /etc/swift/account.builder add --region 1 --zone 1 --ip 10.5.1.$i --port 6200 --device $DEVICE_NAME --weight 1" >> /etc/swift/remakerings.account

    echo "swift-ring-builder /etc/swift/container.builder add --region 1 --zone 1 --ip 10.5.1.$i --port 6201 --device $DEVICE_NAME --weight 1" >> /etc/swift/remakerings.container

    echo "swift-ring-builder /etc/swift/object.builder add --region 1 --zone 1 --ip 10.5.1.$i --port 6202 --device $DEVICE_NAME --weight 1" >> /etc/swift/remakerings.object

done

rm /etc/swift/remakerings
touch /etc/swift/remakerings
chmod +x /etc/swift/remakerings

echo "set -x" >> /etc/swift/remakerings
echo "swift-ring-builder object.builder create $SWIFT_PART_POWER $NB_STORAGE_NODE $SWIFT_MIN_PART_HOURS" >> /etc/swift/remakerings
echo "swift-ring-builder container.builder create $SWIFT_PART_POWER $NB_STORAGE_NODE $SWIFT_MIN_PART_HOURS" >> /etc/swift/remakerings
echo "swift-ring-builder account.builder create $SWIFT_PART_POWER $NB_STORAGE_NODE $SWIFT_MIN_PART_HOURS" >> /etc/swift/remakerings


cat /etc/swift/remakerings.account >> /etc/swift/remakerings;
cat /etc/swift/remakerings.container >> /etc/swift/remakerings;
cat /etc/swift/remakerings.object >> /etc/swift/remakerings;
echo "swift-ring-builder object.builder rebalance " >> /etc/swift/remakerings
echo "swift-ring-builder account.builder rebalance " >> /etc/swift/remakerings
echo "swift-ring-builder container.builder rebalance" >> /etc/swift/remakerings

echo "swift-ring-builder account.builder write_ring" >> /etc/swift/remakerings
echo "swift-ring-builder object.builder write_ring" >> /etc/swift/remakerings
echo "swift-ring-builder container.builder write_ring" >> /etc/swift/remakerings

echo "swift-ring-builder object.builder" >> /etc/swift/remakerings
echo "swift-ring-builder account.builder" >> /etc/swift/remakerings
echo "swift-ring-builder container.builder" >> /etc/swift/remakerings
rm /etc/swift/remakerings.account
rm /etc/swift/remakerings.container
rm /etc/swift/remakerings.object


#  echo "pushed /etc/swift/remakerings.$p to /etc/swift/remakerings"
#  rm -f /etc/swift/remakerings.$p;
#  echo "deleted /etc/swift/remakerings.$p"

echo $(ls /etc/swift)
echo $(cat /etc/swift/remakerings)

/etc/swift/remakerings




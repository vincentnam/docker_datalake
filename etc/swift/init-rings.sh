#!/bin/bash

# Script pour générer les rings et configs Swift pour setup multi-containers
# Exécutez dans un container basé sur dockerfile.base (contient swift-ring-builder)
# Config par défaut: replicas=3, part_power=10, min_part_hours=1, single node (localhost)
# Sortie: ./etc/swift avec rings (.gz) et confs basiques pour proxy/account/container/object
# Utilisation: docker run -v $(pwd)/etc/swift:/etc/swift <image-from-dockerfile.base> bash init-rings.sh

set -e

# Créez dossier pour configs
mkdir -p /etc/swift

# Générez rings (account, container, object)
swift-ring-builder /etc/swift/account.builder create 10 3 1
swift-ring-builder /etc/swift/container.builder create 10 3 1
swift-ring-builder /etc/swift/object.builder create 10 3 1

# Ajoutez devices (simule 3 object nodes sur localhost, ports 6200-6202)
for i in {0..2}; do
  PORT=$((6200 + i))
  swift-ring-builder /etc/swift/account.builder add r1z1-127.0.0.1:$((PORT + 2))/sda$i 100
  swift-ring-builder /etc/swift/container.builder add r1z1-127.0.0.1:$((PORT + 1))/sda$i 100
  swift-ring-builder /etc/swift/object.builder add r1z1-127.0.0.1:$PORT/sda$i 100
done

# Rebalance rings et créez .ring + .gz
# Rebalance rings et écrasez .ring.gz avec write_ring
for ring in account container object; do
  swift-ring-builder /etc/swift/${ring}.builder rebalance
  swift-ring-builder /etc/swift/${ring}.builder write_ring /etc/swift/${ring}.ring.gz
done


# Setup storage devices (simulé pour test)
mkdir -p /srv/node/sda{0,1,2}
chown -R swift:swift /srv/node

echo "Rings et configs générés dans /etc/swift. Lancez docker-compose up -d."
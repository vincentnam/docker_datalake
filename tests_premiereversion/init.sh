#!/bin/bash
# Script d'init pour Swift: build + génère rings/configs via container

docker build -f Dockerfile.base -t swift-base .

echo $(pwd)
mkdir -p ./etc/swift/
# Copie le script init-rings.sh dans le volume (fix pour /etc/swift/init-rings.sh)
cp init-rings.sh etc/swift/
docker run -v $(pwd)/etc/swift:/etc/swift swift-base bash /etc/swift/init-rings.sh


mkdir -p ./srv/node/sda{0,1,2}
mkdir -p ./srv/node/sdb{0,1}


cp conf/* etc/swift/
#!/bin/bash
set -e

if [ ! -d "loci" ]; then
    echo "Clonage du dépôt OpenStack LOCI..."
    git clone https://github.com/openstack/loci.git
fi

BASE_DISTRO="ubuntu:jammy"
BASE_DISTRO_NAME=$(printf '%s\n' "$BASE_DISTRO" | tr ':' '_')
#echo "Distribution name and version : $BASE_DISTRO"
#echo "Distribution tag : $BASE_DISTRO_NAME"

cd loci
echo "=========================================="
echo "Démarrage du build des images LOCI"
echo "=========================================="

# On ajoute PROFILES="python" pour que LOCI installe python3 dans l'image de base
# On peut aussi ajouter "fluentd" ou d'autres si besoin plus tard.


echo "Construction de l'image locale : base image  ($BASE_DISTRO)"

docker build . \
    -f Dockerfile.base \
    --build-arg FROM=$BASE_DISTRO \
    --build-arg CEPH_REPO='deb https://download.ceph.com/debian-reef/ jammy main' \
    --tag base:$BASE_DISTRO_NAME




echo "Construction de l'image locale : requirements image"

 docker build . \
    -f Dockerfile \
    --target requirements \
    --build-arg FROM=base:$BASE_DISTRO_NAME \
    --build-arg PROJECT=requirements \
    --tag requirements:$BASE_DISTRO_NAME


echo "Construction de l'image locale : my-keystone:local"


# MASTER : need to change openstack version chosen
#TODO : Set openstack version variable

docker build . \
    --build-arg FROM=base:$BASE_DISTRO_NAME \
    --build-arg WHEELS=requirements:$BASE_DISTRO_NAME\
    --build-arg PROJECT=keystone \
    --build-arg PROFILES=apache \
    --tag keystone:master-$BASE_DISTRO_NAME

echo "Keystone construit."

echo "Construction de l'image locale : my-horizon:local"
docker build . \
    --build-arg FROM=base:$BASE_DISTRO_NAME \
    --build-arg WHEELS=requirements:$BASE_DISTRO_NAME\
    --build-arg PROJECT=horizon \
    --build-arg PROFILES=apache \
    --build-arg PIP_PACKAGES=pymemcache \
    --tag horizon:master-$BASE_DISTRO_NAME

echo "Terminé !"

docker compose up
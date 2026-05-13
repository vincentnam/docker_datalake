#!/bin/bash
set -e
export $(grep -v '^#' ../../conf.env | sed 's/\r$//' | xargs)
# ===================== CONFIGURATION =====================
OPENSTACK_RELEASE=$OPENSTACK_RELEASE_VAR
BASE_DISTRO=$BASE_DISTRO_VAR
BASE_TAG=$BASE_TAG_VAR

echo $BASE_TAG

# Ceph : Option recommendedf for Noble
CEPH_REPO=""
# CEPH_REPO='deb https://download.ceph.com/debian-tentacle/ noble main'  # Alternative

# ========================================================

if [ ! -d "loci" ]; then
    echo "Clonage du dépôt OpenStack LOCI..."
    git clone https://github.com/openstack/loci.git
fi

cd loci

echo "=========================================="
echo "Build Loci - OpenStack ${OPENSTACK_RELEASE} sur ${BASE_DISTRO}"
echo "=========================================="

# Construction de la base image
echo "Construction base image (${BASE_DISTRO})"
docker build . \
    -f Dockerfile.base \
    --build-arg FROM=$BASE_DISTRO \
    --build-arg CEPH_REPO="${CEPH_REPO}" \
    --tag base:${BASE_TAG}

# Requirements
echo "Construction requirements image"
docker build . \
    -f Dockerfile \
    --target requirements \
    --build-arg FROM=base:${BASE_TAG} \
    --build-arg PROJECT=requirements \
    --build-arg PROJECT_RELEASE=${OPENSTACK_RELEASE} \
    --build-arg PIP_PACKAGES="setuptools wheel cython" \
    --tag requirements:${BASE_TAG}-${OPENSTACK_RELEASE//stable\//}

# Keystone
echo "Construction Keystone"
docker build . \
    -f Dockerfile \
    --build-arg FROM=base:${BASE_TAG} \
    --build-arg WHEELS=requirements:${BASE_TAG}-${OPENSTACK_RELEASE//stable\//} \
    --build-arg PROJECT=keystone \
    --build-arg PROJECT_RELEASE=${OPENSTACK_RELEASE} \
    --build-arg PROJECT_REF=${OPENSTACK_RELEASE} \
    --build-arg PROFILES=apache \
    --build-arg DIST_PACKAGES="python3-openstackclient curl" \
    --tag keystone:${OPENSTACK_RELEASE//stable\//}-${BASE_TAG}

# Horizon
echo "Construction Horizon"
docker build . \
    -f Dockerfile \
    --build-arg FROM=base:${BASE_TAG} \
    --build-arg WHEELS=requirements:${BASE_TAG}-${OPENSTACK_RELEASE//stable\//} \
    --build-arg PROJECT=horizon \
    --build-arg PROJECT_RELEASE=${OPENSTACK_RELEASE} \
    --build-arg PROJECT_REF=${OPENSTACK_RELEASE} \
    --build-arg PROFILES=apache \
    --build-arg PIP_PACKAGES="pymemcache" \
    --tag horizon:${OPENSTACK_RELEASE//stable\//}-${BASE_TAG}

echo "Build terminé !"
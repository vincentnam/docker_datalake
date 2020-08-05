### DOC USED : https://docs.openstack.org/swift/latest/development_saio.html ###
## ROOT PART
##
# Dependecies
    yum -y update  
    yum -y install epel-release
    yum install yum-utils
    
    
    yum-config-manager --enable epel extras 
    yum -y install centos-release-openstack-train  
    # Pour GCC 
    yum install kernel-headers --disableexcludes=all
    
    yum -y install curl gcc memcached rsync sqlite xfsprogs git-core \
                 libffi-devel xinetd liberasurecode-devel \
                 openssl-devel python-setuptools \
                 python-coverage python-devel python-nose \
                 pyxattr python-eventlet \
                 python-greenlet python-paste-deploy \
                 python-netifaces python-pip python-dns \
                 python-mock
                 
    cd /projets/datalake
    mkdir swift_install
    cd swift_install
    sudo pip install --upgrade pip
    
    git clone https://github.com/openstack/python-swiftclient.git

    cd python-swiftclient 
    python setup.py develop --user
    cd .. 
    git clone https://github.com/openstack/swift.git
    
    sudo pip install --no-binary cryptography -r requirements.txt;
    python setup.py develop --user
    PATH=$PATH:"/users/neocampus/vdang/.local.bin"
    
Création de loopback device (for xattr over NFSv3)
    
    truncate -s $TAILLE /projets/datalake/swift_storage/swift_store
    mkfs.xfs /projets/datalake/swift_storage/swift_store
    
    sudo chown vdang:datalake /projets/datalake/swift_storage/swift_store
    mkdir /mnt/swift_store
    # Si on est pas dans le dossier, on peut pas monter, pourquoi ?
    cd /projets/datalake/swift_storage/
    # Option : read-write, loop 
    sudo mount -o loop,noatime,nodiratime,nobarrier,logbufs=8  swift_store /mnt/swift_store/   
    
    # Pas possible à cause des droits NFS
    # sudo echo "/projets/datalake/swift_storage/swift_store /mnt/swift_store xfs loop,noatime 0 0" >> /etc/fstab
    
    
    
Création loopback tmp pour le test
    
    cd /projets/datalake/swift_storage/
    truncate -s 1GB swift_tmp
    mkfs.xfs swift_tmp
    sudo mount -o loop,noatime swift_tmp /mnt/swift_tmp/
    # On bind pour ne pas avoir à changer le TMPDIR et pouvoir 
    # mettre le tmp sur la baie de stockage
    sudo mount --bind /mnt/swift_tmp/ /tmp/
    sudo chmod -R 1777 /mnt/swift_tmp/
    sudo chown -R vdang:datalake /mnt/swift_tmp/
   
    echo "export TMPDIR=/tmp/" >> $HOME/.bashrc
    export TPMDIR=/tmp/

Post loopback creation : 

    sudo mkdir /mnt/swift_store/1 /mnt/swift_store/2 /mnt/swift_store/3 /mnt/swift_store/4
    sudo chown ${USER}:${USER} /mnt/swift_store/*
    for x in {1..4}; do sudo ln -s /mnt/swift_store/$x /srv/$x; done
    sudo mkdir -p /srv/1/node/sdb1 /srv/1/node/sdb5 \
                  /srv/2/node/sdb2 /srv/2/node/sdb6 \
                  /srv/3/node/sdb3 /srv/3/node/sdb7 \
                  /srv/4/node/sdb4 /srv/4/node/sdb8
                  
    # To recreate on each reboot
    sudo mkdir -p /var/run/swift
    sudo chown -R vdang:datalake /var/run/swift
    

    sudo mkdir -p /var/cache/swift /var/cache/swift2 \
                  /var/cache/swift3 /var/cache/swift4
    sudo chown -R vdang:datalake /var/cache/swift*
    # **Make sure to include the trailing slash after /srv/$x/**
    for x in {1..4}; do sudo chown -R vdang:datalake /srv/$x/; done

    # Resize 
    # dd if=/dev/zero bs=1MiB of=/path/to/file conv=notrunc oflag=append count=xxx

Installation de rsync: 

    Modification de /etc/rsyncd.conf pour qu'il soit comme le fichier de ./files

    systemctl enable rsyncd 
    systemctl start rsyncd 
    
 
 Installation de memcached :
 
    sudo systemctl start memcached
    sudo systemctl enable memcached

Installation rsyslog :

    # Don't know why 
    

Config swift : 
   
    sudo cp -r saio/swift/ /etc/swift
    

Lancement swift :
   
#yum -y install sudo

# Create User
    USERNAME="vincentnam" && GROUPNAME="vincentnam"
    HOME=/home/${USERNAME}
     groupadd vincentnam && useradd -g ${GROUPNAME} -G wheel ${USERNAME}
#sed -i 's/User=/User=vincentnam/g' /etc/sddm.conf
# To check if it has been a success :
# id ${USERNAME}
#
    passwd ${USERNAME}
# Partitions set up (need to fit to the real /dev/ spec : TODO)


# Getting the code
    cp /mnt/user_install1.sh /
    chown ${USERNAME}:${GROUPNAME} /user_install1.sh
    sudo su -c "/user_install1.sh" - $USERNAME


# Rsync set up : for node replication
    
    cp /mnt/file/rsyncd.conf /etc/
    sed -i "s/<your-user-name>/${USERNAME}/" /etc/rsyncd.conf   
  # A MODIFIER SUR LA VRAIE MACHINE
    systemctl enable rsyncd
    systemctl start rsyncd
    
    systemctl start memcached
    systemctl enable memcached


## Configuring each node

    sudo rm -rf /etc/swift
    
    sudo cd $HOME/swift/doc; sudo cp -r saio/swift /etc/swift; cd -
    sudo chown -R ${USERNAME}:${USERNAME} /etc/swift
    
    find /etc/swift/ -name \*.conf | xargs sudo sed -i "s/<your-user-name>/${USERNAME}/"
### RING CREATION :
# https://opendev.org/x/swiftonfile/src/branch/master/doc/markdown/quick_start_guide.md
# Sûrement
# devices=/projets/datalake
# Mais besoin de swiftonfile



    

# ON A MODIFIER TOUS LES device en /projets/datalake...

# Creating an XFS tmp dir




# ON A MODIFIER TOUS LES device en /projets/datalake...


# TEST 
    
    echo "export SWIFT_TEST_CONFIG_FILE=/etc/swift/test.conf" >> ~/.bashrc
    echo "export PATH=${PATH}:/projets/datalake/swift_install/bin" >> ~/.bashrc 
    
    
    # Unit test lancement
    /projets/datalake/swift_install/swift/.unittests  3>&1 1>../swift_install/unit_test.log.txt 2>&1
    startmain
    
    curl -v -H 'X-Storage-User: test:tester' -H 'X-Storage-Pass: testing' http://127.0.0.1:8080/auth/v1.0

    curl -v -H 'X-Auth-Token: AUTH_tkf0de8b552e384218bbe5e1210ac3463b'  http://127.0.0.1:8080/v1/AUTH_test

     



     
     
# Configuration du proxy 
    
    scp -r /data/python-project/docker_datalake/docker_build/docker-swift-onlyone/middleware vdang@co2-dl-swift:/etc/swift



# Test
    
    curl -X PUT -T file1 -H 'X-Auth-Token: AUTH_tk65840af9f6f74d1aaefac978cb8f0899' http://10.80.83.68:8077/v1/AUTH_system/mycontainer/
    
    
# Problem resolution : 

    1. Check if loopback device (swift_storage / swift_tmp) are mounted : "connection refused" in API rest 
    2. If custom middleware is not well designed / coded, it will raised a 500 internal error on swift-proxy
    
# On reboot : 
    
    cd /projets/datalake/swift_storage/
    sudo mount -o loop,noatime,nodiratime,nobarrier,logbufs=8  swift_store /mnt/swift_store/   
    sudo mount -o loop,noatime swift_tmp /mnt/swift_tmp/
    
    sudo mount --bind /mnt/swift_tmp/ /tmp/
    sudo chmod -R 1777 /mnt/swift_tmp/
    
    sudo mkdir /var/run/swift
    sudo chown vdang:datalake /var/run/swift
    sudo chown -R vdang:datalake /srv/*
    sudo chown vdang:datalake /mnt/swift_store
    sudo chown vdang:datalake /mnt/swift_tmp
    remakerings
    startmain
    
    
    
# Functional test :

    ...
    ======
    Totals
    ======
    Ran: 950 tests in 571.0000 sec.
     - Passed: 883
     - Skipped: 67
     - Expected Fail: 0
     - Unexpected Success: 0
     - Failed: 0
    Sum of execute time for each test: 502.9311 sec.
    

# Add space to loopback device :
    
    # It can be done while server is on : TOP LIFE
    dd if=/dev/zero bs=1MiB of=swift_store conv=notrunc oflag=append count=1000
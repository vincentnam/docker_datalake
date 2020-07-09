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
    
    
Création de loopback device (for xattr over NFSv3)
    
    truncate -s $TAILLE /projets/datalake/swift_storage/swift_store
    mkfs.xfs /projets/datalake/swift_storage/swift_store
    # Wheel car on a besoin de mount :
    # mount ne peut être fait que par root (ou sudo) et 
    # donc il faut un groupe où root est présent
    sudo chown vdang:wheel /projets/datalake/swift_storage/swift_store
    mkdir /mnt/swift_store
    # Si on est pas dans le dossier, on peut pas monter, pourquoi ?
    cd /projets/datalake/swift_storage/
    # Option : read-write, loop 
    sudo mount swift_store -o rw,loop /mnt/swift_store
    # sudo echo "/projets/datalake/swift_storage/swift_store /mnt/swift_store xfs loop,noatime 0 0" >> /etc/fstab
    sudo chown -R vdang:datalake /mnt/swift_store
    
    
Création loopback tmp pour le test
    
    cd /projets/datalake/swift_storage/
    truncate -s 1GB swift_tmp
    mkfs.xfs swift_tmp
    sudo mount -o loop,noatime swift_tmp /mnt/swift_tmp/
    sudo chmod -R 1777 /mnt/swift_tmp/
    sudo chown -R vdang:datalake /mnt/swift_tmp/
   
    echo "export TMPDIR=/mnt/swift_tmp" >> $HOME/.bashrc
    export TPMDIR=/mnt/swift_tmp

    
Installation de rsync: 

    Modification de /etc/rsyncd.conf pour qu'il soit comme le fichier de ./files

    systemctl enable rsyncd 
    systemctl start rsyncd 
    
 
 Installation de memcached :
 
    sudo systemctl start memcached
    sudo systemctl enable memcached


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
    
    
    FAUT FAIRE UN LOOP BACK DEVICE
    
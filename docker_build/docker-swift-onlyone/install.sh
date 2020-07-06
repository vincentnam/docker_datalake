### DOC USED : https://docs.openstack.org/swift/latest/development_saio.html ###
## ROOT PART
##
USERNAME = "vincentnam"
GROUPNAME = "vincentnam"
# Dependecies
yum -y update && yum -y install epel-release && yum-config-manager --enable epel extras && yum -y install centos-release-openstack-train && yum -y install curl gcc memcached rsync sqlite xfsprogs git-core \
                 libffi-devel xinetd liberasurecode-devel \
                 openssl-devel python-setuptools \
                 python-coverage python-devel python-nose \
                 pyxattr python-eventlet \
                 python-greenlet python-paste-deploy \
                 python-netifaces python-pip python-dns \
                 python-mock

yum -y install sudo

# Create User
groupadd vincentnam
useradd -g ${GROUPNAME} wheel ${$USERNAME}
sed -i 's/User=/User=vincentnam/g' /etc/sddm.conf
# To check if it has been a success :
# id ${USERNAME}
#

# Partitions set up (need to fit to the real /dev/ spec : TODO)


# Getting the code
su $USERNAME
cd $HOME; git clone https://github.com/openstack/python-swiftclient.git
cd $HOME/python-swiftclient; sudo pip install -r requirements.txt; sudo python setup.py develop; cd -
git clone https://github.com/openstack/swift.git
cd $HOME/swift; sudo pip install --no-binary cryptography -r requirements.txt; sudo python setup.py develop; cd -
cd $HOME/swift; sudo pip install -r test-requirements.txt



# Rsync set up : for node replication

cp $HOME/swift/doc/saio/rsyncd.conf /etc/
sed -i "s/<your-user-name>/${USERNAME}/" /etc/rsyncd.conf
  # A MODIFIER SUR LA VRAIE MACHINE



### RING CREATION :
# https://opendev.org/x/swiftonfile/src/branch/master/doc/markdown/quick_start_guide.md
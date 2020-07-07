### DOC USED : https://docs.openstack.org/swift/latest/development_saio.html ###
## ROOT PART
##
# Dependecies
yum -y update && yum -y install epel-release && yum-config-manager --enable epel extras && yum -y install centos-release-openstack-train && yum -y install curl gcc memcached rsync sqlite xfsprogs git-core \
                 libffi-devel xinetd liberasurecode-devel \
                 openssl-devel python-setuptools \
                 python-coverage python-devel python-nose \
                 pyxattr python-eventlet \
                 python-greenlet python-paste-deploy \
                 python-netifaces python-pip python-dns \
                 python-mock sudo

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



# Creating an XFS tmp dir




#yum -y update && yum -y install epel-release && yum-config-manager --enable epel extras && yum -y install centos-release-openstack-train && yum -y install curl gcc memcached rsync sqlite xfsprogs git-core                  libffi-devel xinetd liberasurecode-devel                  openssl-devel python-setuptools                  python-coverage python-devel python-nose                  pyxattr python-eventlet                  python-greenlet python-paste-deploy                  python-netifaces python-pip python-dns                  python-mock sudo
#  995  su
#  996  exit
#  997  sudo
#  998  sudo echo "coucou"
#  999  exit
# 1000  yum update
# 1001  sudo yum update
# 1002  sudo    yum -y install epel-release
# 1003  sudo     yum-config-manager --enable epel extras
# 1004  uname -l
# 1005  uname -a
# 1006  cat /etc/redhat-release
# 1007  sudo yum install yum-utils
# 1008  yum-config-manager --enable epel extras
# 1009      sudo yum-config-manager --enable epel extras
# 1010      yum -y install centos-release-openstack-train
# 1011      sudo yum -y install centos-release-openstack-train
# 1012      yum -y install curl gcc memcached rsync sqlite xfsprogs git-core                  libffi-devel xinetd liberasurecode-devel                  openssl-devel python-setuptools                  python-coverage python-devel python-nose                  pyxattr python-eventlet                  python-greenlet python-paste-deploy                  python-netifaces python-pip python-dns \
# 1013  sudo   yum -y install curl gcc memcached rsync sqlite xfsprogs git-core                  libffi-devel xinetd liberasurecode-devel                  openssl-devel python-setuptools                  python-coverage python-devel python-nose                  pyxattr python-eventlet                  python-greenlet python-paste-deploy                  python-netifaces python-pip python-dns                  python-mock
# 1014  sudo    yum -y install centos-release-openstack-train
# 1015  sudo yum install curl gcc memcached rsync
# 1016  yum search kernel-headers
# 1017  yum install kernel-headers --disableexcludes=all
# 1018  sudo yum install kernel-headers --disableexcludes=all
# 1019  sudo   yum -y install curl gcc memcached rsync sqlite xfsprogs git-core                  libffi-devel xinetd liberasurecode-devel                  openssl-devel python-setuptools                  python-coverage python-devel python-nose                  pyxattr python-eventlet                  python-greenlet python-paste-deploy                  python-netifaces python-pip python-dns                  python-mock
# 1020  env
# 1021  id vdang
# 1022  USER=vdang
# 1023  GROUP=datalake
# 1024  cd $HOME
# 1025  ls
# 1026  cd /projets/datalake/
# 1027  ls
# 1028  mkdir swift_install
# 1029  cd swift_install/
# 1030  ls
# 1031  git clone https://github.com/openstack/python-swiftclient.git
# 1032  ls
# 1033  pwd
# 1034  cd python-swiftclient/
# 1035  pip install -r requirements.txt
# 1036  pip install --user -r requirements.txt
# 1037  python setup.py develop
# 1038  sudo python setup.py develop
# 1039  sudo pip install -r requirements.txt
# 1040  sudo python setup.py develop
# 1041  ls
# 1042  ls -la
# 1043  python setup.py config
# 1044  python setup.py develop
# 1045  sudo python setup.py develop
# 1046   sudo python setup.py develop; cd -
# 1047  ls
# 1048  cd python-swiftclient/
# 1049   sudo python setup.py develop
# 1050  ls -l
# 1051  sudo chmod +x setup.cfg
# 1052  ls -l
# 1053  cat setup.cfg
# 1054  ls
# 1055  sudo pip install --upgrade setuptools
# 1056  yum search python
# 1057  python --version
# 1058  python3
# 1059  ls
# 1060   sudo python setup.py develop
# 1061  sudo pip install --upgrade setuptools
# 1062  yum install python-setuptools
# 1063  yum search python-setuptools
# 1064  sudo yum install python-setuptools
# 1065  sudo yum install python2-setuptools
# 1066  sudo pip install --upgrade setuptools --user python
# 1067  yum search python-dev
# 1068  pip uninstall setuptools
# 1069  sudo pip uninstall setuptools
# 1070  sudo pip install setuptools
# 1071  pip install --upgrade setuptools --user python
# 1072  yum install python-setuptools
# 1073  sudo yum install python-setuptools
# 1074  sudo yum install python2-setuptools
# 1075  wget https://bootstrap.pypa.io/ez_setup.py -O - | python
# 1076  wget https://bootstrap.pypa.io/ez_setup.py -O - | sudo python
# 1077  sudo wget https://bootstrap.pypa.io/ez_setup.py -O - | sudo python
# 1078  sudo yum install python-pkg-ressources
# 1079  sudo yum search python-pkg-ressources
# 1080  sudo yum search python-pkg-
# 1081  sudo yum search python-pk
# 1082  sudo yum install python-setuptools
# 1083  sudo yum install python2-setuptools
# 1084  sudo yum install --reinstall python2-setuptools
# 1085  sudo yum install --upgrade python2-setuptools
# 1086  sudo yum install -upgrade python2-setuptools
# 1087  pip install --force-reinstall -U setuptools
# 1088  pip install --force-reinstall -U pip
# 1089  sudo yum reinstall python2-setuptools
# 1090  pip install --force-reinstall -U pip
# 1091  sudo pip install --force-reinstall -U pip
# 1092  sudo pip install --force-reinstall -U setuptools
# 1093  sudo yum reinstall python2-setuptools
# 1094  ls
# 1095  sudo python setup.py develop
# 1096  sudo id
# 1097  sudo chown root setup.cfg
# 1098   sudo pip install --no-binary cryptography -r requirements.txt; sudo python setup.py develop; cd -
# 1099  sudo yum uninstall python2-setuptools
# 1100  yum
# 1101  yum --help
# 1102  sudo yum remove python2-setuptools
# 1103  sudo yum install python-setuptools
# 1104   sudo pip install --no-binary cryptography -r requirements.txt; sudo python setup.py develop; cd -
# 1105  ls
# 1106  sudo python setup.py develop
# 1107  sudo sudo python setup.py develop
# 1108  sudo python setup.py develop
# 1109  ls
# 1110  ls -a
# 1111  history

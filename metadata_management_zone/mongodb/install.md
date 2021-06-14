# Build a MongoDB enterprise container
To build a MongoDB enterprise container, official documentation exists from MongoDB enterprise : https://docs.mongodb.com/manual/tutorial/install-mongodb-enterprise-with-docker/

Steps (that will be included in an Ansible playbook): 

    $ export MONGODB_VERSION=4.0
    $ curl -O --remote-name-all https://raw.githubusercontent.com/docker-library/mongo/master/$MONGODB_VERSION/{Dockerfile,docker-entrypoint.sh}
    $ export DOCKER_USERNAME=username
    $ chmod 755 ./docker-entrypoint.sh
    $ docker build --build-arg MONGO_PACKAGE=mongodb-enterprise --build-arg MONGO_REPO=repo.mongodb.com -t $DOCKER_USERNAME/mongo-enterprise:$MONGODB_VERSION .



#Install MongoDB in GoldZone
    
    cat <<EOF | sudo tee /etc/yum.repos.d/mongodb-enterprise-4.2.repo
    [mongodb-enterprise-4.2]
    name=MongoDB Enterprise Repository
    baseurl=https://repo.mongodb.com/yum/redhat/\$releasever/mongodb-enterprise/4.2/\$basearch/
    gpgcheck=1
    enabled=1
    gpgkey=https://www.mongodb.org/static/pgp/server-4.2.asc
    EOF    
    
    sudo yum install -y mongodb-enterprise
    sudo systemctl start mongod
    sudo systemctl enable mongod


# Configuration 

Input IP is by default binded on 127.0.0.1. It allows to accept connection only to localhost.

To allow external connection, it has to be binded on 0.0.0.0.

    vim /etc/mongod.conf
    >> bindIp: 127.0.0.1 -> bindIp: 0.0.0.0
    
    
 
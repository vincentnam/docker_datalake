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



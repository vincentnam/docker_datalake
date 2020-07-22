# Install neo4j Centos 7
    
    sudo rpm --import https://debian.neo4j.com/neotechnology.gpg.key
    cat <<EOF | sudo tee /etc/yum.repos.d/neo4j.repo
    [neo4j]
    name=Neo4j RPM Repository
    baseurl=https://yum.neo4j.com/stable
    enabled=1
    gpgcheck=1  
    EOF
    
    sudo yum install -y neo4j-enterprise-4.1.1
    
# Config

To accept non-local connections, uncomment this line in /etc/neo4j/neo4j.conf: 

    dbms.windows_service_name=neo4j

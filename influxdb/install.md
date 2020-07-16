# Install Influxdb centos7 
    
    cat <<EOF | sudo tee /etc/yum.repos.d/influxdb.repo
    [influxdb]
    name = InfluxDB Repository - RHEL \$releasever
    baseurl = https://repos.influxdata.com/rhel/\$releasever/\$basearch/stable
    enabled = 1
    gpgcheck = 1
    gpgkey = https://repos.influxdata.com/influxdb.key
    EOF
    
    
    sudo yum makecache fast
    sudo yum -y install influxdb vim curl
    
    sudo systemctl start influxdb && sudo systemctl enable influxdb
    
    
https://computingforgeeks.com/install-grafana-and-influxdb-on-centos-7/ pour la config 
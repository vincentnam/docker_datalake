# Install Influxdb 1.8 on Centos7 
    
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

# Installation Influxdb 2.0 on Centos7

    wget https://dl.influxdata.com/influxdb/releases/influxdb_2.0.0-alpha.14_linux_amd64.tar.gz
    tar xzvf influxdb_2.0.0-alpha.14_linux_amd64.tar.gz 
    export PATH=$PATH:/projets/datalake/influxdb/
    sudo useradd -rs /bin/false influxdb
    #Systemctl service creation :
    sudo vim /lib/systemd/system/influxdb2.service 
    
    [Unit]                                                                                   
    Description=InfluxDB 2.0 service file.                                                       
    Documentation=https://v2.docs.influxdata.com/v2.0/get-started/                               
    After=network-online.target                                                                  
                                                                                                 
    [Service]                                                                                    
    User=influxdb                                                                                
    Group=datalake                                                                               
    ExecStart=/projets/datalake/influxdb/influxd                                                 
    Restart=on-failure                                                                           
                                                                                                 
    [Install]                                                                                    
    WantedBy=multi-user.target
    
    TO CHANGE : 
    usr : datalake_admin / password : osirim_datalake_admin
    
    
    
{
{"id":1},
{"id":2}
}
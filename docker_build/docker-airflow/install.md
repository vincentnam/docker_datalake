# Installation airflow
    
    sudo yum -y update  
    sudo yum -y install epel-release
    sudo yum install yum-utils
    sudo yum install kernel-headers --disableexcludes=all
    
    sudo yum install gcc gcc-c++ libffi-devel mariadb-devel cyrus-sasl-devel python3-devel
    
    sudo easy_install-3.6 -U setuptools

    alias pip=pip3
    pip install apache-airflow --user
    
    
    
    
# Accès aux ports : par tunnel ssh 
    # Connection au VPN pour accès aux VM (Cf : Doc intranet IRIT accès VPN)   
    sudo openvpn /etc/openvpn/vpn-IRIT/vpn-TCP4-443-client.ovpn
    # Tunnel SSH pour accès aux ports bloqués
    # sss -L PORT_DISTANT:ADRESSE_A_BIND:PORT_LOCAL ADRESSE_DISTANTE
    ssh -L 8080:localhost:8080 vdang@co2-dl-airflow
    # On peut maintenant se connecter via localhost:8080
    
    
# Installation dépendances python 

    pip install pymongo influxdb neo4j python-swiftclient jinja2 --user
    
    
    
    
# Lancement Airflow

    airflow initdb
    tmux 
    # Console 1 :
    airflow webserver -p 8080
    # Console 2 : 
    airflow scheduler 
    # ctrl+B puis D 
    
    # Session TMUX lancée pour Airflow   
    
    # Needed to create an airflow connection (in UI port 8080) for Mongodb
    # Used in Airflow hook but not implemented for neo4j, influxdb
    # 2 connections : mongo_gold & mongo_metadatabase
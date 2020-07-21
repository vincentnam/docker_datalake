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
    # To change the port : change airflow.cfg (url endpoint and port)
    # default : airflow webserver -p 8080
    airflow webserver -p 8081
    # Console 2 : 
    airflow scheduler 
    # ctrl+B puis D 
    
    # Session TMUX lancée pour Airflow   
    
    # Needed to create an airflow connection (in UI port 8080) for Mongodb
    # Used in Airflow hook but not implemented for neo4j, influxdb
    # 2 connections : mongo_gold & mongo_metadatabase
    
    
# Lancement par systemd

Problème de d'accès aux executables de airflow (/users/neocampus/vdang/.local/bin/airflow) par systemd (présents sur la baie, pb de nfs) 


# Config API rest
Since airflow > 1.10, REST api is defined to deny all. 

    [api]
    auth_backend = airflow.api.auth.backend.deny_all

    CHANGED BY 
    
    [api]
    auth_backend = airflow.api.auth.backend.default 
    
    
# Use Curl on REST api 

    curl -X POST http://localhost:8081/api/experimental/dags/new_input/dag_runs -H 'Cache-Control: no-cache' -H 'Content-Type: application/json' -d '{"conf":{"swift_id":0, "swift_container":"mygates"}}'

-d : for data (payload)
    Set any field in "conf" document
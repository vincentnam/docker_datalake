# Install on ansible node / management vm
    cd /datalake/ansible/
    sudo yum install kernel-headers --disableexcludes=all
    sudo yum install python3-venv
    python3 -m venv /datalake/ansible/deployment_venv
    source /datalake/ansible/deployment_venv/bin/activate
    pip install -U pip
    pip install 'ansible<2.10'
    pip install 'kolla-ansible<10'
    sudo mkdir -p /etc/kolla
    sudo chown $USER:$USER /etc/kolla

    cp -r /datalake/ansible/deployment_venv/share/kolla-ansible/etc_examples/kolla/* /etc/kolla
    cp deployment_venv/share/kolla-ansible/ansible/inventory/* .


# Configure ansible 
    
    touch /etc/ansible/ansible.cfg
    
ansible.cfg content : 
    
    [defaults]
    host_keys_checking=False
    pipelining=True
    forks=2

host.cfg content : 

    [ping_group]
    co2-dl-test
    co2-dl-test2
    
    [keystone]
    co2-dl-test
    
    [swift]
    co2-dl-test2


##### Test  
    ansible ping_group -m ping
    # Ping all (via "-m ping") all the nodes in ping_group
    
##### Config kolla 
    
    kolla-genpwd 
    
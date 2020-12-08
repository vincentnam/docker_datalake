# Setup
    # Install python3 ansible version
    yum install python3 
    pip3 install ansible --user 
    # Used for Docker 
    ansible-galaxy collection install community.general 
    
# Launch playbook : 
    ansible-playbook /datalake/ansible/playbook/playbook-1.yml -kK

-kK is for sudo password (cf Ansible doc or man)
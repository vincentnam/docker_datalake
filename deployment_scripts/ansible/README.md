# Directory structure
The latest version of Ansible is the 2.11.1 at the point  
The Ansible directory structure is based on common directory structure defined in Ansible documentation (https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html#role-directory-structure) : 

    roles/
        raw_data_zone/
            tasks/
            handlers/
            library/
            files/
            templates/
            vars/
            defaults/
            meta/
        metadata_management_zone/
            tasks/
            ...


We define a role for each zone.

- tasks/ - contains tasks files
- tasks/main.yml - the main list of tasks that the role executes.
- handlers/ - contains handlers files
- handlers/main.yml - handlers, which may be used within or outside this role.
- library/ - contains library modules / custom modules
- library/my_module.py - modules, which may be used within this role (see Embedding modules and plugins in roles for more information).
- defaults/ - contains defaults variable files
- defaults/main.yml - default variables for the role (see Using Variables for more information). These variables have the lowest priority of any variables available, and can be easily overridden by any other variable, including inventory variables.
- vars/ - contains var files that will override defaults
- vars/main.yml - other variables for the role (see Using Variables for more information).
- files/ - contains files that will be deployed, for services configurations or host configurations. Datalake services files definitions that are needed for services deployment are kept in folder at root of the repository to lmake it easy to custom datalake services.
- files/main.yml - files that the role deploys.
- templates/ - contains templates in .j2 extension / format.
- templates/main.yml - templates that the role deploys.
- meta/ - contains metadata files
- meta/main.yml - metadata for the role, including role dependencies.



### Ansible : 

include_tasks vs import tasks : 

All import* statements are pre-processed at the time playbooks are parsed.
All include* statements are processed as they encountered during the execution of the playbook.


Environnement variable :

See https://docs.ansible.com/ansible/latest/user_guide/playbooks_vars_facts.html

- ansible_play_hosts is the list of all hosts still active in the current play.

- ansible_play_batch is a list of hostnames that are in scope for the current ‘batch’ of the play.

- The batch size is defined by serial, when not set it is equivalent to the whole play (making it the same as ansible_play_hosts).

- ansible_playbook_python is the path to the python executable used to invoke the Ansible command line tool.

- inventory_dir is the pathname of the directory holding Ansible’s inventory host file.

- inventory_file is the pathname and the filename pointing to the Ansible’s inventory host file.
 
- playbook_dir contains the playbook base directory.

- role_path contains the current role’s pathname and only works inside a role.

- ansible_check_mode is a boolean, set to True if you run Ansible with --check.



Access host_vars : 

1. Create a file name as the host (tested with localhost : "127.0.0.1")
   

    ---
    DATA_PATH: "test"

2. Call it through hostvars
ansible.builtin.debug:
      var: hostvars["127.0.0.1"].DATA_PATH
   


Docker module : 

https://docs.ansible.com/ansible/latest/collections/community/docker/index.html


Ansible Variable : 

https://docs.ansible.com/ansible/latest/reference_appendices/special_variables.html#sts=Magic%20variables%C2%B6
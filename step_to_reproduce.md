You can use the same config by copying files in the repository or custom the installation from default installation.

# Raw data zone :
1. Install Openstack Swift (All-in-one, full install or through docker container)  (https://docs.openstack.org/swift/{Swift_version_used}/index.html)
2. Custom Swift configuration files depending on your installation (/etc/swift) : 
    - [DEFAULT] section for each file (depending on your host architecture): 
        - set user (create a service user)
        - set ip
        - set port
        - etc..
3. Add a middleware (https://docs.openstack.org/swift/{Swift_version_used}/development_middleware.html) in <swift-repo>/swift/common/middleware : 
   - create middleware python file "new_data_trigger.py"
   - add content of new_data_trigger.py from the github repository (Openstack/swift/new_data_trigger.py) : this trigger is based on "webhook.py";
   - change URL ("http://IP_ADD:PORT" to Airflow instance (to webserver))/ ENDPOINT_PATH (default : /api/experimental) / DAG_NAME (name used in Airflow to define a DAG) depending on your configuration
4. Add in proxy-server.conf (cf proxy-server.conf in github repository):
   - "[filter:new_data_trigger]
        paste.filter_factory = swift.common.middleware.new_data_trigger:new_data_trigger_factory " at the end of the file 
   - add in proxy-server workflow "new_data_trigger" at the end just before "proxy_server"


# Process zone : 
1. Install Airflow (cf https://airflow.apache.org/docs/apache-airflow/stable/installation.html : apache-airflow vesion used in POC was 1.10.11) with docker, python or python virtual env. 
2. Start services (cf https://airflow.apache.org/docs/apache-airflow/stable/start/local.html)
3. Add Airflow workflow with same name as defined in middleware (the DAG is named "test" for testing in POC) 
g

# Metadata zone : 
1. Install MongoDB (docker container or not)
2. Initialize the database : create "object_id_file" file in stats database in collection in mongodb (cf python_test_script.py and init_db() function)

# Processed data zone : 
1. Deploy any database, reporting tool or service you need. Ex : mongodb, neo4j, influxdb, MsSQL. 

## - - - - - -

Branching in Airflow is based on metadata. Any informations can be found in "{repository_folder}/apache_airflow/dags/dag_creator". 

Tools have been defined in "{repository_folder}/apache_airflow/dags/lib/", defining tools in this lib is a good practice. 

CARE : 
- If Airflow is not up with the new middleware, Openstack Swift will raise 4xx answer


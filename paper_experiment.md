## Step to reproduce the experiment described in "A Zone-Based Data Lake Architecture for IoT, Small and Big Data"
### Requirements : 
    
    - Datalake architecture with Openstack Swift, Apache Airflow, MongoDB for metadata management and InfluxDB in processed data zone (see ./step_to_reproduce.md)
    - a MQTT broker to subscribe to for stream data

### Create news workflows for data

2 pipelines have been created. Those pipeline can be found in [apache_airflow/dags/dag_creator.py]() :
- For batch data 
- For stream data
(see "IDEAS[...]" function)
#### Batch data :
You can find a batch data sub sample in [dataset/batch_data/synop.2021041515.csv]().
You can download these data from https://donneespubliques.meteofrance.fr/?fond=produit&id_produit=90&id_rubrique=32 .

Data have been preprocessed to be faster in development : ";" have been replaced in the file by "," to match CSV default structure with shell tool : 

    $ sed -i "s/;/,/" synop.2021041515.csv

#### Stream data : 

A python process has been set on external virtual machine to subscribe to MQTT broker, read messages and send it to the datalake. The RESTful API isn't full operational, the experiment has been done without. 
Data are directly send to Openstack Swift + MongoDB.

You can find the script for MQTT listening + message sending to datalake in [dataset/MQTT/MQTT_subscriber.py]() file. 

(MQTT logs + address has been removed.)


# Data lake architecture POC hosted on OSIRIM (https://osirim.irit.fr/site/)

This repository is the main working repository for the data lake architecture.
The goals are : 
- Create an opensource architecture for data management based on data lake architecture
- Handle any type of data 
- Handle any volumetry of datas
- Make it easy to deploy the architecture
- Make an interoperable architecture through the usage of REST API whenever it is possible





##Table of content
- [Context](#Context)
- [The project](#Context)
* [Current architecture](#Current architecture)
* [Areas Description](#Areas Description)
+ [Raw data management area / landing area](#Raw data management area or landing area )
+ [Process area](#Process area)
+ [Consumption zone or processed data area or gold zone](#Consumption zone or processed data area or gold zone)
+ [Services area](#Services area)
+ [Security and monitoring area](#Security and monitoring area )
* [Services available](#Services available)
* [Tools used](#Tools used)
* [Diagrams](#Diagrams)
+ [Activity Diagram](#Activity Diagram)
+ [Data integration activity diagram for Apache Airflow](#Data integration activity diagram for Apache Airflow)
* [How to](#How to)
+ [Insert a new data](#Insert a new data)
+ [How to process a data already inserted](#How to process a data already inserted)
+ [Access to services - TODO](#Access to services)
    - [TCP Ports used](#TCP Ports used)
    - [API description - TODO](#API descrption)
+ [Deploy the architecture](#Deploy the architecture)
+ [Integrate a new process pipeline in Airflow](#Integrate a new process pipeline in Airflow)
    - [Problems already encountered](#Integrate a new process pipeline in Airflow)
* [Data formats in](#Data formats in)
+ [Openstack Swift](#Openstack Swift)
+ [MongoDB metadata database - TO REFACTOR](#MongoDB metadata database)
+ [Data exchanges between services](#Data exchanges between services)
- [TODO](#TODO)
* [Development on the project](#Development on the project)
* [Development for the project](#Development for the projet)
+ [Around the architecture](#Around the architecture)
+ [Documentation](#Documentation)
+ [What to change for a production deployment](#What to change for a production deployment)
+ [How to go further](#How to go further)
-[Neo4j example usage for image recommandation system](#Neo4j example usage for image recommandation system)
- [Other informations](#Other informations)
* [Tools not used](#Tools not used)
+ [In the input area](#In the input area)
+ [In process area](#In process area)
+ [In processed data area](#In processed data area)
* [Start Openstack Swift docker container](#Start Openstack Swift docker container)
* [More documentation](#More documentation)
* [Licence](#Licence)
- [Contacts](#Contacts)
    
    
- [Table of content](#Table of content)
    - [Test](#typo3-extension-repository)
    - [Composer](#composer)
- [TYPO3 setup](#typo3-setup)
    - [Extension](#extension)
    - [Database](#database)
- [Page setup](#page-setup)
    - [Upload the page tree file](#upload-the-page-tree-file)
    - [Go to the import view](#go-to-the-import-view)
    - [Import the page tree](#import-the-page-tree)
    - [SEO-friendly URLs](#seo-friendly-urls)
- [License](#license)
- [Links](#links)

# Context
This project is supported by neOCampus, OSIRIM, the CNRS, the IRIT and the SMAC team in IRIT. 

This project has been started with a internship for 2nd year of Master in Statistic and Decisional Computing (SID at Université Toulouse 3 - Paul-Sabatier in Toulouse) funded by neOCampus. 
The project has been continued through a 1year-fixed-term contract by the CNRS and the OSIRIM platform.

- NeOCampus is an operation based in the University with numerous research laboratory. A big part of the network used in this operation is used by sensors and effector. But we can find a lot of other kind of informations. The goal of this project is to create an architecture of data lake that can handle the needs and the data in neOCampus operation.
- OSIRIM (Observatoire des Systèmes d'Indexation et de Recherche d'Information Multimedia) is one of IRIT's platforms. It is mainly supported by the European Regional Development Fund (ERDF), the French government, the Midi-Pyrénées region and the Centre National de la Recherche Scientifique (CNRS).
- The SMAC team is interested in modeling and problem solving in complex systems using multi-agen technology. ( https://www.irit.fr/departement/intelligence-collective-interaction/equipe-smac/ )

# The project 

## Current architecture 
![alt text](./git_image/DataLakeArchiV0-Objectif-Zone.png)

The architecture is divided in 5 functional areas :
- Raw data management area (also known as the landing area)
- Process area
- Processed data area (also known as the gold zone)
- Services area
- Security and monitoring area

### Areas description : 

Each area has its own goal : 

![alt text](./git_image/DataLakeArchiV0.png)

#### Raw data management area or landing area 

The purpose of this area is to handle, store and make available raw data. Each data is stored as is waiting to be processed and transformed into an information.

This area is the core of the architecture, where every data are stored and every service of this architecture are working on. 
This area is composed with 2 services :
- Openstack swift (https://wiki.openstack.org/wiki/Swift) : 
    - Openstack Swift is a cloud storage software. It is an object-oriented store. It is a part of the Openstack cloud platform deployment and has been built for scale and optimized for durability, availability, and concurrency across the entire data set. 
    - Its role is to store all input data as an object. It can handle any type of file or data of any size. 
- MongoDB (https://www.mongodb.com/) :
    - Document oriented NoSQL database. It has been built as a NoSQL database made for high volumetry input. 
    - Its role is to store meta data over the data inserted in Openstack Swift and to make it possible to follow and store data over data and be able to know what is stored in Openstack Swift.

A third service has been integrated in the conception for data stream input :
- Apache Kafka (https://kafka.apache.org/):
    - Apache Kafka is an open-source distributed event streaming platform.
    - Its initial purpose is to handle MQTT message from sensors to raw data management area.
    
#### Process area
This area is composed by 1 service that will handle every workflow and jobs of data processing :
- Apache Airflow (https://airflow.apache.org/)
    - Job and workflow scheduler application. This service make it possible to schedule and monitor workflows written in Python.
    - Based on direct acyclic graphs, the data life is easily monitored.
    - It process raw data from the raw data management area to the processed data area by applying custom workflows developed by and for users needs. 

The deployment of a Hadoop cluster has been thought but the idea could be not implemented or kept.

#### Consumption zone or processed data area or gold zone  
This area is there to create values over data. Its role is to provide information and allow external application to work on data.
The processed data area is supposed to host any database that is needed by users. 
As no real need have been expressed, no real use case are implemented here. 
But some use cases have been imagined :
- InfluxDB (https://www.influxdata.com/):
    - Time serie oriented database with data visualization tools natively integrated.
    - The purpose of this database is to store formatted sensors readings and make it possible to visualize those data easily.
- Neo4J (https://neo4j.com/): 
    - Graph oriented database with data visualization tools natively integrated.
    - The purpose of this database is to store metadata over blob data (image, sound, video) to create a recommendation system for dataset creation.
- MongoDB (https://www.mongodb.com/):
    - Same database as the metadata database used in the raw data management area.
    - The purpose here is to store data for in-production applications
    
#### Services area 
This functional area includes every service to make this platform user-friendly. At this point (23/11/2020), 3 services have been designed :
- Data insertion and download services :
    - Composed with 2 services : web GUI and REST API.
        - The web GUI is based on NodeJS server with a React application for user-friendly data insertion. The data are inserted or shown through a graphical user interface to make it easy to use.
        - The REST API is developed with python Flask API to make it possible to programmatically use the data management services (insert data in raw data management area or download data from processed data area)
- Real-time data consumption service :
    - No solution have been found at this point (23/11/2020) to answer this need.
    - The purpose of this service is to make it possible to consume data in a real-time process (initially designed for autOCampus project in neOCampus)
- Streaming data consumption service :
    - No solution have been found at this point (23/11/2020) to answer this need.
    - The purpose of this service is to make it possible to consume data as a stream for application that works in streaming mode. It has been initialy designed for online machine learning application. 

#### Security and monitoring area  
The purpose of this area is to make it possible to monitor the whole architecture for administrators and give 3 level monitoring.
The area has to be adapted to the host platform so services could change with deployment.
- First monitoring level : User level
    - Openstack Keystone (https://wiki.openstack.org/wiki/Keystone)
        - This service is here to identify and authenticate users in the architecture.
        - It integrate itself well with Openstack Swift and over other authentication services as LDAP or NIS that allow to maintain pre-existing authentication services. 
- Second monitoring level : Service level
    - Openstack Ceilometer (https://docs.openstack.org/ceilometer/latest/):
        - This service is a telemetry service for Openstack services. 
        - The objective is to monitor services state and usages for sizing in operation.
- Third level : Network and system level
    - SNMP + Zabbix : 
        - SNMP is a standard protocol of network management. It allow us to follow machine resources consumption and network usage.
        - Combine with Zabbix, this is a service of network and system monitoring with graphical user interface.

This area has to be work more to better design it. Prometheus could be used to monitor Network and System level and other services could be used for other levels. 

### Services available
TODO : Refactor and update -> new data analysis and new horizons are set

| |Swift | Metadata `MongoDB` | Airflow |Airflow `Jobs` | Neo4J `"Gold" zone`|InfluxDB`"Gold" zone`|Mongodb`"Gold" zone`  
|:-----:|:----------:|:----------:|:--:|:--:|:--:|:-:|:-:| 
Todo |  | |||| | |
Working|<img src="https://image.flaticon.com/icons/svg/2165/2165867.svg" height="32">|<img src="https://image.flaticon.com/icons/svg/2165/2165867.svg" height="32">|<img src="https://image.flaticon.com/icons/svg/2165/2165867.svg" height="32">|<img src="https://image.flaticon.com/icons/svg/2165/2165867.svg" height="32">|<img src="https://image.flaticon.com/icons/svg/2165/2165867.svg" height="32">|<img src="https://image.flaticon.com/icons/svg/2165/2165867.svg" height="32">|<img src="https://image.flaticon.com/icons/svg/2165/2165867.svg" height="32">|
Production state|<img src="https://image.flaticon.com/icons/svg/2165/2165867.svg" height="32">|<img src="https://image.flaticon.com/icons/svg/2165/2165867.svg" height="32">|<img src="https://image.flaticon.com/icons/svg/2165/2165867.svg" height="32">|<img src="https://image.flaticon.com/icons/svg/2165/2165867.svg" height="32">|<img src="https://image.flaticon.com/icons/svg/2165/2165867.svg" height="32">|<img src="https://image.flaticon.com/icons/svg/2165/2165867.svg" height="32">|<img src="https://image.flaticon.com/icons/svg/2165/2165867.svg" height="32">|
Optimized||||||||  
Production state|<img src="https://image.flaticon.com/icons/svg/2165/2165867.svg" height="32">|<img src="https://image.flaticon.com/icons/svg/2165/2165867.svg" height="32">|<img src="https://image.flaticon.com/icons/svg/2165/2165867.svg" height="32">| |<img src="https://image.flaticon.com/icons/svg/2165/2165867.svg" height="32">|<img src="https://image.flaticon.com/icons/svg/2165/2165867.svg" height="32">|<img src="https://image.flaticon.com/icons/svg/2165/2165867.svg" height="32">|

  
All is installed on Osirim : need to be tested.


### Tools used 

- MongoDb
- Openstack Swift
- Apache Airflow 
- Neo4J
- Influxdb
- NodeJS
- React
- Flask

Aiflow DAG tools in the apache_airflow/dag/lib folder has a special nomenclature : 
- *tools : all the tools from a database or to process a specific data type 
- *integrator : implemented tool to put data into a specific database 


## Diagrams
### Activity Diagram  
The data life in this architecture is described in this diagram : 

![alt text](./git_image/Sequence_Datalake.png)

- First, data are inserted simultaneously in Openstack Swift and MongoDB meta database.
- Then, a webhook is triggered by swift proxy to trigger the Airflow workflow for new data containing metadata over the data inserted.
- Depending on the data type, the user and the user group / project, the data is processed, transformed and inserted in the corresponding database in the processed data area. 
- Every operations are logged in the metadata database.
 
### Data integration activity diagram for Apache Airflow
![alt text](git_image/network_diagram.png)

The Proof of Concept hosted on Osirim is hosted on several VM.
Each service has its own virtual machine. 
Data storage is made on a NFS bay. At this point (23/11/2020), the POC is not adapted for this platform and wont be deployed in a production state on OSIRIM.
## How to
### Insert a new data
![alt text](git_image/Sequence_Dataintegration.png)

To develop a tool to insert data in the datalake, you have to :
- Get the Swift ID counter and increase it (use "find_one_and_update" to do it with the same operation and reduce chances of data incoherence between 2 instances)
- Construct metadata to store in mongodb (JSON or Python dictionary)
    - content_type : MIME type of the data 
    - swift_user : the swift user that inserted the data
    - swift_container : the swift container where the data is stored
    - swift_object_id : the swift ID given to the data when it has been inserted
    - application : a description of the data usage : the application on which the data is used (optional)
    - swift_object_name : the name of the data (the original name)
    - creation_date : creation date of the document 
    - last_modified : date of the last document modification (and get the last operation date)
    - successful_operations : list of successful operations containing (tuple) :
        - execution_date : 
        - dag_id : The string of "dag_run" instance containing some informing as the dag_id (ex : <DagRun new_input @ 2020-08-04 14:42:38+00:00: 
        test:tester_neocampus_119:2020-08-04T14:42:38, externally triggered: True>") :
            - If the task has been triggered by the proxy-server trigger, it contains :
                - "manual"
                - the date=
            - If the task has been triggered by the "Check_data_to_process" dag, it contains ("%s_%s_%s:%s"): 
                - the user
                - the container
                - the data swift id
                - the date (datetime)
        - operation_instance : The task id (same format as the dag_id)
    - failed_operations : list of failed operations containing the same as in "successful_operations"
    - other_data : every data that are useful : dictionary 
        - For JSON (jsontools.mongodoc_to_influx()):   
            - template : dictionary for Influxdb to know what field in the json is for : 
                - measurement : str
                - time : datetime 
                - fields : list of couple (key:str ,value : Any)
                - tags : list of couple (key:str ,value: Any)
        - For image JPEG / PNG (neo4jintegrator.insert_image()) : 
            - image_content : every object that are in the image
                - main_object : the main objects in the image
                - secondary_object : object you can see in image in background 
- Check if the swift container exists. If not, creates it.
- Put the data in Swift (with content_type and the swift_id)
- Put the metadata in MongoDB
### How to process a data already inserted

There is a document in "stats" database in "swift" collection in MongoDB that contains list of data to process that will be check every 5 minutes by "Check_data_to_process" dag. Adding a swift
You'll have to add a document in this list containing : 
- swift_id 
- swift_container
- swift_user
- content_type 
For each data in this list, it will trigger a "new_input" dag to process this data.

### Access to services 

#### TCP Ports used 
 
Raw data area : 
- 8080 : Swift 
- 27017 : MongoDB metadatabase

Process zone : 
- 8081 : Airflow (Webserver)

Consumption zone : 
- Influxdb ports depends on InfluxDB version used (InfluxDB 2 beta version or RC version)  
    - 9999 : InfluxDB web interface  
    - 8086 : Influxdb web interface

- 7000 :Neo4J
#### API descrption
TODO : Openstack, MongoDB, API Rest for insertion, web gui, etc..

### Deploy the architecture
TODO : Finish ansible, make fully automatic deployment with ansible (see docker branch) 
- docker-compose up 

If you want to insert data in the datalake (a file) : use the "insert_datalake()" function in  ["python_test_script.py"](./python_test_script.py) 

### Integrate a new process pipeline in Airflow 
TODO : Explain how to add a new Airflow pipeline 
#### Problems already encountered
Dont name your task the same name of the callable : it will lead to an error
    
## Data formats in
![alt text](git_image/DataLakeArchiV0-24_11_2020%20-%20Data%20exchanges.png)
### Openstack Swift 
Object inserted in Openstack swift are renamed with a number id. 
This id is incremented by 1 for every object insert. It allows to follow easily the number of object stored in Openstack Swift.

Only the renamed data are store in Openstack swift. Every metadata are stored in the metadata database (MongoDB).
Each object is stored on a container that match to the project or the user group / team.
### MongoDB metadata database 
(23/11/2020) The metadata database is designed in several parts :
- "stats" database :
    - "swift" collection : 
        - contains only 1 document : 
            - { "_id" : ..., "type" : "object_id_file", "object_id" : last_available_swift_id }
            - used to rename and follow Swift object id
        - could be used to store other data
- "swift" database :
    - a collection for each project has to be created :
        - contains 1 document for each object. Each document contains : 
            - "_id" : MongoDB default ID , 
            - "content_type" : type of data / MIME type ,
            - "data_processing" : type of data processing in Airflow ("custom" or "default") for pipeline choosing,
            - "swift_user" : authenticated user that inserted the data, 
            - "swift_container" : Openstack Swift container referring to project / user group,
            - "swift_object_id" : id from "object_id_file" in stats database,
            - "application" : description of the purpose of the data,
            - "original_object_name" : original name ,
            - "creation_date" : ISODate("..."),
            - "last_modified" : ISODate("..."),
            - "successful_operations" : [ ] : list of successful operations done on the data,
            - "failed_operations" : [ ] : list of failed operations done on the data, 
            - "other_data" : {...} : anything that is needed to know on the data (custom metadata inserted by user) 
                     

## Data exchanges between services

Data exchanges at this point are described in the following schema.
![alt text](./git_image/DataLakeArchiV0-24_11_2020%20-%20Current%20data%20exchanges.png)



# TODO: 
(23/11/2020) At this point, the architecture development is described in this diagram
![alt text](./git_image/DataLakeArchiV0-actual.png)


## Development on the project
TODO list for the project development (i.e. the datalake architecture)
TODO : Update TODO list
- [x]  Raw data mangement area : 
    - [x] Batch mode for data insertion
        - [x] API Rest 
            - [x] Make available the data input
            - [X] API Rest to input 1 or more data
        - [x] Object storage : Openstack swift 
            - [x] Unittest : OK 
            - [x] Functionaltest : OK 
                - Ran: 950 tests in 571.0000 sec.
                    - Passed: 883
                    - Skipped: 67
                    - Expected Fail: 0
                    - Unexpected Success: 0
                    - Failed: 0
                    - Sum of execute time for each test: 502.9311 sec.
            - [ ] Keystone as authentication service
            - [ ] Other Openstack services 
        - [x] MongoDb database for metadata
            - [ ] Replication for single point of failure problem (REALLY IMPORTANT ! -> if MongoDB datas are corrupted, all data in the datalake are useless)  
        - [x] Trigger for new input to launch a new Airflow job
            - [x] Create middleware for swift proxy (Webhook trigger to launch Airflow jobs)
            - [ ] Use X-Webhook in Swift (secure way)
            - [ ] Optimizations 
    - [ ] Streaming mode for data insertion
        - [ ] Kafta integration
- [x]  The process area
    - [x] Airflow deployment (docker image) 
        - [x] Docker image 
        - [x] Installation on VM
        - [ ] Resources optimization 
            - [ ] Celery executor
            - [ ] Hadoop for jobs
    - [x] Airflow job creation / configuration 
        - [x] Handle hook from Swift middleware (Webhook)
        - [x] Set up jobs 
        - [ ] Find a proper way to instantiate dag from JSON file (day_ago function)
        - [x] Handle big file (split big file reading + processing if possible)
- [x] The processed data area / the gold zone : 
    - [ ] Relational database (default)
    - [x] Time serie oriented database (visualisation)
        - [x] Json data :
            - [x] Based on templates given (as an input in metadatabase) 
            - [ ] Improve done work
    - [x] Document oriented database (transactional vision)
    - [x] Graph database 
        - [x] Image files : 
            - [x] Jpeg 
                - [x] Nodes creation for objects in the file
                - [ ] Automatic object detection / segmentation 
        - [ ] Recommendation tool  
    - [ ] ...
- [x] The services area : 
    - [x] RESTFUL API for data insertion and download
        - [x] Python api with Flask 
            - [x] Insertion
            - [x] Download data from database in processed data area
            - [ ] Download data from raw data management area
        - [ ] Improve implementation
    - [x] Web GUI for data insertion and data visualization
        - [x] Dashboard creation
        - [x] Data download with React + Express backend server
            - [x] Drag'n'drop insertion 
            - [x] Progress bar
            - [ ] Handle SLO Openstack Swift insertion (Static Large Object) for > 1 Go files
        - [x] Data visualization with React + D3.JS
            - [x] Basic time series visualization
            - [x] Basic graph visualization
            - [ ] Complex visualization from several different databases
        - [ ] Beautiful dashboard development
    - [ ] Real-time data consumption
    - [ ] Streaming data consumption
- [ ] Security and monitoring area : 
    - [ ] Design the whole area 
    - [ ] Deploy area 
- [x] Set up a "log" database to log operations on data done
    - [x] Operations are logged in MongoDB MetaDataBase : successful and failed operation (Airflow task + id ) + operations per day

## Development for the projet
### Around the architecture
- [ ] Add metadata over transformed data in the goldzone (and be able to find the list of process done to create this processed data)
- [ ] Automatic deployment : Docker + Kubernetes + Ansible
- [ ] Define a licence (certainly MIT licence) : ask for project supervisors
### Documentation 
- [ ] Diagrams for 
    - [x] Software Architecture
        - [x] Basic
        - [ ] Advanced
    - [ ] Hardware Architecture
        - [ ] Basic 
    - [ ] Sequence diagram
        - [x] Basic
        - [ ] Advanced


 
### What to change for a production deployment
For swift : 
- Users authentications :
    - Change the test users 
    - Set up a Keystone service to handle users and authentications
    - Use LDAP (maybe possible ?)
- Size up storage
For MongoDB (metadatabase) :
- Change storage path
For Airflow : 
- Executor : use Celery executor for a better parallisation 
- Handle exceptions more specifically 
For Neo4J (Gold zone) :
- User "neo4j" / mdp "test"
- Change storage path
For InfluxDB (Gold zone) :
- Admin user (user : datalake_admin / password : osirim_datalake_admin)
- Create users
- Change storage path
For MongoDB (Gold Zone) : 
- Listening port  27017 : it will conflicts with the MongoDB metadatabase 
- Change storage path



### How to go further 
- [ ] Job creation automatization for Airflow 
    - Create automatically the job for new data format and the output format
        - Allow us to integrate every kind of data without human action 
- [ ] Ensure that input into Swift and MongoDB is an atomic operation (and if one fail, the other fail)
    - How ? : May not be possible
    - [ ] Solution : Set up a mechanism that check if data are well stored  
- [x] Handle the input of same data (redundant data)
    - [x] Done natively in Swift : all datas are stored even if they already are in the database
    - [ ] Set up a mechanism to handle redundant datas

#### Neo4j example usage for image recommandation system
TODO : Refactor, update and explain
![alt text](git_image/neo4j_data_shema.png )




# Other informations 

## Tools not used

### In the input area
- <img src="https://mapr.com/products/apache-hbase/assets/hbase-logo.png" height="42"> HBase : need for raw input data, HBase would have been used as a key / value database while it's a column store database + difficult to handle raw data reading

### In process area
- <img src="https://upload.wikimedia.org/wikipedia/commons/7/70/TalendLogoCoral.png" height="42"> Talend : difficulties to install on Linux + difficulties to find version that can be integrated in the POC

### In processed data area
Everything should be possible to be used in this area


### Start Openstack Swift docker container 
TODO : Refactor, update 

    docker build -f ./swift/Ubuntu1604.Dockerfile -t ubuntuswift ./swift/
    docker run -p 8080:8080 --privileged --device /dev/loop0 --device /dev/loop-control -it ubuntuswift

To make data persistant, use docker volume bind 
    
    docker run -p 8080:8080 --privileged --device /dev/loop0 --device /dev/loop-control -v /tmp/dev:/data_dev/1 -it ubuntuswift

The volumes are mounted in /tmp, you have to use a mountable object : dev or loopbackdevice file.


## More documentation

Other markdown files are in folder of each service containing some more information over the service.
A pdf is available in the repository. This pdf contains the internship report that I made for the internship. 
It is mainly made of design thinking.

## Licence 

Todo : Apache 2.0 licence ?


### Contacts :

04/01/2021 : 

DANG Vincent-Nam (Repository owner, intern and engineer working on the project)
Vincent-Nam.Dang@irit.fr / dang.vincentnam@gmail.com 
https://www.linkedin.com/in/vincent-nam-dang/  

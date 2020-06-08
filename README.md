# docker_datalake
Docker POC for datalake : neOCampus internship for 2nd year of Master in Statistic and Decisional Computing (SID at Université Toulouse 3 - Paul-Sabatier in Toulouse)
# Context :
NeOCampus is an operation based in the University with numerous research laboratory. A big part of the network used in this operation is used by sensors and effector. But we can find a lot of other kind of informations. The goal of this project is to create an architecture of data lake that can handle the needs and the data in neOCampus operation.

## Architecture (it might change in the future) : 
![alt text](./git_image/DataLakeArchiV0.png)


# Composition : 
The architecture is defined by big 3 parts : 

- [x]  Input part : the first area of the data lake that handle raw input data 
    - [x] Object storage
    - [x] MongoDb database for metadata
        - [ ] MongoDB hook for new input to launch a new Airflow job
- [ ]  Transformation from raw to formatted
    - [x] Airflow deploymen (docker image) 
    - [ ] Airflow job creation / configuration 
- [ ] The "gold" zone : database to store formatted / valuable data
    - [ ] Relational database (default)
    - [ ] Time serie oriented database (visualisation)
    - [ ] Document oriented database (transactional vision)
    - [ ] Graph database (?)
    - [ ] ...
# How to run : 
- docker-compose up 

If you want to insert data in the datalake (a file) : use the "insert_datalake()" function in  ["python_test_script.py"](./python_test_script.py) 



## Les outils : 

- MongoDb
- Openstack Swift
- Apache Airflow 


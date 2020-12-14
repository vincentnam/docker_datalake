# The DAG object; we'll need this to instantiate a DAG
import urllib.request
from urllib.error import HTTPError
from urllib.request import Request
from urllib.request import urlopen
from http.client import HTTPResponse
from pymongo import MongoClient

from airflow import DAG
from airflow.contrib.hooks.mongo_hook import MongoHook
from airflow.operators.dummy_operator import DummyOperator
# Operators; we need this to operate!
from airflow.operators.python_operator import PythonOperator, \
    BranchPythonOperator
from airflow.utils.dates import days_ago
from airflow.utils.helpers import chain
from time import sleep
from pymongo import MongoClient
import datetime
import os
from airflow.operators.bash_operator import BashOperator

from influxdbintegrator import InfluxIntegrator

cwd = os.path.dirname(os.path.abspath(__file__))
import yaml
import json
# { "_id" : ObjectId("5f2c3086409d17caa63230a0"),
#   "content_type" : "application/json",
#   "swift_user" : "test:tester",
#   "swift_container" : "neocampus",
#   "swift_object_id" : "166",
#   "application" : "neocampus sensors log",
#   "creation_date" : ISODate("2020-08-06T18:32:02.511Z"),
#   "last_modified" : ISODate("2020-08-06T18:32:02.511Z"),
#   "successful_operations" : [
#       { "execution_date" : ISODate("2020-08-06T14:32:03Z"),
#         "dag_id" : "<DagRun new_input @ 2020-08-06 14:32:03+00:00: manual__2020-08-06T14:32:03+00:00, externally triggered: True>",
#         "operation_instance" : "<TaskInstance: new_input.Json_log_to_timeserie_influxdb 2020-08-06T14:32:03+00:00 [success]>" } ],
#   "failed_operations" : [ ],
#   "other_data" : { "template" : { "measurement" : "mesurevaleur", "time" : "datemesure", "fields" : [ "value" ], "tags" : [ "idpiece", "idcapteur" ] } }
#   }
def check_type(**kwargs):
    """
    Check data MIME type and return the next task to trigger.
    It depends on MIME type and container.

    :param kwargs: Airflow context
    :return:
    """
    meta_base = MongoClient(
        "mongodb://" + globals()["META_MONGO_IP"] + ":" + globals()[
            "MONGO_PORT"] + "/"
    )

    group = kwargs["dag_run"].conf["swift_container"]
    swift_id = str(kwargs["dag_run"].conf["swift_id"])
    print(group)
    print(swift_id)
    metadata_doc = meta_base.swift[group].find_one({
        "swift_object_id": swift_id})
    # .kwargs["dag_run"].conf["content_type"]. /
    # find_one("mygates", {}, find_one=False)
    print(metadata_doc)
    kwargs["ti"].xcom_push(key="metadata_doc", value=metadata_doc)

    if metadata_doc["content_type"] in task_dict:
        if group in task_dict[metadata_doc["content_type"]]:
            return task_dict[metadata_doc["content_type"]][group][0].task_id
        else:
            return task_dict[metadata_doc["content_type"]]["default"][
                0].task_id
    else:
        if group in task_dict[metadata_doc["not_handled"]]:
            return task_dict[metadata_doc["not_handled"]][group][0].task_id
        else:
            return task_dict[metadata_doc["not_handled"]]["default"][0].task_id
    #
    # if type_dict[doc["content_type"]] in callable_dict:
    #     data_type = type_dict[doc["content_type"]]
    #     if group in callable_dict[data_type]:
    #         return callable_dict[data_type][group]
    #     else:
    #         return callable_dict[data_type]["default"]
    # else:
    #     return callable_dict["not_handled"]["default"]


def workflow_selection(**kwargs):
    # GET AUTH TOKEN
    user, password = 'test:tester', 'testing'
    # TODO: 13/10/2020 CHANGE IP WITH GLOBAL VAR
    url = 'http://141.115.103.30:8080/auth/v1.0'
    headers = {'X-Storage-User': user,
               'X-Storage-Pass': password
               }
    token_response = urlopen(Request(url, headers=headers)).getheaders()


    opener = urllib.request.build_opener()
    opener.addheaders = []

    for i in token_response:
        if i[0] == "X-Auth-Token":
            token = i[1]
        if i[0] == "X-Storage-Url":
            url = i

    container = kwargs["dag_run"].conf["swift_container"]
    swift_id = str(kwargs["dag_run"].conf["swift_id"])

    urllib.request.install_opener(opener)
    # TODO : 13/10/2020 MAKE AIRFLOW_TMP AS ENV VAR
    while(True):
        req = Request(url[1] + "/"+container+"/"+swift_id, method="HEAD")
        req.add_header("X-Auth-Token",token)

        try :
            urllib.request.urlopen(req)
            break
        except HTTPError as e404 :
            print(e404)
            sleep(10)


    meta_base = MongoClient(
        "mongodb://" + globals()["META_MONGO_IP"] + ":" + globals()[
            "MONGO_PORT"] + "/"
    )
    meta_base.server_info()

    # print(group)
    print(swift_id)
    # WAIT THE OBJECT HAS BEEN INSERTED
    print("kwargs['dag_run'].conf")
    print(kwargs["dag_run"].conf)
    metadata_doc = meta_base.swift[kwargs["dag_run"].conf["swift_container"]].find_one({
        "swift_object_id": str(swift_id)})
    kwargs["ti"].xcom_push(key="metadata_doc", value=metadata_doc)
    print(metadata_doc)
    return metadata_doc["data_processing"]
    # if  metadata_doc["data_processing"] == "custom":
    #     return "custom"
    # if metadata_doc["data_processing"] == "default":
    #     return

# import configurations of different services needed :
# IP and port of Swift, MongoDB, etc..
with open(cwd + "/config.yml", "r") as config:
    y = yaml.safe_load(config)
globals().update(y)


def custom_user_workflow(**kwargs):
    metadata_doc = kwargs["ti"].xcom_pull(key="metadata_doc")
    return metadata_doc["swift_container"]


def neocampus_branching(**kwargs):
    metadata_doc = kwargs["ti"].xcom_pull(key="metadata_doc")
    #TODO : 14/10/2020 REFACTOR DICT_TASK
    type_to_task = {"bson":"neocampus_bson_get"}
    return type_to_task[metadata_doc["content_type"]]

def neocampus_bson(**kwargs):
    pass


# TODO : Restructure DAG architecture

# # These args will get passed on to each operator
# # You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(2),
    # # 'email': ['airflow@example.com'],
    # 'email_on_failure': False,
    # 'email_on_retry': False,
    # 'retries': 0,
    # 'retry_delay': timedelta(minutes=0),
    # "schedule_interval" : None
}
dag = DAG(
    'test',
    default_args=default_args,
    description='test',
    schedule_interval=None,

)



run_this_first = DummyOperator(
    task_id='getting_data',
    dag=dag,
)
branch_op = BranchPythonOperator(
    task_id='data_workflow_selection',
    provide_context=True,
    python_callable= workflow_selection,
    dag=dag
)
# branch_op = DummyOperator(
#     task_id='check_data_type',
#     provide_context=True,
#     dag=dag)
join = DummyOperator(
    task_id='dag_end',
    trigger_rule='none_failed',
    dag=dag,
)


with open(cwd + "/dag1.json", "r") as f:
    distros_dict = json.load(f)
run_this_first >> branch_op

callable_dict = {"PythonOperator": PythonOperator,
                 "DummyOperator":DummyOperator,
                 "BranchPythonOperator":BranchPythonOperator
                 }
# TODO : recursive funct to create the pipeline (for n sublevel in dict)



default = DummyOperator(
    task_id='default',
    provide_context=True,
    dag=dag)
db_dump = DummyOperator(
    task_id='database_dump',
    provide_context=True,
    dag=dag)
mongo_db = DummyOperator(
    task_id='Mongodb_restore',
    provide_context=True,
    dag=dag)
SQL = DummyOperator(
    task_id='Relational_db_restore',
    provide_context=True,
    dag=dag)

data = DummyOperator(
    task_id='data',
    provide_context=True,
    dag=dag)

json = DummyOperator(
    task_id='application-json',
    provide_context=True,
    dag=dag)
csv = DummyOperator(
    task_id='text-csv',
    provide_context=True,
    dag=dag)
png = DummyOperator(
    task_id='image-png',
    provide_context=True,
    dag=dag)


def neocampus_get_swift_object(**kwargs):
    #TODO : 13/10/2020 DIRECT READ FILE IF LOOPBACK DEVICE ARE REMOVED (if swift can directly write on storage servers)
    metadata_doc = kwargs["ti"].xcom_pull(key="metadata_doc")

    print("kwargs['dag_run'].conf")
    print(kwargs["dag_run"].conf)
    # TODO: 13/10/2020 CHANGE IP WITH GLOBAL VAR
    # client_mongo = MongoClient("141.115.103.31:27017")
    # req_mongo = {"swift_object_id": swift_id}
    # doc = client_mongo.swift.neocampus.find_one(req_mongo)
    # print(doc["original_object_name"])
    # TODO : 13/10/2020 CHANGE USERS / PASS
    user, password = 'test:tester', 'testing'
    # TODO: 13/10/2020 CHANGE IP WITH GLOBAL VAR
    url = 'http://141.115.103.30:8080/auth/v1.0'
    headers = {'X-Storage-User': user,
               'X-Storage-Pass': password
               }
    token_response = urlopen(Request(url, headers=headers)).getheaders()


    opener = urllib.request.build_opener()
    opener.addheaders = []

    for i in token_response:
        if i[0] == "X-Auth-Token":
            opener.addheaders.append(i)
        if i[0] == "X-Storage-Url":
            url = i
    print(url[1])

    urllib.request.install_opener(opener)
    # TODO : 13/10/2020 MAKE AIRFLOW_TMP AS ENV VAR
    urllib.request.urlretrieve(url[1] + "/"+metadata_doc["swift_container"]+"/"+metadata_doc["swift_object_id"],
                               "/datalake/airflow/airflow_tmp/"+metadata_doc["original_object_name"])

    print(os.path.dirname(os.path.abspath(__file__)))

    print(kwargs["dag_run"].dag_id)


def neocampus_mongoimport(**kwargs):
    metadata_doc = kwargs["ti"].xcom_pull(key="metadata_doc")
    file_name = kwargs["dag_run"].dag_id
    #TODO : 13/10/2020 MAKE AIRFLOW_TMP AS ENV VAR
    #TODO : 13/10/2020 FIND A SOLUTION TO CHOSE DATABASE AND COLLECTION
    print("ssh -i /home/airflow/.ssh/airflow airflow@co2-dl-bd 'mongorestore -d "+
              metadata_doc["swift_container"] +" -c " + metadata_doc["original_object_name"]
              + " /datalake/airflow/airflow_tmp/"+ metadata_doc["original_object_name"] + "'")
    os.system("ssh -i /home/airflow/.ssh/airflow airflow@co2-dl-bd 'mongorestore -d "+
              metadata_doc["swift_container"] +" -c " + metadata_doc["original_object_name"]
              + " /datalake/airflow/airflow_tmp/"+ metadata_doc["original_object_name"] + "'")


custom = BranchPythonOperator(
    task_id='custom',
    provide_context=True,
    python_callable=custom_user_workflow,
    dag=dag)
neocampus = BranchPythonOperator(
    task_id='neocampus',
    provide_context=True,
    python_callable=neocampus_branching,
    dag=dag
)
neocampus_bson_get = PythonOperator(
    task_id='neocampus_bson_get',
    python_callable=neocampus_get_swift_object,
    provide_context=True,
    dag=dag,
)

neocampus_bson_mongorestore = PythonOperator(
    task_id='neocampus_bson_mongorestore',
    python_callable=neocampus_mongoimport,
    # bash_command='ls /datalake  && cp /datalake/co2-dl-bd',
    provide_context=True,
    dag=dag,
)

def datanoos_branching(**kwargs):
    metadata_doc = kwargs["ti"].xcom_pull(key="metadata_doc")
    # TODO : 14/10/2020 REFACTOR DICT_TASK
    type_to_task = {"application/csv": "datanoos_ba_huy_csv_ts"}

    return type_to_task[metadata_doc["content_type"]]


def datanoos_ba_huy_csv_ts(**kwargs):
    metadata_doc = kwargs["ti"].xcom_pull(key="metadata_doc")
    print(metadata_doc)
    metadata = metadata_doc["other_data"]
    print(metadata["dataset_id"])
    if metadata["dataset_id"] == "doi:10.5072/FK2/ILRD2U":
        print("Réalisation de traitements pour le dataset doi:10.5072/FK2/ILRD2U ")


def datanoos_zip(**kwargs):
    print("Pas encore implémenté")


def datanoos_insert_influx(**kwargs):
    import pandas as pd
    metadata_doc = kwargs["ti"].xcom_pull(key="metadata_doc")
    #TODO : 13/10/2020 DIRECT READ FILE IF LOOPBACK DEVICE ARE REMOVED (if swift can directly write on storage servers)

    print("kwargs['dag_run'].conf")
    print(kwargs["dag_run"].conf)
    # TODO: 13/10/2020 CHANGE IP WITH GLOBAL VAR
    # client_mongo = MongoClient("141.115.103.31:27017")
    # req_mongo = {"swift_object_id": swift_id}
    # doc = client_mongo.swift.neocampus.find_one(req_mongo)
    # print(doc["original_object_name"])
    # TODO : 13/10/2020 CHANGE USERS / PASS
    user, password = 'test:tester', 'testing'
    # TODO: 13/10/2020 CHANGE IP WITH GLOBAL VAR
    url = 'http://141.115.103.30:8080/auth/v1.0'
    headers = {'X-Storage-User': user,
               'X-Storage-Pass': password
               }
    token_response = urlopen(Request(url, headers=headers)).getheaders()


    opener = urllib.request.build_opener()
    opener.addheaders = []

    for i in token_response:
        if i[0] == "X-Auth-Token":
            opener.addheaders.append(i)
        if i[0] == "X-Storage-Url":
            url = i
    print(url[1])

    urllib.request.install_opener(opener)
    # TODO : 13/10/2020 MAKE AIRFLOW_TMP AS ENV VAR
    urllib.request.urlretrieve(url[1] + "/"+metadata_doc["swift_container"]+"/"+metadata_doc["swift_object_id"],
                               "/datalake/airflow/airflow_tmp/"+metadata_doc["original_object_name"])
    csv = pd.read_csv("/datalake/airflow/airflow_tmp/"+metadata_doc["original_object_name"], na_values="mq",
                      index_col="date")
    # Remove all the "unnamed" columns
    csv = csv.loc[:, ~csv.columns.str.contains('^Unnamed')]
    print(os.path.dirname(os.path.abspath(__file__)))
    token = "DEa8frzE8NKVlJqzpsUcFKIbFYBzSKaXD7XTNJQhIV4tRveazt-PTJigvxrHrh0wXmUtWDw0NeCK7GL1D_zIpg=="
    org = "test"
    bucket = "DataNoos"
    df_influx_integrator = InfluxIntegrator(token=token, org=org)
    print(kwargs["dag_run"].dag_id)
    print(csv)
    print(csv.keys())
    for index in csv:
        if index is not "numer_sta":
            df_influx_integrator.write_dataframe(csv,bucket,index,tag_list=["numer_sta"], time= None)



DataNoos = BranchPythonOperator(
    task_id='DataNoos',
    provide_context=True,
    python_callable=datanoos_branching,
    dag=dag
)
datanoos_ba_huy_csv_ts= PythonOperator(
    task_id='datanoos_ba_huy_csv_ts',
    python_callable=datanoos_ba_huy_csv_ts,
    provide_context=True,
    dag=dag,
)
datanoos_zip= PythonOperator(
    task_id='datanoos_zip',
    python_callable=datanoos_zip,
    provide_context=True,
    dag=dag,
)
datanoos_insert_influxdb= PythonOperator(
    task_id='datanoos_insert_influxdb',
    python_callable=datanoos_insert_influx,
    provide_context=True,
    dag=dag,
)



# Airflow user / data_processing password
branch_op >> [default, custom]
default >> [db_dump, data]

data >> [json, csv, png] >> join
db_dump >> [mongo_db, SQL] >> join

custom >> [neocampus, DataNoos]
neocampus >> [ neocampus_bson_get]
neocampus_bson_get >> neocampus_bson_mongorestore >> join
DataNoos >> [datanoos_ba_huy_csv_ts, datanoos_zip]
datanoos_ba_huy_csv_ts >> datanoos_insert_influxdb >> join
datanoos_zip >> join
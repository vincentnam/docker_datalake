# The DAG object; we'll need this to instantiate a DAG
import json
import yaml
import urllib.request
from urllib.error import HTTPError
from urllib.request import Request
from urllib.request import urlopen
from http.client import HTTPResponse
from pymongo import MongoClient
import sys
from datetime import timedelta
import datetime
from textwrap import dedent
import swiftclient.service
from swiftclient.service import SwiftService
import config
from services import extract_transform_load_time_series_csv
from services import extract_transform_load_time_series_json
from services import extract_transform_load_time_series_text
from services import extract_transform_load_images
from services import extract_transform_load_dump_sql
from services import extract_transform_load_sge
from services import typefile
from services import connection_mongo_metadata
from services import connection_swift
from services import mqtt_verify
import tempfile
import base64
from zipfile import ZipFile

from airflow import DAG
from airflow.contrib.hooks.mongo_hook import MongoHook
from airflow.operators.dummy_operator import DummyOperator
# Operators; we need this to operate!
from airflow.operators.python_operator import PythonOperator, \
    BranchPythonOperator
from airflow.utils.dates import days_ago
from airflow.utils.helpers import chain
from time import sleep
import datetime
import os
from airflow.operators.bash_operator import BashOperator

cwd = os.path.dirname(os.path.abspath(__file__))

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
    'branching',
    default_args=default_args,
    description='Branching on metadata to apply the right task',
    schedule_interval=None,

)


def content_neo4j_node_creation(**kwargs):
    """

    :param kwargs:
    :return:
    """
    from lib.neo4jintegrator import Neo4jIntegrator

    uri = "bolt://" + globals()["GOLD_NEO4J_IP"] + ":" + globals()[
        "NEO4J_PORT"]
    neo4j_user = "neo4j"
    neo4j_pass = "test"
    driver = Neo4jIntegrator(uri, neo4j_user, neo4j_pass)
    # mongo_uri = globals()["META_MONGO_IP"] + ":" + globals()["MONGO_PORT"]
    meta_base = MongoHook(globals()["MONGO_META_CONN_ID"])

    coll = kwargs["dag_run"].conf["swift_container"]
    swift_id = str(kwargs["dag_run"].conf["swift_id"])
    doc = meta_base.get_conn().swift.get_collection(coll).find_one(
        {"swift_object_id": swift_id})
    driver.insert_image(doc)


def from_mongodb_to_influx(token=None, nb_retry=10, **kwargs):
    """
    Take a mongodb Json like, parse it to find measurement, tags, fields and timestamp
    and create a point to insert into Influxdb.
    :param token : authentication token for InfluxDB
    :type token : str
    :param kwargs: Airflow context, containing XCom and other
    datas see Airflow doc for more informations.
    :return: None
    """
    # Import are done in function to not load useless libraries in other tasks
    from lib.influxdbintegrator import InfluxIntegrator
    from lib.jsontools import mongodoc_to_influx
    import swiftclient
    import json
    # InfluxDB Token to access
    if token is None:
        token = config.token_influxdb
    integrator = InfluxIntegrator(influx_host=globals()["GOLD_INFLUX_IP"],
                                  influx_port=globals()["INFLUXDB_PORT"],
                                  token=token)
    swift_co = swiftclient.Connection(user=globals()["SWIFT_USER"],
                                      key=globals()["SWIFT_KEY"],
                                      authurl=globals()["SWIFT_AUTHURL"], insecure=True)
    # Pull data from XCom instance : come from "check_type" task
    metadata_doc = kwargs["ti"].xcom_pull(key="metadata_doc")

    retry = 0
    while True:
        print("Try " + str(retry) + " : ", end='')
        try:
            # swift_json is a tuple : (meta_data, data)
            swift_json = swift_co.get_object(
                kwargs["dag_run"].conf["swift_container"],
                kwargs["dag_run"].conf["swift_obj_id"])
        except Exception as e:
            # If swift is
            retry += 1
            if retry >= nb_retry:
                # Augments sleep time to be sure to let swift get ready
                sleep(retry)
                # After nb_retry fails, break
                raise Exception("Failed to get swift object. " + e)
        print("Successful")
        # Json parsing
        json_parsed = json.loads(
            swift_json[1].decode("utf8").replace("'", '"'))
        print(json.dumps(json_parsed, indent=4, sort_keys=True))
        influxdb_doc = mongodoc_to_influx(json_parsed,
                                          template=metadata_doc["other_data"][
                                              "template"])
        print(json.dumps(influxdb_doc, indent=4, sort_keys=True))
        try:
            integrator.write(bucket=metadata_doc["swift_container"],
                             time=influxdb_doc["time"],
                             measurement=influxdb_doc["measurement"],
                             field_list=influxdb_doc["fields"],
                             tag_list=influxdb_doc["tags"])
        except Exception as e:
            raise e

        return


def not_handled_call(**kwargs):
    raise NotImplementedError(
        "This data type (:" + kwargs["dag_run"].conf["content_type"] +
        ")is not handled by any workflow.")


def not_implemented_json_call(**kwargs):
    raise NotImplementedError(
        "This json structure can't be handled.")


def failed_data_processing(*args, **kwargs):
    print("The data processing was a fail.")
    print(kwargs.keys())
    print(args[0]["execution_date"])
    print(args[0])
    group = args[0]["dag_run"].conf["swift_container"]
    swift_id = str(args[0]["dag_run"].conf["swift_obj_id"])
    mongodb_url = config.mongodb_url
    meta_base = MongoClient(mongodb_url, username=config.mongodb_user, password=config.mongodb_pwd, authSource=config.mongodb_db_auth, connect=False)
    print(meta_base.swift[group].find_one_and_update(
        {
            "swift_object_id": swift_id,
            "swift_container": group
        },
        {
            "$push": {
                "failed_operation": {
                    "execution_date": args[0]["execution_date"],
                    "dag_id": str(args[0]["dag_run"]),
                    "operation_instance": str(args[0]["task_instance"])
                }
            },
            "$set": {
                "last_modified": datetime.datetime.now()
            }
        }
    )
    )


def successful_data_processing(*args, **kwargs):
    print("The data processing was a success.")
    print(kwargs.keys())
    print(args[0]["execution_date"])
    print(args[0])
    group = args[0]["dag_run"].conf["swift_container"]
    swift_id = str(args[0]["dag_run"].conf["swift_obj_id"])
    mongodb_url = config.mongodb_url
    meta_base = MongoClient(mongodb_url, username=config.mongodb_user, password=config.mongodb_pwd, authSource=config.mongodb_db_auth, connect=False)
    print(meta_base.swift[group].find_one_and_update(
        {
            "swift_object_id": swift_id,
            "swift_container": group
        },
        {
            "$push": {
                "successful_operations": {
                    "execution_date": args[0]["execution_date"],
                    "dag_id": str(args[0]["dag_run"]),
                    "operation_instance": str(args[0]["task_instance"])
                }
            },
            "$set": {
                "last_modified": datetime.datetime.now()
            }
        }
    )
    )


# TODO : Create 1 task to get Swift object and use intern communication to share it
def default_image(**kwargs):
    # metadata_doc = kwargs["ti"].xcom_pull(key="metadata_doc")
    swift_container = kwargs["dag_run"].conf["swift_container"]
    swift_id = str(kwargs["dag_run"].conf["swift_obj_id"])

    #Function return swift_object
    swift_object = connection_swift(swift_container, swift_id)
    
    # Récupération du fichier encoder dans l'object swift
    swift_result = swift_object[1]
    processed_data = {}
    # Compare filetype
    if "image/" in swift_object[0]['content-type']:
        process_type = "images"
        processed_data = extract_transform_load_images(
            swift_result, swift_container, swift_id, process_type)
    return processed_data


def default_application_json(**kwargs):
    
    swift_container = kwargs["dag_run"].conf["swift_container"]
    swift_id = str(kwargs["dag_run"].conf["swift_obj_id"])

    #Function return swift_object
    swift_object = connection_swift(swift_container, swift_id)
    # Récupération du fichier encoder dans l'object swift
    swift_result = swift_object[1]
    processed_data = {}
    if "x-object-meta-source" not in swift_object[0]:
        if "application/json" in swift_object[0]['content-type']:
            process_type = "time_series_json"
            # Json parsing
            processed_data = extract_transform_load_time_series_json(
                swift_result, swift_container, swift_id, process_type)
    return processed_data


def default_application_vnd_ms_excel(**kwargs):
    swift_container = kwargs["dag_run"].conf["swift_container"]
    swift_id = str(kwargs["dag_run"].conf["swift_obj_id"])

    #Function return swift_object
    swift_object = connection_swift(swift_container, swift_id)
    
    # Récupération du fichier encoder dans l'object swift
    swift_result = swift_object[1]
    processed_data = {}

    process_type = "time_series_csv"
    # Json parsing
    processed_data = extract_transform_load_time_series_csv(
        swift_result, swift_container, swift_id, process_type)
    return processed_data


def default_application_sql(**kwargs):
    swift_container = kwargs["dag_run"].conf["swift_container"]
    swift_id = str(kwargs["dag_run"].conf["swift_obj_id"])

    #Function return swift_object
    swift_object = connection_swift(swift_container, swift_id)
    
    # Récupération du fichier encoder dans l'object swift
    swift_result = swift_object[1]
    processed_data = {}
    process_type = "sql_dump"
    # Json parsing
    processed_data = extract_transform_load_dump_sql(
        swift_result, swift_container, swift_id, process_type)
    return processed_data


def default_text_plain(**kwargs):
    swift_container = kwargs["dag_run"].conf["swift_container"]
    swift_id = str(kwargs["dag_run"].conf["swift_obj_id"])

    #Function return swift_object
    swift_object = connection_swift(swift_container, swift_id)
    
    # Récupération du fichier encoder dans l'object swift
    swift_result = swift_object[1]
    processed_data = {}
    process_type = "time_series_txt"
    # Text parsing
    processed_data = extract_transform_load_time_series_text(
        swift_result, swift_container, swift_id, process_type)
    return processed_data


def default_zip(**kwargs):
    swift_container = kwargs["dag_run"].conf["swift_container"]
    swift_id = str(kwargs["dag_run"].conf["swift_obj_id"])

    #Function return swift_object
    swift_object = connection_swift(swift_container, swift_id)
    
    # Récupération du fichier encoder dans l'object swift
    swift_result = swift_object[1]
    processed_data = {}

    # Creation of a temp file for stock the data
    fp = tempfile.TemporaryFile()
    fp.write(swift_result)
    fp.seek(0)
    # Using ZipFile package to unzip zip file data
    zip = ZipFile(fp, 'r')
    # Using a for to read each file in the zip file
    for file in zip.filelist:
        # Read file to retrieve the data
        data_file = zip.read(file.filename)
        # Split the filename to retrieve the extension file for the type file
        typef = file.filename.split('.')
        typef = typef.pop()
        # Function return the type file
        type_file = typefile(typef)
        # Compare filetype
        if "image/" in type_file:
            process_type = "images"
            processed_data = extract_transform_load_images(
                data_file, swift_container, swift_id, process_type)
        if "application/json" in type_file:
            process_type = "time_series_json"
            # Json parsing
            processed_data = extract_transform_load_time_series_json(
                data_file, swift_container, swift_id, process_type)
        if "application/vnd.ms-excel" in type_file:
            process_type = "time_series_csv"
            # CSV parsing
            processed_data = extract_transform_load_time_series_csv(
                data_file, swift_container, swift_id, process_type)
        if "application/sql" in type_file:
            process_type = "sql_dump"
            # Json parsing
            processed_data = extract_transform_load_dump_sql(
                swift_result, swift_container, swift_id, process_type)
        if "text/plain" in type_file:
            process_type = "time_series_txt"
            # Text parsing
            processed_data = extract_transform_load_time_series_text(
                swift_result, swift_container, swift_id, process_type)
    return processed_data

def default_sge(**kwargs):
    swift_container = kwargs["dag_run"].conf["swift_container"]
    swift_id = str(kwargs["dag_run"].conf["swift_obj_id"])

    #Function return swift_object
    swift_object = connection_swift(swift_container, swift_id)
    
    # Récupération du fichier encoder dans l'object swift
    swift_result = swift_object[1]
    processed_data = {}
    process_type = "sge_dump"
    # Text parsing
    processed_data = extract_transform_load_sge(
        swift_result, swift_container, swift_id, process_type)
    
    return processed_data


def default_check_type(**kwargs):
    """
    Check data MIME type and return the next task to trigger.
    It depends on MIME type and container.

    :param kwargs: Airflow context
    :return:
    """

    group = kwargs["dag_run"].conf["swift_container"]
    swift_id = str(kwargs["dag_run"].conf["swift_obj_id"])
    #Return data from the swift_object_id in mongodb metadata
    metadata_doc = connection_mongo_metadata(group, swift_id)
    
    content_type = metadata_doc['content_type']
    
    if "image/" in content_type:
        content_type = "image/"
    
    with open(cwd + "/task_list.json", "r") as f:
        task_dict = json.load(f)

    list_projects = config.list_projects
    if group not in list_projects:
        group = "default"

    if content_type in task_dict:
        if group in task_dict[content_type]:
            return task_dict[content_type][group][0]["task_id"]
        else:
            return task_dict[content_type][group][0]["task_id"]
    else:
        if group in task_dict[content_type]:
            return task_dict[content_type][group][0]["task_id"]
        else:
            return task_dict[content_type][group][0]["task_id"]


def workflow_selection(**kwargs):
    container = kwargs["dag_run"].conf["swift_container"]
    swift_id = str(kwargs["dag_run"].conf["swift_obj_id"])
    print(swift_id)
    # WAIT THE OBJECT HAS BEEN INSERTED
    print("kwargs['dag_run'].conf")
    print(kwargs["dag_run"].conf)

    list_projects = config.list_projects
    if container not in list_projects:
        container = "default"

    return container

def mqtt_verify_task(**kwargs):
    container = kwargs["dag_run"].conf["swift_container"]
    swift_id = str(kwargs["dag_run"].conf["swift_obj_id"])

    task = ""
    result = mqtt_verify(container, swift_id)
    if result == True:
        task = "dag_end"
    else:
        task = "data_workflow_selection"

    return task



# import configurations of different services needed :
# IP and port of Swift, MongoDB, etc..
# with open(cwd + "/config.yml", "r") as config:
#     y = yaml.safe_load(config)
# globals().update(y)


def custom_user_workflow(**kwargs):
    metadata_doc = kwargs["ti"].xcom_pull(key="metadata_doc")
    return metadata_doc["swift_container"]


def neocampus_branching(**kwargs):
    swift_id = str(kwargs["dag_run"].conf["swift_obj_id"])
    swift_container = str(kwargs["dag_run"].conf["swift_container"])
    #Return data from the swift_object_id in mongodb metadata
    metadata_doc = connection_mongo_metadata(swift_container, swift_id)
    
    content_type = metadata_doc['content_type']

    # TODO : 14/10/2020 REFACTOR DICT_TASK
    type_to_task = {"bson": "neocampus_bson_get"}
    
    type_to_task["content_type"] = content_type
    return type_to_task


def neocampus_bson(**kwargs):
    pass

callable_dict = {"PythonOperator": PythonOperator,
                 "DummyOperator": DummyOperator,
                 "BranchPythonOperator": BranchPythonOperator
                 }


# TODO : recursive funct to create the pipeline (for n sublevel in dict)


# def neocampus_get_swift_object(**kwargs):
#     # TODO : 13/10/2020 DIRECT READ FILE IF LOOPBACK DEVICE ARE REMOVED (if swift can directly write on storage servers)
#     # metadata_doc = kwargs["ti"].xcom_pull(key="metadata_doc")
#     swift_container = kwargs["dag_run"].conf["swift_container"]
#     swift_id = str(kwargs["dag_run"].conf["swift_obj_id"])
#
#     print("kwargs['dag_run'].conf")
#     print(kwargs["dag_run"].conf)
#
#     url = config.url_swift
#     user = config.user_swift
#     key = config.key_swift
#     headers = {'X-Storage-User': user,
#                'X-Storage-Pass': key
#                }
#
#     token_response = urlopen(Request(url, headers=headers)).getheaders()
#
#     opener = urllib.request.build_opener()
#     opener.addheaders = []
#
#     for i in token_response:
#         if i[0] == "X-Auth-Token":
#             opener.addheaders.append(i)
#         if i[0] == "X-Storage-Url":
#             url = i
#     print(url[1])
#     swift_container = str(kwargs["dag_run"].conf["swift_container"])
#     #Return data from the swift_object_id in mongodb metadata
#     metadata_doc = connection_mongo_metadata(swift_container, swift_id)
#
#     path = config.airflow_tmp + metadata_doc["original_object_name"]
#
#     # urllib.request.install_opener(opener)
#     # urllib.request.urlretrieve(url[1] + "/" + swift_container + "/" + swift_id, path)
#     #
#     # print(os.path.dirname(os.path.abspath(__file__)))
#
#     print(kwargs["dag_run"].dag_id)


# def neocampus_mongoimport(**kwargs):
#     swift_container = kwargs["dag_run"].conf["swift_container"]
#     swift_id = str(kwargs["dag_run"].conf["swift_obj_id"])
#     metadata_doc = connection_mongo_metadata(swift_container, swift_id)
#
#     file_name = kwargs["dag_run"].dag_id
#     # TODO : 13/10/2020 FIND A SOLUTION TO CHOSE DATABASE AND COLLECTION
#     print("ssh -i /home/airflow/.ssh/airflow airflow@co2-dl-bd 'mongorestore -d " +
#           swift_container + " -c " +
#           metadata_doc["original_object_name"]
#           + config.airflow_tmp + metadata_doc["original_object_name"] + "'")
#     os.system("ssh -i /home/airflow/.ssh/airflow airflow@co2-dl-bd 'mongorestore -d " +
#               swift_container + " -c " +
#               metadata_doc["original_object_name"] + " " +
#               config.airflow_tmp + metadata_doc["original_object_name"] + "'")


def construct_operator(**kwargs):
    # TODO : Raise error
    # TODO : Handle more parameters
    # TODO : Handle start_date
    try:
        if kwargs["operator"] is "PythonOperator":
            return PythonOperator(task_id=kwargs["task_id"],
                                  python_callable=callable_dict[kwargs["python_callable"]],
                                  on_failure_callback=failed_data_processing,
                                  on_success_callback=successful_data_processing
                                  )
    except Exception as e:
        pass


'''
Base operator : Dummy operators
'''

run_this_first = DummyOperator(
    task_id='getting_data',
    dag=dag,
)

join = DummyOperator(
    task_id='dag_end',
    trigger_rule='none_failed',
    dag=dag,
)

''' 
Default operator 
'''

mqtt_verify_branch = BranchPythonOperator(
    task_id='mqtt_verify',
    python_callable=mqtt_verify_task,
    dag=dag
)

branch_op = BranchPythonOperator(
    task_id='data_workflow_selection',
    python_callable=workflow_selection,
    dag=dag
)
default = BranchPythonOperator(
    task_id='default',
    python_callable=default_check_type,
    dag=dag)

neOCampus = BranchPythonOperator(
    task_id='neOCampus',
    python_callable=default_check_type,
    dag=dag)

autOCampus = BranchPythonOperator(
    task_id='autOCampus',
    python_callable=default_check_type,
    dag=dag)

Villagil = BranchPythonOperator(
    task_id='Villagil',
    python_callable=default_check_type,
    dag=dag)

eCOnect = BranchPythonOperator(
    task_id='eCOnect',
    python_callable=default_check_type,
    dag=dag)

'''
Custom operator
'''
custom = BranchPythonOperator(
    task_id='custom',
    # provide_context=True,
    python_callable=custom_user_workflow,
    dag=dag)
# neocampus = BranchPythonOperator(
#     task_id='neocampus',
#     # provide_context=True,
#     python_callable=neocampus_branching,
#     dag=dag
# )
# neocampus_bson_get = PythonOperator(
#     task_id='neocampus_bson_get',
#     python_callable=neocampus_get_swift_object,
#     # provide_context=True,
#     dag=dag,
# )
#
# neocampus_bson_mongorestore = PythonOperator(
#     task_id='neocampus_bson_mongorestore',
#     python_callable=neocampus_mongoimport,
#     # bash_command='ls /datalake  && cp /datalake/co2-dl-bd',
#     # provide_context=True,
#     dag=dag,
# )
'''
===============================================
'''
with open(cwd + "/task_list.json", "r") as f:
    task_dict = json.load(f)

callable_dict = {"content_neo4j_node_creation": content_neo4j_node_creation,
                 "from_mongodb_to_influx": from_mongodb_to_influx,
                 "not_handled_call": not_handled_call,
                 "not_implemented_json_call": not_implemented_json_call,
                 "default_check_type": default_check_type,
                 "failed_data_processing": failed_data_processing,
                 "successful_data_processing": successful_data_processing,
                 "construct_operator": construct_operator,
                 "neocampus_bson": neocampus_bson,
                 "neocampus_branching": neocampus_branching,
                 "custom_user_workflow": custom_user_workflow,
                 "workflow_selection": workflow_selection,
                 "default_image": default_image,
                 "default_application_json": default_application_json,
                 "default_application_vnd_ms_excel": default_application_vnd_ms_excel,
                 "default_application_sql": default_application_sql,
                 "default_text_plain": default_text_plain,
                 "default_zip": default_zip,
                 "default_sge": default_sge,
                 "PythonOperator": PythonOperator,
                 "DummyOperator": DummyOperator,
                 "BranchPythonOperator": BranchPythonOperator
                 }
#"neocampus_get_swift_object": neocampus_get_swift_object,
custom_pipeline = []
default_pipeline = []
neOCampus_pipeline = []
autOCampus_pipeline = []
Villagil_pipeline = []
eCOnect_pipeline = []
for data_type in task_dict:

    for owner_group in task_dict[data_type]:
        custom_sub_pipe = []
        default_sub_pipe = []
        neOCampus_sub_pipe = []
        autOCampus_sub_pipe = []
        Villagil_sub_pipe = []
        eCOnect_sub_pipe = []
        for task in task_dict[data_type][owner_group]:
            # raise(Exception(task["operator"]))
            if task["operator"] == "PythonOperator":
                if owner_group == "default":
                    default_sub_pipe.append(PythonOperator(task_id=task["task_id"],
                                                           python_callable=callable_dict[task["python_callable"]],
                                                           on_failure_callback=failed_data_processing,
                                                           on_success_callback=successful_data_processing,
                                                           start_date=days_ago(
                                                               0)
                                                           ))
                elif owner_group == "neOCampus":
                    neOCampus_sub_pipe.append(PythonOperator(task_id=task["task_id"],
                                                           python_callable=callable_dict[task["python_callable"]],
                                                           on_failure_callback=failed_data_processing,
                                                           on_success_callback=successful_data_processing,
                                                           start_date=days_ago(
                                                               0)
                                                           ))
                elif owner_group == "autOCampus":
                    autOCampus_sub_pipe.append(PythonOperator(task_id=task["task_id"],
                                                           python_callable=callable_dict[task["python_callable"]],
                                                           on_failure_callback=failed_data_processing,
                                                           on_success_callback=successful_data_processing,
                                                           start_date=days_ago(
                                                               0)
                                                           ))
                elif owner_group == "Villagil":
                    Villagil_sub_pipe.append(PythonOperator(task_id=task["task_id"],
                                                           python_callable=callable_dict[task["python_callable"]],
                                                           on_failure_callback=failed_data_processing,
                                                           on_success_callback=successful_data_processing,
                                                           start_date=days_ago(
                                                               0)
                                                           ))
                elif owner_group == "eCOnect":
                    eCOnect_sub_pipe.append(PythonOperator(task_id=task["task_id"],
                                                           python_callable=callable_dict[task["python_callable"]],
                                                           on_failure_callback=failed_data_processing,
                                                           on_success_callback=successful_data_processing,
                                                           start_date=days_ago(
                                                               0)
                                                           ))
                else:
                    custom_sub_pipe.append(PythonOperator(task_id=task["task_id"],
                                                          python_callable=callable_dict[task["python_callable"]],
                                                          on_failure_callback=failed_data_processing,
                                                          on_success_callback=successful_data_processing,
                                                          start_date=days_ago(
                                                              0)
                                                          ))
        custom_pipeline.append([*custom_sub_pipe, ])
        default_pipeline.append([*default_sub_pipe, ])
        neOCampus_pipeline.append([*neOCampus_sub_pipe, ])
        autOCampus_pipeline.append([*autOCampus_sub_pipe, ])
        Villagil_pipeline.append([*Villagil_sub_pipe, ])
        eCOnect_pipeline.append([*eCOnect_sub_pipe, ])

for default_task_list in default_pipeline:
    chain(default, *default_task_list, join)

for neOCampus_task_list in neOCampus_pipeline:
    chain(neOCampus, *neOCampus_task_list, join)
for autOCampus_task_list in autOCampus_pipeline:
    chain(autOCampus, *autOCampus_task_list, join)
for Villagil_task_list in Villagil_pipeline:
    chain(Villagil, *Villagil_task_list, join)
for eCOnect_task_list in eCOnect_pipeline:
    chain(eCOnect, *eCOnect_task_list, join)

for custom_task_list in custom_pipeline:
    if len(custom_task_list) != 0:
        chain(custom, *custom_task_list, join)

# Airflow user / data_processing password
run_this_first >> mqtt_verify_branch >> [branch_op, join]
branch_op >> [default, custom, neOCampus, autOCampus, Villagil, eCOnect]

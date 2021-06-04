from datetime import timedelta, datetime
from textwrap import dedent
from pymongo import MongoClient
import swiftclient.service
from swiftclient.service import SwiftService
import json
from csv import DictReader

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG

# Operators; we need this to operate!
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'sla_miss_callback': yet_another_function,
    # 'trigger_rule': 'all_success'
}

def get_swift_object(*args, **kwargs):
    swift_container = kwargs["params"]["swift_container"]
    swift_id = kwargs["params"]["swift_obj_id"]

    mongodb_url = "mongodb://IP_ADDRESS:PORT"
    container_name = "resultat-traitement"

    # Mongo
    client = MongoClient(mongodb_url, connect=False)
    db = client.data_conso
    coll = db[container_name]

    # Stockage des données traitées
    db_process = client.data_historique
    col_process_data = db_process["historique"]

    # Openstack Swift
    ip_address = "IP_ADDRESS"
    address_name = "ADDRESS_NAME"
    authurl = "http://"+ip_address+":8080/auth/v1.0"
    user = 'test:tester'
    key = 'testing'
    conn = swiftclient.Connection(
        user=user, 
        key=key,
        authurl=authurl
    )

    swift_object = conn.get_object(swift_container, swift_id)
    print('----------- OBJET SWIFT -------------')
    print(swift_object)

    content_type = swift_object[0]['content-type']
    swift_result = swift_object[1]

    process_type = "other"
    processed_data = {}

    # TODO : 2 other functions to handle different filetype
    # Compare filetype
    if "image/" in content_type :
        process_type = "images"
        processed_data = extract_transform_load_images(swift_result, swift_container, swift_id, coll, process_type)

    if "application/json" in content_type:
        process_type = "time_series_json"
        # Json parsing
        processed_data = extract_transform_load_time_series_json(swift_result, swift_container, swift_id, coll, process_type)

    if "application/vnd.ms-excel" in content_type:
        process_type = "time_series_csv"
        # Json parsing
        processed_data = extract_transform_load_time_series_csv(swift_result, swift_container, swift_id, coll, process_type)

    # Handled data
    col_process_data.insert_one(processed_data)

def history_data(
    process_type, 
    swift_container, 
    swift_object_id, 
    task_type,
    mongo_column,
    old_data,
    new_data
):
    meta_data = {} 

    meta_data["creation_date"] = datetime.now()
    meta_data['swift_container'] = swift_container
    meta_data['swift_id'] = swift_object_id
    meta_data['process_type'] = process_type
    meta_data['task_type'] = task_type
    meta_data['old_data'] = old_data
    meta_data['new_data'] = new_data

    # Metadata
    mongo_column.insert_one(meta_data)

def extract_transform_load_time_series_csv(json_object, swift_container, swift_id, coll, process_type):
    result = []

    print(json_object)
    json_object = json_object.decode("utf8").replace("'", '"')
    lines = json_object.split('\\r\\n') # "\r\n" if needed

    for line in lines:
        if line != "": # add other needed checks to skip titles
            cols = line.split(",")

            result_row = {"_id": cols[1], "measuretime" : cols[2], "topic" : cols[3]}

            result.append(result_row)
            history_data(process_type, swift_container, swift_id, "filter_columns", coll, cols, result_row)

    return {"result": result}

def extract_transform_load_time_series_json(json_object, swift_container, swift_id, coll, process_type):
    # TODO : process related to JSON files
    #history_data(process_type, swift_container, swift_id, "parsing_date", coll, row, result_row)
    result = json.loads(json_object)
    x = {"test": "New JSON object"}
    result.append(x)
    return result

def extract_transform_load_images(json_object, swift_container, swift_id, coll, process_type):
    # TODO : process related to images
    #history_data(process_type, swift_container, swift_id, "parsing_date", coll, row, result_row)
    return json_object

# HANDLE CSV Time series
dag = DAG(
    'data-processing-upload',
    default_args=default_args,
    description='Airflow processing related to uploads',
    schedule_interval=None,
    start_date=days_ago(2),
    tags=['data-processing-upload'],
)

task_get_swift_object = PythonOperator(
    task_id='get_swift_object',
    python_callable=get_swift_object,
    provide_context=True,
    dag=dag,
)

task_get_swift_object
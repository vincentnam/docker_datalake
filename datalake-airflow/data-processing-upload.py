from datetime import timedelta, datetime
from textwrap import dedent
from pymongo import MongoClient
import swiftclient.service
from swiftclient.service import SwiftService
import json

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
    swift_id = kwargs["params"]["swift_id"]

    mongodb_url = "mongodb://10.200.156.254:27017"
    container_name = "handle-data"

    # Mongo
    client = MongoClient(mongodb_url, connect=False)
    db = client.airflow
    coll = db[container_name]

    # Openstack Swift
    ip_address = "10.200.156.252"
    address_name = "neocampus-datalake-swift.dev.modiscloud.net"
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
    swift_result = swift_object[1].decode("utf8").replace("'", '"')

    handle_type = "other"

    # TODO : 2 other functions to handle different filetype
    # Compare filetype
    if "image/" in content_type :
        handle_type = "images"

    if "application/json" in content_type:
        handle_type = "time_series_json"
        # Json parsing
        json_parsed = json.loads(swift_result)

    if "application/vnd.ms-excel" in content_type:
        handle_type = "time_series_csv"
        # Json parsing
        json_parsed = json.loads(swift_result)

    #print(json.dumps(json_parsed, indent=4, sort_keys=True))
    #handled_data = extract_transform_load_time_series(json.dumps(json_parsed, indent=4, sort_keys=True))

    meta_data = {}  

    # TODO : handled data to save in MongoDB also ?
    meta_data["creation_date"] = datetime.now()
    meta_data["last_modified"] = datetime.now()
    meta_data['swift_container'] = swift_container
    meta_data['swift_id'] = swift_id
    meta_data['handle_type'] = handle_type

    coll.insert_one(meta_data)

'''def extract_transform_load_time_series_csv(json_object):
    result = json.loads(json_object)
    x = {"test": "New JSON object"}
    result.append(x)
    return result'''

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
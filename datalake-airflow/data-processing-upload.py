import pandas as pd
import sys
from datetime import timedelta, datetime
from textwrap import dedent
from pymongo import MongoClient
import swiftclient.service
from swiftclient.service import SwiftService
import json
from csv import DictReader

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG

# Operators; we need this to operate!
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

if sys.version_info[0] < 3: 
    from StringIO import StringIO
else:
    from io import StringIO
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
}

def get_swift_object(*args, **kwargs):
    swift_container = kwargs["params"]["swift_container"]
    swift_id = kwargs["params"]["swift_obj_id"]

    mongodb_url = "mongodb://10.200.156.254:27017"
    container_name = "traitement_historique"

    # Mongo
    client = MongoClient(mongodb_url, connect=False)
    db = client.data_historique
    coll = db[container_name]

    # Stockage des données traitées
    # db_process = client.data_historique
    # col_process_data = db_process["historique"]

    # Openstack Swift
    ip_address = "IP_ADDRESS"
    address_name = "ADDRESS_NAME"
    authurl = "http://10.200.156.252:8080/auth/v1.0"
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
    
    # processed = {
    #     "swift_id": swift_id,
    #     "processed_data": processed_data
    #     }
    # print(processed)
    # col_process_data.insert_one(processed)
    return processed_data

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

def extract_transform_load_time_series_csv(swift_result, swift_container, swift_id, coll, process_type):
    result = []
    # List fields timestamp
    timestamp_fields_list = [
        "timestamp",
        "temps",
        "date",
        "measuretime"
    ]
    # List fields value
    value_fields_list = [
        "value",
        "valeur",
        "reading",
        "payload.value"
    ]
    # Data proccessing swift_result of bytes to dataframe
    s=str(swift_result,'utf-8').replace("\\n", "\n")
    data = StringIO()
    data.write(s)
    data.seek(0)
    df = pd.read_csv(data, sep=",")
    columns = df.columns
    # swift_data = {"swift_result": swift_result}
    # history_df = {"df": df}
    # history_data(process_type, swift_container, swift_id, "data_processing_swift_result_bytes_to_dataframe", coll, swift_data, history_df)
    
    position_timestamp, position_value, position_topic, position_payload_value_units = get_positions(
        columns, 
        timestamp_fields_list, 
        value_fields_list
    )
    
    # You can generate a Token from the "Tokens Tab" in the UI
    token = "eevr5kWlgdgB1OuiKLKz9lIYD-2N9x1LG7nHDIHHa0cO0XvBJScwnunC3c6xrEvKXXCLbK1nXDsLtqWdXhDriw=="
    org = "modis"
    bucket = "test"

    client = InfluxDBClient(url="http://neocampus-datalake-mongodb.dev.modiscloud.net:8086", token=token, debug=True)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    
    for index, line in df.iterrows():
        # Parsing date timestamp to date milliseconds
        date = line[position_timestamp].replace('t', " ")
        date = date.replace('z', "")
        date = date.replace('.000', "")
        date = date.replace('-', "/")
        datetime_object = datetime.strptime(date, '%Y/%m/%d %H:%M:%S')
        date_milliseconds = int(round(datetime_object.timestamp() * 1000000000))
        history_data(process_type, swift_container, swift_id, "parsing_date_timestamp_to_date_milliseconds", coll, line[position_timestamp], date_milliseconds)
        data = []
        values = {}
        tags = {}
        # Parsing and config values
        if "energy" not in line[position_topic]:
            val = 0
            val = float(line[position_value])
            old_values = values
            unit = line[position_payload_value_units].replace(".", "_")
            values[unit] = val
            history_data(process_type, swift_container, swift_id, "config_values", coll, old_values, values)
        else:
            list_of_tuples = list(zip(line[position_payload_value_units].strip('][').split(','), line[position_value].strip('][').split(',')))
            old_values = values
            for l in list_of_tuples:
                unit, v = l
                unit = unit.replace(".", "_")
                values[unit] = float(v)
            history_data(process_type, swift_container, swift_id, "config_values", coll, old_values, values)
        old_tags = tags
        # Parsing and config tags
        for key, value in enumerate(columns):
            if position_payload_value_units != value and position_value != value:
                val = value.replace(".", "_")
                if line[value] == "":
                    tags[val] = ""
                else:
                    tags[val] = str(line[value])
        history_data(process_type, swift_container, swift_id, "config_tags", coll, old_tags, tags)
        # Create variable for upload in influxdb
        data.append(
            {
                "measurement": line[position_topic],
                "tags": tags,
                "fields": values,
                "time": date_milliseconds
            }
        )
        result.append(data)
        data = {"data", data}
        line = {"line": line}
        #history_data(process_type, swift_container, swift_id, "data_proccessing_for_upload_in_influxdb", coll, line, data)
        # Upload in influxdb
        write_api.write(bucket, org, data, protocol='json') 
    return result

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


def get_positions(columns, timestamp_fields_list, value_fields_list):
    # Search position of filds timestamp, value, topic and value_units
    position_timestamp = ""
    position_value = ""
    position_topic = ""
    position_payload_value_units = ""
    for key, value in enumerate(columns):
        if value in timestamp_fields_list :
            position_timestamp = value
        if value in value_fields_list :
            position_value = value
        if value == "topic":
            position_topic = value
        if value == "payload.value_units":
            position_payload_value_units = value

    return position_timestamp, position_value, position_topic, position_payload_value_units

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
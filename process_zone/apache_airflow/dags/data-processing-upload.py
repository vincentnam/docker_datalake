import sys
from datetime import timedelta
import datetime
from textwrap import dedent
from pymongo import MongoClient
import swiftclient.service
from swiftclient.service import SwiftService
import config
from services import extract_transform_load_time_series_csv
from services import extract_transform_load_time_series_json
from services import extract_transform_load_images
from services import typefile
import tempfile
import base64
from zipfile import ZipFile


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
}

def get_swift_object(*args, **kwargs):
    swift_container = kwargs["params"]["swift_container"]
    swift_id = kwargs["params"]["swift_obj_id"]

    # Stockage des données traitées
    # db_process = client.data_historique
    # col_process_data = db_process["historique"]

    # Openstack Swift
    ip_address = config.ip_address_swift
    address_name = config.address_name_swift
    authurl = "http://" + config.url_swift + "/auth/v1.0"
    user = config.user_swift
    key = config.key_swift
    # Connction à Swift
    conn = swiftclient.Connection(
        user=user, 
        key=key,
        authurl=authurl
    )
    # Récupération de l'object Swift
    swift_object = conn.get_object(swift_container, swift_id)
    print('----------- OBJET SWIFT -------------')
    print(swift_object)
    # Content type récupéré de l'object swift
    content_type = swift_object[0]['content-type']
    # Récupération du fichier encoder dans l'object swift
    swift_result = swift_object[1]

    process_type = "other"
    processed_data = {}
    
    if "application/x-zip-compressed" in content_type or "application/x-gzip" in content_type :
        #Creation of a temp file for stock the data
        fp = tempfile.TemporaryFile()
        fp.write(swift_result)
        fp.seek(0)
        #Using ZipFile package to unzip zip file data
        zip = ZipFile(fp, 'r')
        #Using a for to read each file in the zip file
        for file in zip.filelist:
            #Read file to retrieve the data
            data_file = zip.read(file.filename)
            #Split the filename to retrieve the extension file for the type file
            typef = file.filename.split('.')
            typef = typef[1]
            #Function return the type file
            type_file = typefile(typef)
            # Compare filetype
            if "image/" in type_file :
                process_type = "images"
                processed_data = extract_transform_load_images(data_file, swift_container, swift_id, process_type)
            if "application/json" in type_file:
                process_type = "time_series_json"
                # Json parsing
                processed_data = extract_transform_load_time_series_json(data_file, swift_container, swift_id, process_type)
            if "application/vnd.ms-excel" in type_file:
                process_type = "time_series_csv"
                # Json parsing
                processed_data = extract_transform_load_time_series_csv(data_file, swift_container, swift_id, process_type)
                
    # Compare filetype
    if "image/" in content_type :
        process_type = "images"
        processed_data = extract_transform_load_images(swift_result, swift_container, swift_id, process_type)
    if "application/json" in content_type:
        process_type = "time_series_json"
        # Json parsing
        processed_data = extract_transform_load_time_series_json(swift_result)

    if "application/vnd.ms-excel" in content_type:
        process_type = "time_series_csv"
        # Json parsing
        processed_data = extract_transform_load_time_series_csv(swift_result, swift_container, swift_id, process_type)

    # Handled data
    return processed_data

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
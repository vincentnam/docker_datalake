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


def on_failure_callback(context):
    print(context)
    print(context.get("dag_run"))
    print(context["ti"])
    conf = context.get("dag_run").conf
    meta_base = MongoClient(
        "mongodb://" + globals()["META_MONGO_IP"] + ":" + globals()[
            "MONGO_PORT"] + "/"
    )
    print(meta_base.swift[conf["swift_id"]].find_one_and_update({
        "swift_object_id": conf["swift_id"]}, {
        '$push': {"failed_operations":str(context.get("dag_run"))} ,
        '$set':{"last_modified" : datetime.datetime.now().isoformat()}
    }))

def on_success_callback(context):
    print(context)
    print(context.get("dag_run"))
    print(context.get("dag_run").conf)
    print(context["ti"])
    conf = context.get("dag_run").conf
    meta_base = MongoClient(
        "mongodb://" + globals()["META_MONGO_IP"] + ":" + globals()[
            "MONGO_PORT"] + "/"
    )
    print(meta_base.swift[conf["swift_id"]].find_one_and_update({
        "swift_object_id": conf["swift_id"]}, {
        '$push': {"successful_operations":str(context.get("dag_run"))} ,
        '$set':{"last_modified" : datetime.datetime.now().isoformat()}
    }))


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

    from influxdb_client import InfluxDBClient, Point, WritePrecision
    from influxdb_client.client.write_api import WriteOptions
    import rx
    from rx import operators as ops
    from csv import DictReader

    def parse_row(row):

        list_field = ["pmer", "tend", "cod_tend", "dd", "ff", "t", "td", "u", "vv", "ww", "w1", "w2", "n", "nbas",
                      "hbas", "cl", "cm", "ch",
                      "pres", "niv_bar", "geop", "tend24", "tn12", "tn24", "tx12", "tx24", "tminsol", "sw", "tw",
                      "raf10", "rafper", "per"
            , "etat_sol", "ht_neige", "ssfrai", "perssfrai", "rr1", "rr3", "rr6", "rr12", "rr24", "phenspe1",
                      "phenspe2", "phenspe3",
                      "phenspe4", "nnuage1", "ctype1", "hnuage1", "nnuage2", "ctype2", "hnuage2", "nnuage3", "ctype3",
                      "hnuage3", "nnuage4",
                      "ctype4", "hnuage4"]

        point = Point("MeteoFrance_data") \
            .tag("station", row["numer_sta"]) \
            .time(datetime.datetime.strptime(str(row['date']), "%Y%m%d%H%M%S"), write_precision=WritePrecision.S)
        for field in list_field:
            if row[field] != "mq":
                point.field(field, float(row[field]))
        return point
    token = "c5bgd7j6fJ-YpWiuM8EAQHTlIJmKphEaC72iCzFgzXRtldJYKdDDjvHkUz0cfDEVejDCuU9fnpWGzoS56vupZA=="
    org="test"
    bucket="DataNoos"

    data = rx \
        .from_iterable(DictReader(open("/datalake/airflow/airflow_tmp/"+metadata_doc["original_object_name"], 'r'))) \
        .pipe(ops.map(lambda row: parse_row(row)))

    client = InfluxDBClient(url="http://141.115.103.33:8086", token=token, org=org, debug=True)

    """
    Create client that writes data in batches with 50_000 items.
    """
    write_api = client.write_api(write_options=WriteOptions(batch_size=1000, flush_interval=100))

    """
    Write data into InfluxDB
    """
    write_api.write(bucket=bucket, record=data)
    write_api.__del__()



DataNoos = BranchPythonOperator(
    task_id='DataNoos',
    provide_context=True,
    python_callable=datanoos_branching,
    dag=dag
)
datanoos_ba_huy_csv_ts= PythonOperator(
    task_id='datanoos_csv_ts',
    python_callable=datanoos_ba_huy_csv_ts,
    provide_context=True,
    dag=dag,
    on_failure_callback=on_failure_callback,
    on_success_callback=on_success_callback
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



def IDEAS_use_case_branching(**kwargs):
    metadata_doc = kwargs["ti"].xcom_pull(key="metadata_doc")
    #TODO : 14/10/2020 REFACTOR DICT_TASK
    type_to_task = {"batch": "IDEAS_batch", "stream": "IDEAS_stream"}
    return type_to_task[metadata_doc["other_data"]["flow_type"]]


IDEAS_use_case = BranchPythonOperator(
    task_id='IDEAS_use_case',
    provide_context=True,
    python_callable=IDEAS_use_case_branching,
    dag=dag
)


def IDEAS_batch(**kwargs):
    metadata_doc = kwargs["ti"].xcom_pull(key="metadata_doc")
    # TODO : 14/10/2020 REFACTOR DICT_TASK
    type_to_task = {"application/csv": "IDEAS_csv_ts"}

    return type_to_task[metadata_doc["content_type"]]

IDEAS_batch = PythonOperator(
    task_id='IDEAS_batch',
    python_callable=IDEAS_batch,
    provide_context=True,
    dag=dag,
)


def IDEAS_insert_influx(**kwargs):

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

    from influxdb_client import InfluxDBClient, Point, WritePrecision
    from influxdb_client.client.write_api import WriteOptions
    import rx
    from rx import operators as ops
    from csv import DictReader

    def parse_row(row):

        list_field = ["pmer", "tend", "cod_tend", "dd", "ff", "t", "td", "u", "vv", "ww", "w1", "w2", "n", "nbas",
                      "hbas", "cl", "cm", "ch",
                      "pres", "niv_bar", "geop", "tend24", "tn12", "tn24", "tx12", "tx24", "tminsol", "sw", "tw",
                      "raf10", "rafper", "per"
            , "etat_sol", "ht_neige", "ssfrai", "perssfrai", "rr1", "rr3", "rr6", "rr12", "rr24", "phenspe1",
                      "phenspe2", "phenspe3",
                      "phenspe4", "nnuage1", "ctype1", "hnuage1", "nnuage2", "ctype2", "hnuage2", "nnuage3", "ctype3",
                      "hnuage3", "nnuage4",
                      "ctype4", "hnuage4"]

        point = Point("MeteoFrance_data") \
            .tag("station", row["numer_sta"]) \
            .time(datetime.datetime.strptime(str(row['date']), "%Y%m%d%H%M%S"), write_precision=WritePrecision.S)
        for field in list_field:
            if row[field] != "mq":
                point.field(field, float(row[field]))
        return point
    token = "c5bgd7j6fJ-YpWiuM8EAQHTlIJmKphEaC72iCzFgzXRtldJYKdDDjvHkUz0cfDEVejDCuU9fnpWGzoS56vupZA=="
    org="IDEAS"
    bucket="IDEAS_batch"

    data = rx \
        .from_iterable(DictReader(open("/datalake/airflow/airflow_tmp/"+metadata_doc["original_object_name"], 'r'))) \
        .pipe(ops.map(lambda row: parse_row(row)))

    client = InfluxDBClient(url="http://141.115.103.33:8086", token=token, org=org, debug=True)

    """
    Create client that writes data in batches with 50_000 items.
    """
    write_api = client.write_api(write_options=WriteOptions(batch_size=1000, flush_interval=100))

    """
    Write data into InfluxDB
    """
    write_api.write(bucket=bucket, record=data)
    write_api.__del__()


IDEAS_insert_csv_to_ts= PythonOperator(
    task_id='IDEAS_insert_csv_in_time-serie',
    python_callable=IDEAS_insert_influx,
    provide_context=True,
    dag=dag,
    on_failure_callback=on_failure_callback,
    on_success_callback=on_success_callback
)







def IDEAS_stream(**kwargs):
    metadata_doc = kwargs["ti"].xcom_pull(key="metadata_doc")
    # TODO : 14/10/2020 REFACTOR DICT_TASK
    type_to_task = {"application/json": "IDEAS_sensors_json"}

    return type_to_task[metadata_doc["content_type"]]



IDEAS_stream = PythonOperator(
    task_id='IDEAS_stream',
    python_callable=IDEAS_stream,
    provide_context=True,
    dag=dag,
)

def IDEAS_sensors_json_ts(**kwargs):

    from datetime import datetime
    date = datetime.utcnow()

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
    import ast
    urllib.request.install_opener(opener)
    # TODO : 13/10/2020 MAKE AIRFLOW_TMP AS ENV VAR
    request = urllib.request.urlopen(url[1] + "/"+metadata_doc["swift_container"]+"/"+metadata_doc["swift_object_id"])
    print(request)
    data = request.read()
    print(data)
    dict_str = data.decode("UTF-8")
    data_dict = ast.literal_eval(dict_str)
    print(data_dict)

    value = data_dict.pop("value")
    value_unit = data_dict.pop("value_units")
    data_dict_key_list = list(data_dict.keys())


    from influxdb_client import InfluxDBClient, Point, WritePrecision
    from influxdb_client.client.write_api import SYNCHRONOUS

    # You can generate a Token from the "Tokens Tab" in the UI
    token = "ZaPmyJYZa8HjFQZkOmT-ybhli8UZ-KloUD93QngF1CMlwZjFZmgw6sJAZzAZgKkgzqJG12_Sq8IqVr_JOeW63g=="
    org = "IDEAS"
    bucket = "IDEAS_stream"

    client = InfluxDBClient(url="http://141.115.103.33:8086", token=token)



    write_api = client.write_api(write_options=SYNCHRONOUS)

    if isinstance(type(value),list):
        assert(len(value) == len(value_unit)), "Malformed input data : Value list has not the same length than value_units"

        for val, ind in enumerate(value):

            point = Point(value_unit[ind]) \
                .field("value", val) \
                .time(date, WritePrecision.NS)
            for key in data_dict_key_list:
                point.tag(key, data_dict[key])
            write_api.write(bucket, org, point)
    else:
        point = Point(value_unit) \
            .field("value", value) \
            .time(date, WritePrecision.NS)
        for key in data_dict_key_list:
            point.tag(key, data_dict[key])
        write_api.write(bucket, org, point)

    # from influxdb_client import InfluxDBClient
    # from influxdb_client.client.write_api import WriteOptions
    # from datetime import datetime
    #
    # value = data_dict.pop("value")
    # value_unit = data_dict.pop("value_units")
    # data_dict_key = list(data_dict.keys())
    #
    # token = "_ZENYvIw_Kiw6CsFCDCcchj-IcZijU9K21WD31DKfsjQVwBU-W3mPGqSM-RLTa7PPru5Piy9TZK7wn7ykp8thw=="
    # org="IDEAS"
    # bucket= "IDEAS_stream"
    # from influxdb_client import InfluxDBClient, Point, WritePrecision
    #
    #
    # client = InfluxDBClient(url="http://141.115.103.33:8086", token=token, org=org, debug=True)
    # point = Point(value_unit).field("value", value)
    # for key,value in [(key, data_dict[key]) for key in data_dict_key]:
    #     point.tag(key, value)
    #
    #
    # """
    # Create client that writes data in batches with 50_000 items.
    # """
    # write_api = client.write_api(write_options=WriteOptions(batch_size=1, flush_interval=1))
    # write_api.write(bucket, org, point)
    #
    # """
    # Write data into InfluxDB
    # """

    write_api.__del__()



IDEAS_sensors_insert = PythonOperator(
    task_id='IDEAS_insert_influxdb',
    python_callable=IDEAS_sensors_json_ts,
    provide_context=True,
    dag=dag,
)


# Airflow user / data_processing password
branch_op >> [default, custom]
default >> [db_dump, data]

data >> [json, csv, png] >> join
db_dump >> [mongo_db, SQL] >> join

custom >> [neocampus, DataNoos, IDEAS_use_case]
neocampus >> [ neocampus_bson_get]
neocampus_bson_get >> neocampus_bson_mongorestore >> join
DataNoos >> [datanoos_ba_huy_csv_ts, datanoos_zip]
datanoos_ba_huy_csv_ts >> datanoos_insert_influxdb >> join
datanoos_zip >> join
IDEAS_use_case >> [IDEAS_batch, IDEAS_stream]
IDEAS_batch >> [IDEAS_insert_csv_to_ts] >> join
IDEAS_stream >> [IDEAS_sensors_insert] >> join

# Custom branching : based on metadata_doc["swift_container"]


# To add a pipeline :
# Custom : Add a branch in custom flow -> based on swift_container
# Ideas_use_case : create 2 path : datanoos csv
#                                   Neocampus json
#

# Other_type = {
# flow_type : "stream" ou "batch"


# record is missing label windowPeriod
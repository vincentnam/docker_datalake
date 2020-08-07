# The DAG object; we'll need this to instantiate a DAG
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

import yaml
# import configurations of different services needed :
# IP and port of Swift, MongoDB, etc..
with open("config.yml") as config:
    y = yaml.safe_load(config)
globals().update(y)


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
    'new_input',
    default_args=default_args,
    description='Check for new input data and launch data integration jobs',
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


def from_mongodb_to_influx(token = None, nb_retry = 10, **kwargs):
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
    if token is None :
        token = "SutSmr4uKZ9DxALVa5O7CucjxWMPkccLIn9MAAvgzCxZOSgV6UUfgr3bflIc9YcetB4F3cNohsqJFqiyEXxVwA=="
    integrator = InfluxIntegrator(influx_host=globals()["GOLD_INFLUX_IP"],
                                  influx_port=globals()["INFLUXDB_PORT"],
                                  token=token)
    swift_co = swiftclient.Connection(user=globals()["SWIFT_USER"],
                                      key=globals()["SWIFT_KEY"],
                                      authurl="http://" + globals()[
                                          "OPENSTACK_SWIFT_IP"] + ":"
                                              + globals()[
                                                  "SWIFT_REST_API_PORT"] +
                                              "/auth/v1.0")
    # Pull data from XCom instance : come from "check_type" task
    metadata_doc = kwargs["ti"].xcom_pull(key="metadata_doc")

    retry = 0
    while True:
        print("Try " + str(retry) + " : ", end='')
        try:
            # swift_json is a tuple : (meta_data, data)
            swift_json = swift_co.get_object(
                kwargs["dag_run"].conf["swift_container"],
                kwargs["dag_run"].conf["swift_id"])
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
                             time = influxdb_doc["time"],
                             measurement = influxdb_doc["measurement"],
                             field_list=influxdb_doc["fields"],
                             tag_list=influxdb_doc["tags"])
        except Exception as e:
            raise e

        return

def not_handled(**kwargs):
    raise NotImplementedError(
        "This data type (:" + kwargs["dag_run"].conf["content_type"] +
        ")is not handled by any workflow.")


def Not_implemented_json(**kwargs):
    raise NotImplementedError(
        "This json structure can't be handled.")


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
        if group in task_dict[metadata_doc["content_type"]] :
            return task_dict[metadata_doc["content_type"]][group][0].task_id
        else :
            return task_dict[metadata_doc["content_type"]]["default"][0].task_id
    else :
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


def failed_data_processing(*args, **kwargs):
    print("The data processing was a fail.")
    print(kwargs.keys())
    print(args[0]["execution_date"])
    print(args[0])
    group = args[0]["dag_run"].conf["swift_container"]
    swift_id = str(args[0]["dag_run"].conf["swift_id"])

    meta_base = MongoClient(
        "mongodb://" + globals()["META_MONGO_IP"] + ":" + globals()[
            "MONGO_PORT"] + "/"
    )
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
    swift_id = str(args[0]["dag_run"].conf["swift_id"])

    meta_base = MongoClient(
        "mongodb://" + globals()["META_MONGO_IP"] + ":" + globals()[
            "MONGO_PORT"] + "/"
    )
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


run_this_first = DummyOperator(
    task_id='getting_data',
    dag=dag,
)

branch_op = BranchPythonOperator(
    task_id='check_data_type',
    provide_context=True,
    python_callable=check_type,
    dag=dag)
join = DummyOperator(
    task_id='dag_end',
    trigger_rule='none_failed',

    dag=dag,
)
task_dict = {
        "image/png": {
            "default": [
                PythonOperator(
                    # TODO : Find a task_id naming solution
                    task_id="Object_in_png_in_neo4j",
                    provide_context=True,
                    python_callable=content_neo4j_node_creation,
                    start_date=days_ago(2),
                    on_failure_callback=failed_data_processing,
                    on_success_callback=successful_data_processing
                )
            ],
            "mygates": [
                PythonOperator(
                    # TODO : Find a task_id naming solution
                    task_id="Mygates_object_in_png_in_neo4j",
                    provide_context=True,
                    python_callable=content_neo4j_node_creation,
                    start_date=days_ago(2),
                    on_failure_callback=failed_data_processing,
                    on_success_callback=successful_data_processing
                )
            ]
        },
        "image/jpeg": {
            "default": [
                PythonOperator(
                    # TODO : Find a task_id naming solution
                    task_id="Object_in_jpeg_in_neo4j",
                    provide_context=True,
                    python_callable=content_neo4j_node_creation,
                    start_date=days_ago(2),
                    on_failure_callback=failed_data_processing,
                    on_success_callback=successful_data_processing
                )
            ],
            "mygates": [
                PythonOperator(
                    # TODO : Find a task_id naming solution
                    task_id="Mygates_object_in_jpeg_in_neo4j",
                    provide_context=True,
                    python_callable=content_neo4j_node_creation,
                    start_date=days_ago(2),
                    on_failure_callback=failed_data_processing,
                    on_success_callback=successful_data_processing
                )
            ]
        },
        "application/json": {
            "default": [
                PythonOperator(
                    # TODO : Find a task_id naming solution
                    task_id="Not_implemented_json",
                    provide_context=True,
                    python_callable=Not_implemented_json,
                    start_date=days_ago(2),
                    on_failure_callback=failed_data_processing,
                    on_success_callback=successful_data_processing
                )
            ],
            "neocampus": [
                PythonOperator(
                    # TODO : Find a task_id naming solution
                    task_id="Json_log_to_timeserie_influxdb",
                    provide_context=True,
                    python_callable=from_mongodb_to_influx,
                    start_date=days_ago(2),
                    on_failure_callback=failed_data_processing,
                    on_success_callback=successful_data_processing
                )
            ]
        },
        "not_handled": {
            "default": [
                PythonOperator(
                    # TODO : Find a task_id naming solution
                    task_id="Not_handled",
                    provide_context=True,
                    python_callable=not_handled,
                    start_date=days_ago(2),
                    on_failure_callback=failed_data_processing,
                    on_success_callback=successful_data_processing
                )
            ]
        }
    }
# task_dict = {
#     "png_data": {
#         "default": [
#             PythonOperator(
#                 # TODO : Find a task_id naming solution
#                 task_id="Object_in_png_in_neo4j",
#                 provide_context=True,
#                 python_callable=content_neo4j_node_creation,
#                 start_date=days_ago(2),
#                 on_failure_callback=failed_data_processing,
#                 on_success_callback=successful_data_processing
#             )
#         ],
#         "mygates": [
#             PythonOperator(
#                 # TODO : Find a task_id naming solution
#                 task_id="Mygates_object_in_png_in_neo4j",
#                 provide_context=True,
#                 python_callable=content_neo4j_node_creation,
#                 start_date=days_ago(2),
#                 on_failure_callback=failed_data_processing,
#                 on_success_callback=successful_data_processing
#             )
#         ]
#     },
#     "jpeg_data": {
#         "default": [
#             PythonOperator(
#                 # TODO : Find a task_id naming solution
#                 task_id="Object_in_jpeg_in_neo4j",
#                 provide_context=True,
#                 python_callable=content_neo4j_node_creation,
#                 start_date=days_ago(2),
#                 on_failure_callback=failed_data_processing,
#                 on_success_callback=successful_data_processing
#             )
#         ],
#         "mygates": [
#             PythonOperator(
#                 # TODO : Find a task_id naming solution
#                 task_id="Mygates_object_in_jpeg_in_neo4j",
#                 provide_context=True,
#                 python_callable=content_neo4j_node_creation,
#                 start_date=days_ago(2),
#                 on_failure_callback=failed_data_processing,
#                 on_success_callback=successful_data_processing
#             )
#         ]
#     },
#     "json_data": {
#         "default": [
#             PythonOperator(
#                 # TODO : Find a task_id naming solution
#                 task_id="Not_implemented_json",
#                 provide_context=True,
#                 python_callable=Not_implemented_json,
#                 start_date=days_ago(2),
#                 on_failure_callback=failed_data_processing,
#                 on_success_callback=successful_data_processing
#             )
#         ],
#         "neocampus": [
#             PythonOperator(
#                 # TODO : Find a task_id naming solution
#                 task_id="Json_log_to_timeserie_influxdb",
#                 provide_context=True,
#                 python_callable=from_mongodb_to_influx,
#                 start_date=days_ago(2),
#                 on_failure_callback=failed_data_processing,
#                 on_success_callback=successful_data_processing
#             )
#         ]
#     },
#     "not_handled": {
#         "default": [
#             PythonOperator(
#                 # TODO : Find a task_id naming solution
#                 task_id="Not_handled",
#                 provide_context=True,
#                 python_callable=not_handled,
#                 start_date=days_ago(2),
#                 on_failure_callback=failed_data_processing,
#                 on_success_callback=successful_data_processing
#             )
#         ]
#     }
# }

run_this_first >> branch_op

# TODO : recursive funct to create the pipeline (for n sublevel in dict)

pipeline = []
for data_type in task_dict:

    for owner_group in task_dict[data_type]:
        sub_pipe = []
        for task in task_dict[data_type][owner_group]:
            sub_pipe.append(task)
        pipeline.append([*sub_pipe, ])

for list in pipeline:
    chain(branch_op, *list, join)

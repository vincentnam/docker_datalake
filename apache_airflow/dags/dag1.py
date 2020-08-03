# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG
from airflow.contrib.hooks.mongo_hook import MongoHook
from airflow.operators.dummy_operator import DummyOperator
# Operators; we need this to operate!
from airflow.operators.python_operator import PythonOperator, \
    BranchPythonOperator
from airflow.utils.dates import days_ago
from airflow.utils.helpers import chain

from pymongo import MongoClient

globals()["META_MONGO_IP"] = "141.115.103.31"
globals()["OPENSTACK_SWIFT_IP"] = "141.115.103.30"
globals()["GOLD_MONGO_IP"] = "141.115.103.33"
globals()["GOLD_NEO4J_IP"] = "141.115.103.33"
globals()["GOLD_INFLUX_IP"] = "141.115.103.33"
globals()["MONGO_PORT"] = "27017"
globals()["SWIFT_REST_API_PORT"] = "8080"
globals()["INFLUXDB_PORT"] = "8086"
globals()["NEO4J_PORT"] = "7000"
globals()["SWIFT_USER"] = 'test:tester'
globals()["SWIFT_KEY"] = 'testing'

# Needed for airflow Hook
globals()["MONGO_META_CONN_ID"] = "mongo_metadatabase"
globals()["MONGO_GOLD_CONN_ID"] = "mongo_gold"

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


def from_mongodb_to_influx(**kwargs):
    from lib.influxdbintegrator import InfluxIntegrator
    import swiftclient
    import json
    integrator = InfluxIntegrator(influx_host=globals()["GOLD_INFLUX_IP"],
                                  influx_port=globals()["INFLUXDB_PORT"])
    swift_co = swiftclient.Connection(user=globals()["SWIFT_USER"],
                                      key=globals()["SWIFT_KEY"],
                                      authurl="http://" + globals()[
                                          "OPENSTACK_SWIFT_IP"] + ":"
                                              + globals()[
                                                  "SWIFT_REST_API_PORT"] +
                                              "/auth/v1.0")
    retry = 0

    while True:
        try:
            swift_json = swift_co.get_object(
                kwargs["dag_run"].conf["swift_container"],
                kwargs["dag_run"].conf["swift_id"])
            # If success : break

            print(json.load(swift_json))
            if integrator.write(
                    [integrator.mongodoc_to_influx(json.load(swift_json[1]))],
                    kwargs["dag_run"].conf[
                        "swift_container"]):
                print("successfully writed to influxdb")
            else:
                print("write failed to influxdb")
            return None
        except:
            retry += 1
            if retry >= 3:
                # After 3 fails, break
                break


def not_handled(**kwargs):
    raise NotImplementedError(
        "This data type (:" + kwargs["dag_run"].conf["content_type"] +
        ")is not handled by any workflow.")


def Not_implemented_json(**kwargs):
    raise NotImplementedError(
        "This json structure can't be handled.")


def check_type(**kwargs):
    meta_base = MongoHook(globals()["MONGO_META_CONN_ID"])
    # find(self, mongo_collection, query, find_one=False, mongo_db=None,
    #      **kwargs):

    group = kwargs["dag_run"].conf["swift_container"]
    swift_id = str(kwargs["dag_run"].conf["swift_id"])
    print(group)
    print(swift_id)
    doc = meta_base.get_conn().swift.get_collection(group).find_one({
        "swift_object_id": swift_id})
    # .kwargs["dag_run"].conf["content_type"]. /
    # find_one("mygates", {}, find_one=False)
    print(doc)
    if type_dict[doc["content_type"]] in callable_dict:
        data_type = type_dict[doc["content_type"]]
        if group in callable_dict[data_type]:
            return callable_dict[data_type][group]
        else:
            return callable_dict[data_type]["default"]
    else:
        return callable_dict["not_handled"]["default"]


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
            }
        }
    )
    )


def successful_data_processing(*args, **kwargs):
    print("The data processing was a success.")
    print(kwargs.keys())
    # print(kwargs["ti"].task_id)
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
    trigger_rule='one_success',

    dag=dag,
)
# Needed for lib mime type
type_dict = {"image/jpeg": "jpeg_data", "application/json": "json_data"
    , "image/png": "png_data", None: "not_handled"}
# Callable_dict contains the branch to get / the first task of the branch
callable_dict = \
    {
        "jpeg_data":
            {
                "default": "object_in_image_in_neo4j",
                "mygates": "mygates_object_in_image_in_neo4j",
            },
        "json_data":
            {
                "default": "Not_implemented_json",
                "neocampus": "Json_log_to_timeserie_influxdb",
            },
        "not_handled":
            {
                "default": "Nothing_to_do"
            }
    }

task_dict = {
    "png_data": {
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
    "jpeg_data": {
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
    "json_data": {
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

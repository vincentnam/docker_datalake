# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG
# Operators; we need this to operate!
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from airflow.utils.dates import days_ago
from airflow.contrib.hooks.mongo_hook import MongoHook
from datetime import timedelta
from airflow.operators.dummy_operator import DummyOperator
from airflow.utils.helpers import chain
globals()["META_MONGO_URI"] = ""
globals()["INPUT_SWIFT_API"] = ""
globals()["GOLD_MONGO_URI"] = ""
globals()["GOLD_NEO4J_URI"] = ""
globals()["GOLD_INFLUX_URI"] = ""

# TODO : Restructure DAG architecture

# # These args will get passed on to each operator
# # You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(2),
    # 'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=0),
}
dag = DAG(
    'new_input',
    default_args=default_args,
    description='Check for new input data and launch data integration jobs'
)


def content_neo4j_node_creation(**kwargs):
    from .lib.neo4j_job import Neo4j_dataintegration
    uri = globals()["GOLD_NEO4J_URI"]
    driver = Neo4j_dataintegration(uri, "neo4j", "password")

    meta_base = MongoHook(globals()["META_MONGO_URI"])
    coll = kwargs["dag_run"].conf["swift_container"]
    swift_id = str(kwargs["dag_run"].conf["swift_id"])
    doc = meta_base.get_conn().swift.get_collection(coll).find_one(
        {"swift_object_id": swift_id})
    driver.insert_image(doc)

def from_mongodb_to_influx(**kwargs):
    pass


def not_handled():
    # TODO : Insert in mongodb the fact that the data has not been handled
    pass



def check_type(**kwargs):
    meta_base = MongoHook(globals()["META_MONGO_URI"])
    # find(self, mongo_collection, query, find_one=False, mongo_db=None,
    #      **kwargs):
    coll = kwargs["dag_run"].conf["swift_container"]
    swift_id = str(kwargs["dag_run"].conf["swift_id"])
    print(coll)
    print(swift_id)
    doc = meta_base.get_conn().swift.get_collection(coll).find_one({"swift_object_id" :swift_id })#.kwargs["dag_run"].conf["content_type"].find_one("mygates", {}, find_one=False)
    print(doc)
    if doc["content_type"] not in type_dict:
        return "not_handled"
    else :
        return type_dict[doc["content_type"]]
    # return doc


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
    trigger_rule='all_success',

    dag=dag,
)
type_dict = { "image/jpeg":"jpeg_data" , None:"not_handled"}
callable_dict = {"jpeg_data" : [content_neo4j_node_creation], "not_handled": [not_handled, not_handled] }
run_this_first >> branch_op

pipeline = []
aux = 0
for data_type in type_dict:
    sub_pipe = []influxdb_gold
    for ope in callable_dict[type_dict[data_type]]:

        sub_pipe.append( PythonOperator(
            # TODO : Find a task_id naming solution
            task_id= ope.__name__ + "_" + str(aux),
            provide_context=True,
            python_callable=ope,
            start_date= days_ago(2)) )
        aux = aux + 1
    pipeline.append(sub_pipe)

for list in pipeline:
    chain(branch_op, *list, join)

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG
# Operators; we need this to operate!
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from airflow.utils.dates import days_ago
from airflow.contrib.hooks.mongo_hook import MongoHook
from datetime import timedelta
from airflow.operators.dummy_operator import DummyOperator
# # These args will get passed on to each operator
# # You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(2),
    'email': ['airflow@example.com'],
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


# def print_context(ds, **kwargs):
#     # print(kwargs)
#
#     # Common (Not-so-nice way)
#     # 3 DB connections when the file is parsed
#     # var1 = Variable.get("conf", deserialize_json=True)
#     # var2 = Variable.get("var2")
#     # var3 = Variable.get("var3")
#     for i in kwargs:
#         print(kwargs['dag_run'].conf)
#     # print(ds)
#     # with open("/usr/local/airflow/tests.txt", "w+") as fp:
#         # fp.write(var1)
#     return 'Whatever you return gets printed in the logs'

def jpeg_data(**kwargs):
    from neo4j import GraphDatabase
    uri = "neo4j://neo4j_gold:7687"
    driver = GraphDatabase.driver(uri, auth=("neo4j", "password"))


def not_handled():
    pass


type_dict = { "image/jpeg":"jpeg_data" , None:"not_handled"}
callable_dict = {"jpeg_data" : jpeg_data, "not_handled": not_handled }
def check_type(**kwargs):
    meta_base = MongoHook("metadatabase")
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
    task_id='type_of_data',
    provide_context=True,
    python_callable=check_type,
    dag=dag)
join = DummyOperator(
    task_id='join',
    trigger_rule='all_success',

    dag=dag,
)

run_this_first >> branch_op

for i in type_dict:
    t = PythonOperator(
        task_id=type_dict[i],
        provide_context=True,
        python_callable=callable_dict[type_dict[i]],
        dag=dag,
    )
    branch_op >> t >> join


# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG
# Operators; we need this to operate!
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.contrib.hooks.mongo_hook import MongoHook
from datetime import timedelta
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

def check_type(**kwargs):
    meta_base = MongoHook("metadatabase")
    # find(self, mongo_collection, query, find_one=False, mongo_db=None,
    #      **kwargs):
    doc = meta_base.find("mygates", {}, find_one=False)
    # print(doc)
    for i in doc:
        print(i)
    # return doc
def print_context(ds, **kwargs):
    # print(kwargs)

    # Common (Not-so-nice way)
    # 3 DB connections when the file is parsed
    # var1 = Variable.get("conf", deserialize_json=True)
    # var2 = Variable.get("var2")
    # var3 = Variable.get("var3")
    for i in kwargs:
        print(kwargs['dag_run'].conf)
    # print(ds)
    # with open("/usr/local/airflow/tests.txt", "w+") as fp:
        # fp.write(var1)
    return 'Whatever you return gets printed in the logs'

t1 = PythonOperator(
    task_id='check_type',
    provide_context=True,
    python_callable=check_type,
    dag=dag,
)


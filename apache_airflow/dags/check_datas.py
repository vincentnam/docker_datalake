# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG
# Operators; we need this to operate!
from airflow.operators.python_operator import PythonOperator, \
    BranchPythonOperator
from airflow.utils.dates import days_ago
from airflow.contrib.hooks.mongo_hook import MongoHook
from datetime import timedelta
from airflow.operators.dummy_operator import DummyOperator
from airflow.utils.helpers import chain

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
    'Check_data_to_process',
    default_args=default_args,
    description='Check every 5 minutes if a new data has to be processed',
    schedule_interval='*/5 * * * *',
    dagrun_timeout=timedelta(seconds=5)
)


def get_list_mongo_meta(**kwargs):
    meta_base = MongoHook(globals()["MONGO_META_CONN_ID"])
    list = meta_base.get_conn().swift.get_collection("stats").find_one({"type":""})
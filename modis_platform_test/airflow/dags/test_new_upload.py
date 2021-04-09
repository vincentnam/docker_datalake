from datetime import timedelta

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG

# Operators; we need this to operate!
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}
dag = DAG(
    'test_new_upload',
    default_args=default_args,
    description='A test new upload DAG',
    schedule_interval=None,
    start_date=days_ago(2),
    tags=['xtest'],
)


def get_swift_context(**kwargs):
    conf = kwargs['dag_run'].conf
    swift_version = conf.get("swift_version")
    swift_user = conf.get("swift_user")
    swift_container = conf.get("swift_container")
    swift_obj_id = conf.get("swift_obj_id")

    print("TEST: got swift context")
    print("swift_version: ", swift_version)
    print("swift_user: ", swift_user)
    print("swift_container: ", swift_container)
    print("swift_obj_id: ", swift_obj_id)


def do_something():
    print("TEST: do something")


task_get_swift_context = PythonOperator(
    task_id='get_swift_context',
    python_callable=get_swift_context,
    provide_context=True,
    dag=dag,
)

task_do_something = PythonOperator(
    task_id='do_something',
    python_callable=do_something,
    provide_context=True,
    dag=dag,
)

task_get_swift_context >> task_do_something

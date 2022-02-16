import sys
from datetime import timedelta
import datetime

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG

# Operators; we need this to operate!
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

from services import get_anomaly
import config

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


def data_anomaly_detection(*args, **kwargs):
    print('anomaly detection start')
    return None

def data_anomaly_detection_neOCampus(*args, **kwargs):
    print('anomaly detection neOCampus')
    container_name = "neOCampus"
    get_anomaly(50, 150, container_name)

    return None

def data_anomaly_detection_autOCampus(*args, **kwargs):
    print('anomaly detection autOCampus')
    container_name = "autOCampus"
    get_anomaly(50, 150, container_name)
    return None

def data_anomaly_detection_Villagil(*args, **kwargs):
    print('anomaly detection Villagil')
    container_name = "Villagil"
    get_anomaly(50, 150, container_name)
    return None

def data_anomaly_detection_eCOnect(*args, **kwargs):
    print('anomaly detection eCOnect')
    container_name = "eCOnect"
    get_anomaly(50, 150, container_name)
    return None

def data_anomaly_detection_done(*args, **kwargs):
    print('Done')
    return None

dag = DAG(
    'anomaly_detection',
    default_args=default_args,
    description='Airflow pipeline to detect anomaly',
    schedule_interval=config.schedule_interval,
    start_date=days_ago(2),
    tags=['anomaly_detection'],
)
task_data_anomaly_detection = PythonOperator(
    task_id='data_anomaly_detection',
    python_callable=data_anomaly_detection,
    provide_context=True,
    dag=dag,
)
task_data_anomaly_detection_neOCampus = PythonOperator(
    task_id='anomaly_neOCampus',
    python_callable=data_anomaly_detection_neOCampus,
    provide_context=True,
    dag=dag,
)
task_data_anomaly_detection_autOCampus = PythonOperator(
    task_id='anomaly_autOCampus',
    python_callable=data_anomaly_detection_autOCampus,
    provide_context=True,
    dag=dag,
)
task_data_anomaly_detection_Villagil = PythonOperator(
    task_id='anomaly_Villagil',
    python_callable=data_anomaly_detection_Villagil,
    provide_context=True,
    dag=dag,
)
task_data_anomaly_detection_eCOnect = PythonOperator(
    task_id='anomaly_eCOnect',
    python_callable=data_anomaly_detection_eCOnect,
    provide_context=True,
    dag=dag,
)
task_data_anomaly_detection_done = PythonOperator(
    task_id='data_anomaly_detection_done',
    python_callable=data_anomaly_detection_done,
    provide_context=True,
    dag=dag,
)

task_data_anomaly_detection >> task_data_anomaly_detection_neOCampus
task_data_anomaly_detection >> task_data_anomaly_detection_autOCampus
task_data_anomaly_detection >> task_data_anomaly_detection_Villagil
task_data_anomaly_detection >> task_data_anomaly_detection_eCOnect

task_data_anomaly_detection_neOCampus >> task_data_anomaly_detection_done
task_data_anomaly_detection_autOCampus >> task_data_anomaly_detection_done
task_data_anomaly_detection_Villagil >> task_data_anomaly_detection_done
task_data_anomaly_detection_eCOnect >> task_data_anomaly_detection_done
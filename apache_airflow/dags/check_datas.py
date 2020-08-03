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
import logging
from datetime import datetime
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


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(2),
    'provide_context' : True

}
dag = DAG(
    'Check_data_to_process',
    default_args=default_args,
    description='Check every 5 minutes if a new data has to be processed',
    # schedule_interval='*/5 * * * *',
    schedule_interval=None,
    dagrun_timeout=timedelta(seconds=5)
)

data_account = {
    "neocampus" : {
        "application/json": "new_input"
    },
    "mygates" : {
        "image/jpeg": "new_input",
        "image/png": "new_input"
    },
    "default" : {
        "image/jpeg": "new_input",
        "image/png": "new_input",
        "application/json": "new_input"
    }
}

from airflow.exceptions import AirflowSkipException
from airflow.api.common.experimental.trigger_dag import trigger_dag


def get_list_mongo_meta(**kwargs):
    meta_base = MongoHook(globals()["MONGO_META_CONN_ID"])
    data_to_process_list = meta_base.get_conn().stats.get_collection("swift").find_one({"type":"data_to_process_list"})


    swift_data_list = data_to_process_list["data_to_process"]

    for data_doc in swift_data_list:
        run_id = '%s_%s_%s:%s' % (data_doc["swift_user"],
                                  data_doc["swift_container"],
                                  data_doc["swift_id"],
                                  datetime.utcnow().replace(
            microsecond=0).isoformat())
        trigger_dag(dag_id = data_account[data_doc["swift_container"]][data_doc["content_type"]],
                    run_id = run_id,
                    conf = data_doc)
        logging.info('triggering dag %s with %s' % (run_id, data_doc))

        return
    raise AirflowSkipException('No external dags triggered')

done = DummyOperator(
    task_id='Dag_triggered',
    trigger_rule='none_failed_or_skipped',
    dag=dag,
)



get_data = PythonOperator(task_id="Get_list",
                provide_context=True,
                python_callable=get_list_mongo_meta,
                start_date=days_ago(2))

dag >> get_data >> done

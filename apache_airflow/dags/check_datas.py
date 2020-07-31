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
# from airflow.operators.dagrun_operator import TriggerDagRunOperator,
# from airflow.utils.db import create_session
# from airflow.models.dagbag import DagBag
# from airflow.utils.state import State
# from airflow import settings
# from typing import Dict
# from airflow.api.common.experimental.trigger_dag import trigger_dag
# from airflow.utils.types import DagRunType
# from airflow.utils import timezone


# # These args will get passed on to each operator
# # You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(2),
    'provide_context' : True
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
from airflow.api.common.experimental.get_task_instance import get_task_instance

def get_list_mongo_meta(**kwargs):
    # print(get_task_instance(dag_id = task_id="test").state)
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
        # trigger_dag(
        #     dag_id: str,
        # run_id: Optional[str] = None,
        # conf: Optional[Union[dict, str]] = None,
        # execution_date: Optional[datetime] = None,
        # replace_microseconds: bool = True,
        # )

    #     exp = context['ti'].xcom_pull(task_ids='parse_config',
    #                                   key='experiment')
    #     run_id = '%s_%s_%s:%s' % (data_doc["swift_user"],
    #                               data_doc["swift_container"],
    #                               data_doc["swift_id"],
    #                               datetime.utcnow().replace(
    #         microsecond=0).isoformat())
    #     dro = DagRunOrder(run_id=run_id)
    #     d = {
    #         'directory': context['ti'].xcom_pull(task_ids='parse_config',
    #                                              key='experiment_directory'),
    #         'base': data_doc,
    #         'experiment': exp['name'],
    #     }
    #     logging.info('triggering dag %s with %s' % (run_id, d))
    #     dro.payload = d
    #     yield dro
    # return

done = DummyOperator(
    task_id='Dag_triggered',
    trigger_rule='one_success',
    dag=dag,
)
test = DummyOperator(
    task_id='test',
    trigger_rule='one_success',
    dag=dag,
)


get_data = PythonOperator(task_id="Get_list",
                provide_context=True,
                python_callable=get_list_mongo_meta,
                start_date=days_ago(2))

dag >> test >> get_data >> done

#
# class TriggerMultipleDagRunOperator(TriggerDagRunOperator):
#     def execute(self, context: Dict):
#         if isinstance(self.execution_date, datetime.datetime):
#             execution_date = self.execution_date
#         elif isinstance(self.execution_date, str):
#             execution_date = timezone.parse(self.execution_date)
#             self.execution_date = execution_date
#         else:
#             execution_date = timezone.utcnow()
#
#         run_id = DagRun.generate_run_id(DagRunType.MANUAL, execution_date)
#         # Ignore MyPy type for self.execution_date because it doesn't pick up the timezone.parse() for strings
#         trigger_dag(
#             dag_id=self.trigger_dag_id,
#             run_id=run_id,
#             conf=self.conf,
#             execution_date=self.execution_date,
#             replace_microseconds=False,
#         )
#     # def execute(self, context):
#     #     count = 0
#     #     for dro in self.python_callable(context):
#     #         if dro:
#     #             with create_session() as session:
#     #                 dbag = DagBag(settings.DAGS_FOLDER)
#     #                 trigger_dag = dbag.get_dag(self.trigger_dag_id)
#     #                 dr = trigger_dag.create_dagrun(
#     #                     run_id=dro.run_id,
#     #                     state=State.RUNNING,
#     #                     conf=dro.payload,
#     #                     external_trigger=True)
#     #                 session.add(dr)
#     #                 session.commit()
#     #                 count = count + 1
#     #         else:
#     #             self.log.info("Criteria not met, moving on")
#     #     if count == 0:
#     #         raise AirflowSkipException('No external dags triggered')
# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG
# Operators; we need this to operate!
from airflow.operators.python_operator import PythonOperator, \
    BranchPythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
from airflow.operators.dummy_operator import DummyOperator
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
    'provide_context': True

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
    "neocampus": {
        "application/json": "new_input"
    },
    "mygates": {
        "image/jpeg": "new_input",
        "image/png": "new_input"
    },
    "default": {
        "image/jpeg": "new_input",
        "image/png": "new_input",
        "application/json": "new_input"
    }
}

from airflow.exceptions import AirflowSkipException
from airflow.api.common.experimental.trigger_dag import trigger_dag
from pymongo import MongoClient


def get_list_mongo_meta(**kwargs):
    meta_base = MongoClient(
        "mongodb://" + globals()["META_MONGO_IP"] + ":" + globals()[
            "MONGO_PORT"] + "/"
    )
    # meta_base = MongoHook(globals()["MONGO_META_CONN_ID"])
    data_to_process_list = meta_base.stats["swift"].find_one(
        {"type": "data_to_process_list"})
    swift_data_list = data_to_process_list["data_to_process"]

    for data_doc in swift_data_list:
        run_id = '%s_%s_%s:%s' % (data_doc["swift_user"],
                                  data_doc["swift_container"],
                                  data_doc["swift_id"],
                                  datetime.utcnow().replace(
                                      microsecond=0).isoformat())
        trigger_dag(dag_id=data_account[data_doc["swift_container"]][
            data_doc["content_type"]],
                    run_id=run_id,
                    conf=data_doc)
        logging.info('triggering dag %s with %s' % (run_id, data_doc))
        meta_base.stats["swift"].find_one_and_update(
            {"type": "data_to_process_list"},
            {
                "$pop":
                    {"data_to_process": -1}
            }
        )
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        today = datetime.datetime(today.year, today.month, today.day)
        tomorrow = datetime.datetime(tomorrow.year,
                                     tomorrow.month,
                                     tomorrow.day)
        if meta_base.stats["data_log"].find_one(
                {
                    "date":
                        {
                            "$gte": today,
                            "$lt": tomorrow
                        }
                }
        ) is None:
            meta_base.stats["data_log"].insert_one(
                {
                    "date": today,
                    "data_processed":
                        [
                            {
                                "swift_id": data_doc["swift_id"],
                                "swift_container": data_doc["swift_container"],
                                "content_type": data_doc["content_type"]
                            }
                        ]
                }
            )
        else:
            meta_base.stats["data_log"].find_one_and_update(
                {
                    "date":
                        {
                            "$gte": today,
                            "$lt": tomorrow
                        }
                },
                {
                    "$push": {
                        "data_processed": {
                            "swift_id": data_doc["swift_id"],
                            "swift_container": data_doc["swift_container"],
                            "content_type": data_doc["content_type"]
                        }
                    }
                }
            )
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


# https://bazaar.launchpad.net/~hudson-openstack/swift/trunk/revision/336/test/__init__.py#test/__init__.py






#
#
# Jul 30 17:37:05 co2-dl-swift proxy-server:
# Error: An error occurred:
#012Traceback (most recent call last):
# #012  File "/projets/datalake/swift_install/swift/swift/common/middleware/catch_errors.py", line 75, in handle_request
# #012    resp = self._app_call(env)
# #012  File "/projets/datalake/swift_install/swift/swift/common/wsgi.py", line 1387, in _app_call
# #012    resp = self.app(env, self._start_response)
# #012  File "/projets/datalake/swift_install/swift/swift/common/middleware/gatekeeper.py", line 129, in __call__
# #012    #012  File "/projets/datalake/swift_install/swift/swift/common/middleware/healthcheck.py", line 52, in __call__
# #012    return self.app(env, start_response)
# #012  File "/projets/datalake/swift_install/swift/swift/common/middleware/proxy_logging.py", line 424, in __call__
# #012    iterable = self.app(env, my_start_response)
# #012  File "/projets/datalake/swift_install/swift/swift/common/middleware/memcache.py", line 112, in __call__
# #012    return self.app(env, start_response)
# #012  File "/projets/datalake/swift_install/swift/swift/common/middleware/listing_formats.py", line 157, in __call__
# #012    returnself.app(env, start_response)
# #012  File "/projets/datalake/swift_install/swift/swift/common/swob.py", line 1570, in _wsgify
# #012    return func(*new_args)(env, start_response)
# #012  File "/projets/datalake/swift_install/swift/swift/common/middleware/tempurl.py", line 504, in __call__
# #012    return self.app(env, start_response)
# #012  File "/projets/datalake/swift_install/swift/swift/common/middleware/slo.py", line 1585, in __call__
# #012    return self.handle_multipart_get_or_head(req, start_response)
# #012  File "/projets/datalake/swift_install/swift/swift/common/middleware/slo.py", line 1121, in handle_multipart_get_or_head
# #012    return SloGetContext(self).handle_slo_get_or_head(req, start_response)
# #012  File "/projets/datalake/swift_install/swift/swift/common/middleware/slo.py", line 770, in handle_slo_get_or_head
# #012    resp_iter = self._app_call(req.environ)
# #012  File "/projets/datalake/swift_install/swift/swift/common/wsgi.py", line 1387, in _app_call
# #012    resp = self.app(env, self._start_response)
# #012  File "/projets/datalake/swift_install/swift/swift/common/middleware/dlo.py", line 436, in __call__
# #012    handle_request(req, start_response)
# #012  File "/projets/datalake/swift_install/swift/swift/common/middleware/dlo.py", line 374, in handle_request
# #012    resp_iter = self._app_call(req.environ)
# #012  File "/projets/datalake/swift_install/swift/swift/common/wsgi.py", line 1387, in _app_call
# #012    resp = self.app(env, self._start_response)
# #012  File "/projets/datalake/swift_install/swift/swift/common/middleware/ratelimit.py", line 318, in __call__
# #012    return self.app(env, start_response)
# #012  File "/projets/datalake/swift_install/swift/swift/common/middleware/crossdomain.py", line 82, in __call__
# #012    return self.app(env, start_response)
# #012  File "/projets/datalake/swift_install/swift/swift/common/middleware/tempauth.py", line 341, in __call__
# #012    return self.app(env, start_response)
# #012  File "/projets/datalake/swift_install/swift/swift/common/middleware/staticweb.py", line 546, in __call__
# #012    return self.app(env, start_response)
# #012  File "/projets/datalake/swift_install/swift/swift/common/middleware/copy.py", line 253, in __call__
# #012    return self.app(env, start_response)
# #012  File "/projets/datalake/swift_install/swift/swift/common/middleware/versioned_writes/legacy.py", line 872, in __call__
# #012    return self.app(env, start_response)
# #012  File "/projets/datalake/swift_install/swift/swift/common/swob.py", line 1570, in _wsgify
# #012    return func(*new_args)(env, start_response)
# #012  File "/projets/datalake/swift_install/swift/swift/common/swob.py", line 1570, in _wsgify
# #012    return func(*new_args)(env, start_response)
# #012  File "/projets/datalake/swift_install/swift/swift/common/middleware/proxy_logging.py", line 340, in __call__#
# 012    return self.app(env, start_response)#012  File "/projets/datalake/swift_install/swift/swift/common/swob.py", line 1570, in _wsgify
# #012    return func(*new_args)(env, start_response)
# #012 TypeError: 'NoneType' object is not callable (txn: txf02db390d9604b0683824-005f22e921)

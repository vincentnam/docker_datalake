# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG
# Operators; we need this to operate!
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
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
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'sla_miss_callback': yet_another_function,
    # 'trigger_rule': 'all_success'
}
dag = DAG(
    'new_input',
    default_args=default_args,
    description='Check for new input data and launch data integration jobs'
)
# print(dag.conf)
# t1, t2 and t3 are examples of tasks created by instantiating operators
# t1 = BashOperator(
#     task_id='print_date',
#     bash_command='echo "coucou" ',
#     dag=dag,
# )
from airflow.models import Variable


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
    task_id='print_the_context',
    provide_context=True,
    python_callable=print_context,
    dag=dag,
)

# dag.doc_md = __doc__
#
# t1.doc_md = """\
# #### Task Documentation
# You can document your task using the attributes `doc_md` (markdown),
# `doc` (plain text), `doc_rst`, `doc_json`, `doc_yaml` which gets
# rendered in the UI's Task Instance Details page.
# ![img](http://montcs.bloomu.edu/~bobmon/Semesters/2012-01/491/import%20soul.png)
# """

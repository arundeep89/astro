from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator

from datetime import datetime, timedelta

default_args={
    'retry': 5,
    'retry_delay' : timedelta(minutes=2)
}

def _downloading_data(ti):
    with open('/tmp/my_file.txt','w') as f:
        f.write('my_data')
    ti.xcom_push(key='my_key', value=43)

def _checking_data(ti):
    my_xcom=ti.xcom_pull(task_ids=['downloading_data'], key='my_key')
    print(my_xcom)
    

with DAG(dag_id='simple_dag', default_args=default_args, start_date=days_ago(2),
 schedule_interval="@daily", catchup=False) as dag:
    
    downloading_data=PythonOperator(
        task_id='downloading_data',
        python_callable=_downloading_data
    )

    checking_data=PythonOperator(
        task_id='checking_data',
        python_callable=_checking_data
    )

    waiting_for_data=FileSensor(
        task_id='waiting_for_data',
        fs_conn_id='fs_default',
        filepath='my_file.txt'
    )

    processing_data = BashOperator(
        task_id='processing_data',
        bash_command='exit 0'
    )

    downloading_data >> checking_data >> waiting_for_data >> processing_data
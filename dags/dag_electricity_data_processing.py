from distutils import command
import os

from datetime import datetime, timedelta
from tracemalloc import start
from airflow import DAG
from airflow.operators.docker_operator import DockerOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator
from airflow.contrib.operators.ssh_operator import SSHOperator
from docker.types import Mount
import pendulum


default_args = {
'owner'                 : 'airflow',
'description'           : 'Electricity overview data processing ',
'depend_on_past'        : False,
'start_date'            : datetime.today(),
'email_on_failure'      : False,
'email_on_retry'        : False,
'retries'               : 0,
'retry_delay'           : timedelta(minutes=5)
}

GINLONG_USERNAME = os.environ.get('USERNAME')
GINLONG_PASSWORD = os.environ.get('PASSWORD')
INVERTER_SERIAL_NUMBER = os.environ.get('INVERTER_SERIAL_NUMBER')

with DAG(
    'electricity_data_processing', 
    default_args=default_args, 
    schedule_interval="0 7 * * 1", 
    catchup=False
) as dag_edp:
    start_dag = DummyOperator(
        task_id='start_dag'
        )

    end_dag = DummyOperator(
        task_id='end_dag'
        )
    
    wait_task = BashOperator(
        task_id='wait_task',
        bash_command='sleep 60'
    )

    setup_firefox_docker_env =  SSHOperator(
        task_id='setup_firefox_docker_env',
        ssh_conn_id='ssh_localhost',
        command='bash --login /scripts/setup_docker_env.sh firefox_container'
    )

    spin_firefox_task = SSHOperator(
        task_id='spin_firefox',
        ssh_conn_id='ssh_localhost',
        command='set -e; bash --login /scripts/run_firefox_container.sh '
    )

    export_data_task = DockerOperator(
        task_id="rpa_daily_export",
        container_name='rpa_daily_export',
        image="rpa_panouri_python_app",
        command="python src/export_utility/export_daily_data.py",
        docker_url="unix://var/run/docker.sock",
        network_mode="web",
        api_version="auto",
        auto_remove=True,
        mount_tmp_dir=False,
        mounts=[
            Mount(source="/tmp/export_folder", target="/tmp/export_folder", type="bind")
        ],
        privileged=True,
        environment={
            'USERNAME': GINLONG_USERNAME,
            'PASSWORD': GINLONG_PASSWORD,
            'RPA_EXPORT_IN_DOCKER': 1,
            'PYTHONPATH': '/app/src',
            'INVERTER_SERIAL_NUMBER': INVERTER_SERIAL_NUMBER
        },
        retries=2, 
        retry_delay=timedelta(seconds=300)
    )

    cleanup_docker_env = SSHOperator(
        trigger_rule='all_done',
        task_id='cleanup_docker_env',
        ssh_conn_id='ssh_localhost',
        command='bash --login /scripts/cleanup_docker_env.sh '
    )

    check_file_exported = SSHOperator(
        task_id='check_file_exported',
        ssh_conn_id='ssh_localhost',
        command='set -e; bash --login /scripts/check_export_file.sh '
    )

    start_dag.set_downstream(setup_firefox_docker_env)
    setup_firefox_docker_env.set_downstream(spin_firefox_task)
    spin_firefox_task.set_downstream(wait_task)  
    wait_task.set_downstream(export_data_task) 
    export_data_task.set_downstream(cleanup_docker_env)
    cleanup_docker_env.set_downstream(check_file_exported)
    check_file_exported.set_downstream(end_dag)

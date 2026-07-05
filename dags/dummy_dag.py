from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator


def say_hello():
    print("Hello from the dummy DAG! Airflow is working locally.")


with DAG(
    dag_id="dummy_test_dag",
    description="DAG de teste para validar o setup local do Airflow com Docker",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["teste", "dummy"],
) as dag:

    task_python = PythonOperator(
        task_id="hello_python",
        python_callable=say_hello,
    )

    task_bash = BashOperator(
        task_id="hello_bash",
        bash_command="echo 'Hello from BashOperator!' && date",
    )

    task_python >> task_bash

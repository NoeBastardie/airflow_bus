from airflow.operators.bash import BashOperator
from airflow.models import DAG
from airflow.utils.dates import days_ago
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from datetime import datetime

filename = 'train_pos.csv'
default_args = {
   'owner': 'noe',
}

with DAG(
    'train_pos_etl',
    default_args=default_args,
    start_date=days_ago(1),
    schedule_interval='@daily',
    tags=['train_project','train_pos']
    ) as dag:

    t1 = BashOperator(
        task_id="etl_train_pos",
        bash_command="python /opt/airflow/dags/etl/etl_train_pos.py",
    )

    t2 = GCSToBigQueryOperator(
    task_id='load_to_bq',
    bucket='etl-airflow-train-pos-bucket',
    source_objects=[filename],
    field_delimiter =',',
    destination_project_dataset_table='midyear-cursor-371415.train_dataset.staging__train_pos',
    skip_leading_rows=1,
    write_disposition='WRITE_APPEND',
    )

    t1 >> t2 
from adzuna_function import adzuna_response_func
from exchange_rate_function import exchange_rate_function

import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
from google.cloud import bigquery
from google.oauth2 import service_account
from airflow import DAG
from airflow.operators.python import PythonOperator

def process_career_data():

    adzuna_uk_df = pd.DataFrame(adzuna_response_func("gb"))
    adzuna_us_df = pd.DataFrame(adzuna_response_func("us"))

    exchange_rate_gbp_php = exchange_rate_function("GBP").get("conversion_rates", {}).get("PHP", 0)
    exchange_rate_usd_php = exchange_rate_function("USD").get("conversion_rates", {}).get("PHP", 0)

    adzuna_uk_df['Original_Currency'] = "GBP"
    adzuna_uk_df['Salary_Min_PHP'] = (adzuna_uk_df['Salary_Min'] * exchange_rate_gbp_php).round(2)
    adzuna_uk_df['Salary_Max_PHP'] = (adzuna_uk_df['Salary_Max'] * exchange_rate_gbp_php).round(2)

    adzuna_us_df['Original_Currency'] = "USD"
    adzuna_us_df['Salary_Min_PHP'] = (adzuna_us_df['Salary_Min'] * exchange_rate_usd_php).round(2)
    adzuna_us_df['Salary_Max_PHP'] = (adzuna_us_df['Salary_Max'] * exchange_rate_usd_php).round(2)

    master_df = pd.concat([adzuna_uk_df, adzuna_us_df], ignore_index=True)

    table_id = "remote-career-gcp-airflow.remote_career_dataset.remote_career_table"
    key_path = "/opt/airflow/remote-career-gcp-airflow-2a2be5c0edcf.json"
    gcp_credentials = service_account.Credentials.from_service_account_file(key_path)
    client = bigquery.Client(credentials=gcp_credentials, project="remote-career-gcp-airflow")

    query = f"SELECT Job_ID FROM {table_id}"

    try:
        existing_ids_df = client.query(query).to_dataframe()
        existing_ids = existing_ids_df['Job_ID'].tolist()
        print(f"Existing IDs: {len(existing_ids)}")
    except Exception as e:
        print(f"Table not found. Error:\n{e}")
        existing_ids = []

    new_jobs_df = master_df[~master_df['Job_ID'].isin(existing_ids)]

    job_config = bigquery.LoadJobConfig(
        schema=[
            bigquery.SchemaField("Job_ID", "STRING"),
            bigquery.SchemaField("Title", "STRING"),
            bigquery.SchemaField("Country", "STRING"),
            bigquery.SchemaField("Salary_Min", "FLOAT"),
            bigquery.SchemaField("Salary_Max", "FLOAT"),
            bigquery.SchemaField("Company", "STRING"),
            bigquery.SchemaField("Location", "STRING"),
            bigquery.SchemaField("Original_Currency", "STRING"),
            bigquery.SchemaField("Salary_Min_PHP", "FLOAT"),
            bigquery.SchemaField("Salary_Max_PHP", "FLOAT"),
        ],
        write_disposition="WRITE_APPEND", # Appends new rows instead of overwriting
    )

    if not new_jobs_df.empty:
        job = client.load_table_from_dataframe(
            new_jobs_df, table_id, job_config=job_config
        )
        job.result()
        print(f"Success! Loaded {job.output_rows} rows to {table_id}.")
    else:
        print("No new jobs to load.")

default_args = {
    'owner': 'tom',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='career_daily_extraction',
    default_args=default_args,
    description="Fetches Junior Data Engineer career listings from Adzuna API",
    schedule_interval='@daily',
    start_date=dt(2026, 8, 15),
    catchup=False
) as dag:
    extract_load_task = PythonOperator(
        task_id="extract_transform_load_career",
        python_callable=process_career_data,
    )

extract_load_task

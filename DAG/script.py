from airflow import DAG

from airflow.operators.python import PythonOperator

from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator

from airflow.utils.dates import days_ago

from datetime import datetime, timedelta

import requests

import json

from google.cloud import storage




# CONFIG



PROJECT_ID = "crypto-data-engineering"

DATASET_RAW = "crypto"

TABLE_RAW = "raw_prices"

TABLE_CLEAN = "prices_hourly"

GCS_BUCKET = "***-crypto-data-bucket"




# DEFAULT 

default_args = {

    "owner": "airflow",

    "retries": 3,

    "retry_delay": timedelta(minutes=2),

    "email_on_failure": False,

    "email_on_retry": False,

}




# FUNCTION: Fetch Top 20 Coins → Save to GCS



def fetch_top_coins_prices(**kwargs):

    r_coins = requests.get(

        "https://api.coingecko.com/api/v3/coins/markets",

        params={"vs_currency": "usd", "order": "market_cap_desc", "per_page": 20, "page": 1},

        timeout=10

    )

    r_coins.raise_for_status()

    top_coins = [c["id"] for c in r_coins.json()]


    r_prices = requests.get(

        "https://api.coingecko.com/api/v3/simple/price",

        params={"ids": ",".join(top_coins), "vs_currencies": "usd"},

        timeout=10

    )

    r_prices.raise_for_status()

    data = r_prices.json()


    ts = datetime.utcnow().isoformat()

    records = []


    for coin, values in data.items():

        records.append({

            "symbol": coin.upper(),

            "price": float(values["usd"]),

            "event_ts": ts,

            "payload": json.dumps(values)

        })


    # Save raw JSON to GCS

    client = storage.Client()

    bucket = client.bucket(GCS_BUCKET)

    blob_name = f"crypto_raw/prices_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.json"

    blob = bucket.blob(blob_name)

    blob.upload_from_string('\n'.join(json.dumps(r) for r in records), content_type='application/json')


    gcs_uri = f"gs://{GCS_BUCKET}/{blob_name}"

    print(f"Uploaded to: {gcs_uri}")

    return gcs_uri




# DAG DEFINITION



with DAG(

    dag_id="crypto_etl_pipeline_top20",

    default_args=default_args,

    description="Fetch top 20 crypto prices from CoinGecko, save to GCS, load to BigQuery, transform",

    schedule_interval="*/5 * * * *",

    start_date=days_ago(1),

    catchup=False,

    tags=["crypto", "etl"],

) as dag:


    # Fetch prices and save to GCS

    fetch_prices = PythonOperator(

        task_id="fetch_prices",

        python_callable=fetch_top_coins_prices,

    )


    # Load raw JSON from GCS to BigQuery

    load_raw = BigQueryInsertJobOperator(

        task_id="load_raw_to_bq",

        configuration={

            "load": {

                "destinationTable": {

                    "projectId": PROJECT_ID,

                    "datasetId": DATASET_RAW,

                    "tableId": TABLE_RAW,

                },

                "sourceUris": ["{{ ti.xcom_pull(task_ids='fetch_prices') }}"],

                "sourceFormat": "NEWLINE_DELIMITED_JSON",

                "writeDisposition": "WRITE_APPEND",

                "autodetect": True,

                "schemaUpdateOptions": ["ALLOW_FIELD_ADDITION"],

            }

        },

        location="US",

    )


    # 

    # Transform raw table → clean hourly table (WITH PARTITIONING)

transform = BigQueryInsertJobOperator(

    task_id="transform_to_clean_table",

    configuration={

        "query": {

            "query": f"""

                CREATE OR REPLACE TABLE `{PROJECT_ID}.{DATASET_RAW}.{TABLE_CLEAN}`

                PARTITION BY price_date

                AS

                SELECT DISTINCT

                    symbol,

                    price,

                    event_ts AS price_ts,

                    DATE(event_ts) AS price_date,

                    EXTRACT(HOUR FROM event_ts) AS price_hour,

                    'coingecko' AS source

                FROM `{PROJECT_ID}.{DATASET_RAW}.{TABLE_RAW}`

                WHERE event_ts IS NOT NULL

            """,

            "useLegacySql": False

        }

    },

    location="US",

)


    # DAG order

fetch_prices >> load_raw >> transform

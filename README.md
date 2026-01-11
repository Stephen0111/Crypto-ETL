# Crypto ETL Pipeline with Apache Airflow, GCS & BigQuery  
*A Production-Grade, Scalable Cloud Data Engineering Pipeline on Google Cloud*

This project implements a **high‑throughput, production‑ready ETL pipeline** engineered to ingest, process, and serve real‑time cryptocurrency market data at scale. The system continuously retrieves pricing data for the **Top 20 cryptocurrencies**, persists immutable raw payloads in **Google Cloud Storage (GCS)**, loads them into **BigQuery**, applies deterministic SQL transformations, and exposes curated analytical datasets to **Looker Studio**.

The pipeline is orchestrated using **Cloud Composer (Managed Apache Airflow)** and executes on a 5‑minute interval with built‑in observability, operational resilience, and cost‑optimized data processing patterns.

---

## Architecture Overview

         ┌─────────────────────┐
         │   CoinGecko API     │
         └─────────┬───────────┘
                   │  JSON (Top 20 Coins)
                   ▼
         ┌─────────────────────┐
         │  Google Cloud Storage│
         │  (Raw Landing Zone)  │
         └─────────┬───────────┘
                   │  GCS → BigQuery Load Job
                   ▼
         ┌─────────────────────┐
         │   BigQuery Raw Table │
         │    crypto.raw_prices │
         └─────────┬───────────┘
                   │  SQL MERGE Transform
                   ▼
         ┌─────────────────────┐
         │ BigQuery Clean Table│
         │ crypto.prices_hourly│
         └─────────┬───────────┘
                   │  Analytics Layer
                   ▼
         ┌─────────────────────┐
         │    Looker Studio    │
         │ (Dashboards/Reports)│
         └─────────────────────┘

---

## Key Features

### Automated Real-Time Crypto Ingestion  
Continuously ingests pricing data for the **Top 20 cryptocurrencies** at 5‑minute intervals, ensuring consistent coverage and minimal API overhead.

### Cloud-Orchestrated ETL with Airflow  
Cloud Composer provides managed orchestration with retry policies, SLA monitoring, lineage visibility, and modular DAG design for long‑term maintainability.

### Scalable Data Lake + Warehouse Architecture  
- GCS acts as a cost‑efficient, durable raw landing zone  
- BigQuery stores both raw and refined datasets optimized for analytical workloads  
- SQL transformations enforce schema consistency, deduplication, and time‑series alignment  
- Partitioning and clustering strategies reduce query cost and improve performance  

### Production-Ready Operational Design  
- Idempotent ingestion and MERGE‑based transformations prevent duplication  
- Schema evolution is handled through raw‑zone autodetection and controlled downstream modeling  
- Logging, alerting, and monitoring integrated through Cloud Composer and GCP native tools  

### Analytics-Ready Reporting Layer  
Curated datasets are exposed to **Looker Studio**, enabling analysts to build dashboards without requiring direct access to raw or semi‑structured data.

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Orchestration** | Apache Airflow (Cloud Composer) | Managed scheduling, retries, monitoring, and DAG orchestration |
| **Data Lake** | Google Cloud Storage | Immutable raw data storage with low-cost retention |
| **Warehouse** | Google BigQuery | Scalable analytical engine for transformations and reporting |
| **API Source** | CoinGecko API | Real-time cryptocurrency market data |
| **Visualization** | Looker Studio | Business intelligence and dashboarding |
| **Language** | Python | ETL logic, API integration, and GCP client operations |

---

## Output Tables (BigQuery)

### **crypto.raw_prices**  
Stores raw JSON API responses with ingestion timestamps.  
Schema is autodetected to support upstream API changes without pipeline interruption.

### **crypto.prices_hourly**  
A refined, analytics‑ready dataset designed for time‑series analysis and dashboard consumption.  
Partitioned by date and clustered by symbol to optimize query performance and cost.

| Column | Description |
|--------|-------------|
| symbol | Token symbol |
| price | USD price |
| price_ts | Timestamp extracted from the raw event |
| price_date | Date component of the timestamp |
| price_hour | Hour extracted for aggregation |
| source | Data provider identifier |

---

## Project Screenshots

### **1. Airflow**
![DAG](Assets/dag1.png)

![DAG](Assets/dag2.png)

### **2. GCS Bucket**
![GCS Bucket](Assets/bucket.png)
![GCS Object](Assets/object.png)

### **3. BigQuery**
![Big Query](Assets/bigquery1.png)
![Big Query](Assets/bigqueryclean.png)

### **4. Looker**
![Looker](Assets/looker.png)

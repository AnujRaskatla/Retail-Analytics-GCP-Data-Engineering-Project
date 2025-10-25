# 🏢 GCP Retailer Data Lake Project

![Python](https://img.shields.io/badge/python-3.8+-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![GCP](https://img.shields.io/badge/Google_Cloud-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)
![Apache Spark](https://img.shields.io/badge/Apache_Spark-E25A1C?style=for-the-badge&logo=apachespark&logoColor=white)
![BigQuery](https://img.shields.io/badge/BigQuery-4285F4?style=for-the-badge&logo=googlebigquery&logoColor=white)
![Apache Airflow](https://img.shields.io/badge/Apache_Airflow-017CEE?style=for-the-badge&logo=apache-airflow&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)

> **An enterprise-grade, end-to-end data engineering solution built on Google Cloud Platform for retail analytics**

Transform raw retail data into actionable business insights using modern cloud-native technologies. This project demonstrates a complete data pipeline from ingestion to analytics, implementing industry best practices for data lake architecture.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Data Pipeline](#-data-pipeline)
- [Data Models](#-data-models)
- [Monitoring & Logging](#-monitoring--logging)
- [Configuration](#-configuration)
- [Deployment](#-deployment)
- [Use Cases](#-use-cases)
- [License](#-license)
- [Contact](#-contact)

---

## 🎯 Overview

This project implements a **production-ready data lake architecture** on Google Cloud Platform that ingests data from multiple sources (MySQL databases and REST APIs), processes it through a medallion architecture (Bronze → Silver → Gold), and delivers analytics-ready datasets for business intelligence.

### Key Highlights

- **Multi-source data ingestion** from Cloud SQL MySQL and external APIs
- **Scalable processing** with PySpark on Cloud Dataproc
- **Medallion architecture** (Bronze, Silver, Gold layers) in BigQuery
- **Incremental loading** with CDC (Change Data Capture) support
- **Automated orchestration** using Cloud Composer (Apache Airflow)
- **Data quality management** with quarantine mechanisms
- **Slowly Changing Dimensions (SCD Type 2)** implementation
- **CI/CD pipeline** with Cloud Build

---

## 🏗️ Architecture

![Architecture Diagram](docs/images/architecture-diagram.png)

### Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                          DATA SOURCES                                │
├─────────────────────────────────────────────────────────────────────┤
│  Cloud SQL (Retailer DB)  │  Cloud SQL (Supplier DB)  │  REST API   │
└───────────────┬─────────────────────────┬──────────────────┬─────────┘
                │                         │                   │
                ▼                         ▼                   ▼
    ┌──────────────────────────────────────────────────────────────┐
    │              Cloud Dataproc (PySpark Processing)             │
    └──────────────────────────┬───────────────────────────────────┘
                               │
                               ▼
              ┌────────────────────────────────┐
              │   Cloud Storage (Data Lake)    │
              │   ├── Landing Zone             │
              │   ├── Archive                  │
              │   ├── Configs                  │
              │   └── Logs                     │
              └────────────┬───────────────────┘
                           │
                           ▼
          ┌─────────────────────────────────────────┐
          │         BigQuery (Analytics)            │
          │  ┌────────────────────────────────┐     │
          │  │  Bronze Layer (Raw Data)       │     │
          │  └──────────┬─────────────────────┘     │
          │             │                            │
          │             ▼                            │
          │  ┌────────────────────────────────┐     │
          │  │  Silver Layer (Cleansed)       │     │
          │  │  • Data Quality Checks         │     │
          │  │  • SCD Type 2                  │     │
          │  └──────────┬─────────────────────┘     │
          │             │                            │
          │             ▼                            │
          │  ┌────────────────────────────────┐     │
          │  │  Gold Layer (Business Ready)   │     │
          │  │  • Aggregations                │     │
          │  │  • Business KPIs               │     │
          │  └────────────────────────────────┘     │
          └─────────────────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────────┐
              │  Cloud Composer (Airflow)  │
              │  Workflow Orchestration     │
              └────────────────────────────┘
```

---

## ✨ Features

### Data Engineering

- ✅ **Incremental Data Loading**: Watermark-based CDC for efficient data synchronization
- ✅ **Full & Incremental Loads**: Support for both loading patterns
- ✅ **Data Versioning**: SCD Type 2 implementation for historical tracking
- ✅ **Data Quality**: Automated validation and quarantine mechanisms
- ✅ **Archival Strategy**: Automated archival with date-partitioned structure
- ✅ **Audit Logging**: Comprehensive tracking of all data pipeline runs

### Cloud Infrastructure

- ✅ **Serverless Architecture**: Auto-scaling with Cloud Dataproc
- ✅ **Cost Optimization**: Preemptible VMs and ephemeral clusters
- ✅ **High Availability**: Multi-region data replication
- ✅ **Security**: IAM-based access control and encrypted storage

### Orchestration

- ✅ **DAG-based Workflows**: Modular and reusable pipeline components
- ✅ **Error Handling**: Retry mechanisms and failure notifications
- ✅ **Monitoring**: Built-in logging and alerting
- ✅ **Scheduling**: Cron-based automated execution

---

## 🛠️ Tech Stack

### Core Technologies

| Category | Technology | Purpose |
|----------|-----------|---------|
| **Cloud Platform** | Google Cloud Platform | Infrastructure |
| **Compute** | Cloud Dataproc | Distributed processing |
| **Processing Engine** | Apache Spark (PySpark) | Data transformation |
| **Data Warehouse** | BigQuery | Analytics storage |
| **Object Storage** | Cloud Storage | Data lake storage |
| **Database** | Cloud SQL (MySQL) | Source databases |
| **Orchestration** | Cloud Composer (Apache Airflow) | Workflow management |
| **CI/CD** | Cloud Build | Deployment automation |
| **Language** | Python 3.8+ | Primary programming language |

### Python Libraries

```
google-cloud-storage
google-cloud-bigquery
pyspark==3.3.0
pandas
requests
apache-airflow
mysql-connector-python
```

---

## 📁 Project Structure

```
gcp-retailer-datalake/
│
├── README.md                          # This file
├── LICENSE                            # MIT License
├── .gitignore                         # Git ignore patterns
├── requirements.txt                   # Python dependencies
├── cloudbuild.yaml                    # CI/CD configuration
│
├── workflows/                         # Airflow DAGs
│   ├── parent_dag.py                 # Master orchestration DAG
│   ├── pyspark_dag.py                # PySpark job scheduler
│   └── bigquery_dag.py               # BigQuery layer processor
│
├── scripts/                           # PySpark processing scripts
│   ├── retailer_mysql_to_landing.py  # Retailer DB ingestion
│   ├── supplier_mysql_to_landing.py  # Supplier DB ingestion
│   └── customer_reviews_to_landing.py # API data ingestion
│
├── data/                              # SQL and config files
│   └── BQ/
│       ├── bronzeTable.sql           # Bronze layer DDL
│       ├── silverTable.sql           # Silver layer transformations
│       └── goldTable.sql             # Gold layer aggregations
│
├── configs/                           # Configuration files
│   ├── retailer_config.csv           # Retailer DB table configs
│   └── supplier_config.csv           # Supplier DB table configs
│
├── utils/                             # Utility scripts
│   ├── add_dags_to_composer.py       # DAG deployment utility
│   ├── requirements.txt              # Utility dependencies
│   └── __init__.py
│
├── docs/                              # Documentation
   ├── architecture.md               # Architecture details
   ├── setup.md                      # Setup instructions
   └── api_reference.md              # API documentation│
      
```

---

## 🚀 Getting Started

### Prerequisites

1. **Google Cloud Platform Account**
   - Active GCP project with billing enabled
   - Required APIs enabled:
     - Cloud Storage API
     - BigQuery API
     - Cloud Dataproc API
     - Cloud Composer API
     - Cloud SQL Admin API
     - Cloud Build API

2. **Local Development Environment**
   - Python 3.8 or higher
   - Google Cloud SDK (`gcloud` CLI)
   - Git

3. **Access & Permissions**
   - IAM roles:
     - `BigQuery Admin`
     - `Storage Admin`
     - `Dataproc Administrator`
     - `Cloud Composer Administrator`
     - `Cloud SQL Admin`

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/gcp-retailer-datalake.git
   cd gcp-retailer-datalake
   ```

2. **Set Up GCP Project**
   ```bash
   # Set your GCP project
   export PROJECT_ID="your-gcp-project-id"
   gcloud config set project $PROJECT_ID
   
   # Enable required APIs
   gcloud services enable \
     storage.googleapis.com \
     bigquery.googleapis.com \
     dataproc.googleapis.com \
     composer.googleapis.com \
     sqladmin.googleapis.com \
     cloudbuild.googleapis.com
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Authentication**
   ```bash
   # Create service account
   gcloud iam service-accounts create data-pipeline-sa \
     --display-name="Data Pipeline Service Account"
   
   # Grant necessary roles
   gcloud projects add-iam-policy-binding $PROJECT_ID \
     --member="serviceAccount:data-pipeline-sa@$PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/bigquery.admin"
   
   # Download credentials
   gcloud iam service-accounts keys create ~/gcp-key.json \
     --iam-account=data-pipeline-sa@$PROJECT_ID.iam.gserviceaccount.com
   
   export GOOGLE_APPLICATION_CREDENTIALS=~/gcp-key.json
   ```

### Quick Start

For detailed setup instructions, see [docs/setup.md](docs/setup.md)

1. **Create Cloud Storage Bucket**
   ```bash
   gsutil mb -l us-central1 gs://your-bucket-name
   gsutil -m cp -r configs/ gs://your-bucket-name/
   ```

2. **Set Up Cloud SQL Instances**
   - Create Retailer Database instance
   - Create Supplier Database instance
   - Run SQL scripts to create tables and load sample data

3. **Create BigQuery Datasets**
   ```bash
   bq mk --dataset $PROJECT_ID:bronze_dataset
   bq mk --dataset $PROJECT_ID:silver_dataset
   bq mk --dataset $PROJECT_ID:gold_dataset
   bq mk --dataset $PROJECT_ID:temp_dataset
   ```

4. **Deploy to Cloud Composer**
   - Create Composer environment
   - Upload DAGs and dependencies
   - Configure variables and connections

---

## 📊 Data Pipeline

### Ingestion Layer

#### 1. MySQL Database Ingestion
- **Source**: Cloud SQL MySQL (Retailer & Supplier DBs)
- **Method**: JDBC connection via PySpark
- **Pattern**: 
  - Full Load for static dimension tables
  - Incremental Load with watermark for fact tables
- **Format**: JSON files in Cloud Storage
- **Schedule**: Daily at 5:00 AM UTC

#### 2. API Data Ingestion
- **Source**: MockAPI.io (Customer Reviews)
- **Method**: REST API with requests library
- **Format**: Parquet files
- **Schedule**: Daily at 5:30 AM UTC

### Processing Layers

#### Bronze Layer (Raw Data)
- **Purpose**: Store raw data exactly as received
- **Implementation**: BigQuery External Tables
- **Schema**: Same as source systems
- **Data Quality**: None (accept all data)

#### Silver Layer (Cleansed Data)
- **Purpose**: Cleaned, validated, and standardized data
- **Implementation**: BigQuery managed tables
- **Features**:
  - Data quality checks with quarantine flag
  - SCD Type 2 for change tracking
  - Type conversion and standardization
  - Deduplication
- **Update Pattern**: MERGE statements (UPSERT)

#### Gold Layer (Business Ready)
- **Purpose**: Aggregated, business-ready datasets
- **Implementation**: BigQuery tables
- **Contents**:
  - Sales summary by product/category
  - Customer engagement metrics
  - Product performance analytics
  - Supplier analysis
  - Review sentiment summaries

### Orchestration

#### DAG Structure

```python
parent_dag
  ├── trigger_pyspark_dag
  │     ├── retailer_ingestion
  │     ├── supplier_ingestion
  │     └── api_ingestion
  │
  └── trigger_bigquery_dag
        ├── create_bronze_tables
        ├── process_silver_layer
        └── aggregate_gold_layer
```

---

## 📐 Data Models

### Source Data

#### Retailer Database
- **products**: Product catalog
- **categories**: Product categories
- **customers**: Customer master
- **orders**: Order transactions
- **order_items**: Order line items

#### Supplier Database
- **suppliers**: Supplier master
- **product_suppliers**: Product-supplier mapping with pricing

#### External API
- **customer_reviews**: Product reviews and ratings

### Gold Layer Metrics

#### 1. Sales Summary
```sql
-- Daily sales by product and category
-- Metrics: total_units_sold, total_sales, unique_customers
```

#### 2. Customer Engagement
```sql
-- Customer lifetime value and behavior
-- Metrics: total_orders, total_spent, avg_order_value, days_since_last_order
```

#### 3. Product Performance
```sql
-- Product analytics with supplier info
-- Metrics: total_units_sold, total_revenue, avg_rating, total_reviews
```

#### 4. Supplier Analysis
```sql
-- Supplier contribution metrics
-- Metrics: total_products_supplied, total_units_sold, total_revenue
```

#### 5. Customer Reviews Summary
```sql
-- Sentiment and rating analysis
-- Metrics: avg_rating, positive_reviews, negative_reviews
```

---

## 📈 Monitoring & Logging

### Audit Logging

All pipeline executions are logged to `temp_dataset.audit_log`:

| Field | Description |
|-------|-------------|
| `tablename` | Source table name |
| `load_type` | Full Load or Incremental |
| `record_count` | Number of records processed |
| `load_timestamp` | Execution timestamp |
| `status` | SUCCESS or ERROR |

### Pipeline Logs

Detailed execution logs stored in `temp_dataset.pipeline_logs`:
- JSON format with timestamp
- Event type (INFO, SUCCESS, ERROR)
- Detailed error messages
- Also exported to Cloud Storage for long-term retention

### Monitoring

- **Airflow UI**: DAG execution status and task logs
- **BigQuery**: Query performance and slot usage
- **Cloud Monitoring**: Custom metrics and alerting
- **Cloud Logging**: Centralized log aggregation

---

## ⚙️ Configuration

### Config Files

#### retailer_config.csv
```csv
database,datasource,tablename,loadtype,watermark,is_active,targetpath
retailer,retailer_db,products,Full Load,,1,landing/retailer-db/products
retailer,retailer_db,customers,Incremental,updated_at,1,landing/retailer-db/customers
```

#### supplier_config.csv
```csv
database,datasource,tablename,loadtype,watermark,is_active,targetpath
supplier-db,mysql-db,suppliers,Full Load,created_at,1,supplier
```

### Environment Variables

Set these in Cloud Composer:
```bash
GCS_BUCKET=your-bucket-name
BQ_PROJECT=your-project-id
MYSQL_RETAILER_HOST=retailer-db-ip
MYSQL_SUPPLIER_HOST=supplier-db-ip
API_ENDPOINT=your-api-url
```

---

## 🚢 Deployment

### Automated Deployment with Cloud Build

The project includes CI/CD configuration in `cloudbuild.yaml`:

```bash
# Trigger deployment
gcloud builds submit --config=cloudbuild.yaml
```

**Deployment Steps:**
1. Install Python dependencies
2. Run unit tests
3. Upload DAGs to Composer bucket
4. Upload SQL scripts to Composer bucket
5. Validate Airflow DAGs

### Manual Deployment

```bash
# Set variables
export COMPOSER_ENV="your-composer-env"
export COMPOSER_LOCATION="us-central1"
export COMPOSER_BUCKET="us-central1-demo-instance-xxxxx-bucket"

# Deploy DAGs
gsutil -m cp workflows/*.py gs://$COMPOSER_BUCKET/dags/

# Deploy data files
gsutil -m cp -r data/ gs://$COMPOSER_BUCKET/data/

# Deploy utilities
gsutil -m cp utils/*.py gs://$COMPOSER_BUCKET/data/utils/
```

---

## 💼 Use Cases

This data lake architecture enables:

1. **Real-time Business Analytics**
   - Sales performance dashboards
   - Inventory optimization
   - Customer segmentation

2. **Data Science & ML**
   - Demand forecasting
   - Product recommendation engines
   - Customer churn prediction

3. **Operational Reporting**
   - Daily sales reports
   - Supplier performance tracking
   - Order fulfillment metrics

4. **Strategic Decision Making**
   - Market basket analysis
   - Pricing optimization
   - Supplier relationship management


---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Contact

**Anuj Raskatla** - Data Engineer

- 💼 LinkedIn: [Anuj Raskatla](https://www.linkedin.com/in/anuj-raskatla/)
- 🐙 GitHub: [@AnujRaskatla](https://github.com/AnujRaskatla)
- 📧 Email: anuj.raskatla@gmail.com
- 🌐 Portfolio: [Here](https://yourwebsite.com)

**Project Link**: [Retail-Analytics-GCP-Data-Engineering-Project](https://github.com/AnujRaskatla/Retail-Analytics-GCP-Data-Engineering-Project)

---

## 🙏 Acknowledgments

- Google Cloud Platform documentation
- Apache Spark community
- Apache Airflow project
- Open-source contributors

---

## 📚 Additional Resources

- [Google Cloud Documentation](https://cloud.google.com/docs)
- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [BigQuery Best Practices](https://cloud.google.com/bigquery/docs/best-practices)

---

⭐ **If you find this project helpful, please consider giving it a star!**


# Architecture Documentation

## GCP Retailer Data Lake Architecture

### Table of Contents

1. [Overview](#overview)
2. [Architecture Principles](#architecture-principles)
3. [System Components](#system-components)
4. [Data Flow](#data-flow)
5. [Data Layer Architecture](#data-layer-architecture)
6. [Technology Stack](#technology-stack)
7. [Security & Access Control](#security--access-control)
8. [Scalability & Performance](#scalability--performance)
9. [Data Quality & Governance](#data-quality--governance)
10. [Disaster Recovery](#disaster-recovery)

---

## Overview

The GCP Retailer Data Lake implements a modern, cloud-native architecture following the **medallion pattern** (Bronze → Silver → Gold) to transform raw retail data into actionable business intelligence. The system ingests data from multiple sources, processes it through distributed computing frameworks, and delivers analytics-ready datasets.

### Business Objectives

- Centralize retail data from disparate sources
- Enable real-time and batch analytics
- Support data-driven decision making
- Provide scalable, cost-effective data infrastructure
- Ensure data quality and governance

### Key Metrics

- **Data Volume**: 1M+ records processed daily
- **Latency**: Batch processing within 30 minutes
- **Availability**: 99.9% SLA
- **Cost Efficiency**: 40% reduction vs traditional on-premise

---

## Architecture Principles

### 1. Cloud-Native Design
- Leverage managed GCP services
- Serverless where possible
- Auto-scaling infrastructure

### 2. Separation of Concerns
- Decoupled ingestion, processing, and serving layers
- Independent scaling of components
- Modular architecture for easy maintenance

### 3. Data Lake Philosophy
- Schema-on-read approach
- Store raw data in its native format
- Support structured and semi-structured data

### 4. Medallion Architecture
- **Bronze Layer**: Raw, immutable data
- **Silver Layer**: Cleansed, validated data with SCD Type 2
- **Gold Layer**: Business-ready, aggregated metrics

### 5. Cost Optimization
- Use of preemptible VMs
- Lifecycle policies on Cloud Storage
- BigQuery partitioning and clustering
- Ephemeral Dataproc clusters

---

## System Components

### 1. Data Sources

#### Cloud SQL (MySQL)
- **Retailer Database**
  - Tables: products, categories, customers, orders, order_items
  - Connection: JDBC
  - Instance: db-n1-standard-2
  - Storage: 20GB SSD

- **Supplier Database**
  - Tables: suppliers, product_suppliers
  - Connection: JDBC
  - Instance: db-n1-standard-1
  - Storage: 10GB SSD

#### External API
- **Customer Reviews API**
  - Source: MockAPI.io
  - Format: REST API (JSON)
  - Schema: id, customer_id, product_id, rating, review_text, review_date
  - Update Frequency: Daily

### 2. Ingestion Layer

#### Cloud Dataproc
- **Cluster Configuration**
  - Master: n1-standard-4 (4 vCPUs, 15GB RAM)
  - Workers: 2x n1-standard-4
  - Auto-scaling: Enabled
  - Max idle: 30 minutes
  - Image: 2.1-debian11

- **PySpark Jobs**
  - Retailer MySQL ingestion
  - Supplier MySQL ingestion
  - Customer Reviews API ingestion
  - Incremental and full load support

### 3. Storage Layer

#### Cloud Storage
```
gs://retailer-datalake-project/
├── landing/                  # Raw ingested data
│   ├── retailer-db/
│   ├── supplier-db/
│   └── customer_reviews/
├── archive/                  # Historical data
│   └── {table}/{YYYY}/{MM}/{DD}/
├── configs/                  # Configuration files
│   ├── retailer_config.csv
│   └── supplier_config.csv
├── temp/                     # Temporary processing
└── logs/                     # Pipeline execution logs
```

**Lifecycle Policies**:
- Logs: Delete after 90 days
- Archive: Move to Nearline after 30 days

### 4. Processing Layer

#### BigQuery

**Bronze Dataset** (bronze_dataset)
- External tables pointing to Cloud Storage
- No transformations
- Formats: JSON, Parquet
- Schema: Auto-detected from source

**Silver Dataset** (silver_dataset)
- Managed tables
- Data quality checks
- SCD Type 2 implementation
- Effective date tracking
- Quarantine flagging

**Gold Dataset** (gold_dataset)
- Business metrics and KPIs
- Aggregated tables
- Denormalized for query performance
- Partitioned by date

**Temp Dataset** (temp_dataset)
- Audit logs
- Pipeline execution logs
- Temporary processing tables

### 5. Orchestration Layer

#### Cloud Composer (Apache Airflow)
- **Environment**: n1-standard-2, 3 nodes
- **Python Version**: 3.10
- **DAGs**:
  - `parent_dag`: Master orchestrator
  - `pyspark_dag`: Ingestion workflows
  - `bigquery_dag`: Layer processing
  
**Schedule**: Daily at 5:00 AM UTC

### 6. CI/CD Layer

#### Cloud Build
- Automated DAG deployment
- SQL script validation
- Dependency installation
- Trigger: Git push to main branch

---

## Data Flow

### End-to-End Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA INGESTION                            │
└─────────────────────────────────────────────────────────────────┘
                               ↓
    ┌──────────────┬────────────────────┬──────────────┐
    │              │                    │              │
Cloud SQL      Cloud SQL           REST API      
(Retailer)     (Supplier)        (Reviews)
    │              │                    │
    └──────────────┴────────────────────┴──────────────┘
                               ↓
              ┌────────────────────────────────┐
              │   Cloud Dataproc (PySpark)     │
              │   • JDBC Connection            │
              │   • HTTP Requests              │
              │   • Watermark-based CDC        │
              │   • JSON/Parquet Output        │
              └────────────┬───────────────────┘
                           │
                           ↓
              ┌────────────────────────────────┐
              │   Cloud Storage (Landing)      │
              │   • JSON files (MySQL data)    │
              │   • Parquet files (API data)   │
              │   • Date-partitioned           │
              └────────────┬───────────────────┘
                           │
┌──────────────────────────┴──────────────────────────┐
│                  BRONZE LAYER                       │
│  External Tables → Schema-on-Read → Raw Data Store  │
└─────────────────────────┬───────────────────────────┘
                          │
                          ↓
┌──────────────────────────────────────────────────────┐
│                  SILVER LAYER                        │
│  • Data Validation                                   │
│  • Type Conversion                                   │
│  • Deduplication                                     │
│  • SCD Type 2 (effective_start_date, is_active)     │
│  • Quarantine Invalid Records                        │
└─────────────────────────┬────────────────────────────┘
                          │
                          ↓
┌──────────────────────────────────────────────────────┐
│                   GOLD LAYER                         │
│  • sales_summary                                     │
│  • customer_engagement                               │
│  • product_performance                               │
│  • supplier_analysis                                 │
│  • customer_reviews_summary                          │
└──────────────────────────────────────────────────────┘
                          │
                          ↓
                  BI Tools / Analytics
```

### Detailed Flow

#### 1. Ingestion Phase (5:00 AM UTC)

**Step 1: Trigger Parent DAG**
- Cloud Scheduler triggers `parent_dag`
- Checks dependencies and prerequisites

**Step 2: Execute PySpark Jobs**
- `pyspark_dag` triggered
- Parallel execution of ingestion jobs:
  - Retailer DB → Landing
  - Supplier DB → Landing
  - Customer Reviews API → Landing

**Step 3: Data Landing**
- Files written to Cloud Storage
- Old files archived with date partitions
- Audit logs updated in BigQuery

#### 2. Processing Phase

**Step 4: Bronze Layer Creation**
- External tables created/updated
- Point to latest files in Cloud Storage
- No data movement

**Step 5: Silver Layer Processing**
- MERGE operations for incremental tables
- TRUNCATE + INSERT for full load tables
- SCD Type 2 implementation:
  - Update existing records: `is_active = FALSE`
  - Insert new versions with new timestamps
- Data quality checks with quarantine flags

**Step 6: Gold Layer Aggregation**
- Join operations across silver tables
- Business metric calculations
- Create/replace gold tables

#### 3. Monitoring & Logging

**Step 7: Audit Trail**
- Record counts in `temp_dataset.audit_log`
- Pipeline execution logs in `temp_dataset.pipeline_logs`
- Logs exported to Cloud Storage
- Airflow task logs in Composer UI

---

## Data Layer Architecture

### Bronze Layer (Raw Data)

**Purpose**: Immutable storage of raw data

**Characteristics**:
- External tables (no data copy)
- Schema-on-read
- Support for JSON and Parquet
- No transformations
- Historical archive in Cloud Storage

**Tables**:
```sql
bronze_dataset.products
bronze_dataset.categories
bronze_dataset.customers
bronze_dataset.orders
bronze_dataset.order_items
bronze_dataset.suppliers
bronze_dataset.product_suppliers
bronze_dataset.customer_reviews
```

### Silver Layer (Cleansed Data)

**Purpose**: Cleaned, validated, and historized data

**Characteristics**:
- Managed tables (data copied to BigQuery)
- Schema-on-write
- Data quality checks
- SCD Type 2 for change tracking
- Quarantine mechanism

**Schema Pattern** (SCD Type 2):
```sql
{original_columns}
effective_start_date TIMESTAMP
effective_end_date TIMESTAMP
is_active BOOL
is_quarantined BOOL  -- For dimension tables
```

**Processing Logic**:
```sql
-- Step 1: Mark changed records as inactive
UPDATE silver_table
SET is_active = FALSE, 
    effective_end_date = CURRENT_TIMESTAMP()
WHERE key_column = new_data.key_column
  AND is_active = TRUE
  AND (col1 != new_col1 OR col2 != new_col2)

-- Step 2: Insert new/updated records
INSERT INTO silver_table
SELECT *, 
       CURRENT_TIMESTAMP() AS effective_start_date,
       NULL AS effective_end_date,
       TRUE AS is_active
FROM new_data
```

**Tables**:
```sql
silver_dataset.products (is_quarantined)
silver_dataset.categories (is_quarantined)
silver_dataset.customers (SCD Type 2)
silver_dataset.orders (SCD Type 2)
silver_dataset.order_items (SCD Type 2)
silver_dataset.suppliers (is_quarantined)
silver_dataset.product_suppliers (SCD Type 2)
silver_dataset.customer_reviews (SCD Type 2)
```

### Gold Layer (Business Ready)

**Purpose**: Aggregated metrics and KPIs

**Characteristics**:
- Denormalized tables
- Pre-aggregated for performance
- Business logic embedded
- Optimized for BI tools

**Tables & Metrics**:

1. **sales_summary**
   ```sql
   - order_date
   - category_id, category_name
   - product_id, product_name
   - total_units_sold
   - total_sales
   - unique_customers
   ```

2. **customer_engagement**
   ```sql
   - customer_id, customer_name
   - total_orders
   - total_spent
   - last_order_date
   - days_since_last_order
   - avg_order_value
   ```

3. **product_performance**
   ```sql
   - product_id, product_name
   - category_id, category_name
   - supplier_id, supplier_name
   - total_units_sold
   - total_revenue
   - avg_rating
   - total_reviews
   ```

4. **supplier_analysis**
   ```sql
   - supplier_id, supplier_name
   - total_products_supplied
   - total_units_sold
   - total_revenue
   ```

5. **customer_reviews_summary**
   ```sql
   - product_id, product_name
   - avg_rating
   - total_reviews
   - positive_reviews (rating >= 4)
   - negative_reviews (rating < 3)
   ```

---

## Technology Stack

### Compute & Processing
| Technology | Version | Purpose |
|------------|---------|---------|
| Cloud Dataproc | 2.1 | Distributed processing |
| Apache Spark | 3.3.0 | Data transformation engine |
| PySpark | 3.3.0 | Python API for Spark |

### Storage & Database
| Technology | Version | Purpose |
|------------|---------|---------|
| Cloud Storage | Standard | Data lake storage |
| BigQuery | Latest | Analytics warehouse |
| Cloud SQL (MySQL) | 8.0 | Source databases |

### Orchestration & Workflow
| Technology | Version | Purpose |
|------------|---------|---------|
| Cloud Composer | 2.x | Workflow orchestration |
| Apache Airflow | 2.7.1 | DAG scheduling |

### Development & CI/CD
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.8+ | Primary language |
| Cloud Build | Latest | CI/CD automation |

### Monitoring & Logging
| Technology | Version | Purpose |
|------------|---------|---------|
| Cloud Logging | Latest | Centralized logging |
| Cloud Monitoring | Latest | Metrics and alerting |

---

## Security & Access Control

### Authentication
- Service account-based authentication
- IAM roles and permissions
- Cloud SQL authorized networks
- API key management for external APIs

### Authorization (IAM Roles)
```
data-pipeline-sa:
  - roles/bigquery.admin
  - roles/storage.admin
  - roles/dataproc.admin
  - roles/composer.worker
  - roles/cloudsql.client
  - roles/logging.logWriter
```

### Data Encryption
- **At Rest**: Google-managed encryption keys
- **In Transit**: TLS 1.2+ for all connections
- **Database**: Encrypted connections to Cloud SQL

### Network Security
- VPC with private IP addressing
- Authorized networks for Cloud SQL
- Service account key rotation policy

### Audit & Compliance
- All data access logged
- Audit log retention: 90 days
- Compliance with data privacy regulations

---

## Scalability & Performance

### Horizontal Scaling
- **Dataproc**: Auto-scaling workers (2-10 nodes)
- **BigQuery**: Automatic slot allocation
- **Cloud Storage**: Unlimited storage capacity

### Vertical Scaling
- Adjustable VM types for Dataproc
- BigQuery reservation for guaranteed slots

### Performance Optimizations
1. **Partitioning**: Date-based partitioning in BigQuery
2. **Clustering**: Key columns for query optimization
3. **File Format**: Parquet for columnar storage efficiency
4. **Caching**: BigQuery query result caching
5. **Batch Processing**: Bulk operations over row-by-row

### Cost Optimization
- Preemptible VMs for non-critical workloads
- Lifecycle policies (Standard → Nearline → Coldline)
- BigQuery slot reservations vs on-demand
- Dataproc auto-delete after 30 min idle

---

## Data Quality & Governance

### Data Quality Checks

**Silver Layer Validations**:
```python
is_quarantined = (
    customer_id IS NULL OR 
    email IS NULL OR 
    name IS NULL
)
```

**Metrics Tracked**:
- Null value percentages
- Duplicate records
- Data freshness (last update timestamp)
- Record counts at each layer

### Data Lineage
- Source → Bronze → Silver → Gold
- Tracked via audit logs
- Timestamp tracking at each stage

### Metadata Management
- Configuration-driven ingestion
- CSV-based table metadata
- Schema evolution support

---

## Disaster Recovery

### Backup Strategy
- **Cloud SQL**: Automated daily backups at 3:00 AM
- **BigQuery**: 7-day time travel
- **Cloud Storage**: Versioning enabled on configs

### Recovery Point Objective (RPO)
- **Database**: 24 hours
- **Data Lake**: Real-time (multi-region replication)

### Recovery Time Objective (RTO)
- **Database Restore**: < 1 hour
- **Pipeline Restart**: < 30 minutes

### High Availability
- Multi-zone Cloud SQL instances
- Regional Cloud Storage buckets
- Composer environment with multiple nodes

---

## Future Enhancements

1. **Streaming Ingestion**: Pub/Sub + Dataflow for real-time data
2. **Advanced Analytics**: BigQuery ML for predictive models
3. **Data Catalog**: Google Data Catalog for metadata management
4. **Enhanced Monitoring**: Custom dashboards with Looker Studio
5. **Data Quality Framework**: Great Expectations integration
6. **Multi-Region**: Global data distribution

---

For implementation details, see [setup.md](setup.md). For API documentation, see [api_reference.md](api_reference.md).

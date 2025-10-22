# API Reference Documentation

## GCP Retailer Data Lake - API & Configuration Reference

### Table of Contents

1. [Configuration Files](#configuration-files)
2. [PySpark Scripts API](#pyspark-scripts-api)
3. [BigQuery SQL API](#bigquery-sql-api)
4. [Airflow DAGs API](#airflow-dags-api)
5. [Cloud Build Configuration](#cloud-build-configuration)
6. [Environment Variables](#environment-variables)
7. [Function Reference](#function-reference)

---

## Configuration Files

### retailer_config.csv

Configuration file for retailer database ingestion.

**Location**: `gs://{BUCKET_NAME}/configs/retailer_config.csv`

**Schema**:
| Column | Type | Description |
|--------|------|-------------|
| `database` | STRING | Database identifier |
| `datasource` | STRING | Source database name |
| `tablename` | STRING | Table name to ingest |
| `loadtype` | STRING | "Full Load" or "Incremental" |
| `watermark` | STRING | Column for incremental loading (empty for full load) |
| `is_active` | INT | 1 = active, 0 = inactive |
| `targetpath` | STRING | GCS path for output |

**Example**:
```csv
database,datasource,tablename,loadtype,watermark,is_active,targetpath
retailer,retailer_db,products,Full Load,,1,landing/retailer-db/products
retailer,retailer_db,customers,Incremental,updated_at,1,landing/retailer-db/customers
```

**Usage**:
- Read by PySpark ingestion scripts
- Determines which tables to process
- Controls full vs incremental load strategy

---

### supplier_config.csv

Configuration file for supplier database ingestion.

**Location**: `gs://{BUCKET_NAME}/configs/supplier_config.csv`

**Schema**: Same as retailer_config.csv

**Example**:
```csv
database,datasource,tablename,loadtype,watermark,is_active,targetpath
supplier-db,mysql-db,suppliers,Full Load,created_at,1,supplier
supplier-db,mysql-db,product_suppliers,Incremental,last_updated,1,supplier
```

---

## PySpark Scripts API

### retailer_mysql_to_landing.py

Ingests data from Retailer MySQL database to Cloud Storage landing zone.

#### Configuration Variables

```python
GCS_BUCKET = "retailer-datalake-project-27032025"
LANDING_PATH = f"gs://{GCS_BUCKET}/landing/retailer-db/"
ARCHIVE_PATH = f"gs://{GCS_BUCKET}/landing/retailer-db/archive/"
CONFIG_FILE_PATH = f"gs://{GCS_BUCKET}/configs/retailer_config.csv"

BQ_PROJECT = "your-project-id"
BQ_AUDIT_TABLE = f"{BQ_PROJECT}.temp_dataset.audit_log"
BQ_LOG_TABLE = f"{BQ_PROJECT}.temp_dataset.pipeline_logs"

MYSQL_CONFIG = {
    "url": "jdbc:mysql://{HOST}:3306/retailerDB",
    "driver": "com.mysql.cj.jdbc.Driver",
    "user": "username",
    "password": "password"
}
```

#### Functions

##### `log_event(event_type, message, table=None)`

Logs pipeline events for monitoring and debugging.

**Parameters**:
- `event_type` (str): Type of event ("INFO", "SUCCESS", "ERROR")
- `message` (str): Log message
- `table` (str, optional): Table name associated with the event

**Returns**: None

**Example**:
```python
log_event("INFO", "Starting data extraction", table="customers")
log_event("SUCCESS", "Data extraction completed", table="customers")
log_event("ERROR", "Connection failed", table="orders")
```

---

##### `save_logs_to_gcs()`

Saves accumulated logs to Cloud Storage as JSON.

**Parameters**: None

**Returns**: None

**Output**: `gs://{BUCKET}/temp/pipeline_logs/pipeline_log_{timestamp}.json`

**Format**:
```json
[
  {
    "timestamp": "2025-10-23T05:30:15.123456",
    "event_type": "INFO",
    "message": "Starting extraction",
    "table": "customers"
  }
]
```

---

##### `save_logs_to_bigquery()`

Saves logs to BigQuery for analysis.

**Parameters**: None

**Returns**: None

**Target Table**: `{PROJECT}.temp_dataset.pipeline_logs`

**Schema**:
```sql
timestamp STRING
event_type STRING
message STRING
table STRING
```

---

##### `read_config_file()`

Reads configuration CSV from Cloud Storage.

**Parameters**: None

**Returns**: Spark DataFrame with configuration

**Example**:
```python
config_df = read_config_file()
# Returns DataFrame with columns: database, datasource, tablename, loadtype, watermark, is_active, targetpath
```

---

##### `move_existing_files_to_archive(table)`

Moves existing data files to date-partitioned archive folder.

**Parameters**:
- `table` (str): Table name

**Returns**: None

**Archive Structure**:
```
gs://{BUCKET}/landing/retailer-db/archive/
  └── {table}/
      └── {YYYY}/
          └── {MM}/
              └── {DD}/
                  └── {table}_{DDMMYYYY}.json
```

**Example**:
```python
move_existing_files_to_archive("customers")
# Moves: landing/retailer-db/customers/customers_23102025.json
# To: landing/retailer-db/archive/customers/2025/10/23/customers_23102025.json
```

---

##### `get_latest_watermark(table_name)`

Retrieves the latest watermark timestamp from audit log.

**Parameters**:
- `table_name` (str): Table name

**Returns**: str - Latest timestamp or "1900-01-01 00:00:00"

**Example**:
```python
watermark = get_latest_watermark("customers")
# Returns: "2025-10-22 05:30:15"
```

**SQL Query**:
```sql
SELECT MAX(load_timestamp) AS latest_timestamp
FROM `{BQ_AUDIT_TABLE}`
WHERE tablename = '{table_name}'
```

---

##### `extract_and_save_to_landing(table, load_type, watermark_col)`

Main extraction function that reads from MySQL and writes to Cloud Storage.

**Parameters**:
- `table` (str): Table name to extract
- `load_type` (str): "Full Load" or "Incremental"
- `watermark_col` (str): Column name for incremental loading

**Returns**: None

**Process**:
1. Get latest watermark (for incremental)
2. Build SQL query
3. Extract data via JDBC
4. Convert to JSON
5. Write to Cloud Storage
6. Update audit log

**Example**:
```python
extract_and_save_to_landing(
    table="customers",
    load_type="Incremental",
    watermark_col="updated_at"
)
```

**Output File**: `gs://{BUCKET}/landing/retailer-db/customers/customers_23102025.json`

**Audit Log Entry**:
```sql
INSERT INTO audit_log VALUES (
  'customers',
  'Incremental',
  1523,  -- record count
  '2025-10-23 05:30:15',
  'SUCCESS'
)
```

---

### supplier_mysql_to_landing.py

Similar to retailer script but configured for supplier database.

**Key Differences**:
- Different MySQL connection URL
- Different config file: `supplier_config.csv`
- Different landing path: `landing/supplier-db/`

---

### customer_reviews_to_landing.py

Ingests customer reviews from external API.

#### Configuration

```python
API_URL = "https://{api-id}.mockapi.io/retailer/reviews"
GCS_BUCKET = "retailer-datalake-project-27032025"
GCS_PATH = "landing/customer_reviews/customer_reviews_{date}.parquet"
```

#### Process Flow

1. **Fetch from API**:
```python
response = requests.get(API_URL)
data = response.json()
```

2. **Convert to DataFrame**:
```python
df_pandas = pd.DataFrame(data)
```

3. **Save as Parquet**:
```python
df_pandas.to_parquet(local_file, index=False)
```

4. **Upload to GCS**:
```python
blob.upload_from_filename(local_file)
```

**Output**: `gs://{BUCKET}/landing/customer_reviews/customer_reviews_20251023.parquet`

---

## BigQuery SQL API

### Bronze Layer - External Tables

#### Products Table

```sql
CREATE EXTERNAL TABLE IF NOT EXISTS `{PROJECT}.bronze_dataset.products`(
    product_id INT64,
    name STRING,
    category_id INT64,
    price FLOAT64,
    updated_at STRING
)
OPTIONS (
  format = 'JSON',
  uris = ['gs://{BUCKET}/landing/retailer-db/products/*.json']
);
```

**Usage**:
```sql
-- Query bronze data
SELECT * FROM `{PROJECT}.bronze_dataset.products`
WHERE product_id = 101;
```

---

### Silver Layer - Managed Tables with SCD Type 2

#### Customers Table (SCD Type 2 Pattern)

**Schema**:
```sql
CREATE TABLE IF NOT EXISTS `{PROJECT}.Silver_dataset.customers`(
    customer_id INT64,
    name STRING,
    email STRING,
    updated_at STRING,
    is_quarantined BOOL,
    effective_start_date TIMESTAMP,
    effective_end_date TIMESTAMP,
    is_active BOOL
);
```

**Update Process**:

**Step 1: Mark Changed Records as Inactive**
```sql
MERGE INTO `{PROJECT}.Silver_dataset.customers` target
USING (
  SELECT DISTINCT *,
    CASE 
      WHEN customer_id IS NULL OR email IS NULL OR name IS NULL 
      THEN TRUE ELSE FALSE 
    END AS is_quarantined,
    CURRENT_TIMESTAMP() AS effective_start_date,
    CURRENT_TIMESTAMP() AS effective_end_date,
    TRUE as is_active
  FROM `{PROJECT}.Bronze_dataset.customers`
) source
ON target.customer_id = source.customer_id 
   AND target.is_active = true
WHEN MATCHED AND (
  target.name != source.name OR
  target.email != source.email OR
  target.updated_at != source.updated_at
) THEN UPDATE SET 
  target.is_active = false,
  target.effective_end_date = current_timestamp();
```

**Step 2: Insert New Versions**
```sql
MERGE INTO `{PROJECT}.Silver_dataset.customers` target
USING (
  SELECT DISTINCT *,
    CASE 
      WHEN customer_id IS NULL OR email IS NULL OR name IS NULL 
      THEN TRUE ELSE FALSE 
    END AS is_quarantined,
    CURRENT_TIMESTAMP() AS effective_start_date,
    CURRENT_TIMESTAMP() AS effective_end_date,
    TRUE as is_active
  FROM `{PROJECT}.Bronze_dataset.customers`
) source
ON target.customer_id = source.customer_id 
   AND target.is_active = true
WHEN NOT MATCHED THEN 
  INSERT (customer_id, name, email, updated_at, is_quarantined, 
          effective_start_date, effective_end_date, is_active)
  VALUES (source.customer_id, source.name, source.email, 
          source.updated_at, source.is_quarantined, 
          source.effective_start_date, source.effective_end_date, 
          source.is_active);
```

**Querying Historical Data**:
```sql
-- Get current active records
SELECT * FROM `{PROJECT}.Silver_dataset.customers`
WHERE is_active = TRUE;

-- Get historical versions for a customer
SELECT * FROM `{PROJECT}.Silver_dataset.customers`
WHERE customer_id = 123
ORDER BY effective_start_date DESC;

-- Point-in-time query (as of specific date)
SELECT * FROM `{PROJECT}.Silver_dataset.customers`
WHERE customer_id = 123
  AND effective_start_date <= '2025-10-15'
  AND (effective_end_date > '2025-10-15' OR is_active = TRUE);
```

---

### Gold Layer - Business Metrics

#### Sales Summary Table

```sql
CREATE TABLE IF NOT EXISTS `{PROJECT}.Gold_dataset.sales_summary`
AS
SELECT 
    o.order_date,
    p.category_id,
    c.name AS category_name,
    oi.product_id,
    p.name AS product_name,
    SUM(oi.quantity) AS total_units_sold,
    SUM(oi.price * oi.quantity) AS total_sales,
    COUNT(DISTINCT o.customer_id) AS unique_customers
FROM `{PROJECT}.Silver_dataset.orders` o
JOIN `{PROJECT}.Silver_dataset.order_items` oi 
  ON o.order_id = oi.order_id
JOIN `{PROJECT}.Silver_dataset.products` p 
  ON oi.product_id = p.product_id
JOIN `{PROJECT}.Silver_dataset.categories` c 
  ON p.category_id = c.category_id
WHERE o.is_active = TRUE
GROUP BY 1, 2, 3, 4, 5;
```

**Usage**:
```sql
-- Top selling products
SELECT product_name, total_sales
FROM `{PROJECT}.Gold_dataset.sales_summary`
ORDER BY total_sales DESC
LIMIT 10;

-- Sales by category
SELECT category_name, SUM(total_sales) as category_sales
FROM `{PROJECT}.Gold_dataset.sales_summary`
GROUP BY category_name
ORDER BY category_sales DESC;
```

---

## Airflow DAGs API

### parent_dag.py

Master orchestrator that triggers child DAGs.

**DAG ID**: `parent_dag`

**Schedule**: `0 5 * * *` (Daily at 5:00 AM UTC)

**Configuration**:
```python
ARGS = {
    "owner": "data-engineering-team",
    "start_date": days_ago(1),
    "depends_on_past": False,
    "email_on_failure": True,
    "email": ["alerts@company.com"],
    "retries": 1,
    "retry_delay": timedelta(minutes=5)
}
```

**Tasks**:
1. `trigger_pyspark_dag`: Triggers data ingestion
2. `trigger_bigquery_dag`: Triggers layer processing

**Dependency**: `trigger_pyspark_dag >> trigger_bigquery_dag`

---

### pyspark_dag.py

Executes PySpark ingestion jobs on Cloud Dataproc.

**DAG ID**: `pyspark_dag`

**Schedule**: None (triggered by parent)

**Tasks**:
```python
retailer_ingestion = DataprocSubmitJobOperator(
    task_id="retailer_ingestion",
    job={
        "reference": {"project_id": PROJECT_ID},
        "placement": {"cluster_name": CLUSTER_NAME},
        "pyspark_job": {
            "main_python_file_uri": "gs://{BUCKET}/scripts/retailer_mysql_to_landing.py"
        }
    }
)

supplier_ingestion = DataprocSubmitJobOperator(...)
api_ingestion = DataprocSubmitJobOperator(...)
```

**Parallel Execution**: All three tasks run in parallel

---

### bigquery_dag.py

Executes BigQuery SQL scripts for Bronze, Silver, Gold layers.

**DAG ID**: `bigquery_dag`

**Schedule**: None (triggered by parent)

**Tasks**:

```python
bronze_tables = BigQueryInsertJobOperator(
    task_id="bronze_tables",
    configuration={
        "query": {
            "query": BRONZE_QUERY,  # Read from bronzeTable.sql
            "useLegacySql": False,
            "priority": "BATCH"
        }
    }
)

silver_tables = BigQueryInsertJobOperator(...)
gold_tables = BigQueryInsertJobOperator(...)
```

**Dependency**: `bronze_tables >> silver_tables >> gold_tables`

**SQL Files**:
- `/home/airflow/gcs/data/BQ/bronzeTable.sql`
- `/home/airflow/gcs/data/BQ/silverTable.sql`
- `/home/airflow/gcs/data/BQ/goldTable.sql`

---

## Cloud Build Configuration

### cloudbuild.yaml

Automates DAG and data file deployment to Composer.

**Trigger**: Git push to main branch

**Steps**:

**Step 1: Install Dependencies**
```yaml
- name: 'python'
  entrypoint: pip
  args: ["install", "-r", "utils/requirements.txt", "--user"]
```

**Step 2: Deploy to Composer**
```yaml
- name: 'python'
  entrypoint: python
  args:
    - "utils/add_dags_to_composer.py"
    - "--dags_directory=workflows/"
    - "--dags_bucket=us-central1-demo-instance-xxxxx-bucket"
    - "--data_directory=data/"
```

**Substitutions**:
```yaml
_DAGS_DIRECTORY: "workflows/"
_DAGS_BUCKET: "{composer-bucket-name}"
_DATA_DIRECTORY: "data/"
```

---

## Environment Variables

### Cloud Composer Variables

Set via Airflow UI or `gcloud` command:

```bash
gcloud composer environments update {ENV_NAME} \
  --location={REGION} \
  --update-env-variables \
    GCS_BUCKET=retailer-datalake-project,\
    BQ_PROJECT=your-project-id,\
    REGION=us-central1,\
    MYSQL_RETAILER_HOST=34.123.137.7,\
    MYSQL_SUPPLIER_HOST=34.57.241.120,\
    API_ENDPOINT=https://mockapi.io/reviews
```

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GCS_BUCKET` | Cloud Storage bucket name | `retailer-datalake-project` |
| `BQ_PROJECT` | BigQuery project ID | `your-project-id` |
| `REGION` | GCP region | `us-central1` |
| `MYSQL_RETAILER_HOST` | Retailer DB IP | `34.123.137.7` |
| `MYSQL_SUPPLIER_HOST` | Supplier DB IP | `34.57.241.120` |
| `API_ENDPOINT` | Customer reviews API URL | `https://api.mock.io/reviews` |

---

## Function Reference

### Utility Functions

#### add_dags_to_composer.py

##### `_create_file_list(directory, name_replacement)`

Creates a temporary copy of files for upload.

**Parameters**:
- `directory` (str): Source directory path
- `name_replacement` (str): GCS path prefix

**Returns**: (str, list) - Temp directory path and file list

---

##### `upload_to_composer(directory, bucket_name, name_replacement)`

Uploads files to Composer's GCS bucket.

**Parameters**:
- `directory` (str): Local directory with files
- `bucket_name` (str): Composer bucket name
- `name_replacement` (str): "dags/" or "data/"

**Example**:
```python
upload_to_composer(
    directory="workflows/",
    bucket_name="us-central1-composer-bucket",
    name_replacement="dags/"
)
```

---

## Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| `CONNECTION_ERROR` | Failed to connect to MySQL | Check network, credentials |
| `FILE_NOT_FOUND` | Config file missing | Verify GCS path |
| `SCHEMA_MISMATCH` | Unexpected data types | Review bronze table schema |
| `QUARANTINE_THRESHOLD` | >10% records quarantined | Investigate data quality |
| `TIMEOUT` | Job exceeded 30 min | Optimize query or increase timeout |

---

For architecture details, see [architecture.md](architecture.md). For setup instructions, see [setup.md](setup.md).

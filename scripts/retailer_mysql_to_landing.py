from google.cloud import storage, bigquery
import pandas as pd
from pyspark.sql import SparkSession
import datetime
import json

# Initialize Spark Session
spark = SparkSession.builder.appName("RetailerMySQLToLanding").getOrCreate()

# Google Cloud Storage (GCS) Configuration variables
GCS_BUCKET = "retailer-datalake-project-27032025"
LANDING_PATH = f"gs://{GCS_BUCKET}/landing/retailer-db/"
ARCHIVE_PATH = f"gs://{GCS_BUCKET}/landing/retailer-db/archive/"
CONFIG_FILE_PATH = f"gs://{GCS_BUCKET}/configs/retailer_config.csv"

# BigQuery Configuration
BQ_PROJECT = "avd-databricks-demo"
BQ_AUDIT_TABLE = f"{BQ_PROJECT}.temp_dataset.audit_log"
BQ_LOG_TABLE = f"{BQ_PROJECT}.temp_dataset.pipeline_logs"
BQ_TEMP_PATH = f"{GCS_BUCKET}/temp/"  

# MySQL Configuration
MYSQL_CONFIG = {
    "url": "jdbc:mysql://34.123.137.7:3306/retailerDB?useSSL=false&allowPublicKeyRetrieval=true",
    "driver": "com.mysql.cj.jdbc.Driver",
    "user": "anuj",
    "password": "Ananyadrank7up?"
}

# Initialize GCS & BigQuery Clients
storage_client = storage.Client()
bq_client = bigquery.Client()

# Logging Mechanism
log_entries = []  # Stores logs before writing to GCS
##---------------------------------------------------------------------------------------------------##
def log_event(event_type, message, table=None):
    """Log an event and store it in the log list"""
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "event_type": event_type,
        "message": message,
        "table": table
    }
    log_entries.append(log_entry)
    print(f"[{log_entry['timestamp']}] {event_type} - {message}")  # Print for visibility
##---------------------------------------------------------------------------------------------------##
def save_logs_to_gcs():
    """Save logs to a JSON file and upload to GCS"""
    log_filename = f"pipeline_log_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    log_filepath = f"temp/pipeline_logs/{log_filename}"  
    
    json_data = json.dumps(log_entries, indent=4)

    # Get GCS bucket
    bucket = storage_client.bucket(GCS_BUCKET)
    blob = bucket.blob(log_filepath)
    
    # Upload JSON data as a file
    blob.upload_from_string(json_data, content_type="application/json")

    print(f"✅ Logs successfully saved to GCS at gs://{GCS_BUCKET}/{log_filepath}")
    
def save_logs_to_bigquery():
    """Save logs to BigQuery"""
    if log_entries:
        log_df = spark.createDataFrame(log_entries)
        log_df.write.format("bigquery") \
            .option("table", BQ_LOG_TABLE) \
            .option("temporaryGcsBucket", BQ_TEMP_PATH) \
            .mode("append") \
            .save()
        print("✅ Logs stored in BigQuery for future analysis")


##---------------------------------------------------------------------------------------------------##
# Function to Read Config File from GCS
def read_config_file():
    df = spark.read.csv(CONFIG_FILE_PATH, header=True)
    log_event("INFO", "✅ Successfully read the config file")
    return df
##---------------------------------------------------------------------------------------------------##
# Function to Move Existing Files to Archive
def move_existing_files_to_archive(table):
    blobs = list(storage_client.bucket(GCS_BUCKET).list_blobs(prefix=f"landing/retailer-db/{table}/"))
    existing_files = [blob.name for blob in blobs if blob.name.endswith(".json")]
    
    if not existing_files:
        log_event("INFO", f"No existing files for table {table}")
        return
    
    for file in existing_files:
        source_blob = storage_client.bucket(GCS_BUCKET).blob(file)
        
        # Extract Date from File Name (products_27032025.json)
        date_part = file.split("_")[-1].split(".")[0]
        year, month, day = date_part[-4:], date_part[2:4], date_part[:2]
        
        # Move to Archive
        archive_path = f"landing/retailer-db/archive/{table}/{year}/{month}/{day}/{file.split('/')[-1]}"
        destination_blob = storage_client.bucket(GCS_BUCKET).blob(archive_path)
        
        # Copy file to archive and delete original
        storage_client.bucket(GCS_BUCKET).copy_blob(source_blob, storage_client.bucket(GCS_BUCKET), destination_blob.name)
        source_blob.delete()
        
        log_event("INFO", f"✅ Moved {file} to {archive_path}", table=table)    
        
##---------------------------------------------------------------------------------------------------##

# Function to Get Latest Watermark from BigQuery Audit Table
def get_latest_watermark(table_name):
    query = f"""
        SELECT MAX(load_timestamp) AS latest_timestamp
        FROM `{BQ_AUDIT_TABLE}`
        WHERE tablename = '{table_name}'
    """
    query_job = bq_client.query(query)
    result = query_job.result()
    for row in result:
        return row.latest_timestamp if row.latest_timestamp else "1900-01-01 00:00:00"
    return "1900-01-01 00:00:00"
        
##---------------------------------------------------------------------------------------------------##

# Function to Extract Data from MySQL and Save to GCS
def extract_and_save_to_landing(table, load_type, watermark_col):
    try:
        # Get Latest Watermark
        last_watermark = get_latest_watermark(table) if load_type.lower() == "incremental" else None
        log_event("INFO", f"Latest watermark for {table}: {last_watermark}", table=table)
        
        # Generate SQL Query
        query = f"(SELECT * FROM {table}) AS t" if load_type.lower() == "full load" else \
                f"(SELECT * FROM {table} WHERE {watermark_col} > '{last_watermark}') AS t"
        
        # Read Data from MySQL
        df = (spark.read
                .format("jdbc")
                .option("url", MYSQL_CONFIG["url"])
                .option("user", MYSQL_CONFIG["user"])
                .option("password", MYSQL_CONFIG["password"])
                .option("driver", MYSQL_CONFIG["driver"])
                .option("dbtable", query)
                .load())
        log_event("SUCCESS", f"✅ Successfully extracted data from {table}", table=table)
        
        # Convert Spark DataFrame to JSON
        pandas_df = df.toPandas()
        json_data = pandas_df.to_json(orient="records", lines=True)
        
        # Generate File Path in GCS
        today = datetime.datetime.today().strftime('%d%m%Y')
        JSON_FILE_PATH = f"landing/retailer-db/{table}/{table}_{today}.json"
        
        # Upload JSON to GCS
        bucket = storage_client.bucket(GCS_BUCKET)
        blob = bucket.blob(JSON_FILE_PATH)
        blob.upload_from_string(json_data, content_type="application/json")

        log_event("SUCCESS", f"✅ JSON file successfully written to gs://{GCS_BUCKET}/{JSON_FILE_PATH}", table=table)
        
        # Insert Audit Entry
        audit_df = spark.createDataFrame([
            (table, load_type, df.count(), datetime.datetime.now(), "SUCCESS")], ["tablename", "load_type", "record_count", "load_timestamp", "status"])

        (audit_df.write.format("bigquery")
            .option("table", BQ_AUDIT_TABLE)
            .option("temporaryGcsBucket", GCS_BUCKET)
            .mode("append")
            .save())

        log_event("SUCCESS", f"✅ Audit log updated for {table}", table=table)
    
    except Exception as e:
        log_event("ERROR", f"Error processing {table}: {str(e)}", table=table)
        
##---------------------------------------------------------------------------------------------------##

# Main Execution
config_df = read_config_file()

for row in config_df.collect():
    if row["is_active"] == '1':
        db, src, table, load_type, watermark, _, targetpath = row
        move_existing_files_to_archive(table)
        extract_and_save_to_landing(table, load_type, watermark)

save_logs_to_gcs()
save_logs_to_bigquery()       
        
print("✅ Pipeline completed successfully!")
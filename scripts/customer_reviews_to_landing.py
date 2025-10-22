from pyspark.sql import SparkSession
import requests
import json
import pandas as pd
import datetime
from google.cloud import storage

# Initialize Spark Session
spark = SparkSession.builder.appName("CustomerReviewsAPI").getOrCreate()

# API Endpoint
API_URL = "https://67e51d5418194932a5849592.mockapi.io/retailer/reviews"

# Step 1: Fetch data from API
response = requests.get(API_URL)

if response.status_code == 200:
    data = response.json()
    print(f"✅ Successfully fetched {len(data)} records.")
else:
    print(f"❌ Failed to fetch data. Status Code: {response.status_code}")
    exit()
    
# Step 2: Convert API Data to Pandas DataFrame
df_pandas = pd.DataFrame(data)

# Step 3: Get Current Date for File Naming
today = datetime.datetime.today().strftime('%Y%m%d')  # Format: YYYYMMDD

# Step 4: Define File Paths with Date
local_parquet_file = f"/tmp/customer_reviews_{today}.parquet"
GCS_BUCKET = "retailer-datalake-project-27032025"
GCS_PATH = f"landing/customer_reviews/customer_reviews_{today}.parquet"

# Step 5: Save Pandas DataFrame as Parquet Locally
df_pandas.to_parquet(local_parquet_file, index=False)

# Step 6: Upload Parquet File to GCS
storage_client = storage.Client()
bucket = storage_client.bucket(GCS_BUCKET)
blob = bucket.blob(GCS_PATH)
blob.upload_from_filename(local_parquet_file)

print(f"✅ Data successfully written to gs://{GCS_BUCKET}/{GCS_PATH}")
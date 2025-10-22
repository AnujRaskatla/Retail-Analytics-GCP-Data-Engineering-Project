CREATE EXTERNAL TABLE IF NOT EXISTS `avd-databricks-demo.bronze_dataset.orders`(
    order_id INT64,
    customer_id INT64,
    order_date STRING,
    total_amount FLOAT64,
    updated_at STRING
)
OPTIONS (
  format = 'JSON',
  uris = ['gs://retailer-datalake-project-27032025/landing/retailer-db/orders/*.json']
);

CREATE EXTERNAL TABLE IF NOT EXISTS `avd-databricks-demo.bronze_dataset.customers`
(
    customer_id INT64,
    name STRING,
    email STRING,
    updated_at STRING
)
OPTIONS (
    format = 'JSON',
    uris = ['gs://retailer-datalake-project-27032025/landing/retailer-db/customers/*.json']
);

CREATE EXTERNAL TABLE IF NOT EXISTS `avd-databricks-demo.bronze_dataset.products`
(
    product_id INT64,
    name STRING,
    category_id INT64,
    price FLOAT64,
    updated_at STRING
)
OPTIONS (
    format = 'JSON',
    uris = ['gs://retailer-datalake-project-27032025/landing/retailer-db/products/*.json']
);

CREATE EXTERNAL TABLE IF NOT EXISTS `avd-databricks-demo.bronze_dataset.categories`
(
    category_id INT64,
    name STRING,
    updated_at STRING
)
OPTIONS (
    format = 'JSON',
    uris = ['gs://retailer-datalake-project-27032025/landing/retailer-db/categories/*.json']
);

CREATE EXTERNAL TABLE IF NOT EXISTS `avd-databricks-demo.bronze_dataset.order_items`
(
    order_item_id INT64,
    order_id INT64,
    product_id INT64,
    quantity INT64,
    price FLOAT64,
    updated_at STRING
)
OPTIONS (
    format = 'JSON',
    uris = ['gs://retailer-datalake-project-27032025/landing/retailer-db/order_items/*.json']
);
-------------------------------------------------------------------------------------------------------------
-- Suppliers Table
CREATE EXTERNAL TABLE IF NOT EXISTS `avd-databricks-demo.bronze_dataset.suppliers` (
    supplier_id INT64,
    supplier_name STRING,
    contact_name STRING,
    phone STRING,
    email STRING,
    address STRING,
    city STRING,
    country STRING,
    created_at STRING
)
OPTIONS (
  format = 'JSON',
  uris = ['gs://retailer-datalake-project-27032025/landing/supplier-db/suppliers/*.json']
);

-- Product Suppliers Table (Mapping suppliers to products)
CREATE EXTERNAL TABLE IF NOT EXISTS `avd-databricks-demo.bronze_dataset.product_suppliers` (
    supplier_id INT64,
    product_id INT64,
    supply_price FLOAT64,
    last_updated STRING
)
OPTIONS (
  format = 'JSON',
  uris = ['gs://retailer-datalake-project-27032025/landing/supplier-db/product_suppliers/*.json']
);

-------------------------------------------------------------------------------------------------------------

CREATE OR REPLACE EXTERNAL TABLE `avd-databricks-demo.bronze_dataset.customer_reviews` (
  id STRING,
  customer_id INT64,
  product_id INT64,
  rating INT64,
  review_text STRING,
  review_date STRING
)
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://retailer-datalake-project-27032025/landing/customer_reviews/customer_reviews_*.parquet']
);

-------------------------------------------------------------------------------------------------------------
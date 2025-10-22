--1️. Sales Summary (sales_summary)
CREATE TABLE IF NOT EXISTS `oceanic-throne-472718-k1.Gold_dataset.sales_summary`
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
FROM `oceanic-throne-472718-k1.Silver_dataset.orders` o
JOIN `oceanic-throne-472718-k1.Silver_dataset.order_items` oi ON o.order_id = oi.order_id
JOIN `oceanic-throne-472718-k1.Silver_dataset.products` p ON oi.product_id = p.product_id
JOIN `oceanic-throne-472718-k1.Silver_dataset.categories` c ON p.category_id = c.category_id
WHERE o.is_active = TRUE
GROUP BY 1, 2, 3, 4, 5;

-----------------------------------------------------------------------------------------------------------
-- 2. Customer Engagement Metrics (customer_engagement)

CREATE TABLE IF NOT EXISTS `oceanic-throne-472718-k1.Gold_dataset.customer_engagement`
AS
SELECT 
    c.customer_id,
    c.name AS customer_name,
    COUNT(o.order_id) AS total_orders,
    SUM(oi.price * oi.quantity) AS total_spent,
    MAX(o.order_date) AS last_order_date,
    DATE_DIFF(CURRENT_DATE(), DATE(TIMESTAMP_MILLIS(CAST(o.order_date AS INT64))), DAY) AS days_since_last_order,
    AVG(oi.price * oi.quantity) AS avg_order_value
FROM `oceanic-throne-472718-k1.Silver_dataset.customers` c
LEFT JOIN `oceanic-throne-472718-k1.Silver_dataset.orders` o ON c.customer_id = o.customer_id
LEFT JOIN `oceanic-throne-472718-k1.Silver_dataset.order_items` oi ON o.order_id = oi.order_id
WHERE c.is_active = TRUE
GROUP BY 1, 2, 6;

-----------------------------------------------------------------------------------------------------------
--3. Product Performance (product_performance)

CREATE TABLE IF NOT EXISTS `oceanic-throne-472718-k1.Gold_dataset.product_performance`
AS
SELECT 
    p.product_id,
    p.name AS product_name,
    p.category_id,
    c.name AS category_name,
    ps.supplier_id,
    s.supplier_name,
    SUM(oi.quantity) AS total_units_sold,
    SUM(oi.price * oi.quantity) AS total_revenue,
    AVG(cr.rating) AS avg_rating,
    COUNT(cr.review_text) AS total_reviews
FROM `oceanic-throne-472718-k1.Silver_dataset.products` p
LEFT JOIN `oceanic-throne-472718-k1.Silver_dataset.categories` c ON p.category_id = c.category_id
LEFT JOIN `oceanic-throne-472718-k1.Silver_dataset.product_suppliers` ps ON p.product_id = ps.product_id
LEFT JOIN `oceanic-throne-472718-k1.Silver_dataset.suppliers` s ON ps.supplier_id = s.supplier_id
LEFT JOIN `oceanic-throne-472718-k1.Silver_dataset.order_items` oi ON p.product_id = oi.product_id
LEFT JOIN `oceanic-throne-472718-k1.Silver_dataset.customer_reviews` cr ON p.product_id = cr.product_id
WHERE p.is_quarantined = FALSE
GROUP BY 1, 2, 3, 4, 5, 6;

-----------------------------------------------------------------------------------------------------------
--4. Supplier Performance (supplier_analysis)
CREATE TABLE IF NOT EXISTS `oceanic-throne-472718-k1.Gold_dataset.supplier_analysis`
AS
SELECT 
    s.supplier_id,
    s.supplier_name,
    COUNT(DISTINCT ps.product_id) AS total_products_supplied,
    SUM(oi.quantity) AS total_units_sold,
    SUM(oi.price * oi.quantity) AS total_revenue
FROM `oceanic-throne-472718-k1.Silver_dataset.suppliers` s
LEFT JOIN `oceanic-throne-472718-k1.Silver_dataset.product_suppliers` ps ON s.supplier_id = ps.supplier_id
LEFT JOIN `oceanic-throne-472718-k1.Silver_dataset.order_items` oi ON ps.product_id = oi.product_id
WHERE s.is_quarantined = FALSE
GROUP BY 1, 2;

-----------------------------------------------------------------------------------------------------------
--5. Customer Reviews Summary (customer_reviews_summary)
CREATE TABLE IF NOT EXISTS `oceanic-throne-472718-k1.Gold_dataset.customer_reviews_summary`
AS
SELECT 
    p.product_id,
    p.name AS product_name,
    AVG(cr.rating) AS avg_rating,
    COUNT(cr.review_text) AS total_reviews,
    COUNT(CASE WHEN cr.rating >= 4 THEN 1 END) AS positive_reviews,
    COUNT(CASE WHEN cr.rating < 3 THEN 1 END) AS negative_reviews
FROM `oceanic-throne-472718-k1.Silver_dataset.products` p
LEFT JOIN `oceanic-throne-472718-k1.Silver_dataset.customer_reviews` cr ON p.product_id = cr.product_id
WHERE p.is_quarantined = FALSE
GROUP BY 1, 2;

-----------------------------------------------------------------------------------------------------------
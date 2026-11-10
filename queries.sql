-- ====================================================================
-- RETAIL STORE SQL QUERIES (Basic to Intermediate)
-- Database: retail_store.db
-- ====================================================================

-- --------------------------------------------------------------------
-- QUERY 1: Product-Wise Sales, Costs, and Gross Profit
-- Concepts: LEFT JOIN, SUM(), ROUND(), COALESCE(), Calculated Fields
-- --------------------------------------------------------------------
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    p.cost_price,
    p.selling_price,
    COALESCE(SUM(s.quantity), 0) AS total_units_sold,
    ROUND(COALESCE(SUM(s.quantity * p.selling_price * (1.0 - s.discount_pct)), 0), 2) AS net_revenue,
    ROUND(COALESCE(SUM(s.quantity * p.cost_price), 0), 2) AS total_cogs,
    ROUND(COALESCE(SUM(s.quantity * (p.selling_price * (1.0 - s.discount_pct) - p.cost_price)), 0), 2) AS gross_profit
FROM products p
LEFT JOIN sales s ON p.product_id = s.product_id
GROUP BY p.product_id, p.product_name, p.category, p.cost_price, p.selling_price
ORDER BY gross_profit DESC;


-- --------------------------------------------------------------------
-- QUERY 2: Monthly Sales Performance by Category
-- Concepts: Date String Slicing (substr), Multi-column GROUP BY
-- --------------------------------------------------------------------
SELECT 
    SUBSTR(s.sale_date, 1, 7) AS sale_month,
    p.category,
    COUNT(s.sale_id) AS total_transactions,
    SUM(s.quantity) AS total_items_sold,
    ROUND(SUM(s.quantity * p.selling_price * (1.0 - s.discount_pct)), 2) AS monthly_revenue
FROM sales s
INNER JOIN products p ON s.product_id = p.product_id
GROUP BY sale_month, p.category
ORDER BY sale_month ASC, monthly_revenue DESC;


-- --------------------------------------------------------------------
-- QUERY 3: Customer Value Segmentation
-- Concepts: Common Table Expression (CTE), CASE WHEN, Customer Ranking
-- --------------------------------------------------------------------
WITH customer_orders AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        c.city,
        COUNT(s.sale_id) AS order_count,
        COALESCE(SUM(s.quantity), 0) AS total_units_purchased,
        ROUND(COALESCE(SUM(s.quantity * p.selling_price * (1.0 - s.discount_pct)), 0), 2) AS total_spend
    FROM customers c
    LEFT JOIN sales s ON c.customer_id = s.customer_id
    LEFT JOIN products p ON s.product_id = p.product_id
    GROUP BY c.customer_id, c.customer_name, c.city
)
SELECT 
    customer_id,
    customer_name,
    city,
    order_count,
    total_units_purchased,
    total_spend,
    CASE 
        WHEN total_spend >= 300 THEN 'Gold Tier'
        WHEN total_spend >= 150 THEN 'Silver Tier'
        ELSE 'Bronze Tier'
    END AS loyalty_segment
FROM customer_orders
ORDER BY total_spend DESC;


-- --------------------------------------------------------------------
-- QUERY 4: Top Customer in Each City (Window Function)
-- Concepts: Window Functions (ROW_NUMBER() OVER PARTITION BY), CTE
-- --------------------------------------------------------------------
WITH customer_spending AS (
    SELECT 
        c.city,
        c.customer_name,
        COUNT(s.sale_id) AS total_orders,
        ROUND(COALESCE(SUM(s.quantity * p.selling_price * (1.0 - s.discount_pct)), 0), 2) AS total_spent
    FROM customers c
    LEFT JOIN sales s ON c.customer_id = s.customer_id
    LEFT JOIN products p ON s.product_id = p.product_id
    GROUP BY c.city, c.customer_name
),
ranked_customers AS (
    SELECT 
        city,
        customer_name,
        total_orders,
        total_spent,
        ROW_NUMBER() OVER (
            PARTITION BY city 
            ORDER BY total_spent DESC
        ) AS rank_in_city
    FROM customer_spending
)
SELECT 
    city,
    customer_name AS top_customer,
    total_orders,
    total_spent
FROM ranked_customers
WHERE rank_in_city = 1
ORDER BY total_spent DESC;


-- --------------------------------------------------------------------
-- QUERY 5: Discount Impact Analysis
-- Concepts: Aggregate calculations, comparing Gross vs Net Revenue
-- --------------------------------------------------------------------
SELECT 
    p.category,
    COUNT(s.sale_id) AS total_transactions,
    SUM(s.quantity) AS total_units_sold,
    ROUND(SUM(s.quantity * p.selling_price), 2) AS gross_revenue_before_discount,
    ROUND(SUM(s.quantity * p.selling_price * (1.0 - s.discount_pct)), 2) AS net_revenue_after_discount,
    ROUND(SUM(s.quantity * p.selling_price * s.discount_pct), 2) AS total_discount_given,
    ROUND(AVG(s.discount_pct * 100), 1) AS avg_discount_pct
FROM sales s
JOIN products p ON s.product_id = p.product_id
GROUP BY p.category
ORDER BY total_discount_given DESC;

"""
Flask Web Application for Render Deployment
- Runs on standard library sqlite3 queries
- Serves the interactive Retail Analytics Dashboard
- Provides endpoints to download Excel CSV reports
"""

import os
import sqlite3
from flask import Flask, render_template, send_from_directory, abort

app = Flask(__name__)
DB_NAME = "retail_store.db"


def ensure_database_ready():
    """Ensure database and initial CSV reports exist before handling requests."""
    if not os.path.exists(DB_NAME):
        import database_setup
        import analysis_and_export
        database_setup.main()
        analysis_and_export.main()


@app.route("/")
def dashboard():
    ensure_database_ready()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 1. Product Profitability Query
    cursor.execute("""
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
    """)
    products = cursor.fetchall()

    # Calculate High-Level KPIs
    total_rev = sum(p[6] for p in products)
    total_prof = sum(p[8] for p in products)
    total_units = sum(p[5] for p in products)
    avg_margin = (total_prof / total_rev * 100) if total_rev > 0 else 0.0

    kpis = {
        "total_revenue": total_rev,
        "total_profit": total_prof,
        "total_units": total_units,
        "avg_margin": avg_margin
    }

    # 2. Top Customer per City Query (SQL Window Function)
    cursor.execute("""
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
    ranked AS (
        SELECT 
            city,
            customer_name,
            total_orders,
            total_spent,
            ROW_NUMBER() OVER (PARTITION BY city ORDER BY total_spent DESC) AS city_rank
        FROM customer_spending
    )
    SELECT city, customer_name, total_orders, total_spent
    FROM ranked
    WHERE city_rank = 1
    ORDER BY total_spent DESC;
    """)
    city_top = cursor.fetchall()

    # 3. Discount Impact Query
    cursor.execute("""
    SELECT 
        p.category,
        COUNT(s.sale_id) AS total_transactions,
        SUM(s.quantity) AS total_units_sold,
        ROUND(SUM(s.quantity * p.selling_price), 2) AS gross_revenue,
        ROUND(SUM(s.quantity * p.selling_price * (1.0 - s.discount_pct)), 2) AS net_revenue,
        ROUND(SUM(s.quantity * p.selling_price * s.discount_pct), 2) AS total_discounts_given
    FROM sales s
    JOIN products p ON s.product_id = p.product_id
    GROUP BY p.category
    ORDER BY total_discounts_given DESC;
    """)
    discounts = cursor.fetchall()

    conn.close()

    return render_template(
        "index.html",
        kpis=kpis,
        products=products,
        city_top=city_top,
        discounts=discounts
    )


@app.route("/download/<path:filename>")
def download_file(filename):
    """Allows downloading the CSV files directly for Excel."""
    allowed_files = {
        "product_profitability_report.csv",
        "customer_segments_report.csv",
        "top_customers_by_city.csv",
        "monthly_category_trend.csv",
        "discount_impact_analysis.csv"
    }
    if filename not in allowed_files:
        abort(404)

    return send_from_directory(".", filename, as_attachment=True)


@app.route("/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    ensure_database_ready()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

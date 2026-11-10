"""
Analysis & CSV Export Script (Standard Library Only)
Features:
- Product Profitability with Margins
- Customer Value & Loyalty Tier Segmentation
- Monthly Sales Trends
- NEW: Top Customer per City (Window Function in SQL)
- NEW: Discount Impact Analysis & Date-Range Filtering
"""

import csv
import sqlite3

DATABASE_NAME = "retail_store.db"


def export_product_profitability(cursor):
    """Fetches product sales and cost numbers, applies business rules, and saves to CSV."""
    query = """
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
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    csv_file = "product_profitability_report.csv"
    with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Product ID", "Product Name", "Category", "Cost Price ($)",
            "Selling Price ($)", "Units Sold", "Net Revenue ($)",
            "Total Cost ($)", "Gross Profit ($)", "Profit Margin (%)", "Performance Status"
        ])

        for row in rows:
            p_id, name, cat, cost, price, units, rev, total_cost, profit = row
            margin = round((profit / rev) * 100, 2) if rev > 0 else 0.0

            if profit >= 150:
                status = "Star Product"
            elif profit >= 60:
                status = "Moderate"
            else:
                status = "Underperforming"

            writer.writerow([
                p_id, name, cat, f"{cost:.2f}", f"{price:.2f}", units,
                f"{rev:.2f}", f"{total_cost:.2f}", f"{profit:.2f}",
                f"{margin:.2f}", status
            ])

    print(f"Generated: {csv_file} ({len(rows)} products)")


def export_customer_segments(cursor):
    """Analyzes customer spend and frequency, outputs customer loyalty report."""
    query = """
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
        total_spend
    FROM customer_orders
    ORDER BY total_spend DESC;
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    csv_file = "customer_segments_report.csv"
    with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Customer ID", "Customer Name", "City", "Total Orders",
            "Units Purchased", "Total Spend ($)", "Avg Spend per Order ($)", "Loyalty Tier"
        ])

        for row in rows:
            c_id, name, city, orders, units, spend = row
            avg_per_order = round(spend / orders, 2) if orders > 0 else 0.0

            if spend >= 250:
                tier = "Platinum"
            elif spend >= 150:
                tier = "Gold"
            elif spend >= 50:
                tier = "Silver"
            else:
                tier = "Bronze"

            writer.writerow([
                c_id, name, city, orders, units, f"{spend:.2f}", f"{avg_per_order:.2f}", tier
            ])

    print(f"Generated: {csv_file} ({len(rows)} customers)")


def export_top_customers_by_city(cursor):
    """NEW: Identifies the top customer in each city using a SQL Window function."""
    query = """
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
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    csv_file = "top_customers_by_city.csv"
    with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["City", "Top Customer", "Total Orders", "Total Spent ($)"])
        for row in rows:
            city, name, orders, spent = row
            writer.writerow([city, name, orders, f"{spent:.2f}"])

    print(f"Generated: {csv_file} ({len(rows)} cities)")


def export_discount_analysis(cursor, start_date=None, end_date=None):
    """NEW: Analyzes the revenue impact of discounts with optional date filtering."""
    where_clause = ""
    params = []

    if start_date and end_date:
        where_clause = "WHERE s.sale_date BETWEEN ? AND ?"
        params = [start_date, end_date]

    query = f"""
    SELECT 
        p.category,
        COUNT(s.sale_id) AS total_transactions,
        SUM(s.quantity) AS total_units_sold,
        ROUND(SUM(s.quantity * p.selling_price), 2) AS gross_revenue,
        ROUND(SUM(s.quantity * p.selling_price * (1.0 - s.discount_pct)), 2) AS net_revenue,
        ROUND(SUM(s.quantity * p.selling_price * s.discount_pct), 2) AS total_discounts_given,
        ROUND(AVG(s.discount_pct * 100), 1) AS avg_discount_pct
    FROM sales s
    JOIN products p ON s.product_id = p.product_id
    {where_clause}
    GROUP BY p.category
    ORDER BY total_discounts_given DESC;
    """

    cursor.execute(query, params)
    rows = cursor.fetchall()

    filename = "discount_impact_filtered.csv" if start_date else "discount_impact_analysis.csv"
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Category", "Transactions", "Units Sold",
            "Gross Revenue ($)", "Net Revenue ($)",
            "Discounts Given ($)", "Avg Discount (%)", "Discount Loss Rate (%)"
        ])

        for row in rows:
            cat, txns, units, gross, net, discount, avg_disc = row
            loss_rate = round((discount / gross) * 100, 2) if gross > 0 else 0.0

            writer.writerow([
                cat, txns, units, f"{gross:.2f}", f"{net:.2f}",
                f"{discount:.2f}", f"{avg_disc:.1f}%", f"{loss_rate:.2f}%"
            ])

    date_tag = f" [{start_date} to {end_date}]" if start_date else ""
    print(f"Generated: {filename}{date_tag}")


def main():
    print(f"Opening database: {DATABASE_NAME}...")
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Core reports
    export_product_profitability(cursor)
    export_customer_segments(cursor)

    # NEW Feature 1: Window functions in SQL (Top customer in each city)
    export_top_customers_by_city(cursor)

    # NEW Feature 2: Discount analysis (All time)
    export_discount_analysis(cursor)

    # NEW Feature 3: Discount analysis with Date-Range Filter (e.g., Jan-Feb 2026)
    export_discount_analysis(cursor, start_date="2026-01-01", end_date="2026-02-28")

    conn.close()
    print("\nAll CSV exports created successfully! Open them in Excel to inspect.")


if __name__ == "__main__":
    main()

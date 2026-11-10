"""
Standard Library WSGI Application (NO Flask, NO third-party frameworks)
Compatible with:
- gunicorn app:app (Render production)
- python app.py (Local standalone using wsgiref)
"""

import csv
import io
import json
import os
import sqlite3
from urllib.parse import parse_qs

DB_NAME = "retail_store.db"

CURRENCIES = {
    "IN": {"name": "India", "symbol": "₹", "code": "INR", "rate": 84.5},
    "US": {"name": "United States", "symbol": "$", "code": "USD", "rate": 1.0},
    "GB": {"name": "United Kingdom", "symbol": "£", "code": "GBP", "rate": 0.79},
    "EU": {"name": "European Union", "symbol": "€", "code": "EUR", "rate": 0.92},
    "JP": {"name": "Japan", "symbol": "¥", "code": "JPY", "rate": 152.0},
    "CA": {"name": "Canada", "symbol": "CA$", "code": "CAD", "rate": 1.38},
    "AU": {"name": "Australia", "symbol": "A$", "code": "AUD", "rate": 1.52},
}


def ensure_db():
    if not os.path.exists(DB_NAME):
        import database_setup
        database_setup.main()


def app(environ, start_response):
    """Pure Python WSGI handler (Zero Flask)."""
    ensure_db()
    path = environ.get("PATH_INFO", "/")
    query_string = environ.get("QUERY_STRING", "")
    params = parse_qs(query_string)

    if path == "/" or path == "":
        template_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
        with open(template_path, "rb") as f:
            content = f.read()
        headers = [
            ("Content-Type", "text/html; charset=utf-8"),
            ("Content-Length", str(len(content))),
            ("Cache-Control", "no-cache, no-store, must-revalidate")
        ]
        start_response("200 OK", headers)
        return [content]

    elif path == "/api/data":
        country_code = params.get("country", ["US"])[0].upper()
        country_info = CURRENCIES.get(country_code, CURRENCIES["US"])
        rate = country_info["rate"]

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Product Profitability
        cursor.execute("""
        SELECT 
            p.product_id, p.product_name, p.category, p.cost_price, p.selling_price,
            COALESCE(SUM(s.quantity), 0),
            ROUND(COALESCE(SUM(s.quantity * p.selling_price * (1.0 - s.discount_pct)), 0), 2),
            ROUND(COALESCE(SUM(s.quantity * p.cost_price), 0), 2),
            ROUND(COALESCE(SUM(s.quantity * (p.selling_price * (1.0 - s.discount_pct) - p.cost_price)), 0), 2)
        FROM products p
        LEFT JOIN sales s ON p.product_id = s.product_id
        GROUP BY p.product_id, p.product_name, p.category, p.cost_price, p.selling_price
        ORDER BY 9 DESC;
        """)
        products = []
        for p in cursor.fetchall():
            products.append({
                "product_id": p[0],
                "product_name": p[1],
                "category": p[2],
                "cost_price": round(p[3] * rate, 2),
                "selling_price": round(p[4] * rate, 2),
                "units_sold": p[5],
                "net_revenue": round(p[6] * rate, 2),
                "total_cogs": round(p[7] * rate, 2),
                "gross_profit": round(p[8] * rate, 2)
            })

        total_rev = sum(p["net_revenue"] for p in products)
        total_prof = sum(p["gross_profit"] for p in products)
        total_units = sum(p["units_sold"] for p in products)
        avg_margin = (total_prof / total_rev * 100) if total_rev > 0 else 0.0

        # City Top Customers
        cursor.execute("""
        WITH customer_spending AS (
            SELECT c.city, c.customer_name, COUNT(s.sale_id) AS total_orders,
                   ROUND(COALESCE(SUM(s.quantity * p.selling_price * (1.0 - s.discount_pct)), 0), 2) AS total_spent
            FROM customers c
            LEFT JOIN sales s ON c.customer_id = s.customer_id
            LEFT JOIN products p ON s.product_id = p.product_id
            GROUP BY c.city, c.customer_name
        ),
        ranked AS (
            SELECT city, customer_name, total_orders, total_spent,
                   ROW_NUMBER() OVER (PARTITION BY city ORDER BY total_spent DESC) AS city_rank
            FROM customer_spending
        )
        SELECT city, customer_name, total_orders, total_spent
        FROM ranked WHERE city_rank = 1 ORDER BY total_spent DESC;
        """)
        city_top = []
        for c in cursor.fetchall():
            city_top.append({
                "city": c[0],
                "customer_name": c[1],
                "total_orders": c[2],
                "total_spent": round(c[3] * rate, 2)
            })

        # Discount Impact
        cursor.execute("""
        SELECT p.category, COUNT(s.sale_id), SUM(s.quantity),
               ROUND(SUM(s.quantity * p.selling_price), 2),
               ROUND(SUM(s.quantity * p.selling_price * (1.0 - s.discount_pct)), 2),
               ROUND(SUM(s.quantity * p.selling_price * s.discount_pct), 2)
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        GROUP BY p.category
        ORDER BY 6 DESC;
        """)
        discounts = []
        for d in cursor.fetchall():
            discounts.append({
                "category": d[0],
                "transactions": d[1],
                "units_sold": d[2],
                "gross_revenue": round(d[3] * rate, 2),
                "net_revenue": round(d[4] * rate, 2),
                "discounts_given": round(d[5] * rate, 2)
            })

        conn.close()

        payload = {
            "country_code": country_code,
            "country_name": country_info["name"],
            "currency_symbol": country_info["symbol"],
            "currency_code": country_info["code"],
            "rate": rate,
            "kpis": {
                "total_revenue": round(total_rev, 2),
                "total_profit": round(total_prof, 2),
                "total_units": total_units,
                "avg_margin": round(avg_margin, 2)
            },
            "products": products,
            "city_top": city_top,
            "discounts": discounts
        }

        output = json.dumps(payload).encode("utf-8")
        headers = [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(output)))
        ]
        start_response("200 OK", headers)
        return [output]

    elif path == "/download":
        country_code = params.get("country", ["US"])[0].upper()
        country_info = CURRENCIES.get(country_code, CURRENCIES["US"])
        report_type = params.get("type", ["products"])[0]
        sym = country_info["symbol"]
        code = country_info["code"]
        rate = country_info["rate"]

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        output_io = io.StringIO()
        writer = csv.writer(output_io)

        if report_type == "customers":
            filename = f"customers_report_{code}.csv"
            writer.writerow(["Customer ID", "Customer Name", "City", "Orders", f"Total Spend ({sym} {code})", "Loyalty Tier"])
            cursor.execute("""
            SELECT c.customer_id, c.customer_name, c.city, COUNT(s.sale_id),
                   COALESCE(SUM(s.quantity * p.selling_price * (1.0 - s.discount_pct)), 0)
            FROM customers c
            LEFT JOIN sales s ON c.customer_id = s.customer_id
            LEFT JOIN products p ON s.product_id = p.product_id
            GROUP BY c.customer_id;
            """)
            for row in cursor.fetchall():
                cid, name, city, orders, spend = row
                conv_spend = spend * rate
                tier = "Platinum" if conv_spend >= (250 * rate) else ("Gold" if conv_spend >= (150 * rate) else "Silver")
                writer.writerow([cid, name, city, orders, f"{conv_spend:.2f}", tier])
        else:
            filename = f"product_profitability_{code}.csv"
            writer.writerow(["Product ID", "Product Name", "Category", f"Cost ({sym})", f"Price ({sym})", "Units Sold", f"Net Revenue ({sym})", f"Gross Profit ({sym})", "Margin (%)"])
            cursor.execute("""
            SELECT p.product_id, p.product_name, p.category, p.cost_price, p.selling_price,
                   COALESCE(SUM(s.quantity), 0),
                   COALESCE(SUM(s.quantity * p.selling_price * (1.0 - s.discount_pct)), 0),
                   COALESCE(SUM(s.quantity * (p.selling_price * (1.0 - s.discount_pct) - p.cost_price)), 0)
            FROM products p
            LEFT JOIN sales s ON p.product_id = s.product_id
            GROUP BY p.product_id;
            """)
            for row in cursor.fetchall():
                pid, name, cat, cost, price, units, rev, prof = row
                margin = (prof / rev * 100) if rev > 0 else 0.0
                writer.writerow([pid, name, cat, f"{cost * rate:.2f}", f"{price * rate:.2f}", units, f"{rev * rate:.2f}", f"{prof * rate:.2f}", f"{margin:.1f}%"])

        conn.close()
        csv_bytes = output_io.getvalue().encode("utf-8")
        headers = [
            ("Content-Type", "text/csv; charset=utf-8"),
            ("Content-Disposition", f'attachment; filename="{filename}"'),
            ("Content-Length", str(len(csv_bytes)))
        ]
        start_response("200 OK", headers)
        return [csv_bytes]

    elif path == "/health":
        body = b'{"status": "ok"}'
        start_response("200 OK", [("Content-Type", "application/json"), ("Content-Length", str(len(body)))])
        return [body]

    start_response("404 Not Found", [("Content-Type", "text/plain")])
    return [b"Not Found"]


if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    port = int(os.environ.get("PORT", 5000))
    ensure_db()
    with make_server("0.0.0.0", port, app) as httpd:
        print(f"Serving WSGI on port {port} (Zero Flask)...")
        httpd.serve_forever()

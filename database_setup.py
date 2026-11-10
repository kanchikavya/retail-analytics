"""
Database Setup Script
Sets up 'retail_store.db' with normalized tables:
- customers (customer_id, customer_name, city, join_date)
- products  (product_id, product_name, category, cost_price, selling_price)
- sales     (sale_id, customer_id, product_id, sale_date, quantity, discount_pct)
"""

import sqlite3

DATABASE_NAME = "retail_store.db"


def create_schema(cursor):
    """Creates the relational database schema."""
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY,
        customer_name TEXT NOT NULL,
        city TEXT NOT NULL,
        join_date TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY,
        product_name TEXT NOT NULL,
        category TEXT NOT NULL,
        cost_price REAL NOT NULL,
        selling_price REAL NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        sale_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        product_id INTEGER,
        sale_date TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        discount_pct REAL DEFAULT 0.0,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    );
    """)


def seed_data(cursor):
    """Populates tables with realistic sample data."""
    # Reset existing rows to allow re-runs
    cursor.execute("DELETE FROM sales;")
    cursor.execute("DELETE FROM products;")
    cursor.execute("DELETE FROM customers;")

    # 1. Customers
    customers = [
        (1, "Aarav Sharma", "Mumbai", "2025-08-15"),
        (2, "Priya Patel", "Ahmedabad", "2025-09-10"),
        (3, "Rohan Verma", "Delhi", "2025-10-01"),
        (4, "Sneha Reddy", "Hyderabad", "2025-11-20"),
        (5, "Vikram Malhotra", "Bangalore", "2025-12-05"),
        (6, "Ananya Sen", "Kolkata", "2026-01-12"),
        (7, "Karan Joshi", "Pune", "2026-01-25"),
        (8, "Meera Nair", "Chennai", "2026-02-02"),
    ]
    cursor.executemany("INSERT INTO customers VALUES (?, ?, ?, ?);", customers)

    # 2. Products (Cost Price vs Selling Price)
    products = [
        (101, "Wireless Optical Mouse", "Electronics", 12.00, 24.99),
        (102, "Mechanical Keyboard", "Electronics", 35.00, 74.99),
        (103, "USB-C Fast Cable (2m)", "Accessories", 2.50, 9.99),
        (104, "Aluminum Laptop Stand", "Accessories", 14.00, 32.50),
        (105, "Ceramic Coffee Tumbler", "Home & Office", 4.50, 14.99),
        (106, "Hardcover Dotted Journal", "Home & Office", 3.00, 8.50),
        (107, "Noise-Cancelling Earbuds", "Electronics", 28.00, 59.99),
        (108, "Webcam HD 1080p", "Electronics", 22.00, 48.00),
        (109, "Microfiber Desk Mat", "Accessories", 6.00, 18.00),
        (110, "Ergonomic Lumbar Cushion", "Home & Office", 11.00, 26.00),
    ]
    cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?);", products)

    # 3. Sales Transactions (sale_id, customer_id, product_id, sale_date, quantity, discount_pct)
    sales = [
        (1001, 1, 101, "2026-01-05", 2, 0.00),
        (1002, 2, 103, "2026-01-07", 5, 0.10),
        (1003, 3, 102, "2026-01-10", 1, 0.05),
        (1004, 4, 105, "2026-01-12", 4, 0.00),
        (1005, 5, 107, "2026-01-15", 2, 0.10),
        (1006, 1, 104, "2026-01-20", 1, 0.00),
        (1007, 6, 106, "2026-01-22", 6, 0.00),
        (1008, 7, 108, "2026-01-28", 2, 0.05),
        (1009, 2, 101, "2026-02-01", 3, 0.00),
        (1010, 3, 109, "2026-02-04", 2, 0.00),
        (1011, 4, 110, "2026-02-08", 3, 0.10),
        (1012, 5, 102, "2026-02-12", 2, 0.00),
        (1013, 8, 103, "2026-02-14", 10, 0.15),
        (1014, 1, 107, "2026-02-18", 1, 0.00),
        (1015, 6, 105, "2026-02-22", 3, 0.00),
        (1016, 7, 104, "2026-02-25", 2, 0.05),
        (1017, 2, 108, "2026-03-01", 1, 0.00),
        (1018, 3, 101, "2026-03-03", 4, 0.00),
        (1019, 4, 102, "2026-03-05", 1, 0.10),
        (1020, 5, 109, "2026-03-07", 5, 0.05),
        (1021, 8, 106, "2026-03-08", 8, 0.00),
        (1022, 1, 110, "2026-03-09", 2, 0.00),
    ]
    cursor.executemany("INSERT INTO sales VALUES (?, ?, ?, ?, ?, ?);", sales)


def main():
    print(f"Connecting to database: {DATABASE_NAME}...")
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    create_schema(cursor)
    seed_data(cursor)
    conn.commit()

    print("Database tables created and seeded successfully.")
    conn.close()


if __name__ == "__main__":
    main()

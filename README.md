# 🏪 Retail Store Sales & Profit Analysis System

An end-to-end data analytics project demonstrating data modeling, business metrics calculation, and reporting using **pure Python**, **relational SQL**, and **Microsoft Excel**.

---

## 🎯 Project Overview
This project provides a clean pipeline for retail analytics without relying on heavy external dependencies:
1. **SQL (SQLite)**: Relational schema design with normalized tables (`customers`, `products`, `sales`), analytical window functions (`ROW_NUMBER() OVER PARTITION BY`), and profit aggregation queries.
2. **Python (Standard Library Only)**: Automated data pipeline using built-in `sqlite3` and `csv` modules to calculate margins, evaluate discount impacts, filter by date ranges, and export clean reports.
3. **Microsoft Excel**: Multi-table reporting with interactive formulas (`SUMIFS`, `XLOOKUP`), Pivot Tables, and visual KPI cards.

---

## 📂 Repository Structure
```
├── database_setup.py          # Creates SQLite schema and seeds transaction data
├── queries.sql                # Documented pure SQL queries (CTEs, Window functions, Joins)
├── analysis_and_export.py     # Python script generating CSV reports for Excel
├── EXCEL_GUIDE.md             # Step-by-step Excel instructions (Formulas, Pivot Tables, Charts)
├── .gitignore                 # Standard Python & database ignore file
└── README.md                  # Project documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.8+** (No external packages required—uses standard library only)
- **Microsoft Excel** (or Google Sheets / LibreOffice Calc)

### 2. Setup Database & Generate Reports
Run the following commands in your terminal:
```bash
# 1. Initialize and seed the SQLite database
python database_setup.py

# 2. Run queries and generate Excel-ready CSV reports
python analysis_and_export.py
```

### 3. Open in Excel
Open any of the generated CSV files to explore:
* `product_profitability_report.csv` - Revenue, COGS, Profit, and Margins per SKU.
* `customer_segments_report.csv` - Customer Lifetime Spend & Loyalty Tiers (Platinum, Gold, Silver).
* `top_customers_by_city.csv` - Top spender in each city using SQL window ranking.
* `discount_impact_analysis.csv` - Gross vs. Net revenue and discount loss rates.

Refer to [`EXCEL_GUIDE.md`](./EXCEL_GUIDE.md) for formulas and dashboard layout.

---

## 💡 Key SQL Skills Demonstrated
* **Window Functions**: `ROW_NUMBER() OVER (PARTITION BY city ORDER BY total_spent DESC)`
* **Common Table Expressions (CTEs)**: Modular query design using `WITH ... AS`
* **Relational Joins**: Multi-table `LEFT JOIN` and `INNER JOIN`
* **Conditional Logic**: `CASE WHEN ... THEN ... ELSE` for business tier classification

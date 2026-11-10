# 🏪 Retail Store Sales & Profit Analysis System

An end-to-end data analytics web application demonstrating data modeling, business metrics calculation, and reporting using **pure Python**, **relational SQL**, and **Microsoft Excel**.

---

## 🎯 Project Overview
This project provides a clean pipeline for retail analytics:
1. **SQL (SQLite)**: Relational schema design with normalized tables (`customers`, `products`, `sales`), analytical window functions (`ROW_NUMBER() OVER PARTITION BY`), and profit aggregation queries.
2. **Python (Standard Library Core)**: Automated data pipeline using built-in `sqlite3` and `csv` modules to calculate margins, evaluate discount impacts, filter by date ranges, and export clean reports.
3. **Flask Web Dashboard**: Responsive analytics web interface with live KPI cards, SQL query tables, and direct CSV downloads.
4. **Microsoft Excel**: Multi-table reporting with interactive formulas (`SUMIFS`, `XLOOKUP`), Pivot Tables, and visual KPI cards.

---

## 📂 Repository Structure
```
├── app.py                     # Flask web app serving dashboard & CSV downloads
├── database_setup.py          # Creates SQLite schema and seeds transaction data
├── queries.sql                # Documented pure SQL queries (CTEs, Window functions, Joins)
├── analysis_and_export.py     # Python script generating CSV reports for Excel
├── templates/
│   └── index.html             # Responsive HTML web dashboard
├── requirements.txt           # Deployment dependencies (Flask & gunicorn)
├── render.yaml                # Render cloud deployment blueprint
├── EXCEL_GUIDE.md             # Step-by-step Excel instructions (Formulas, Pivot Tables, Charts)
├── .gitignore                 # Standard Python & database ignore file
└── README.md                  # Project documentation
```

---

## 🚀 Running Locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the application
python app.py
```
Open your browser at `http://127.0.0.1:5000` to view the live dashboard and download the CSVs.

---

## ☁️ Deploying to Render (Free Web Service)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Add web dashboard and Render configuration"
   git push origin main
   ```

2. **Deploy on Render**:
   - Go to [dashboard.render.com](https://dashboard.render.com/) and click **New +** → **Web Service**.
   - Connect your GitHub repository.
   - Configure the following settings:
     * **Name**: `retail-sales-analytics`
     * **Language**: `Python 3`
     * **Build Command**: `pip install -r requirements.txt && python database_setup.py && python analysis_and_export.py`
     * **Start Command**: `gunicorn app:app`
     * **Instance Type**: `Free`
   - Click **Deploy Web Service**.

Your analytics dashboard will be live on a public Render URL (e.g. `https://retail-sales-analytics.onrender.com`)!

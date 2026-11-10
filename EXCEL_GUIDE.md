# 📊 Excel Dashboard & Analysis Guide

This guide walks you step-by-step through analyzing the exported CSV reports in Microsoft Excel.

---

## 📁 Files Generated for Excel
Located in: `retail_sales_project/`
1. `product_profitability_report.csv`
2. `customer_segments_report.csv`
3. `monthly_category_trend.csv`

---

## Step 1: Open & Format the Data

1. Open `product_profitability_report.csv` in Excel.
2. Select row 1 (Headers) → **Bold (`Ctrl + B`)** and add a background color (e.g. Navy Blue with White text).
3. Select columns **D, E, G, H, I** (`Cost Price`, `Selling Price`, `Net Revenue`, `Total Cost`, `Gross Profit`) → change format to **Currency ($)** (`Ctrl + Shift + $` or from the Home ribbon).
4. Select column **J** (`Profit Margin`) → ensure it has a `%` sign or format as Percentage.
5. Auto-fit column widths by double-clicking the column dividers.

---

## Step 2: Intermediate Excel Formulas to Apply

Add these summary calculations below your table (e.g., in rows 13 to 16):

### 1. Total Store Revenue
```excel
=SUM(G2:G11)
```

### 2. Total Gross Profit
```excel
=SUM(I2:I11)
```

### 3. Overall Store Profit Margin
```excel
=I14 / G13
```
*(Total Profit divided by Total Revenue, formatted as %)*

### 4. Category-Specific Revenue (`SUMIFS`)
Calculate total revenue generated specifically by the "Electronics" category:
```excel
=SUMIFS(G2:G11, C2:C11, "Electronics")
```

### 5. Product Lookup (`XLOOKUP` or `VLOOKUP`)
To dynamically look up the Gross Profit of any product by Product ID (e.g. `102` in cell `M2`):
```excel
=XLOOKUP(M2, A2:A11, I2:I11, "Not Found")
```
*(Or classic VLOOKUP):*
```excel
=VLOOKUP(M2, A2:I11, 9, FALSE)
```

---

## Step 3: Conditional Formatting

Make key metrics pop visually:
1. Select the **Performance Status** column (`K2:K11`).
2. Go to **Home → Conditional Formatting → Highlight Cells Rules → Equal To...**
   * Value: `"Star Product"` → Custom Format: **Light Green Fill** with Dark Green text.
3. Repeat for:
   * Value: `"Underperforming"` → Custom Format: **Light Red Fill** with Dark Red text.
4. Select the **Profit Margin (%)** column (`J2:J11`):
   * Go to **Conditional Formatting → Data Bars** → choose a soft gradient bar.

---

## Step 4: Pivot Tables & Visual Charts

### A. Category Revenue vs. Profit (Pivot Table)
1. Select the data range `A1:K11`.
2. Click **Insert → PivotTable** → New Worksheet.
3. Drag fields:
   * **Rows**: `Category`
   * **Values**: `Sum of Net Revenue`, `Sum of Gross Profit`
4. Click **Insert → 2D Clustered Column Chart**.
   * Add a chart title: *"Revenue vs. Profit by Product Category"*.

### B. Customer Loyalty Breakdown (Donut Chart)
1. Open `customer_segments_report.csv`.
2. Select range `A1:H9` → **Insert → PivotTable**.
3. Drag fields:
   * **Rows**: `Loyalty Tier`
   * **Values**: `Count of Customer ID`
4. Click **Insert → Pie / Doughnut Chart**.
   * Add Data Labels to show the count of customers per tier.

---

## Step 5: Executive KPI Cards (Dashboard View)

On a new sheet named **"Executive Dashboard"**, merge and style 3 cells across the top:

| KPI Card | Formula / Value | Suggested Styling |
| :--- | :--- | :--- |
| **Total Revenue** | `='product_profitability_report'!G13` | Large font (22pt), Blue accent |
| **Total Gross Profit** | `='product_profitability_report'!I14` | Large font (22pt), Green accent |
| **Top Performing Product** | `=INDEX(B2:B11, MATCH(MAX(I2:I11), I2:I11, 0))` | Large font (18pt), Gold accent |

---

## 🏆 Project Wrap-Up Checklist
- [x] SQLite database created with 3 related tables (`customers`, `products`, `sales`).
- [x] SQL queries written using `JOIN`, `GROUP BY`, `SUM`, and Common Table Expressions (`WITH`).
- [x] Python script cleanly reads database rows, calculates profit margins and customer tiers, and writes formatted CSVs without any third-party libraries.
- [x] Excel dashboard configured with `SUMIFS`, `XLOOKUP`, Pivot Tables, and KPI cards.

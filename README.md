# 🍕 Foodpanda Data Analysis Dashboard

> **An end-to-end interactive data analysis dashboard built with Python, Streamlit, and Plotly.**  
> Analyses customer orders, delivery performance, restaurant ratings, and churn behaviour across major Pakistani cities.

---

## 📌 Project Overview

This project performs a complete data analysis pipeline on a real-world Foodpanda orders dataset. It covers data loading, quality validation, statistical summarisation, visual comparison through 14 interactive charts, and actionable business insights — all presented through a live, filterable Streamlit web dashboard.

| Detail | Value |
|--------|-------|
| **Author** | Simran Manav |
| **Project File** | `SimranManav_FoodpandaAnalysis.py` |
| **Dataset** | `Foodpanda_Cleaned_Dataset.csv` |
| **Records** | 6,000 rows × 21 columns |
| **Total Revenue** | PKR 14,343,912 |
| **Cities Covered** | Peshawar, Multan, Lahore, Karachi, Islamabad |
| **Restaurants** | McDonald's, KFC, Pizza Hut, Subway, Burger King |

---

## 📂 Dataset

| File | Description |
|------|-------------|
| [`Foodpanda Analysis Dataset.csv`](Foodpanda%20Analysis%20Dataset.csv) | Original raw dataset (6,000 rows × 20 columns) |
| [`Foodpanda_Cleaned_Dataset.csv`](Foodpanda_Cleaned_Dataset.csv) | Cleaned dataset used by the dashboard (6,000 rows × 21 columns) |

### 🔗 Dataset Source

**Kaggle:** [Foodpanda Orders and Customer Behavior Dataset](https://www.kaggle.com/datasets/ranaghulamnabi/foodpanda-orders-and-customer-behavior-dataset)

### Dataset Columns

| Column | Type | Description |
|--------|------|-------------|
| `customer_id` | String | Unique customer identifier |
| `gender` | String | Male / Female / Other |
| `age` | String | Teenager / Adult / Senior |
| `city` | String | City of the customer |
| `signup_date` | Date | Date the customer registered |
| `order_id` | String | Unique order identifier |
| `order_date` | Date | Date the order was placed |
| `restaurant_name` | String | Restaurant name |
| `dish_name` | String | Name of the dish ordered |
| `category` | String | Italian / Fast Food / Chinese / Continental / Dessert |
| `quantity` | Integer | Items ordered (1–5) |
| `price` | Float | Price per item (PKR) |
| `payment_method` | String | Cash / Card / Wallet |
| `order_frequency` | Integer | Total orders by this customer (1–50) |
| `last_order_date` | Date | Most recent order date |
| `loyalty_points` | Integer | Loyalty reward points (0–500) |
| `churned` | String | Active / Inactive |
| `rating` | Integer | Customer rating (1–5) |
| `rating_date` | Date | Date the rating was submitted |
| `delivery_status` | String | Delivered / Delayed / Cancelled |
| `revenue` | Float | **Derived:** quantity × price |

---

## 🛠️ Technologies Used

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.10+ | Core programming language |
| **Streamlit** | ≥ 1.35.0 | Web dashboard framework — tabs, sidebar, widgets, caching |
| **Pandas** | ≥ 2.0.0 | Data loading, filtering, group-by aggregations, pivot tables |
| **Plotly** | ≥ 5.20.0 | 14 interactive charts (bar, pie, heatmap, scatter, box, histogram) |
| **NumPy** | ≥ 1.26.0 | Numerical operations (used internally by Pandas and Plotly) |

---

## 🚀 Setup & Run Instructions

### Prerequisites

- Python 3.10 or higher ([download here](https://www.python.org/downloads/))
- `pip` package manager

### Step 1 — Clone or Download the Project

Download all files into a single folder:

```
SimranManav_FoodpandaAnalysis.py
Foodpanda_Cleaned_Dataset.csv
requirements.txt
README.md
```

### Step 2 — Install Dependencies

Open a terminal in the project folder and run:

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install streamlit>=1.35.0
pip install pandas>=2.0.0
pip install plotly>=5.20.0
pip install numpy>=1.26.0
```

### Step 3 — Launch the Dashboard

```bash
streamlit run SimranManav_FoodpandaAnalysis.py
```

### Step 4 — Open in Browser

Streamlit will automatically open the dashboard in your default browser at:

```
http://localhost:8501
```

---

## 📊 Dashboard Features

The dashboard is organised into **5 tabs** with a **sidebar filter panel**:

### Sidebar Filters
Dynamically filter all tabs by:
- **City** — Peshawar · Multan · Lahore · Karachi · Islamabad
- **Restaurant** — McDonald's · KFC · Pizza Hut · Subway · Burger King
- **Food Category** — Italian · Fast Food · Chinese · Continental · Dessert
- **Customer Status** — Active · Inactive

---

### 📋 Tab 1 — Overview
- 5 KPI metric cards: Total Orders, Total Revenue (PKR), Unique Customers, Avg Rating, Delivery Rate
- Full dataset preview (first 100 rows)
- Column schema reference table with descriptions for all 21 columns

---

### 🔍 Tab 2 — Data Quality
- Missing value analysis with percentage per column
- Duplicate row and duplicate Order ID detection
- Numerical range validation (price, quantity, rating, loyalty points, order frequency)
- Categorical value validation against expected sets
- Date integrity check (parse errors + signup > last_order logic)
- Outlier detection via box plots (price, quantity, rating)

---

### 📊 Tab 3 — Summary Statistics
- Dynamic **Group By** selector across 9 dimensions
- Aggregated KPIs: Total Revenue, Total Orders, Avg Price, Avg Rating, Avg Quantity, Avg Loyalty Points, Avg Order Frequency
- Cross-tab pivot: Revenue by City × Restaurant
- Cross-tab pivot: Order Count by City × Delivery Status
- Descriptive statistics (mean, min, max, std dev) for all numeric columns

---

### 📈 Tab 4 — Charts (14 Interactive Charts)

| # | Chart | Type |
|---|-------|------|
| 4.1 | Revenue by City | Vertical Bar |
| 4.2 | Revenue by Restaurant | Vertical Bar |
| 4.3 | Revenue by Food Category | Donut Pie |
| 4.4 | Order Count by Delivery Status | Donut Pie |
| 4.5 | Average Rating by Restaurant | Horizontal Bar |
| 4.6 | Orders by Age Group | Vertical Bar |
| 4.7 | Payment Method Distribution | Donut Pie |
| 4.8 | Revenue by Gender × Age Group | Grouped Bar |
| 4.9 | Active vs Inactive Customers by City | Grouped Bar |
| 4.10 | Loyalty Points Distribution | Box Plot |
| 4.11 | Revenue Heatmap: City × Restaurant | Heatmap |
| 4.12 | Price vs. Rating | Bubble Scatter |
| 4.13 | Order Frequency Distribution | Overlapping Histogram |
| 4.14 | Top Dishes by Revenue | Horizontal Bar |

---

### 💡 Tab 5 — Business Insights
- **10 Key Findings** with data-driven analysis
- **8 Strategic Recommendations** with specific action items
- **Decision Scorecard** — 6 KPIs vs industry benchmarks (pass/fail)

| Metric | Actual | Benchmark | Status |
|--------|--------|-----------|--------|
| Delivery Success Rate | 34.4% | ≥ 85% | ❌ Needs Work |
| Cancellation Rate | 32.8% | ≤ 5% | ❌ Needs Work |
| Delay Rate | 32.8% | ≤ 10% | ❌ Needs Work |
| Churn (Inactive) Rate | 49.7% | ≤ 20% | ❌ Needs Work |
| Average Rating | 3.00 / 5 | ≥ 4.0 / 5 | ❌ Needs Work |
| Average Loyalty Points | 250 | ≥ 300 | ❌ Needs Work |

---

## 🧹 Data Cleaning

The raw dataset was cleaned through 10 steps before use:

1. Load raw CSV (6,000 rows × 20 columns)
2. Strip whitespace from all string columns
3. Standardise categorical columns to Title Case
4. Parse 4 date columns to `datetime` objects
5. **Fix 1,467 rows** where `signup_date > last_order_date` (dates swapped)
6. Remove fully duplicate rows (0 found)
7. Remove duplicate Order IDs (0 found)
8. Clip numeric columns to valid ranges
9. Add derived `revenue` column (`quantity × price`)
10. Format all dates to ISO 8601 (`YYYY-MM-DD`) and save

---

## 📁 Project Files

```
📁 Project Folder
├── SimranManav_FoodpandaAnalysis.py       ← Main Streamlit app (run this)
├── Foodpanda_Cleaned_Dataset.csv          ← Cleaned dataset used by the app
├── Foodpanda Analysis Dataset.csv         ← Original raw dataset
├── requirements.txt                       ← Python dependencies
├── SimranManav_FoodpandaAnalysisReport.docx ← Full project documentation (Word)
└── README.md                              ← This file
```

---

## 📄 Documentation

Full project documentation is available in:  
📄 [`SimranManav_FoodpandaAnalysisReport.docx`](SimranManav_FoodpandaAnalysisReport.docx)

The report covers:
- Project objectives and scope
- Dataset description and column reference
- Data cleaning process (10 steps)
- Data quality check results
- Summary statistics and group analysis
- All 14 charts described
- 10 key findings + 8 strategic recommendations
- Decision scorecard
- Technical requirements and setup instructions

---

## 📜 License

This project uses a publicly available dataset from Kaggle for educational and analytical purposes.  
Dataset: [Foodpanda Orders and Customer Behavior Dataset](https://www.kaggle.com/datasets/ranaghulamnabi/foodpanda-orders-and-customer-behavior-dataset) by [ranaghulamnabi](https://www.kaggle.com/ranaghulamnabi)

---

*Foodpanda Data Analysis Dashboard · Built with Streamlit & Plotly · Simran Manav*

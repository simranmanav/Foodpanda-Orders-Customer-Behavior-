"""
complete_code.py
================
Foodpanda Analysis Dashboard — Complete Project Code (Single File)
===================================================================
All modules compiled into one standalone file:
  - Configuration (constants, colours, column lists)
  - Data Loading  (CSV load, date parsing, filter logic)
  - Data Quality  (missing values, duplicates, range checks, date integrity)
  - Summary Stats (group-by aggregations, pivot tables, descriptive stats)
  - Charts        (14 Plotly chart builders)
  - Business Insights (KPI computation, findings, recommendations, scorecard)
  - Styles        (custom CSS)
  - App           (Streamlit page layout, sidebar, tabs)

Run with:
    streamlit run complete_code.py

Requirements:
    pip install streamlit pandas plotly numpy
"""

# ==============================================================================
# IMPORTS
# ==============================================================================
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==============================================================================
# SECTION 1 — CONFIGURATION
# Constants, file paths, colour palette, and expected categorical values.
# ==============================================================================

DATASET_PATH = "Foodpanda_Cleaned_Dataset.csv"

DATE_COLS = ["signup_date", "order_date", "last_order_date", "rating_date"]

NUMERIC_COLS = [
    "price", "quantity", "rating",
    "loyalty_points", "order_frequency", "revenue",
]

EXPECTED_VALUES = {
    "gender":          {"Male", "Female", "Other"},
    "age":             {"Teenager", "Adult", "Senior"},
    "delivery_status": {"Delivered", "Delayed", "Cancelled"},
    "churned":         {"Active", "Inactive"},
    "payment_method":  {"Cash", "Card", "Wallet"},
}

PINK   = "#e21e74"
ORANGE = "#f76b1c"
GREEN  = "#10b981"
AMBER  = "#f59e0b"
PURPLE = "#7c3aed"
PALETTE = px.colors.qualitative.Bold

DELIVERY_COLOR_MAP = {"Delivered": GREEN, "Delayed": AMBER, "Cancelled": PINK}
CHURN_COLOR_MAP    = {"Active": GREEN, "Inactive": PINK}

GROUP_DIMENSIONS = {
    "City":            "city",
    "Restaurant":      "restaurant_name",
    "Food Category":   "category",
    "Dish":            "dish_name",
    "Payment Method":  "payment_method",
    "Age Group":       "age",
    "Gender":          "gender",
    "Delivery Status": "delivery_status",
    "Customer Status": "churned",
}

# ==============================================================================
# SECTION 2 — STYLES
# Custom CSS injected once at page load.
# ==============================================================================

_CSS = """
<style>
.main-header {
    background: linear-gradient(135deg, #e21e74 0%, #f76b1c 100%);
    padding: 1.5rem 2rem;
    border-radius: 12px;
    color: white;
    margin-bottom: 1.5rem;
}
.main-header h1 { margin: 0; font-size: 2rem; font-weight: 700; }
.main-header p  { margin: 0.3rem 0 0; font-size: 1rem; opacity: 0.9; }

.kpi-card {
    background: #fff;
    border: 1px solid #e5e7eb;
    border-left: 5px solid #e21e74;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.5rem;
}
.kpi-card .label {
    font-size: 0.78rem;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.kpi-card .value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #111827;
    line-height: 1.2;
}

.section-header {
    border-left: 4px solid #e21e74;
    padding-left: 0.75rem;
    margin: 1.5rem 0 1rem;
    font-size: 1.25rem;
    font-weight: 700;
    color: #111827;
}

.insight-card {
    background: #fff7ed;
    border: 1px solid #fdba74;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.75rem;
}
.insight-card .title { font-weight: 700; color: #c2410c; font-size: 0.95rem; }
.insight-card .body  { color: #374151; font-size: 0.88rem; margin-top: 0.3rem; line-height: 1.6; }

.rec-card {
    background: #f0fdf4;
    border: 1px solid #86efac;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.75rem;
}
.rec-card .title { font-weight: 700; color: #15803d; font-size: 0.95rem; }
.rec-card .body  { color: #374151; font-size: 0.88rem; margin-top: 0.3rem; line-height: 1.6; }

footer { visibility: hidden; }
</style>
"""

def inject_css():
    st.markdown(_CSS, unsafe_allow_html=True)

# ==============================================================================
# SECTION 3 — DATA LOADING
# Load and cache the cleaned CSV; add derived columns; apply sidebar filters.
# ==============================================================================

@st.cache_data(show_spinner="Loading dataset...")
def load_data(path: str = DATASET_PATH) -> pd.DataFrame:
    """Load cleaned CSV, parse dates, and add derived columns."""
    df = pd.read_csv(path)
    for col in DATE_COLS:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    if "revenue" not in df.columns:
        df["revenue"] = (df["quantity"] * df["price"]).round(2)
    if "order_year_month" not in df.columns:
        df["order_year_month"] = df["order_date"].dt.to_period("M").astype(str)
    return df


def apply_filters(
    df: pd.DataFrame,
    city: str = "All",
    restaurant: str = "All",
    category: str = "All",
    churn: str = "All",
) -> pd.DataFrame:
    """Return a filtered copy of df based on sidebar selections."""
    mask = pd.Series(True, index=df.index)
    if city       != "All": mask &= df["city"]            == city
    if restaurant != "All": mask &= df["restaurant_name"] == restaurant
    if category   != "All": mask &= df["category"]        == category
    if churn      != "All": mask &= df["churned"]         == churn
    return df[mask].copy()

# ==============================================================================
# SECTION 4 — DATA QUALITY
# All quality-check helpers and the Tab 2 renderer.
# ==============================================================================

def check_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Summarise missing-value counts per column."""
    m = df.isnull().sum().reset_index()
    m.columns = ["Column", "Missing Count"]
    m["Missing %"] = (m["Missing Count"] / len(df) * 100).round(2)
    m["Status"] = m["Missing Count"].apply(
        lambda x: "Clean" if x == 0 else ("Low" if x / len(df) < 0.05 else "High")
    )
    return m


def check_duplicates(df: pd.DataFrame) -> dict:
    """Return counts of fully duplicate rows and duplicate order IDs."""
    return {
        "full_duplicates":     int(df.duplicated().sum()),
        "order_id_duplicates": int(df.duplicated(subset=["order_id"]).sum()),
    }


def check_numeric_ranges(df: pd.DataFrame) -> pd.DataFrame:
    """Validate numeric columns are within expected ranges."""
    checks = {
        "price > 0":            (df["price"] > 0).all(),
        "quantity between 1-5": df["quantity"].between(1, 5).all(),
        "rating between 1-5":   df["rating"].between(1, 5).all(),
        "loyalty_points >= 0":  (df["loyalty_points"] >= 0).all(),
        "order_frequency >= 1": (df["order_frequency"] >= 1).all(),
    }
    return pd.DataFrame(
        [(k, "Pass" if v else "Fail") for k, v in checks.items()],
        columns=["Check", "Result"],
    )


def check_categorical_values(df: pd.DataFrame) -> pd.DataFrame:
    """Compare actual unique values against expected sets."""
    rows = []
    for col, expected in EXPECTED_VALUES.items():
        actual     = set(df[col].dropna().unique())
        unexpected = actual - expected
        rows.append({
            "Column":          col,
            "Expected Values": ", ".join(sorted(expected)),
            "Found Values":    ", ".join(sorted(actual)),
            "Unexpected":      ", ".join(sorted(unexpected)) if unexpected else "None",
            "Status":          "Clean" if not unexpected else "Issue Found",
        })
    return pd.DataFrame(rows)


def check_date_integrity(df: pd.DataFrame) -> pd.DataFrame:
    """Check date parse errors and signup <= last_order logic."""
    rows = []
    for col in DATE_COLS:
        errors = df[col].isnull().sum() if pd.api.types.is_datetime64_any_dtype(df[col]) else 0
        rows.append((col, int(errors), "Clean" if errors == 0 else "Parse Errors"))
    if pd.api.types.is_datetime64_any_dtype(df["signup_date"]) and \
       pd.api.types.is_datetime64_any_dtype(df["last_order_date"]):
        bad = int((df["signup_date"] > df["last_order_date"]).sum())
    else:
        bad = int((pd.to_datetime(df["signup_date"], errors="coerce") >
                   pd.to_datetime(df["last_order_date"], errors="coerce")).sum())
    rows.append(("signup_date > last_order_date", bad, "Clean" if bad == 0 else "Logic Error"))
    return pd.DataFrame(rows, columns=["Check", "Count", "Status"])


def build_outlier_boxplots(df: pd.DataFrame) -> go.Figure:
    """3-panel box-plot for price, quantity, and rating."""
    fig = make_subplots(rows=1, cols=3, subplot_titles=["Price (PKR)", "Quantity", "Rating"])
    for i, col in enumerate(["price", "quantity", "rating"], 1):
        fig.add_trace(go.Box(y=df[col], name=col, marker_color=PINK, showlegend=False), row=1, col=i)
    fig.update_layout(height=350, margin=dict(t=40, b=20))
    return fig


def render_quality_tab(df_raw: pd.DataFrame) -> None:
    """Render the complete Data Quality tab."""
    st.markdown('<div class="section-header">2. Data Quality Check</div>', unsafe_allow_html=True)

    st.subheader("Missing Values")
    m = check_missing(df_raw)
    st.dataframe(m, use_container_width=True, hide_index=True)
    if m["Missing Count"].sum() == 0:
        st.success("No missing values found in any column.")
    else:
        st.warning("Some columns contain missing values — review above.")

    st.subheader("Duplicate Rows")
    dups = check_duplicates(df_raw)
    dc1, dc2 = st.columns(2)
    dc1.metric("Fully Duplicate Rows", dups["full_duplicates"])
    dc2.metric("Duplicate Order IDs",  dups["order_id_duplicates"])
    if dups["full_duplicates"] == 0 and dups["order_id_duplicates"] == 0:
        st.success("No duplicate rows or order IDs detected.")
    else:
        st.warning(f"{dups['full_duplicates']} duplicate row(s), {dups['order_id_duplicates']} duplicate order ID(s).")

    st.subheader("Numerical Range Validation")
    st.dataframe(check_numeric_ranges(df_raw), use_container_width=True, hide_index=True)

    st.subheader("Categorical Value Validation")
    st.dataframe(check_categorical_values(df_raw), use_container_width=True, hide_index=True)

    st.subheader("Date Integrity")
    st.dataframe(check_date_integrity(df_raw), use_container_width=True, hide_index=True)

    st.subheader("Outlier Detection (Box Plots)")
    st.plotly_chart(build_outlier_boxplots(df_raw), use_container_width=True)

# ==============================================================================
# SECTION 5 — SUMMARY STATISTICS
# Group-by aggregations, pivot tables, descriptive stats, and Tab 3 renderer.
# ==============================================================================

def make_summary(group_col: str, df: pd.DataFrame) -> pd.DataFrame:
    """Group df by group_col and compute standard revenue/order KPIs."""
    grp = df.groupby(group_col, as_index=False).agg(
        Total_Revenue       =("revenue",        "sum"),
        Total_Orders        =("order_id",        "count"),
        Avg_Price           =("price",           "mean"),
        Avg_Rating          =("rating",          "mean"),
        Avg_Quantity        =("quantity",        "mean"),
        Avg_Loyalty_Points  =("loyalty_points",  "mean"),
        Avg_Order_Frequency =("order_frequency", "mean"),
    )
    for c in ["Total_Revenue", "Avg_Price", "Avg_Rating", "Avg_Quantity"]:
        grp[c] = grp[c].round(2)
    grp["Avg_Loyalty_Points"]  = grp["Avg_Loyalty_Points"].round(1)
    grp["Avg_Order_Frequency"] = grp["Avg_Order_Frequency"].round(1)
    return grp.sort_values("Total_Revenue", ascending=False).reset_index(drop=True)


def revenue_pivot(df: pd.DataFrame) -> pd.DataFrame:
    """Cross-tab: total revenue by city x restaurant."""
    return (
        df.pivot_table(values="revenue", index="city", columns="restaurant_name",
                       aggfunc="sum", fill_value=0)
        .round(0).astype(int)
    )


def delivery_pivot(df: pd.DataFrame) -> pd.DataFrame:
    """Cross-tab: order count by city x delivery_status."""
    return df.pivot_table(values="order_id", index="city", columns="delivery_status",
                          aggfunc="count", fill_value=0)


def descriptive_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Transposed descriptive statistics for key numeric columns."""
    return df[NUMERIC_COLS].describe().T.round(2)


def render_summary_tab(df_f: pd.DataFrame) -> None:
    """Render the complete Summary Stats tab."""
    st.markdown('<div class="section-header">3. Group & Summarise</div>', unsafe_allow_html=True)

    sel_dim = st.selectbox("Group by dimension", list(GROUP_DIMENSIONS.keys()))
    col_key = GROUP_DIMENSIONS[sel_dim]
    summary_df = make_summary(col_key, df_f)
    display_cols = {
        col_key:               sel_dim,
        "Total_Revenue":       "Total Revenue (PKR)",
        "Total_Orders":        "Total Orders",
        "Avg_Price":           "Avg Price (PKR)",
        "Avg_Rating":          "Avg Rating",
        "Avg_Quantity":        "Avg Quantity",
        "Avg_Loyalty_Points":  "Avg Loyalty Points",
        "Avg_Order_Frequency": "Avg Order Frequency",
    }
    st.dataframe(summary_df.rename(columns=display_cols), use_container_width=True, hide_index=True)

    st.subheader("Cross-Tab: Revenue by City x Restaurant")
    st.dataframe(revenue_pivot(df_f), use_container_width=True)

    st.subheader("Cross-Tab: Order Count by City x Delivery Status")
    st.dataframe(delivery_pivot(df_f), use_container_width=True)

    st.subheader("Descriptive Statistics (Numeric Columns)")
    st.dataframe(descriptive_stats(df_f), use_container_width=True)

# ==============================================================================
# SECTION 6 — CHARTS
# 14 individual Plotly chart builders and the Tab 4 renderer.
# ==============================================================================

def chart_revenue_by_city(df: pd.DataFrame) -> go.Figure:
    data = df.groupby("city")["revenue"].sum().reset_index().sort_values("revenue", ascending=False)
    fig = px.bar(data, x="city", y="revenue", color="city", color_discrete_sequence=PALETTE,
                 labels={"city": "City", "revenue": "Total Revenue (PKR)"}, text_auto=".3s")
    fig.update_layout(showlegend=False, xaxis_title="City", yaxis_title="Revenue (PKR)", height=380)
    return fig


def chart_revenue_by_restaurant(df: pd.DataFrame) -> go.Figure:
    data = df.groupby("restaurant_name")["revenue"].sum().reset_index().sort_values("revenue", ascending=False)
    fig = px.bar(data, x="restaurant_name", y="revenue", color="restaurant_name",
                 color_discrete_sequence=PALETTE,
                 labels={"restaurant_name": "Restaurant", "revenue": "Total Revenue (PKR)"},
                 text_auto=".3s")
    fig.update_layout(showlegend=False, xaxis_title="Restaurant", yaxis_title="Revenue (PKR)", height=380)
    return fig


def chart_revenue_by_category(df: pd.DataFrame) -> go.Figure:
    data = df.groupby("category")["revenue"].sum().reset_index()
    fig = px.pie(data, names="category", values="revenue",
                 color_discrete_sequence=PALETTE, hole=0.4)
    fig.update_layout(height=380)
    return fig


def chart_delivery_status_distribution(df: pd.DataFrame) -> go.Figure:
    data = df["delivery_status"].value_counts().reset_index()
    data.columns = ["delivery_status", "count"]
    fig = px.pie(data, names="delivery_status", values="count",
                 color="delivery_status", color_discrete_map=DELIVERY_COLOR_MAP, hole=0.4)
    fig.update_layout(height=380)
    return fig


def chart_avg_rating_by_restaurant(df: pd.DataFrame) -> go.Figure:
    data = df.groupby("restaurant_name")["rating"].mean().reset_index().sort_values("rating", ascending=True)
    fig = px.bar(data, x="rating", y="restaurant_name", orientation="h",
                 color="rating", color_continuous_scale=["#fee2e2", PINK],
                 labels={"restaurant_name": "Restaurant", "rating": "Avg Rating"}, text_auto=".2f")
    fig.update_layout(height=330, coloraxis_showscale=False)
    return fig


def chart_orders_by_age_group(df: pd.DataFrame) -> go.Figure:
    data = df["age"].value_counts().reset_index()
    data.columns = ["age", "count"]
    fig = px.bar(data, x="age", y="count", color="age", color_discrete_sequence=PALETTE,
                 text_auto=True, labels={"age": "Age Group", "count": "Order Count"})
    fig.update_layout(showlegend=False, height=350)
    return fig


def chart_payment_method_distribution(df: pd.DataFrame) -> go.Figure:
    data = df["payment_method"].value_counts().reset_index()
    data.columns = ["payment_method", "count"]
    fig = px.pie(data, names="payment_method", values="count",
                 color_discrete_sequence=[PINK, ORANGE, PURPLE], hole=0.4)
    fig.update_layout(height=350)
    return fig


def chart_revenue_by_gender_age(df: pd.DataFrame) -> go.Figure:
    data = (df.groupby(["gender", "age"])["revenue"].sum().reset_index()
            .rename(columns={"revenue": "Total Revenue (PKR)"}))
    fig = px.bar(data, x="gender", y="Total Revenue (PKR)", color="age",
                 barmode="group", color_discrete_sequence=PALETTE,
                 labels={"gender": "Gender", "age": "Age Group"}, text_auto=".3s")
    fig.update_layout(height=380)
    return fig


def chart_churn_by_city(df: pd.DataFrame) -> go.Figure:
    data = (df.groupby(["city", "churned"])["customer_id"].nunique().reset_index()
            .rename(columns={"customer_id": "Customers"}))
    fig = px.bar(data, x="city", y="Customers", color="churned", barmode="group",
                 color_discrete_map=CHURN_COLOR_MAP,
                 labels={"city": "City", "churned": "Status"}, text_auto=True)
    fig.update_layout(height=380)
    return fig


def chart_loyalty_points_by_churn(df: pd.DataFrame) -> go.Figure:
    fig = px.box(df, x="churned", y="loyalty_points", color="churned",
                 color_discrete_map=CHURN_COLOR_MAP,
                 labels={"churned": "Customer Status", "loyalty_points": "Loyalty Points"},
                 points="outliers")
    fig.update_layout(showlegend=False, height=380)
    return fig


def chart_revenue_heatmap(df: pd.DataFrame) -> go.Figure:
    pivot = df.pivot_table(values="revenue", index="city",
                           columns="restaurant_name", aggfunc="sum").round(0)
    fig = px.imshow(pivot, text_auto=".3s",
                    color_continuous_scale=["#fff1f2", PINK],
                    labels=dict(x="Restaurant", y="City", color="Revenue (PKR)"), aspect="auto")
    fig.update_layout(height=380)
    return fig


def chart_price_vs_rating_scatter(df: pd.DataFrame) -> go.Figure:
    data = df.groupby(["restaurant_name", "dish_name"], as_index=False).agg(
        Avg_Price=("price", "mean"), Avg_Rating=("rating", "mean"), Orders=("order_id", "count"))
    fig = px.scatter(data, x="Avg_Price", y="Avg_Rating", size="Orders",
                     color="restaurant_name", hover_name="dish_name",
                     color_discrete_sequence=PALETTE,
                     labels={"Avg_Price": "Avg Price (PKR)", "Avg_Rating": "Avg Rating",
                             "restaurant_name": "Restaurant"})
    fig.update_layout(height=400)
    return fig


def chart_order_frequency_histogram(df: pd.DataFrame) -> go.Figure:
    fig = px.histogram(df, x="order_frequency", color="churned",
                       color_discrete_map=CHURN_COLOR_MAP,
                       nbins=30, barmode="overlay", opacity=0.7,
                       labels={"order_frequency": "Order Frequency", "churned": "Status"})
    fig.update_layout(height=370)
    return fig


def chart_top_dishes_by_revenue(df: pd.DataFrame) -> go.Figure:
    data = df.groupby("dish_name")["revenue"].sum().reset_index().sort_values("revenue", ascending=True)
    fig = px.bar(data, x="revenue", y="dish_name", orientation="h",
                 color="revenue", color_continuous_scale=["#fce7f3", PINK],
                 labels={"dish_name": "Dish", "revenue": "Total Revenue (PKR)"}, text_auto=".3s")
    fig.update_layout(height=330, coloraxis_showscale=False)
    return fig


def render_charts_tab(df_f: pd.DataFrame) -> None:
    """Render all 14 charts inside the active tab context."""
    st.markdown('<div class="section-header">4. Charts & Visual Comparisons</div>', unsafe_allow_html=True)

    st.subheader("4.1 Revenue by City")
    st.plotly_chart(chart_revenue_by_city(df_f), use_container_width=True)

    st.subheader("4.2 Revenue by Restaurant")
    st.plotly_chart(chart_revenue_by_restaurant(df_f), use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("4.3 Revenue by Food Category")
        st.plotly_chart(chart_revenue_by_category(df_f), use_container_width=True)
    with c2:
        st.subheader("4.4 Order Count by Delivery Status")
        st.plotly_chart(chart_delivery_status_distribution(df_f), use_container_width=True)

    st.subheader("4.5 Average Rating by Restaurant")
    st.plotly_chart(chart_avg_rating_by_restaurant(df_f), use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("4.6 Orders by Age Group")
        st.plotly_chart(chart_orders_by_age_group(df_f), use_container_width=True)
    with c4:
        st.subheader("4.7 Payment Method Distribution")
        st.plotly_chart(chart_payment_method_distribution(df_f), use_container_width=True)

    st.subheader("4.8 Revenue by Gender x Age Group")
    st.plotly_chart(chart_revenue_by_gender_age(df_f), use_container_width=True)

    st.subheader("4.9 Active vs Inactive Customers by City")
    st.plotly_chart(chart_churn_by_city(df_f), use_container_width=True)

    st.subheader("4.10 Loyalty Points Distribution (Active vs Inactive)")
    st.plotly_chart(chart_loyalty_points_by_churn(df_f), use_container_width=True)

    st.subheader("4.11 Revenue Heatmap: City x Restaurant")
    st.plotly_chart(chart_revenue_heatmap(df_f), use_container_width=True)

    st.subheader("4.12 Price vs. Rating (Scatter)")
    st.plotly_chart(chart_price_vs_rating_scatter(df_f), use_container_width=True)

    st.subheader("4.13 Order Frequency Distribution")
    st.plotly_chart(chart_order_frequency_histogram(df_f), use_container_width=True)

    st.subheader("4.14 Top Dishes by Revenue")
    st.plotly_chart(chart_top_dishes_by_revenue(df_f), use_container_width=True)

# ==============================================================================
# SECTION 7 — BUSINESS INSIGHTS
# KPI computation, key findings, strategic recommendations, decision scorecard.
# ==============================================================================

def compute_insights(df: pd.DataFrame) -> dict:
    """Compute all business insight KPIs from the full (unfiltered) dataset."""
    top_city     = df.groupby("city")["revenue"].sum().idxmax()
    top_city_rev = df.groupby("city")["revenue"].sum().max()
    top_rest     = df.groupby("restaurant_name")["revenue"].sum().idxmax()
    top_rest_rev = df.groupby("restaurant_name")["revenue"].sum().max()
    best_rated   = df.groupby("restaurant_name")["rating"].mean().idxmax()
    worst_rated  = df.groupby("restaurant_name")["rating"].mean().idxmin()
    delivered_pct = (df["delivery_status"] == "Delivered").mean() * 100
    delayed_pct   = (df["delivery_status"] == "Delayed").mean()   * 100
    cancelled_pct = (df["delivery_status"] == "Cancelled").mean() * 100
    inactive_pct  = (df["churned"] == "Inactive").mean() * 100
    top_cat       = df.groupby("category")["revenue"].sum().idxmax()
    top_pay       = df["payment_method"].value_counts().idxmax()
    top_pay_pct   = df["payment_method"].value_counts(normalize=True).max() * 100
    top_age       = df.groupby("age")["revenue"].sum().idxmax()
    avg_loy_act   = df[df["churned"] == "Active"]["loyalty_points"].mean()
    avg_loy_inact = df[df["churned"] == "Inactive"]["loyalty_points"].mean()
    freq_act      = df[df["churned"] == "Active"]["order_frequency"].mean()
    freq_inact    = df[df["churned"] == "Inactive"]["order_frequency"].mean()
    city_cancel_s = df.groupby("city").apply(lambda x: (x["delivery_status"] == "Cancelled").mean() * 100)
    city_cancel   = city_cancel_s.idxmax()
    city_cancel_p = city_cancel_s.max()
    return dict(
        top_city=top_city, top_city_rev=top_city_rev,
        top_rest=top_rest, top_rest_rev=top_rest_rev,
        best_rated_rest=best_rated, worst_rated_rest=worst_rated,
        delivered_pct=delivered_pct, delayed_pct=delayed_pct, cancelled_pct=cancelled_pct,
        inactive_pct=inactive_pct, top_cat=top_cat,
        top_pay=top_pay, top_pay_pct=top_pay_pct, top_age=top_age,
        avg_loyalty_active=avg_loy_act, avg_loyalty_inactive=avg_loy_inact,
        freq_active=freq_act, freq_inactive=freq_inact,
        city_cancel=city_cancel, city_cancel_pct=city_cancel_p,
        avg_rating=df["rating"].mean(), avg_loyalty_all=df["loyalty_points"].mean(),
    )


def render_insights_tab(df: pd.DataFrame) -> None:
    """Render the Business Insights tab using the full (unfiltered) dataset."""
    st.markdown('<div class="section-header">5. Business Insights & Recommendations</div>',
                unsafe_allow_html=True)
    kv = compute_insights(df)

    st.subheader("Key Findings")
    findings = [
        (f"Top Revenue City: {kv['top_city']}",
         f"{kv['top_city']} generates the highest total revenue of PKR {kv['top_city_rev']:,.0f}. "
         f"Foodpanda should prioritise promotions, rider capacity, and restaurant partnerships here."),
        (f"Top Restaurant: {kv['top_rest']}",
         f"{kv['top_rest']} leads in total revenue (PKR {kv['top_rest_rev']:,.0f}). Strengthening "
         f"this partnership through exclusive deals and featured placement can drive further growth."),
        (f"Highest Rated Restaurant: {kv['best_rated_rest']}",
         f"{kv['best_rated_rest']} has the best average customer rating. Showcasing their ratings "
         f"in the app builds trust and drives order volume."),
        (f"Lowest Rated Restaurant: {kv['worst_rated_rest']}",
         f"{kv['worst_rated_rest']} has the lowest average rating. A quality review and customer "
         f"feedback follow-up programme is recommended."),
        (f"Delivery Performance: {kv['delivered_pct']:.1f}% Delivered, "
         f"{kv['delayed_pct']:.1f}% Delayed, {kv['cancelled_pct']:.1f}% Cancelled",
         f"Only {kv['delivered_pct']:.1f}% of orders arrive on time. Improving last-mile logistics "
         f"is critical to customer satisfaction and retention."),
        (f"Churn Rate: {kv['inactive_pct']:.1f}% Inactive Customers",
         f"{kv['inactive_pct']:.1f}% of customers are inactive. Active customers average "
         f"{kv['avg_loyalty_active']:.0f} loyalty points vs {kv['avg_loyalty_inactive']:.0f} for "
         f"inactive — the loyalty programme needs a re-engagement push."),
        (f"Top Food Category: {kv['top_cat']}",
         f"The {kv['top_cat']} category generates the most revenue. Curating more options and "
         f"running targeted campaigns can boost this segment further."),
        (f"Dominant Payment Method: {kv['top_pay']} ({kv['top_pay_pct']:.1f}%)",
         f"Cashback incentives for Card/Wallet orders can reduce cash handling costs and enrich "
         f"customer transaction data."),
        (f"Highest Spending Age Group: {kv['top_age']}",
         f"{kv['top_age']} customers contribute the most revenue. Campaigns should be tailored for "
         f"this segment while also engaging Teenagers and Seniors."),
        ("Order Frequency Insight",
         f"Active customers order {kv['freq_active']:.1f}x vs {kv['freq_inactive']:.1f}x for "
         f"inactive. Personalised vouchers can bridge this gap."),
    ]
    for title, body in findings:
        st.markdown(f'<div class="insight-card"><div class="title">{title}</div>'
                    f'<div class="body">{body}</div></div>', unsafe_allow_html=True)

    st.subheader("Strategic Recommendations")
    recs = [
        ("1. Double down on top-performing markets",
         f"Invest in advertising and rider incentives in {kv['top_city']} and other high-revenue "
         f"cities. Expand restaurant coverage in lower-revenue cities to grow market share."),
        ("2. Improve delivery reliability",
         f"The combined Delayed + Cancelled rate of {kv['delayed_pct'] + kv['cancelled_pct']:.1f}% "
         f"signals operational inefficiencies. Optimise routing and set SLA penalties — especially "
         f"in {kv['city_cancel']} ({kv['city_cancel_pct']:.1f}% cancellation rate)."),
        ("3. Re-engage churned customers",
         f"Target the {kv['inactive_pct']:.1f}% inactive base with 'We miss you' notifications, "
         f"limited-time discounts (20% off next 3 orders), and loyalty point bonuses."),
        ("4. Boost the loyalty programme",
         f"Introduce tier-based rewards (Bronze / Silver / Gold) and double-point events to drive "
         f"more frequent orders and reduce churn."),
        ("5. Elevate poorly rated restaurants",
         f"Partner with {kv['worst_rated_rest']} on quality improvements. Restaurants below 2.5 "
         f"stars should receive a quality audit before continued listing."),
        ("6. Promote digital payments",
         f"Offer PKR 50-100 cashback on first-time Card or Wallet orders to shift away from "
         f"cash, reduce handling costs, and enable richer customer data."),
        ("7. Category-specific campaigns",
         f"Run bundles and chef-spotlight campaigns for the high-revenue {kv['top_cat']} category. "
         f"Trial Dessert and niche categories to diversify revenue streams."),
        ("8. Age group targeting",
         f"Create youth-friendly meal deals for Teenagers and convenience bundles for Seniors, "
         f"broadening the addressable market beyond the core {kv['top_age']} segment."),
    ]
    for title, body in recs:
        st.markdown(f'<div class="rec-card"><div class="title">{title}</div>'
                    f'<div class="body">{body}</div></div>', unsafe_allow_html=True)

    st.subheader("Decision Scorecard")
    scorecard = pd.DataFrame({
        "Metric":    ["Delivery Success Rate", "Cancellation Rate", "Delay Rate",
                      "Churn (Inactive) Rate", "Avg Rating", "Avg Loyalty Points"],
        "Value":     [f"{kv['delivered_pct']:.1f}%", f"{kv['cancelled_pct']:.1f}%",
                      f"{kv['delayed_pct']:.1f}%",   f"{kv['inactive_pct']:.1f}%",
                      f"{kv['avg_rating']:.2f}/5",   f"{kv['avg_loyalty_all']:.0f}"],
        "Benchmark": [">=85%", "<=5%", "<=10%", "<=20%", ">=4.0/5", ">=300"],
        "Status":    [
            "OK" if kv["delivered_pct"]  >= 85  else "Needs Work",
            "OK" if kv["cancelled_pct"]  <= 5   else "Needs Work",
            "OK" if kv["delayed_pct"]    <= 10  else "Needs Work",
            "OK" if kv["inactive_pct"]   <= 20  else "Needs Work",
            "OK" if kv["avg_rating"]     >= 4.0 else "Needs Work",
            "OK" if kv["avg_loyalty_all"]>= 300 else "Needs Work",
        ],
    })
    st.dataframe(scorecard, use_container_width=True, hide_index=True)

# ==============================================================================
# SECTION 8 — APP ENTRY POINT
# Streamlit page config, sidebar, tab layout — delegates to sections above.
# ==============================================================================

st.set_page_config(
    page_title="Foodpanda Analysis Dashboard",
    page_icon="🍕",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# ── Load data ──────────────────────────────────────────────────────────────────
df_raw = load_data(DATASET_PATH)
df     = df_raw.copy()

# ── Sidebar filters ────────────────────────────────────────────────────────────
with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Foodpanda_logo.svg/200px-Foodpanda_logo.svg.png",
        width=160,
    )
    st.markdown("## Filters")
    sel_city  = st.selectbox("City",            ["All"] + sorted(df["city"].dropna().unique().tolist()))
    sel_rest  = st.selectbox("Restaurant",      ["All"] + sorted(df["restaurant_name"].dropna().unique().tolist()))
    sel_cat   = st.selectbox("Food Category",   ["All"] + sorted(df["category"].dropna().unique().tolist()))
    sel_churn = st.selectbox("Customer Status", ["All", "Active", "Inactive"])
    st.markdown("---")
    st.caption(f"Dataset: {DATASET_PATH}")
    st.caption(f"Total records: **{len(df_raw):,}**")

df_f = apply_filters(df, city=sel_city, restaurant=sel_rest, category=sel_cat, churn=sel_churn)

# ── Page header ────────────────────────────────────────────────────────────────
st.markdown("""
    <div class="main-header">
        <h1>🍕 Foodpanda Analysis Dashboard</h1>
        <p>End-to-end data analysis: quality checks &middot; summaries &middot; charts &middot; business decisions</p>
    </div>""", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_overview, tab_quality, tab_summary, tab_charts, tab_insights = st.tabs(
    ["📋 Overview", "🔍 Data Quality", "📊 Summary Stats", "📈 Charts", "💡 Business Insights"]
)

# Tab 1 — Overview
with tab_overview:
    st.markdown('<div class="section-header">Dataset Overview</div>', unsafe_allow_html=True)

    total_orders  = len(df_f)
    total_revenue = df_f["revenue"].sum()
    unique_cust   = df_f["customer_id"].nunique()
    avg_rating    = df_f["rating"].mean()
    delivered_pct = (df_f["delivery_status"] == "Delivered").mean() * 100

    c1, c2, c3, c4, c5 = st.columns(5)
    for col, label, fmt in [
        (c1, "Total Orders",        f"{total_orders:,}"),
        (c2, "Total Revenue (PKR)", f"PKR {total_revenue:,.0f}"),
        (c3, "Unique Customers",    f"{unique_cust:,}"),
        (c4, "Avg Rating",          f"{avg_rating:.2f} / 5"),
        (c5, "Delivery Rate",       f"{delivered_pct:.1f} %"),
    ]:
        col.markdown(
            f'<div class="kpi-card"><div class="label">{label}</div>'
            f'<div class="value">{fmt}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-header">Dataset Preview (first 100 rows)</div>', unsafe_allow_html=True)
    st.dataframe(df_f.head(100).reset_index(drop=True), use_container_width=True, height=380)

    st.markdown('<div class="section-header">Column Descriptions</div>', unsafe_allow_html=True)
    st.dataframe(pd.DataFrame({
        "Column": [
            "customer_id","gender","age","city","signup_date","order_id","order_date",
            "restaurant_name","dish_name","category","quantity","price","payment_method",
            "order_frequency","last_order_date","loyalty_points","churned","rating",
            "rating_date","delivery_status","revenue",
        ],
        "Description": [
            "Unique customer identifier",
            "Gender of the customer (Male / Female / Other)",
            "Age group (Teenager / Adult / Senior)",
            "City where the customer is located",
            "Date the customer signed up (YYYY-MM-DD)",
            "Unique order identifier",
            "Date the order was placed (YYYY-MM-DD)",
            "Name of the restaurant",
            "Name of the dish ordered",
            "Food category (Italian / Fast Food / Chinese / Continental / Dessert)",
            "Number of items ordered (1-5)",
            "Price per item in PKR",
            "Payment method used (Cash / Card / Wallet)",
            "Total number of orders placed by this customer",
            "Date of the customer's most recent order (YYYY-MM-DD)",
            "Loyalty reward points accumulated",
            "Customer retention status (Active / Inactive)",
            "Customer satisfaction rating (1-5)",
            "Date the rating was submitted (YYYY-MM-DD)",
            "Delivery outcome (Delivered / Delayed / Cancelled)",
            "Derived: quantity x price (total revenue for this order row)",
        ],
    }), use_container_width=True, hide_index=True)

# Tab 2 — Data Quality
with tab_quality:
    render_quality_tab(df_raw)

# Tab 3 — Summary Stats
with tab_summary:
    render_summary_tab(df_f)

# Tab 4 — Charts
with tab_charts:
    render_charts_tab(df_f)

# Tab 5 — Business Insights (always uses full dataset)
with tab_insights:
    render_insights_tab(df)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
    <hr style="margin-top:2rem; border-color:#e5e7eb;">
    <p style="text-align:center; font-size:0.78rem; color:#9ca3af;">
        Foodpanda Analysis Dashboard &nbsp;&middot;&nbsp; Built with Streamlit &amp; Plotly
        &nbsp;&middot;&nbsp; Dataset: Foodpanda_Cleaned_Dataset.csv
    </p>""", unsafe_allow_html=True)

"""
Airline Loyalty Program Analytics Dashboard
Streamlit Application
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import sys
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import GradientBoostingRegressor

# ──────────────────────────────────────────────
# PAGE CONFIG & CUSTOM CSS FOR PREMIUM LOOK
# ──────────────────────────────────────────────

st.set_page_config(
    page_title="Airline Loyalty & Demographics Analytics",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Premium Custom CSS (Outfit font, gradient header, styled cards, glassmorphism)
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Outfit', sans-serif;
        }
        
        .main {
            background-color: #f7f9fc;
        }
        
        /* Metric Card Styling */
        .metric-card {
            padding: 16px;
            border-radius: 16px;
            color: white;
            box-shadow: 0 10px 20px rgba(0,0,0,0.08);
            margin-bottom: 20px;
            transition: transform 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
        }
        
        .metric-title {
            font-size: 11px;
            font-weight: 300;
            text-transform: uppercase;
            letter-spacing: 1px;
            opacity: 0.9;
            margin-bottom: 6px;
        }
        
        .metric-value {
            font-size: 20px;
            font-weight: 700;
            margin: 0;
            white-space: nowrap;
        }
        
        /* Glassmorphism card for standard text containers */
        .glass-card {
            background: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.18);
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)


# Helper function to generate HTML metric cards
def render_metric_card(title, value, gradient_style):
    st.markdown(f"""
        <div class="metric-card" style="background: {gradient_style};">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
        </div>
    """, unsafe_allow_html=True)


def format_large_number(num, is_currency=False):
    prefix = "$" if is_currency else ""
    if pd.isna(num):
        return "N/A"
    if num >= 1_000_000_000:
        return f"{prefix}{num / 1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"{prefix}{num / 1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{prefix}{num / 1_000:.1f}K"
    else:
        return f"{prefix}{num:.2f}" if is_currency else f"{num:,.0f}"


# ──────────────────────────────────────────────
# DATA LOADING & CACHING
# ──────────────────────────────────────────────

@st.cache_data
def load_processed_data():
    data_dir = "data/processed"
    cust_path = os.path.join(data_dir, "dim_customer.csv")
    act_path = os.path.join(data_dir, "fact_activity.csv")
    date_path = os.path.join(data_dir, "dim_date.csv")
    
    if os.path.exists(cust_path) and os.path.exists(act_path) and os.path.exists(date_path):
        customers = pd.read_csv(cust_path)
        activity = pd.read_csv(act_path)
        dates = pd.read_csv(date_path)
        
        # Merge activities with dates and demographics for full analytical capacity
        df_merged = activity.merge(customers, on="customer_id", how="inner")
        df_merged = df_merged.merge(dates, on="date_id", how="inner")
        
        return customers, df_merged, dates
    else:
        st.error("Processed data files not found! Please make sure you have run `python etl_pipeline.py` first.")
        st.stop()

customers, df_merged, dates = load_processed_data()


# ──────────────────────────────────────────────
# SIDEBAR FILTERS
# ──────────────────────────────────────────────

st.sidebar.title("✈️ Analytics Filters")
st.sidebar.markdown("Filter details across all charts:")

# Year Filter
years = sorted(df_merged["year"].unique())
sel_year = st.sidebar.multiselect("Select Years", years, default=years)

# Loyalty Card Filter
card_tiers = sorted(customers["loyalty_card"].unique())
sel_tier = st.sidebar.multiselect("Select Loyalty Card Tiers", card_tiers, default=card_tiers)

# Province Filter
provinces = sorted(customers["province"].unique())
sel_province = st.sidebar.multiselect("Select Provinces", provinces, default=provinces)

# Apply filters
filtered_df = df_merged[
    df_merged["year"].isin(sel_year) &
    df_merged["loyalty_card"].isin(sel_tier) &
    df_merged["province"].isin(sel_province)
]

filtered_cust = customers[
    customers["loyalty_card"].isin(sel_tier) &
    customers["province"].isin(sel_province)
]


# ──────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────

st.title("✈️ Airline Customer Loyalty Analytics")
st.caption("Data Warehouse Star Schema · Customer Profiles & Flight Activity Analysis")
st.divider()


# ──────────────────────────────────────────────
# KPI METRICS ROW (Gradients & Shadows)
# ──────────────────────────────────────────────

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    total_flights = filtered_df["total_flights"].sum()
    render_metric_card("Total Flights Booked", format_large_number(total_flights), "linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)")

with c2:
    total_distance = filtered_df["distance"].sum()
    render_metric_card("Total Distance Flown", f"{format_large_number(total_distance)} km", "linear-gradient(135deg, #2C3E50 0%, #FD746C 100%)")

with c3:
    pts_acc = filtered_df["points_accumulated"].sum()
    render_metric_card("Points Accumulated", format_large_number(pts_acc), "linear-gradient(135deg, #11998e 0%, #38ef7d 100%)")

with c4:
    pts_red = filtered_df["points_redeemed"].sum()
    render_metric_card("Points Redeemed", format_large_number(pts_red), "linear-gradient(135deg, #8E54E9 0%, #4776E6 100%)")

with c5:
    avg_clv = filtered_cust["clv"].mean()
    render_metric_card("Average Customer CLV", format_large_number(avg_clv, is_currency=True), "linear-gradient(135deg, #FC466B 0%, #3F5EFB 100%)")

st.divider()


# ──────────────────────────────────────────────
# ROW 1: POINTS & FLIGHT TRENDS
# ──────────────────────────────────────────────

col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Monthly Loyalty Activity Trends")
    # Group by chronological order
    trend_df = (
        filtered_df.groupby(["year", "month", "month_name"])
        .agg(
            total_flights=("total_flights", "sum"),
            points_accumulated=("points_accumulated", "sum"),
            points_redeemed=("points_redeemed", "sum")
        )
        .reset_index()
    )
    trend_df["period"] = pd.to_datetime(trend_df.assign(day=1)[["year", "month", "day"]])
    trend_df = trend_df.sort_values("period")
    
    fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Points Accumulated Line
    fig_trend.add_trace(
        go.Scatter(x=trend_df["period"], y=trend_df["points_accumulated"], 
                   name="Points Accumulated", line=dict(color="#11998e", width=3)),
        secondary_y=False
    )
    
    # Points Redeemed Line
    fig_trend.add_trace(
        go.Scatter(x=trend_df["period"], y=trend_df["points_redeemed"], 
                   name="Points Redeemed", line=dict(color="#8E54E9", width=3, dash="dash")),
        secondary_y=False
    )
    
    # Total Flights Booked (Bar on secondary axis)
    fig_trend.add_trace(
        go.Bar(x=trend_df["period"], y=trend_df["total_flights"], 
               name="Flights Booked", marker_color="rgba(42, 82, 152, 0.35)"),
        secondary_y=True
    )
    
    fig_trend.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=20, r=20, t=30, b=20),
        height=380,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    fig_trend.update_yaxes(title_text="Points Value", secondary_y=False, gridcolor="rgba(0,0,0,0.05)")
    fig_trend.update_yaxes(title_text="Flight Count", secondary_y=True)
    
    st.plotly_chart(fig_trend, use_container_width=True)

with col2:
    st.subheader("🍰 Loyalty Tier Breakdown & Engagement")
    tier_df = (
        filtered_cust.groupby("loyalty_card")
        .agg(
            customer_count=("customer_id", "count"),
            avg_salary=("salary", "mean"),
            avg_clv=("clv", "mean")
        )
        .reset_index()
    )
    
    fig_pie = px.pie(
        tier_df, names="loyalty_card", values="customer_count",
        color="loyalty_card",
        color_discrete_map={"Star": "#2a5298", "Nova": "#FD746C", "Aurora": "#8E54E9"},
        hole=0.5
    )
    fig_pie.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        height=380,
    )
    st.plotly_chart(fig_pie, use_container_width=True)


# ──────────────────────────────────────────────
# ROW 2: DEMOGRAPHICS & GEOGRAPHY
# ──────────────────────────────────────────────

col3, col4 = st.columns(2)

with col3:
    st.subheader("💰 Salary Distribution by Education Level")
    
    fig_box = px.box(
        filtered_cust, x="education", y="salary", 
        color="education",
        color_discrete_sequence=px.colors.qualitative.Safe,
        category_orders={"education": ["High School or Below", "College", "Bachelor", "Master", "Doctor"]},
        labels={"education": "Education Level", "salary": "Salary ($)"}
    )
    fig_box.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        height=380,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False
    )
    fig_box.update_yaxes(gridcolor="rgba(0,0,0,0.05)")
    st.plotly_chart(fig_box, use_container_width=True)

with col4:
    st.subheader("📍 Customer Distribution by Province")
    prov_df = (
        filtered_cust.groupby("province")
        .agg(
            customer_count=("customer_id", "count"),
            avg_clv=("clv", "mean")
        )
        .reset_index()
        .sort_values("customer_count", ascending=True)
    )
    
    fig_prov = px.bar(
        prov_df, x="customer_count", y="province", orientation="h",
        color="avg_clv", color_continuous_scale="Viridis",
        labels={"customer_count": "Customers", "province": "Province", "avg_clv": "Average CLV ($)"}
    )
    fig_prov.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        height=380,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_prov, use_container_width=True)


# ──────────────────────────────────────────────
# ROW 3: POINTS EFFICIENCY ANALYSIS & DEMOGRAPHICS
# ──────────────────────────────────────────────

col5, col6 = st.columns(2)

with col5:
    st.subheader("💡 Points Redemption Efficiency by Loyalty Card Tier")
    # Ratio of points redeemed to points accumulated
    redemp_df = (
        filtered_df.groupby("loyalty_card")
        .agg(
            points_accumulated=("points_accumulated", "sum"),
            points_redeemed=("points_redeemed", "sum"),
            dollar_cost=("dollar_cost_points_redeemed", "sum")
        )
        .reset_index()
    )
    redemp_df["redemption_ratio"] = (redemp_df["points_redeemed"] / redemp_df["points_accumulated"] * 100).round(2)
    
    fig_redemp = px.bar(
        redemp_df, x="loyalty_card", y="redemption_ratio",
        color="loyalty_card",
        color_discrete_map={"Star": "#2a5298", "Nova": "#FD746C", "Aurora": "#8E54E9"},
        labels={"loyalty_card": "Loyalty Tier", "redemption_ratio": "Redemption Rate (%)"}
    )
    fig_redemp.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        height=350,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False
    )
    st.plotly_chart(fig_redemp, use_container_width=True)

with col6:
    st.subheader("💍 Average CLV by Marital Status & Gender")
    marital_df = (
        filtered_cust.groupby(["marital_status", "gender"])
        .agg(avg_clv=("clv", "mean"))
        .reset_index()
    )
    
    fig_marital = px.bar(
        marital_df, x="marital_status", y="avg_clv", color="gender",
        barmode="group",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        labels={"marital_status": "Marital Status", "avg_clv": "Average CLV ($)"}
    )
    fig_marital.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        height=350,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_marital, use_container_width=True)


# ──────────────────────────────────────────────
# MACHINE LEARNING INTERACTIVE CLV PREDICTOR
# ──────────────────────────────────────────────

st.divider()
st.subheader("🔮 Interactive Customer Value (CLV) Predictor")

# Run a quick training of a high-performance Gradient Boosting model for the UI
@st.cache_resource
def get_trained_predictor(df_cust):
    df = df_cust.copy()
    feature_cols = ["gender", "education", "marital_status", "loyalty_card", "salary", "enrollment_type"]
    
    # Store encoders
    encoders = {}
    for col in ["gender", "education", "marital_status", "loyalty_card", "enrollment_type"]:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        encoders[col] = le
        
    df = df.dropna(subset=feature_cols + ["clv"])
    X = df[feature_cols].values
    y = df["clv"].values
    
    model = GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42)
    model.fit(X, y)
    
    return model, encoders

model, encoders = get_trained_predictor(customers)

# Setup layout for predictor
col_inputs, col_prediction = st.columns([2, 1])

with col_inputs:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("##### Fill Demographics:")
    
    c_in1, c_in2, c_in3 = st.columns(3)
    with c_in1:
        sel_gen = st.selectbox("Gender", encoders["gender"].classes_)
        sel_edu = st.selectbox("Education Level", encoders["education"].classes_)
    with c_in2:
        sel_mar = st.selectbox("Marital Status", encoders["marital_status"].classes_)
        sel_card = st.selectbox("Loyalty Card Tier", encoders["loyalty_card"].classes_)
    with c_in3:
        sel_salary = st.number_input("Annual Salary ($)", min_value=0, max_value=500000, value=75000, step=1000)
        sel_enroll = st.selectbox("Enrollment Type", encoders["enrollment_type"].classes_)
        
    st.markdown("</div>", unsafe_allow_html=True)

with col_prediction:
    st.markdown("<div class='glass-card' style='height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center;'>", unsafe_allow_html=True)
    st.markdown("<h4 style='margin-bottom: 0;'>Predicted CLV</h4>", unsafe_allow_html=True)
    
    # Encode inputs
    encoded_vals = [
        encoders["gender"].transform([sel_gen])[0],
        encoders["education"].transform([sel_edu])[0],
        encoders["marital_status"].transform([sel_mar])[0],
        encoders["loyalty_card"].transform([sel_card])[0],
        sel_salary,
        encoders["enrollment_type"].transform([sel_enroll])[0]
    ]
    
    prediction = model.predict(np.array(encoded_vals).reshape(1, -1))[0]
    
    st.markdown(f"<h1 style='color: #8E54E9; font-size: 44px; font-weight: 700; margin: 15px 0;'>${prediction:,.2f}</h1>", unsafe_allow_html=True)
    st.info("💡 Calculation is processed using an active Gradient Boosting Regressor trained on the real historical loyalty program data.")
    st.markdown("</div>", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# RAW DATA TABLE
# ──────────────────────────────────────────────

st.divider()
with st.expander("📋 Processed Loyalty Log (Sample of first 200 records)"):
    display_cols = [
        "customer_id", "gender", "education", "salary", "marital_status",
        "loyalty_card", "clv", "province", "city", "total_flights",
        "distance", "points_accumulated", "points_redeemed", "month_name", "year"
    ]
    st.dataframe(filtered_df[display_cols].head(200), use_container_width=True, hide_index=True)

st.caption("Star Schema Airline Loyalty Program Data Warehouse · Built with SQLite & PostgreSQL · Python · Streamlit")
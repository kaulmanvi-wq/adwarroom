"""
Competitor Ad War Room
Streamlit Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import os, sys

sys.path.insert(0, os.path.dirname(__file__))

from scraper import load_data
from insights import run_full_analysis, ensure_classified


st.set_page_config(
    page_title="Competitor Ad War Room",
    layout="wide"
)

st.title("🔴 Competitor Ad War Room")


# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def get_data():
    df = load_data()
    df = ensure_classified(df)
    return df


df_full = get_data()


# -----------------------------
# SAFETY FIXES
# -----------------------------

required_cols = [
    "brand",
    "category",
    "format",
    "theme",
    "ad_text",
    "days_running"
]

for col in required_cols:
    if col not in df_full.columns:
        df_full[col] = "unknown"


df_full["days_running"] = pd.to_numeric(
    df_full["days_running"], errors="coerce"
).fillna(0)


# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("Filters")

categories = ["All"] + sorted(df_full["category"].unique())
sel_category = st.sidebar.selectbox("Category", categories)

brands = ["All"] + sorted(df_full["brand"].unique())
sel_brand = st.sidebar.selectbox("Brand", brands)

formats = ["All"] + sorted(df_full["format"].unique())
sel_format = st.sidebar.selectbox("Format", formats)

themes = ["All"] + sorted(df_full["theme"].unique())
sel_theme = st.sidebar.selectbox("Theme", themes)


# -----------------------------
# SAFE SLIDER
# -----------------------------
if df_full.empty:
    min_days = 0
    max_days = 100
else:
    min_days = int(df_full["days_running"].min())
    max_days = int(df_full["days_running"].max())

if min_days == max_days:
    max_days = min_days + 1


days_range = st.sidebar.slider(
    "Days Running",
    min_value=min_days,
    max_value=max_days,
    value=(min_days, max_days)
)


# -----------------------------
# APPLY FILTERS
# -----------------------------
df = df_full.copy()

if sel_category != "All":
    df = df[df["category"] == sel_category]

if sel_brand != "All":
    df = df[df["brand"] == sel_brand]

if sel_format != "All":
    df = df[df["format"] == sel_format]

if sel_theme != "All":
    df = df[df["theme"] == sel_theme]

df = df[
    (df["days_running"] >= days_range[0]) &
    (df["days_running"] <= days_range[1])
]


# -----------------------------
# OVERVIEW
# -----------------------------
st.subheader("Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Total Ads", len(df))
col2.metric("Brands", df["brand"].nunique())
col3.metric("Avg Days Running", int(df["days_running"].mean()))


# -----------------------------
# FORMAT CHART
# -----------------------------
if len(df) > 0:

    format_data = df["format"].value_counts().reset_index()
    format_data.columns = ["Format", "Count"]

    fig = px.pie(
        format_data,
        names="Format",
        values="Count",
        title="Ad Format Distribution"
    )

    st.plotly_chart(fig, use_container_width=True)


# -----------------------------
# THEME CHART
# -----------------------------
if len(df) > 0:

    theme_data = df["theme"].value_counts().reset_index()
    theme_data.columns = ["Theme", "Count"]

    fig = px.bar(
        theme_data,
        x="Theme",
        y="Count",
        title="Message Themes"
    )

    st.plotly_chart(fig, use_container_width=True)


# -----------------------------
# AD EXPLORER
# -----------------------------
st.subheader("Ad Explorer")

if len(df) == 0:
    st.info("No ads found")
else:

    for _, row in df.head(50).iterrows():

        st.markdown(f"""
        **Brand:** {row['brand']}  
        **Category:** {row['category']}  
        **Format:** {row['format']}  
        **Theme:** {row['theme']}  
        **Days Running:** {int(row['days_running'])}

        {row['ad_text']}

        ---
        """)


# -----------------------------
# INSIGHTS
# -----------------------------
st.subheader("AI Insights")

insights = run_full_analysis(df)

for item in insights:
    st.write("•", item)

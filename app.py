"""
app.py — Competitor Ad War Room
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import os, sys

sys.path.insert(0, os.path.dirname(__file__))

from scraper import load_data, BRANDS
from insights import run_full_analysis, ensure_classified


st.set_page_config(
    page_title="Competitor Ad War Room",
    page_icon="🔴",
    layout="wide",
)

# ---------------------------------------------------
# DATA LOADING
# ---------------------------------------------------

@st.cache_data(ttl=3600)
def get_data(token=""):
    try:
        df = load_data(access_token=token if token else None)
    except:
        df = pd.DataFrame()

    return df


# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

with st.sidebar:

    st.title("🔴 Ad War Room")

    meta_token = st.text_input(
        "Meta Access Token (Optional)",
        type="password"
    )

    with st.spinner("Loading data..."):
        df_full = get_data(meta_token)

    # if empty create fallback
    if df_full is None or len(df_full) == 0:
        df_full = pd.DataFrame({
            "brand":[],
            "category":[],
            "format":[],
            "theme":[],
            "days_running":[],
            "ad_text":[],
            "platform":[]
        })

    df_full = ensure_classified(df_full)

    # ensure columns exist
    required_cols = [
        "brand","category","format","theme",
        "days_running","ad_text","platform"
    ]

    for col in required_cols:
        if col not in df_full.columns:
            df_full[col] = ""

    # fix days_running
    df_full["days_running"] = pd.to_numeric(
        df_full["days_running"],
        errors="coerce"
    ).fillna(30)

    st.markdown("---")

    # category filter
    categories = ["All"] + sorted(df_full["category"].dropna().unique().tolist())
    sel_category = st.selectbox("Category", categories)

    df_cat = df_full if sel_category == "All" else df_full[df_full["category"]==sel_category]

    # brand filter
    brands = sorted(df_cat["brand"].dropna().unique().tolist())
    sel_brands = st.multiselect("Brands", brands)

    # format filter
    formats = ["All"] + sorted(df_full["format"].dropna().unique().tolist())
    sel_format = st.selectbox("Format", formats)

    # days slider SAFE
    min_days = int(df_full["days_running"].min()) if len(df_full)>0 else 0
    max_days = int(df_full["days_running"].max()) if len(df_full)>0 else 100

    days_range = st.slider(
        "Days Running",
        min_days,
        max_days,
        (min_days,max_days)
    )


# ---------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------

df = df_full.copy()

if sel_category != "All":
    df = df[df["category"]==sel_category]

if sel_brands:
    df = df[df["brand"].isin(sel_brands)]

if sel_format != "All":
    df = df[df["format"]==sel_format]

df = df[
    (df["days_running"]>=days_range[0]) &
    (df["days_running"]<=days_range[1])
]


# ---------------------------------------------------
# HEADER
# ---------------------------------------------------

st.title("🔴 Competitor Ad War Room")
st.caption("Competitive intelligence from Meta Ad Library")


# ---------------------------------------------------
# TABS
# ---------------------------------------------------

tab1,tab2,tab3 = st.tabs([
    "Overview",
    "Insights",
    "Ad Explorer"
])


# ---------------------------------------------------
# TAB 1
# ---------------------------------------------------

with tab1:

    col1,col2,col3 = st.columns(3)

    col1.metric("Total Ads", len(df))
    col2.metric("Brands", df["brand"].nunique())
    col3.metric("Avg Days Running",
        int(df["days_running"].mean()) if len(df)>0 else 0
    )

    if len(df)>0:

        format_data = df["format"].value_counts().reset_index()
        format_data.columns=["Format","Count"]

        fig = px.pie(
            format_data,
            values="Count",
            names="Format"
        )

        st.plotly_chart(fig,use_container_width=True)

    else:
        st.info("No data available")


# ---------------------------------------------------
# TAB 2
# ---------------------------------------------------

with tab2:

    if len(df_full)==0:
        st.info("No data available for insights")
    else:

        insights = run_full_analysis(df_full)

        for section in insights.values():
            for item in section:
                st.markdown(f"""
**{item['title']}**

{item['body']}
""")


# ---------------------------------------------------
# TAB 3
# ---------------------------------------------------

with tab3:

    if len(df)==0:
        st.info("No ads found")
    else:

        df_display = df.sort_values(
            "days_running",
            ascending=False
        ).head(50)

        for _,row in df_display.iterrows():

            st.markdown(f"""
**{row['brand']}**

{row['ad_text']}

Days running: {int(row['days_running'])}

---
""")

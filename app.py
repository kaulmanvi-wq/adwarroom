import os
import json
import ast
import pandas as pd
import streamlit as st
import altair as alt

DATA_PATH = "data/structured_ads.csv"
INSIGHTS_PATH = "data/insights_summary.json"
TOP_ADS_PATH = "data/top_ads.csv"
BRIEF_PATH = "data/weekly_brief.txt"

st.set_page_config(
    page_title="Competitor Ad War Room",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def load_ads():
    if not os.path.exists(DATA_PATH):
        return pd.DataFrame()

    df = pd.read_csv(DATA_PATH)

    if "start_date" in df.columns:
        df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")

    if "ad_age_days" in df.columns:
        df["ad_age_days"] = pd.to_numeric(df["ad_age_days"], errors="coerce").fillna(0).astype(int)

    if "theme_count" in df.columns:
        df["theme_count"] = pd.to_numeric(df["theme_count"], errors="coerce").fillna(0).astype(int)

    if "text_length" in df.columns:
        df["text_length"] = pd.to_numeric(df["text_length"], errors="coerce").fillna(0).astype(int)

    df["brand"] = df.get("brand", "").fillna("").astype(str)
    df["category"] = df.get("category", "").fillna("").astype(str)
    df["ad_text"] = df.get("ad_text", "").fillna("").astype(str)
    df["format"] = df.get("format", "unknown").fillna("unknown").astype(str)
    df["platform"] = df.get("platform", "Unknown").fillna("Unknown").astype(str)
    df["primary_theme"] = df.get("primary_theme", "other / unclassified").fillna("other / unclassified").astype(str)
    df["url"] = df.get("url", "").fillna("").astype(str)

    if "theme_list" not in df.columns:
        df["theme_list"] = [["other / unclassified"]] * len(df)
    else:
        df["theme_list"] = df["theme_list"].apply(parse_theme_list)

    return df


@st.cache_data
def load_insights():
    if not os.path.exists(INSIGHTS_PATH):
        return {}
    with open(INSIGHTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def load_top_ads():
    if not os.path.exists(TOP_ADS_PATH):
        return pd.DataFrame()
    df = pd.read_csv(TOP_ADS_PATH)
    if "ad_age_days" in df.columns:
        df["ad_age_days"] = pd.to_numeric(df["ad_age_days"], errors="coerce").fillna(0).astype(int)
    if "performance_proxy_score" in df.columns:
        df["performance_proxy_score"] = pd.to_numeric(df["performance_proxy_score"], errors="coerce").fillna(0)
    return df


@st.cache_data
def load_brief():
    if not os.path.exists(BRIEF_PATH):
        return ""
    with open(BRIEF_PATH, "r", encoding="utf-8") as f:
        return f.read()


def parse_theme_list(value):
    if isinstance(value, list):
        return value
    if pd.isna(value):
        return ["other / unclassified"]
    text = str(value).strip()
    if not text:
        return ["other / unclassified"]
    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, list) and parsed:
            return [str(x) for x in parsed]
    except:
        pass
    return [text]


def filter_by_theme(df, selected_themes):
    if not selected_themes:
        return df
    selected_set = set(selected_themes)
    return df[df["theme_list"].apply(lambda themes: len(selected_set.intersection(set(themes))) > 0)]


def build_theme_chart_df(df):
    if df.empty:
        return pd.DataFrame(columns=["theme", "count"])
    exploded = df.explode("theme_list").rename(columns={"theme_list": "theme"})
    exploded["theme"] = exploded["theme"].fillna("other / unclassified").astype(str)
    out = (
        exploded.groupby("theme")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    return out


def metric_card_data(df):
    total_ads = len(df)
    brands = df["brand"].nunique() if not df.empty else 0
    avg_age = round(df["ad_age_days"].mean(), 1) if not df.empty else 0
    top_format = df["format"].mode().iloc[0] if not df.empty else "N/A"
    return total_ads, brands, avg_age, top_format


def render_bullet_list(items, empty_text="No insights available yet."):
    if not items:
        st.write(empty_text)
        return
    for item in items:
        st.markdown(f"- {item}")


ads_df = load_ads()
insights = load_insights()
top_ads_df = load_top_ads()
weekly_brief = load_brief()

st.title("Competitor Ad War Room")
st.caption("Live Meta Ad Library intelligence for D2C growth teams")

if ads_df.empty:
    st.error("No data found. Run scraper.py, processor.py, and insights.py first.")
    st.stop()

# Sidebar filters
st.sidebar.header("Filters")

brand_options = sorted([b for b in ads_df["brand"].dropna().unique().tolist() if b])
format_options = sorted([f for f in ads_df["format"].dropna().unique().tolist() if f])

all_themes = sorted(
    {
        theme
        for themes in ads_df["theme_list"].tolist()
        for theme in themes
        if str(theme).strip()
    }
)

selected_brands = st.sidebar.multiselect(
    "Brand",
    options=brand_options,
    default=brand_options
)

selected_formats = st.sidebar.multiselect(
    "Ad format",
    options=format_options,
    default=format_options
)

selected_themes = st.sidebar.multiselect(
    "Message theme",
    options=all_themes,
    default=all_themes
)

valid_dates = ads_df["start_date"].dropna()
if not valid_dates.empty:
    min_date = valid_dates.min().date()
    max_date = valid_dates.max().date()
    selected_date_range = st.sidebar.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
else:
    selected_date_range = None

filtered_df = ads_df.copy()

if selected_brands:
    filtered_df = filtered_df[filtered_df["brand"].isin(selected_brands)]

if selected_formats:
    filtered_df = filtered_df[filtered_df["format"].isin(selected_formats)]

filtered_df = filter_by_theme(filtered_df, selected_themes)

if selected_date_range and isinstance(selected_date_range, tuple) and len(selected_date_range) == 2:
    start_date, end_date = selected_date_range
    filtered_df = filtered_df[
        (filtered_df["start_date"].dt.date >= start_date) &
        (filtered_df["start_date"].dt.date <= end_date)
    ]

# Top metrics
total_ads, brands_count, avg_age, top_format = metric_card_data(filtered_df)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Tracked ads", total_ads)
c2.metric("Brands in view", brands_count)
c3.metric("Avg. live days", avg_age)
c4.metric("Leading format", top_format.title() if isinstance(top_format, str) else top_format)

st.divider()

# Weekly brief
left, right = st.columns([1.2, 1])

with left:
    st.subheader("Weekly Intelligence Brief")
    if weekly_brief:
        st.code(weekly_brief, language=None)
    else:
        st.info("Weekly brief will appear after you run insights.py")

with right:
    st.subheader("Snapshot")
    overview = insights.get("overview", {})
    if overview:
        st.write(f"**Total ads tracked:** {overview.get('total_ads', 0)}")
        st.write(f"**Brands tracked:** {overview.get('brands_tracked', 0)}")
        st.write(f"**Average ad age:** {overview.get('avg_ad_age_days', 0)} days")
        st.write(f"**Most common format:** {overview.get('top_format', 'N/A')}")
        st.write(f"**Most common theme:** {overview.get('top_theme', 'N/A')}")
    else:
        st.info("Overview will appear after you run insights.py")

st.divider()

# Charts
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Creative format distribution")
    if filtered_df.empty:
        st.info("No ads match the selected filters.")
    else:
        format_chart_df = (
            filtered_df.groupby("format")
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
        )

        format_chart = (
            alt.Chart(format_chart_df)
            .mark_bar()
            .encode(
                x=alt.X("count:Q", title="Ads"),
                y=alt.Y("format:N", sort="-x", title="Format"),
                tooltip=["format", "count"]
            )
            .properties(height=300)
        )
        st.altair_chart(format_chart, use_container_width=True)

with chart_col2:
    st.subheader("Message theme breakdown")
    theme_chart_df = build_theme_chart_df(filtered_df)

    if theme_chart_df.empty:
        st.info("No themes available for the selected filters.")
    else:
        theme_chart = (
            alt.Chart(theme_chart_df.head(12))
            .mark_bar()
            .encode(
                x=alt.X("count:Q", title="Theme mentions"),
                y=alt.Y("theme:N", sort="-x", title="Theme"),
                tooltip=["theme", "count"]
            )
            .properties(height=300)
        )
        st.altair_chart(theme_chart, use_container_width=True)

st.divider()

# Longest running ads + top ads
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Longest running ads")
    longest_ads = (
        filtered_df.sort_values(["ad_age_days", "start_date"], ascending=[False, False])
        [["brand", "category", "format", "primary_theme", "ad_age_days", "start_date", "platform", "url"]]
        .head(15)
        .copy()
    )

    if longest_ads.empty:
        st.info("No ads found for the current filters.")
    else:
        st.dataframe(
            longest_ads,
            hide_index=True,
            use_container_width=True,
            column_config={
                "brand": "Brand",
                "category": "Category",
                "format": "Format",
                "primary_theme": "Theme",
                "ad_age_days": st.column_config.NumberColumn("Live days", format="%d"),
                "start_date": st.column_config.DateColumn("Start date", format="YYYY-MM-DD"),
                "platform": "Platform",
                "url": st.column_config.LinkColumn("Ad URL", display_text="Open ad")
            }
        )

with col_b:
    st.subheader("Likely top-performing ads")
    if top_ads_df.empty:
        st.info("Run insights.py to generate scored ads.")
    else:
        filtered_top_ads = top_ads_df.copy()

        if selected_brands:
            filtered_top_ads = filtered_top_ads[filtered_top_ads["brand"].isin(selected_brands)]
        if selected_formats:
            filtered_top_ads = filtered_top_ads[filtered_top_ads["format"].isin(selected_formats)]
        if selected_themes:
            filtered_top_ads = filtered_top_ads[filtered_top_ads["primary_theme"].isin(selected_themes)]

        filtered_top_ads = filtered_top_ads.head(15)

        st.dataframe(
            filtered_top_ads,
            hide_index=True,
            use_container_width=True,
            column_config={
                "brand": "Brand",
                "category": "Category",
                "format": "Format",
                "primary_theme": "Theme",
                "ad_age_days": st.column_config.NumberColumn("Live days", format="%d"),
                "performance_proxy_score": st.column_config.NumberColumn("Score", format="%.1f"),
                "platform": "Platform",
                "url": st.column_config.LinkColumn("Ad URL", display_text="Open ad"),
                "ad_text": st.column_config.Column("Ad text", width="large")
            }
        )

st.divider()

# AI insights panel
st.subheader("AI insights")

insight_tab1, insight_tab2, insight_tab3, insight_tab4 = st.tabs([
    "Creative trends",
    "Longevity + saturation",
    "Strategic insights",
    "Opportunity gaps"
])

with insight_tab1:
    render_bullet_list(insights.get("creative_trends", []))
    st.markdown("**Format shifts**")
    render_bullet_list(insights.get("format_shifts", []))

with insight_tab2:
    render_bullet_list(insights.get("longevity_signals", []))
    st.markdown("**Message saturation**")
    render_bullet_list(insights.get("message_saturation", []))

with insight_tab3:
    render_bullet_list(insights.get("strategic_insights", []))

with insight_tab4:
    render_bullet_list(insights.get("gap_detection", []))

st.divider()

# Competitor ads table
st.subheader("Competitor ads")

display_df = filtered_df.copy()

if display_df.empty:
    st.warning("No ads match your current filters.")
else:
    display_df = display_df.sort_values(["start_date", "ad_age_days"], ascending=[False, False])

    st.dataframe(
        display_df[[
            "brand",
            "category",
            "format",
            "primary_theme",
            "start_date",
            "ad_age_days",
            "platform",
            "ad_text",
            "url"
        ]],
        hide_index=True,
        use_container_width=True,
        height=500,
        column_config={
            "brand": "Brand",
            "category": "Category",
            "format": "Format",
            "primary_theme": "Theme",
            "start_date": st.column_config.DateColumn("Start date", format="YYYY-MM-DD"),
            "ad_age_days": st.column_config.NumberColumn("Live days", format="%d"),
            "platform": "Platform",
            "ad_text": st.column_config.Column("Ad text", width="large"),
            "url": st.column_config.LinkColumn("Ad URL", display_text="Open ad")
        }
    )

    csv_bytes = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered ads as CSV",
        data=csv_bytes,
        file_name="filtered_competitor_ads.csv",
        mime="text/csv"
    )

st.caption("Built for rapid D2C competitor intelligence using live Meta Ad Library data.")

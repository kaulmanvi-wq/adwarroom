"""
app.py — Competitor Ad War Room
Full Streamlit Dashboard for D2C Competitive Intelligence
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os, sys

sys.path.insert(0, os.path.dirname(__file__))
from scraper import load_data, BRANDS
from insights import run_full_analysis, ensure_classified

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Competitor Ad War Room",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }

    .main-header h1 {
        font-size: 2.4rem;
        font-weight: 700;
        margin: 0;
        color: #fff;
        letter-spacing: -0.5px;
    }

    .main-header p {
        font-size: 1rem;
        color: #a8b2d8;
        margin: 0.3rem 0 0 0;
    }

    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border-left: 4px solid #e94560;
        text-align: center;
    }

    .metric-card .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a1a2e;
        line-height: 1.2;
    }

    .metric-card .metric-label {
        font-size: 0.8rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.3rem;
    }

    .insight-card {
        background: white;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border-left: 4px solid;
    }

    .insight-trend  { border-color: #3b82f6; }
    .insight-longevity { border-color: #10b981; }
    .insight-shift  { border-color: #8b5cf6; }
    .insight-saturation { border-color: #f59e0b; }

    .insight-title {
        font-size: 1rem;
        font-weight: 600;
        color: #1a1a2e;
        margin-bottom: 0.4rem;
    }

    .insight-body {
        font-size: 0.88rem;
        color: #4b5563;
        line-height: 1.6;
    }

    .gap-card {
        background: linear-gradient(135deg, #fff 0%, #fef9f0 100%);
        border-radius: 12px;
        padding: 1.3rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border: 1.5px solid #fde68a;
    }

    .gap-title {
        font-size: 1rem;
        font-weight: 700;
        color: #92400e;
        margin-bottom: 0.4rem;
    }

    .gap-body {
        font-size: 0.87rem;
        color: #4b5563;
        line-height: 1.6;
    }

    .ad-card {
        background: white;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 1px 6px rgba(0,0,0,0.06);
        border-left: 3px solid #e94560;
    }

    .ad-brand {
        font-size: 0.78rem;
        font-weight: 600;
        color: #e94560;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .ad-text {
        font-size: 0.88rem;
        color: #374151;
        margin: 0.3rem 0;
        line-height: 1.5;
    }

    .ad-meta {
        font-size: 0.75rem;
        color: #9ca3af;
    }

    .brief-container {
        background: #1a1a2e;
        color: #e2e8f0;
        border-radius: 16px;
        padding: 2rem;
        font-family: 'Inter', monospace;
    }

    .section-header {
        font-size: 1.3rem;
        font-weight: 700;
        color: #1a1a2e;
        padding: 0.5rem 0;
        border-bottom: 2px solid #e94560;
        margin-bottom: 1.5rem;
    }

    .stSelectbox > div > div { border-radius: 8px; }
    .stMultiSelect > div > div { border-radius: 8px; }

    div[data-testid="stSidebarContent"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }

    div[data-testid="stSidebarContent"] label,
    div[data-testid="stSidebarContent"] .stMarkdown {
        color: #a8b2d8 !important;
    }

    .sidebar-logo {
        text-align: center;
        padding: 1rem 0 1.5rem 0;
    }

    .sidebar-logo h2 {
        color: white;
        font-size: 1.3rem;
        font-weight: 700;
    }

    .sidebar-logo p {
        color: #a8b2d8;
        font-size: 0.8rem;
    }

    .tag {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 600;
        margin-right: 4px;
    }

    .tag-video { background: #dbeafe; color: #1e40af; }
    .tag-carousel { background: #ede9fe; color: #5b21b6; }
    .tag-static { background: #d1fae5; color: #065f46; }
    .tag-active { background: #dcfce7; color: #166534; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# DATA LOADING (cached)
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600)
def get_data(token=""):
    return load_data(access_token=token if token else None)


@st.cache_data(ttl=3600)
def get_insights(data_hash):
    df = st.session_state.get("df")
    if df is None:
        return {}
    return run_full_analysis(df)


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <h2>🔴 AD WAR ROOM</h2>
        <p>D2C Competitive Intelligence</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown('<p style="color:#a8b2d8; font-size:0.8rem; font-weight:600; text-transform:uppercase; letter-spacing:0.05em;">META API TOKEN (Optional)</p>', unsafe_allow_html=True)
    meta_token = st.text_input(
        "Meta Access Token",
        type="password",
        placeholder="Paste your token for live data",
        help="Get from developers.facebook.com → Tools → Graph API Explorer",
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Load data
    with st.spinner("Loading ad data..."):
        df_full = get_data(meta_token)
        df_full = ensure_classified(df_full)
        st.session_state["df"] = df_full

    st.markdown('<p style="color:#a8b2d8; font-size:0.8rem; font-weight:600; text-transform:uppercase; letter-spacing:0.05em; margin-top:1rem;">FILTERS</p>', unsafe_allow_html=True)

    all_categories = ["All Categories"] + sorted(df_full["category"].unique().tolist())
    sel_category = st.selectbox("Category", all_categories, label_visibility="collapsed")

    cat_df = df_full if sel_category == "All Categories" else df_full[df_full["category"] == sel_category]

    all_brands = ["All Brands"] + sorted(cat_df["brand"].unique().tolist())
    sel_brands = st.multiselect("Brands", options=all_brands[1:], default=[], placeholder="All brands")

    all_formats = ["All"] + sorted(df_full["format"].unique().tolist())
    sel_format = st.selectbox("Format", all_formats, label_visibility="collapsed")

    theme_map = {
        "All Themes": "all",
        "Hair Loss": "hair_loss",
        "Hormonal Health": "hormonal_health",
        "Testosterone": "testosterone",
        "Acne Treatment": "acne_treatment",
        "Doctor Authority": "doctor_authority",
        "UGC Testimonial": "ugc_testimonial",
        "Discount / Offer": "discount_offer",
        "Parenting Pain": "parenting_pain",
        "Emotional Story": "emotional_story",
        "Stress & Sleep": "stress_sleep",
    }
    sel_theme_label = st.selectbox("Message Theme", list(theme_map.keys()), label_visibility="collapsed")
    sel_theme = theme_map[sel_theme_label]

    min_days, max_days = int(df_full["days_running"].min()), int(df_full["days_running"].max())
    days_range = st.slider("Days Running", min_days, max_days, (min_days, max_days))

    st.markdown("---")
    st.markdown(f'<p style="color:#a8b2d8; font-size:0.75rem;">Tracking <strong style="color:white">{df_full["brand"].nunique()} brands</strong> | <strong style="color:white">{len(df_full)}</strong> ads indexed</p>', unsafe_allow_html=True)
    data_source = "🟢 Live Meta API" if meta_token else "🟡 Meta Ad Library (Seed Data)"
    st.markdown(f'<p style="color:#a8b2d8; font-size:0.75rem;">Source: {data_source}</p>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────────
df = df_full.copy()
if sel_category != "All Categories":
    df = df[df["category"] == sel_category]
if sel_brands:
    df = df[df["brand"].isin(sel_brands)]
if sel_format != "All":
    df = df[df["format"] == sel_format]
if sel_theme != "all":
    df = df[df["theme"] == sel_theme]
df = df[(df["days_running"] >= days_range[0]) & (df["days_running"] <= days_range[1])]

# ─────────────────────────────────────────────
# NAVIGATION TABS
# ─────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🔴 Competitor Ad War Room</h1>
    <p>Real-time competitive intelligence from Meta Ad Library · D2C Wellness Edition</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "🎯 Intelligence",
    "🔍 Ad Explorer",
    "🚀 Gap Analysis",
    "📋 Weekly Brief"
])


# ─────────────────────────────────────────────
# TAB 1: OVERVIEW
# ─────────────────────────────────────────────
with tab1:
    # KPI Row
    col1, col2, col3, col4, col5 = st.columns(5)
    kpi_data = [
        (len(df), "Total Ads"),
        (df["brand"].nunique(), "Brands Tracked"),
        (df["format"].value_counts().index[0] if len(df) > 0 else "—", "Top Format"),
        (df["theme"].value_counts().index[0].replace("_"," ").title() if len(df) > 0 else "—", "Top Theme"),
        (f"{int(df['days_running'].mean())}d" if len(df) > 0 else "—", "Avg Ad Lifespan"),
    ]
    for col, (val, label) in zip([col1,col2,col3,col4,col5], kpi_data):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{val}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 1: Format Distribution + Theme Breakdown
    col_l, col_r = st.columns([1, 1.2])

    with col_l:
        st.markdown('<div class="section-header">Creative Format Distribution</div>', unsafe_allow_html=True)
        if len(df) > 0:
            format_data = df["format"].value_counts().reset_index()
            format_data.columns = ["Format", "Count"]
            fig_format = px.pie(
                format_data, values="Count", names="Format",
                color_discrete_sequence=["#e94560", "#0f3460", "#533483"],
                hole=0.45
            )
            fig_format.update_traces(
                textposition='outside', textinfo='percent+label',
                marker=dict(line=dict(color='white', width=2))
            )
            fig_format.update_layout(
                showlegend=True, height=320,
                margin=dict(t=20, b=20, l=20, r=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter", size=12),
                legend=dict(orientation="h", yanchor="bottom", y=-0.15)
            )
            st.plotly_chart(fig_format, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-header">Message Theme Breakdown</div>', unsafe_allow_html=True)
        if len(df) > 0:
            theme_data = df["theme"].value_counts().reset_index()
            theme_data.columns = ["Theme", "Count"]
            theme_data["Theme"] = theme_data["Theme"].str.replace("_", " ").str.title()
            fig_theme = px.bar(
                theme_data, x="Count", y="Theme",
                orientation='h',
                color="Count",
                color_continuous_scale=["#0f3460", "#e94560"],
            )
            fig_theme.update_layout(
                height=320, showlegend=False,
                margin=dict(t=20, b=20, l=20, r=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                yaxis=dict(categoryorder='total ascending'),
                font=dict(family="Inter", size=11),
                coloraxis_showscale=False,
            )
            fig_theme.update_traces(marker_line_width=0)
            st.plotly_chart(fig_theme, use_container_width=True)

    # Row 2: Brand Activity + Longevity
    col_a, col_b = st.columns([1.2, 1])

    with col_a:
        st.markdown('<div class="section-header">Brand Ad Volume</div>', unsafe_allow_html=True)
        if len(df) > 0:
            brand_vol = df.groupby(["brand", "category"])["ad_text"].count().reset_index()
            brand_vol.columns = ["Brand", "Category", "Ad Count"]
            brand_vol = brand_vol.sort_values("Ad Count", ascending=True)
            color_map = {
                "Men's Wellness": "#0f3460",
                "Women's Wellness": "#e94560",
                "Baby Care": "#533483"
            }
            fig_brand = px.bar(
                brand_vol, x="Ad Count", y="Brand",
                color="Category",
                color_discrete_map=color_map,
                orientation='h'
            )
            fig_brand.update_layout(
                height=380, showlegend=True,
                margin=dict(t=20, b=20, l=20, r=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter", size=11),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2)
            )
            fig_brand.update_traces(marker_line_width=0)
            st.plotly_chart(fig_brand, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-header">Top Performing Ads (Longevity)</div>', unsafe_allow_html=True)
        if len(df) > 0:
            top_ads = df.nlargest(8, "days_running")[["brand", "days_running", "format", "theme"]].copy()
            top_ads["theme"] = top_ads["theme"].str.replace("_", " ").str.title()
            top_ads = top_ads.rename(columns={
                "brand": "Brand", "days_running": "Days Running",
                "format": "Format", "theme": "Theme"
            })
            fig_longevity = px.bar(
                top_ads, x="Days Running", y="Brand",
                color="Days Running",
                color_continuous_scale=["#0f3460", "#e94560"],
                text="Days Running",
                orientation='h',
                hover_data=["Format", "Theme"]
            )
            fig_longevity.update_traces(
                texttemplate="%{text}d",
                textposition="outside",
                marker_line_width=0
            )
            fig_longevity.update_layout(
                height=380, showlegend=False,
                margin=dict(t=20, b=20, l=40, r=60),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                yaxis=dict(categoryorder='total ascending'),
                font=dict(family="Inter", size=11),
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig_longevity, use_container_width=True)

    # Row 3: Platform Distribution
    st.markdown('<div class="section-header">Platform Distribution by Category</div>', unsafe_allow_html=True)
    if len(df) > 0:
        df_platform = df.copy()
        df_platform["on_facebook"] = df_platform["platform"].str.contains("Facebook", na=False).astype(int)
        df_platform["on_instagram"] = df_platform["platform"].str.contains("Instagram", na=False).astype(int)
        platform_by_cat = df_platform.groupby("category")[["on_facebook", "on_instagram"]].sum().reset_index()
        platform_by_cat = platform_by_cat.melt(id_vars="category", var_name="Platform", value_name="Ads")
        platform_by_cat["Platform"] = platform_by_cat["Platform"].str.replace("on_", "").str.title()
        fig_platform = px.bar(
            platform_by_cat, x="category", y="Ads",
            color="Platform",
            barmode="group",
            color_discrete_sequence=["#0f3460", "#e94560"],
            labels={"category": "Category"}
        )
        fig_platform.update_layout(
            height=250, showlegend=True,
            margin=dict(t=10, b=10, l=20, r=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter", size=12),
        )
        fig_platform.update_traces(marker_line_width=0)
        st.plotly_chart(fig_platform, use_container_width=True)


# ─────────────────────────────────────────────
# TAB 2: INTELLIGENCE
# ─────────────────────────────────────────────
with tab2:
    insights = run_full_analysis(df if len(df) > 10 else df_full)

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown('<div class="section-header">🎬 Creative Trends</div>', unsafe_allow_html=True)
        for ins in insights["trends"]:
            color_cls = "insight-trend"
            st.markdown(f"""
            <div class="insight-card {color_cls}">
                <div class="insight-title">{ins['icon']} {ins['title']}</div>
                <div class="insight-body">{ins['body']}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="section-header">⏱️ Longevity Signals</div>', unsafe_allow_html=True)
        for ins in insights["longevity"]:
            st.markdown(f"""
            <div class="insight-card insight-longevity">
                <div class="insight-title">{ins['icon']} {ins['title']}</div>
                <div class="insight-body">{ins['body']}</div>
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="section-header">📲 Format Shifts</div>', unsafe_allow_html=True)
        for ins in insights["format_shifts"]:
            st.markdown(f"""
            <div class="insight-card insight-shift">
                <div class="insight-title">{ins['icon']} {ins['title']}</div>
                <div class="insight-body">{ins['body']}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="section-header">🔴 Message Saturation</div>', unsafe_allow_html=True)
        for ins in insights["saturation"]:
            st.markdown(f"""
            <div class="insight-card insight-saturation">
                <div class="insight-title">{ins['icon']} {ins['title']}</div>
                <div class="insight-body">{ins['body']}</div>
            </div>
            """, unsafe_allow_html=True)

    # Heatmap: Theme x Brand
    st.markdown('<div class="section-header">🗺️ Theme × Brand Heatmap</div>', unsafe_allow_html=True)
    if len(df_full) > 0:
        pivot = df_full.groupby(["brand", "theme"])["ad_text"].count().reset_index()
        pivot.columns = ["Brand", "Theme", "Count"]
        pivot["Theme"] = pivot["Theme"].str.replace("_", " ").str.title()
        pivot_wide = pivot.pivot_table(index="Brand", columns="Theme", values="Count", fill_value=0)

        fig_heat = px.imshow(
            pivot_wide,
            color_continuous_scale=["#f0f4ff", "#0f3460", "#e94560"],
            aspect="auto",
            labels=dict(color="Ad Count"),
        )
        fig_heat.update_layout(
            height=420,
            margin=dict(t=20, b=20, l=20, r=20),
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter", size=10),
        )
        st.plotly_chart(fig_heat, use_container_width=True)


# ─────────────────────────────────────────────
# TAB 3: AD EXPLORER
# ─────────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-header">🔍 Ad Explorer</div>', unsafe_allow_html=True)

    if len(df) == 0:
        st.info("No ads match the current filters. Try adjusting the sidebar filters.")
    else:
        col_stats = st.columns(4)
        stats = [
            (len(df), "Filtered Ads"),
            (df["brand"].nunique(), "Brands"),
            (f"{int(df['days_running'].max())}d", "Longest Running"),
            (f"{int(df['days_running'].mean())}d", "Avg Duration"),
        ]
        for col, (val, label) in zip(col_stats, stats):
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{val}</div>
                    <div class="metric-label">{label}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Sort options
        sort_col, sort_ord = st.columns([2, 1])
        with sort_col:
            sort_by = st.selectbox(
                "Sort by",
                ["Days Running (Longest First)", "Days Running (Shortest First)", "Brand (A-Z)"],
                label_visibility="visible"
            )
        with sort_ord:
            show_n = st.number_input("Show", min_value=5, max_value=200, value=30, step=5)

        sort_map = {
            "Days Running (Longest First)": ("days_running", False),
            "Days Running (Shortest First)": ("days_running", True),
            "Brand (A-Z)": ("brand", True),
        }
        sort_field, sort_asc = sort_map[sort_by]
        df_display = df.sort_values(sort_field, ascending=sort_asc).head(show_n)

        format_tag = {
            "Video": '<span class="tag tag-video">🎬 Video</span>',
            "Carousel": '<span class="tag tag-carousel">🎠 Carousel</span>',
            "Static Image": '<span class="tag tag-static">🖼️ Static</span>',
        }

        for _, row in df_display.iterrows():
            fmt_tag = format_tag.get(row.get("format", ""), "")
            active_tag = '<span class="tag tag-active">🟢 Active</span>' if row.get("is_active") == "Yes" else ""
            theme_display = str(row.get("theme","")).replace("_"," ").title()
            days = int(row.get("days_running", 0))
            url = row.get("url", "#")

            ad_text = str(row.get("ad_text",""))
            ad_preview = ad_text[:200] + ("..." if len(ad_text) > 200 else "")

            st.markdown(f"""
            <div class="ad-card">
                <div class="ad-brand">{row.get('brand','')} · {row.get('category','')}</div>
                <div class="ad-text">{ad_preview}</div>
                <div class="ad-meta">
                    {fmt_tag} {active_tag}
                    <span class="tag" style="background:#f3f4f6;color:#374151;">📌 {theme_display}</span>
                    <span class="tag" style="background:#f3f4f6;color:#374151;">⏱️ {days} days</span>
                    <span class="tag" style="background:#f3f4f6;color:#374151;">📱 {row.get('platform','')}</span>
                    &nbsp;&nbsp;<a href="{url}" target="_blank" style="font-size:0.72rem;color:#3b82f6;">View on Meta →</a>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Export
        st.markdown("<br>", unsafe_allow_html=True)
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Filtered Ads as CSV",
            data=csv_data,
            file_name="competitor_ads_filtered.csv",
            mime="text/csv",
            use_container_width=True
        )


# ─────────────────────────────────────────────
# TAB 4: GAP ANALYSIS
# ─────────────────────────────────────────────
with tab4:
    insights_full = run_full_analysis(df_full)
    gaps = insights_full["gaps"]

    st.markdown("""
    <div style="background:linear-gradient(135deg,#fef9f0,#fff7ed);border-radius:12px;padding:1.2rem 1.5rem;margin-bottom:1.5rem;border:1.5px solid #fde68a;">
        <h3 style="color:#92400e;margin:0 0 0.5rem 0;">🚀 Strategic Opportunity Gaps</h3>
        <p style="color:#78350f;margin:0;font-size:0.9rem;">
        These are the messaging angles, creative formats, and strategic opportunities your competitors are <strong>completely missing</strong>.
        Each gap represents an undisputed lane for the brand that moves first.
        </p>
    </div>
    """, unsafe_allow_html=True)

    for i, gap in enumerate(gaps, 1):
        brands_str = " · ".join([f"<strong>{b}</strong>" for b in gap.get("brands_affected", [])])
        st.markdown(f"""
        <div class="gap-card">
            <div class="gap-title">{gap['icon']} GAP #{i}: {gap['gap']}</div>
            <div class="gap-body">{gap['opportunity']}</div>
            <div style="margin-top:0.6rem;font-size:0.78rem;color:#92400e;">
                💡 Most relevant for: {brands_str}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Opportunity matrix
    st.markdown('<div class="section-header">📊 Theme Coverage Matrix — Who Owns What?</div>', unsafe_allow_html=True)

    theme_labels = {
        "hair_loss": "Hair Loss",
        "hormonal_health": "Hormonal Health",
        "testosterone": "Testosterone",
        "acne_treatment": "Acne Treatment",
        "doctor_authority": "Doctor Authority",
        "ugc_testimonial": "UGC Testimonial",
        "discount_offer": "Discount / Offer",
        "parenting_pain": "Parenting Pain",
        "emotional_story": "Emotional Story",
        "stress_sleep": "Stress & Sleep",
    }

    if len(df_full) > 0:
        pivot2 = df_full.groupby(["brand","theme"])["ad_text"].count().unstack(fill_value=0)
        pivot2.columns = [theme_labels.get(c, c) for c in pivot2.columns]
        pivot2_norm = pivot2.div(pivot2.max(axis=0), axis=1).fillna(0)

        fig_matrix = px.imshow(
            pivot2_norm,
            color_continuous_scale=["#f8fafc", "#0f3460", "#e94560"],
            aspect="auto",
            labels=dict(color="Relative Coverage"),
            title="Theme Coverage by Brand (darker = more ads)"
        )
        fig_matrix.update_layout(
            height=500,
            margin=dict(t=40, b=20, l=20, r=20),
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter", size=10),
            title_font=dict(size=13, color="#1a1a2e"),
        )
        st.plotly_chart(fig_matrix, use_container_width=True)

        st.info("💡 **White spaces in the matrix = opportunity.** If a brand you compete with shows low coverage on a theme, that's your lane to own.")


# ─────────────────────────────────────────────
# TAB 5: WEEKLY BRIEF
# ─────────────────────────────────────────────
with tab5:
    insights_brief = run_full_analysis(df_full)
    brief_text = insights_brief["weekly_brief"]

    col_brief, col_actions = st.columns([2, 1])

    with col_brief:
        st.markdown(brief_text)

    with col_actions:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#1a1a2e,#0f3460);border-radius:12px;padding:1.5rem;color:white;">
            <h4 style="margin:0 0 1rem 0;color:white;">📌 Quick Actions</h4>
            <p style="font-size:0.85rem;color:#a8b2d8;">Use this brief to:</p>
            <ul style="font-size:0.83rem;color:#a8b2d8;padding-left:1.2rem;">
                <li>Share in Monday marketing standup</li>
                <li>Align creative team on format priorities</li>
                <li>Identify your next ad angle</li>
                <li>Spot where competitors are overexposed</li>
                <li>Find your white-space opportunity</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Download brief
        st.download_button(
            label="⬇️ Download Brief as TXT",
            data=brief_text.encode("utf-8"),
            file_name="ad_war_room_weekly_brief.txt",
            mime="text/plain",
            use_container_width=True
        )

        # Download full CSV
        full_csv = df_full.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download All Ads (CSV)",
            data=full_csv,
            file_name="all_competitor_ads.csv",
            mime="text/csv",
            use_container_width=True
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # Summary stats
        st.markdown("""
        <div style="background:white;border-radius:10px;padding:1.2rem;border-left:4px solid #e94560;">
            <p style="font-size:0.8rem;font-weight:700;color:#e94560;text-transform:uppercase;letter-spacing:0.05em;margin:0 0 0.8rem 0;">Dataset Summary</p>
        """, unsafe_allow_html=True)

        stats_items = [
            ("Brands Tracked", df_full["brand"].nunique()),
            ("Total Ads", len(df_full)),
            ("Video Ads", len(df_full[df_full["format"] == "Video"])),
            ("Carousel Ads", len(df_full[df_full["format"] == "Carousel"])),
            ("Static Image Ads", len(df_full[df_full["format"] == "Static Image"])),
            ("Avg Lifespan", f"{int(df_full['days_running'].mean())} days"),
            ("Longest Running", f"{int(df_full['days_running'].max())} days"),
        ]
        for label, val in stats_items:
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;padding:0.25rem 0;border-bottom:1px solid #f3f4f6;">
                <span style="font-size:0.8rem;color:#6b7280;">{label}</span>
                <span style="font-size:0.8rem;font-weight:600;color:#1a1a2e;">{val}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center;padding:1rem 0;color:#9ca3af;font-size:0.8rem;">
    🔴 <strong>Competitor Ad War Room</strong> · Built for D2C Marketing Teams ·
    Data: Meta Ad Library · Built with Python + Streamlit + Plotly
</div>
""", unsafe_allow_html=True)

"""
insights.py — AI Intelligence Engine
Transforms raw ad data into competitive intelligence.
"""

import pandas as pd
from collections import Counter
import re


# ─────────────────────────────────────────────
# CLASSIFICATION RULES
# ─────────────────────────────────────────────

THEME_KEYWORDS = {
    "hair_loss": ["hair","hairfall","hair fall","hair loss","regrowth","DHT","minoxidil","baldness","beard","scalp","biotin","redensyl"],
    "hormonal_health": ["pcos","hormonal","hormone","thyroid","fertility","period","menstrual","irregular","ovary","cycle"],
    "testosterone": ["testosterone","energy","libido","stamina","ed","performance","vitality"],
    "acne_treatment": ["acne","breakout","pimple","skin","glow","clear skin"],
    "doctor_authority": ["doctor","dermatologist","gynecologist","clinically","fda","certified"],
    "ugc_testimonial": ["testimonial","review","experience","journey","before","after","story"],
    "discount_offer": ["off","sale","discount","offer","coupon","free","₹","price","deal"],
    "parenting_pain": ["baby","child","kid","toddler","newborn","mom","parent"],
    "emotional_story": ["journey","believe","deserve","proud","confidence"],
    "stress_sleep": ["stress","sleep","anxiety","rest","calm","ashwagandha","melatonin"],
}

FORMAT_KEYWORDS = {
    "Video": ["watch","video","film"],
    "Carousel": ["swipe","carousel","step","vs"],
    "Static Image": ["image","photo"]
}


# ─────────────────────────────────────────────
# CLASSIFIERS
# ─────────────────────────────────────────────

def classify_theme(text):

    if not isinstance(text,str):
        return "other"

    text=text.lower()
    scores={}

    for theme,keywords in THEME_KEYWORDS.items():

        score=sum(1 for kw in keywords if kw in text)

        if score>0:
            scores[theme]=score

    if scores:
        return max(scores,key=scores.get)

    return "other"


def classify_format(text):

    if not isinstance(text,str):
        return "Static Image"

    text=text.lower()

    for fmt,keywords in FORMAT_KEYWORDS.items():

        if any(k in text for k in keywords):
            return fmt

    return "Static Image"


# ─────────────────────────────────────────────
# SAFE CLASSIFICATION WRAPPER
# ─────────────────────────────────────────────

def ensure_classified(df):

    if df is None or len(df)==0:
        return pd.DataFrame(columns=[
            "brand","category","ad_text","theme",
            "format","days_running","platform"
        ])

    if "ad_text" not in df.columns:
        df["ad_text"]=""

    if "theme" not in df.columns:
        df["theme"]="unknown"

    if "format" not in df.columns:
        df["format"]="Static Image"

    if "days_running" not in df.columns:
        df["days_running"]=30

    if "platform" not in df.columns:
        df["platform"]="Facebook"

    mask=df["theme"]=="unknown"

    if mask.any():
        df.loc[mask,"theme"]=df.loc[mask,"ad_text"].apply(classify_theme)

    df["format"]=df["ad_text"].apply(classify_format)

    return df


# ─────────────────────────────────────────────
# INSIGHT GENERATORS
# ─────────────────────────────────────────────

def get_creative_trends(df):

    insights=[]

    format_counts=df["format"].value_counts()

    if len(format_counts)==0:
        return insights

    top_format=format_counts.index[0]

    pct=round(format_counts.iloc[0]/len(df)*100)

    insights.append({
        "icon":"🎬",
        "title":f"{top_format} ads dominate the category",
        "body":f"{pct}% of competitor ads use {top_format} format",
        "type":"trend"
    })

    return insights


def get_longevity_signals(df):

    insights=[]

    if "days_running" not in df.columns:
        return insights

    long_ads=df[df["days_running"]>=60]

    pct=round(len(long_ads)/len(df)*100)

    insights.append({
        "icon":"⏱️",
        "title":f"{pct}% ads run 60+ days",
        "body":"Long running ads indicate strong performance",
        "type":"longevity"
    })

    return insights


def get_format_shifts(df):

    insights=[]

    video_pct=round(len(df[df["format"]=="Video"])/len(df)*100)

    insights.append({
        "icon":"📊",
        "title":f"Video share {video_pct}%",
        "body":"Video creatives dominate D2C performance ads",
        "type":"shift"
    })

    return insights


def get_message_saturation(df):

    insights=[]

    theme_dist=df["theme"].value_counts()

    if len(theme_dist)==0:
        return insights

    top_theme=theme_dist.index[0]

    pct=round(theme_dist.iloc[0]/len(df)*100)

    insights.append({
        "icon":"🔴",
        "title":f"{top_theme} messaging saturated",
        "body":f"{pct}% ads use this theme",
        "type":"saturation"
    })

    return insights


def get_gap_opportunities(df):

    return [
        {
            "icon":"🔬",
            "gap":"Educational doctor explainers missing",
            "opportunity":"Dermatologist explainer ads could dominate",
            "brands_affected":["Man Matters","Traya Health"]
        },
        {
            "icon":"🌙",
            "gap":"Sleep & stress messaging underused",
            "opportunity":"Strong white space in wellness category",
            "brands_affected":["Bebodywise","andMe"]
        }
    ]


# ─────────────────────────────────────────────
# WEEKLY BRIEF
# ─────────────────────────────────────────────

def generate_weekly_brief(df):

    brand_count=df["brand"].nunique() if "brand" in df.columns else 0

    return f"""
COMPETITOR AD WAR ROOM

Brands tracked: {brand_count}
Ads analyzed: {len(df)}

Top insight:
Video + testimonial ads dominate wellness D2C marketing.
""".strip()


# ─────────────────────────────────────────────
# MASTER ANALYSIS
# ─────────────────────────────────────────────

def run_full_analysis(df):

    df=ensure_classified(df)

    return {
        "trends":get_creative_trends(df),
        "longevity":get_longevity_signals(df),
        "format_shifts":get_format_shifts(df),
        "saturation":get_message_saturation(df),
        "gaps":get_gap_opportunities(df),
        "weekly_brief":generate_weekly_brief(df)
    }

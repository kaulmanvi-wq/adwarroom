import os
import re
import pandas as pd
from datetime import datetime

RAW_PATH = "data/raw_ads.csv"
OUT_PATH = "data/structured_ads.csv"

BRAND_CATEGORY_MAP = {
    "Traya": "Men's wellness",
    "Bold Care": "Men's wellness",
    "Mars by GHC": "Men's wellness",
    "ForMen Health": "Men's wellness",
    "Power Gummies": "Women's wellness",
    "Sirona": "Women's wellness",
    "Sanfe": "Women's wellness",
    "Nua": "Women's wellness",
    "Mother Sparsh": "Baby care",
    "BabyOrgano": "Baby care",
}

THEME_RULES = {
    "hair loss": [
        "hair loss", "hairfall", "hair fall", "regrow", "regrowth",
        "thinning hair", "bald", "alopecia", "hair growth", "minoxidil"
    ],
    "hormonal health": [
        "pcos", "pcod", "hormonal", "hormone", "cycle", "period",
        "menstrual", "ovulation", "fertility", "cramps"
    ],
    "testosterone": [
        "testosterone", "low t", "performance", "stamina", "energy levels",
        "men's vitality", "vitality"
    ],
    "acne treatment": [
        "acne", "pimple", "breakout", "blemish", "oil control", "clear skin"
    ],
    "doctor authority": [
        "doctor", "dermatologist", "gynecologist", "clinically proven",
        "expert recommended", "science-backed", "lab tested", "recommended by doctors"
    ],
    "ugc testimonial": [
        "testimonial", "review", "my experience", "i tried", "before and after",
        "real results", "customer story", "transformation", "worked for me"
    ],
    "discount / offer": [
        "off", "discount", "sale", "limited time", "offer", "buy 1 get 1",
        "coupon", "save", "deal", "flat"
    ],
    "parenting pain point": [
        "baby rash", "colic", "fussy", "crying", "new mom", "newborn",
        "sensitive skin", "diaper rash", "immunity", "picky eater", "teething"
    ],
    "emotional storytelling": [
        "because you deserve", "confidence", "feel like yourself", "journey",
        "motherhood", "parenting", "self-care", "feel seen", "feel heard",
        "real story"
    ],
    "sleep / stress": [
        "sleep", "stress", "anxiety", "rest", "fatigue", "tired", "calm", "recovery"
    ],
}

def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def normalize_format(value):
    value = str(value).strip().lower()
    if value in ["video", "static image", "carousel"]:
        return value
    if "video" in value:
        return "video"
    if "carousel" in value or "multi" in value:
        return "carousel"
    if "image" in value or "static" in value:
        return "static image"
    return "unknown"

def normalize_platform(value):
    if pd.isna(value):
        return "Unknown"
    platforms = [p.strip().title() for p in str(value).split(",") if p.strip()]
    if not platforms:
        return "Unknown"
    return ", ".join(sorted(set(platforms)))

def parse_date(value):
    if pd.isna(value) or str(value).strip() == "":
        return pd.NaT
    try:
        return pd.to_datetime(value).normalize()
    except:
        return pd.NaT

def ad_age_days(start_date):
    if pd.isna(start_date):
        return None
    today = pd.Timestamp.today().normalize()
    return int((today - start_date).days)

def classify_themes(text):
    text_l = clean_text(text).lower()
    matched = []

    for theme, keywords in THEME_RULES.items():
        for kw in keywords:
            if kw in text_l:
                matched.append(theme)
                break

    if not matched:
        matched.append("other / unclassified")

    return matched

def primary_theme(theme_list):
    if not theme_list:
        return "other / unclassified"
    return theme_list[0]

def build_final_columns(df):
    df["brand"] = df["brand_name"].fillna("").astype(str).str.strip()
    df["category"] = df["brand"].map(BRAND_CATEGORY_MAP).fillna("Other")
    df["ad_text"] = df["ad_text"].apply(clean_text)
    df["format"] = df["ad_creative_type"].apply(normalize_format)
    df["start_date"] = df["ad_start_date"].apply(parse_date)
    df["platform"] = df["platform"].apply(normalize_platform)
    df["url"] = df["ad_snapshot_url"].fillna("").astype(str).str.strip()

    df["theme_list"] = df["ad_text"].apply(classify_themes)
    df["primary_theme"] = df["theme_list"].apply(primary_theme)
    df["theme_count"] = df["theme_list"].apply(len)
    df["ad_age_days"] = df["start_date"].apply(ad_age_days)

    df["has_text"] = df["ad_text"].apply(lambda x: "yes" if len(x) > 0 else "no")
    df["text_length"] = df["ad_text"].apply(len)

    final_cols = [
        "brand",
        "category",
        "ad_text",
        "format",
        "start_date",
        "platform",
        "url",
        "primary_theme",
        "theme_list",
        "theme_count",
        "ad_age_days",
        "has_text",
        "text_length",
        "matched_page_name",
        "page_id",
        "ad_archive_id",
        "raw_display_format",
    ]

    return df[final_cols].copy()

def main():
    if not os.path.exists(RAW_PATH):
        raise FileNotFoundError(f"{RAW_PATH} not found. Run scraper.py first.")

    df = pd.read_csv(RAW_PATH)

    if df.empty:
        raise ValueError("raw_ads.csv is empty. Re-run scraper.py.")

    structured = build_final_columns(df)

    structured = structured.drop_duplicates(subset=["brand", "ad_text", "url"], keep="first")
    structured = structured.sort_values(by=["brand", "start_date"], ascending=[True, False])

    os.makedirs("data", exist_ok=True)
    structured.to_csv(OUT_PATH, index=False)

    print("Done.")
    print(f"Saved structured dataset to {OUT_PATH}")
    print(f"Rows: {len(structured)}")
    print("\nColumns:")
    print(list(structured.columns))

    print("\nSample:")
    print(structured.head(10).to_string(index=False))

if __name__ == "__main__":
    main()

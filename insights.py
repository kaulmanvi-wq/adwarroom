import os
import ast
import json
import math
import pandas as pd
from datetime import timedelta

INPUT_PATH = "data/structured_ads.csv"
OUTPUT_JSON = "data/insights_summary.json"
OUTPUT_TOP_ADS = "data/top_ads.csv"
OUTPUT_BRIEF = "data/weekly_brief.txt"

EXPECTED_THEMES_BY_CATEGORY = {
    "Men's wellness": [
        "hair loss", "testosterone", "doctor authority",
        "ugc testimonial", "discount / offer", "sleep / stress"
    ],
    "Women's wellness": [
        "hormonal health", "acne treatment", "doctor authority",
        "ugc testimonial", "discount / offer", "emotional storytelling"
    ],
    "Baby care": [
        "parenting pain point", "doctor authority", "ugc testimonial",
        "discount / offer", "emotional storytelling"
    ]
}

FORMAT_SCORE = {
    "video": 20,
    "carousel": 14,
    "static image": 10,
    "unknown": 8
}

def pct(part, whole):
    if whole == 0:
        return 0.0
    return round((part / whole) * 100, 1)

def safe_int(x, default=0):
    try:
        if pd.isna(x):
            return default
        return int(x)
    except:
        return default

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
            return parsed
    except:
        pass
    return [text]

def load_data():
    if not os.path.exists(INPUT_PATH):
        raise FileNotFoundError(f"{INPUT_PATH} not found. Run processor.py first.")

    df = pd.read_csv(INPUT_PATH)
    if df.empty:
        raise ValueError("structured_ads.csv is empty.")

    df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")
    df["ad_age_days"] = pd.to_numeric(df["ad_age_days"], errors="coerce").fillna(0).astype(int)
    df["text_length"] = pd.to_numeric(df["text_length"], errors="coerce").fillna(0).astype(int)
    df["theme_count"] = pd.to_numeric(df["theme_count"], errors="coerce").fillna(0).astype(int)
    df["theme_list"] = df["theme_list"].apply(parse_theme_list)
    df["primary_theme"] = df["primary_theme"].fillna("other / unclassified").astype(str)
    df["format"] = df["format"].fillna("unknown").astype(str).str.lower()
    df["category"] = df["category"].fillna("Other").astype(str)
    df["brand"] = df["brand"].fillna("Unknown").astype(str)
    df["ad_text"] = df["ad_text"].fillna("").astype(str)
    df["platform"] = df["platform"].fillna("Unknown").astype(str)
    df["url"] = df["url"].fillna("").astype(str)

    return df

def explode_themes(df):
    temp = df.copy()
    temp = temp.explode("theme_list")
    temp["theme_list"] = temp["theme_list"].fillna("other / unclassified").astype(str)
    temp = temp.rename(columns={"theme_list": "theme"})
    return temp

def score_ads(df):
    def score_row(row):
        score = 0

        # longevity proxy: longer-running active ads are more likely to be retained for performance
        age_days = safe_int(row["ad_age_days"])
        score += min(age_days, 120) / 120 * 45

        # format weight
        score += FORMAT_SCORE.get(str(row["format"]).lower(), 8)

        # multiple themes often indicate richer messaging
        score += min(safe_int(row["theme_count"]) * 3, 12)

        text = str(row["ad_text"]).lower()
        text_len = len(text)

        if 50 <= text_len <= 280:
            score += 8
        elif text_len > 0:
            score += 4

        bonus_keywords = {
            "ugc testimonial": ["testimonial", "review", "before and after", "worked for me", "real results"],
            "doctor authority": ["doctor", "dermatologist", "gynecologist", "science-backed", "clinically proven"],
            "discount / offer": ["off", "discount", "sale", "offer", "save", "deal"],
            "emotional storytelling": ["journey", "confidence", "motherhood", "self-care", "real story"],
        }

        for _, kws in bonus_keywords.items():
            if any(kw in text for kw in kws):
                score += 4

        return round(min(score, 100), 1)

    scored = df.copy()
    scored["performance_proxy_score"] = scored.apply(score_row, axis=1)
    scored["performance_bucket"] = pd.cut(
        scored["performance_proxy_score"],
        bins=[-1, 35, 60, 80, 100],
        labels=["low", "medium", "high", "very high"]
    )

    return scored.sort_values(["performance_proxy_score", "ad_age_days"], ascending=[False, False])

def creative_trends(df, themes_df):
    insights = []
    total_ads = len(df)

    if total_ads == 0:
        return ["No ads available to analyze creative trends."]

    format_counts = df["format"].value_counts()
    top_format = format_counts.index[0]
    top_format_share = pct(format_counts.iloc[0], total_ads)

    insights.append(
        f"{top_format.title()} is the leading creative format, used in {top_format_share}% of tracked active ads ({format_counts.iloc[0]} of {total_ads})."
    )

    category_group = (
        df.groupby(["category", "format"])
          .size()
          .reset_index(name="ads")
    )

    for category in df["category"].dropna().unique():
        sub = category_group[category_group["category"] == category].sort_values("ads", ascending=False)
        if not sub.empty:
            lead = sub.iloc[0]
            cat_total = sub["ads"].sum()
            insights.append(
                f"In {category}, {lead['format']} leads with {pct(lead['ads'], cat_total)}% share ({lead['ads']} ads)."
            )

    # theme-format combo
    theme_format = (
        themes_df.groupby(["theme", "format"])
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    if not theme_format.empty:
        row = theme_format.iloc[0]
        insights.append(
            f"The most common message-format combo is '{row['theme']}' in {row['format']} ads ({row['count']} occurrences)."
        )

    return insights[:5]

def longevity_signals(df, themes_df):
    insights = []
    total_ads = len(df)

    if total_ads == 0:
        return ["No ads available to analyze longevity."]

    long_30 = df[df["ad_age_days"] >= 30]
    long_60 = df[df["ad_age_days"] >= 60]
    long_90 = df[df["ad_age_days"] >= 90]

    insights.append(
        f"{pct(len(long_30), total_ads)}% of tracked ads have been live for at least 30 days; {pct(len(long_60), total_ads)}% have been live for 60+ days."
    )

    if len(long_60) > 0:
        top_formats = long_60["format"].value_counts()
        top_fmt = top_formats.index[0]
        insights.append(
            f"Among 60+ day ads, {top_fmt} leads with {pct(top_formats.iloc[0], len(long_60))}% share, making it the strongest format-retention signal."
        )

        long_60_themes = themes_df[themes_df["url"].isin(long_60["url"])]
        if not long_60_themes.empty:
            top_theme_counts = long_60_themes["theme"].value_counts()
            top_theme = top_theme_counts.index[0]
            insights.append(
                f"The most persistent message among 60+ day ads is '{top_theme}' ({top_theme_counts.iloc[0]} occurrences)."
            )

    if len(long_90) > 0:
        brand_avg = long_90.groupby("brand")["ad_age_days"].mean().sort_values(ascending=False)
        top_brand = brand_avg.index[0]
        insights.append(
            f"{top_brand} has the oldest surviving creative set, with 90+ day ads averaging {round(brand_avg.iloc[0], 1)} days live."
        )

    return insights[:5]

def format_shifts(df):
    insights = []
    if df["start_date"].notna().sum() < 6:
        return ["Not enough valid start dates to estimate recent format shifts."]

    latest_date = df["start_date"].max()
    if pd.isna(latest_date):
        return ["Not enough valid start dates to estimate recent format shifts."]

    recent_cutoff = latest_date - timedelta(days=21)
    recent = df[df["start_date"] >= recent_cutoff]
    older = df[df["start_date"] < recent_cutoff]

    if len(recent) < 3 or len(older) < 3:
        return ["Not enough recent-vs-older ad split to estimate format shifts reliably."]

    recent_share = recent["format"].value_counts(normalize=True)
    older_share = older["format"].value_counts(normalize=True)

    all_formats = sorted(set(recent_share.index).union(set(older_share.index)))

    deltas = []
    for fmt in all_formats:
        r = recent_share.get(fmt, 0)
        o = older_share.get(fmt, 0)
        delta_pp = round((r - o) * 100, 1)
        deltas.append((fmt, delta_pp, r, o))

    deltas_sorted = sorted(deltas, key=lambda x: abs(x[1]), reverse=True)

    for fmt, delta_pp, r, o in deltas_sorted[:3]:
        if abs(delta_pp) < 8:
            continue
        direction = "up" if delta_pp > 0 else "down"
        insights.append(
            f"{fmt.title()} usage is {direction} {abs(delta_pp)} percentage points in newer ads (≤21 days) versus older surviving ads."
        )

    if not insights:
        insights.append("Format mix is relatively stable; no major recent shift crossed an 8-point threshold.")

    return insights

def message_saturation(themes_df):
    insights = []
    if themes_df.empty:
        return ["No theme data available for saturation analysis."]

    total_theme_rows = len(themes_df)
    overall_counts = themes_df["theme"].value_counts()

    top_themes = overall_counts.head(3)
    for theme, count in top_themes.items():
        insights.append(
            f"'{theme}' is saturated, appearing in {pct(count, total_theme_rows)}% of classified theme mentions ({count} occurrences)."
        )

    # category-specific saturation
    category_theme = (
        themes_df.groupby(["category", "theme"])
        .size()
        .reset_index(name="count")
    )

    for category in themes_df["category"].dropna().unique():
        sub = category_theme[category_theme["category"] == category].sort_values("count", ascending=False)
        if not sub.empty:
            lead = sub.iloc[0]
            cat_total = sub["count"].sum()
            insights.append(
                f"In {category}, the most repeated message is '{lead['theme']}' at {pct(lead['count'], cat_total)}% share."
            )

    return insights[:6]

def gap_detection(df, themes_df):
    gaps = []

    # underused formats overall
    format_counts = df["format"].value_counts()
    total_ads = len(df)
    for fmt in ["video", "carousel", "static image"]:
        share = pct(format_counts.get(fmt, 0), total_ads)
        if share > 0 and share < 15:
            gaps.append(f"{fmt.title()} is underused at just {share}% of tracked ads.")

    # category theme gaps
    for category, expected_themes in EXPECTED_THEMES_BY_CATEGORY.items():
        cat = themes_df[themes_df["category"] == category]
        if cat.empty:
            continue

        counts = cat["theme"].value_counts()
        cat_total = len(cat)

        for theme in expected_themes:
            share = pct(counts.get(theme, 0), cat_total)
            if counts.get(theme, 0) == 0:
                gaps.append(f"No tracked {category} ads use the theme '{theme}'.")
            elif share < 6:
                gaps.append(f"'{theme}' is weakly represented in {category} at only {share}% share.")

    # theme + format whitespace
    doctor_video = themes_df[
        (themes_df["theme"] == "doctor authority") &
        (themes_df["format"] == "video")
    ]
    if doctor_video.empty:
        gaps.append("None of the tracked ads combine doctor-authority messaging with video, leaving expert-led video explainers open.")

    story_carousel = themes_df[
        (themes_df["theme"] == "emotional storytelling") &
        (themes_df["format"] == "carousel")
    ]
    if story_carousel.empty:
        gaps.append("No brand is using emotional storytelling in carousel format, which could work for sequential before/after or journey narratives.")

    return gaps[:8]

def strategic_insights(df, themes_df, scored_df):
    insights = []

    # likely top performers
    top_ads = scored_df.head(10)
    if not top_ads.empty:
        top_fmt = top_ads["format"].value_counts().idxmax()
        top_theme = top_ads["primary_theme"].value_counts().idxmax()
        avg_age = round(top_ads["ad_age_days"].mean(), 1)
        insights.append(
            f"Likely winning ads skew toward {top_fmt} and mostly lead with '{top_theme}', with the top 10 ads averaging {avg_age} live days."
        )

    # category whitespace vs saturation
    all_theme_counts = themes_df["theme"].value_counts()
    if "sleep / stress" not in all_theme_counts.index or all_theme_counts.get("sleep / stress", 0) <= 1:
        insights.append(
            "Sleep / stress is largely missing from the competitive set, even though adjacent wellness brands often overload hair-loss and hormonal messaging."
        )

    # cross-brand concentration
    brand_theme = (
        themes_df.groupby(["brand", "theme"])
        .size()
        .reset_index(name="count")
        .sort_values(["brand", "count"], ascending=[True, False])
    )
    dominant_brands = []
    for brand in df["brand"].unique():
        sub = brand_theme[brand_theme["brand"] == brand]
        if not sub.empty:
            dominant_brands.append((brand, sub.iloc[0]["theme"], int(sub.iloc[0]["count"])))

    if dominant_brands:
        brand, theme, count = sorted(dominant_brands, key=lambda x: x[2], reverse=True)[0]
        insights.append(
            f"{brand} appears most concentrated around a single message pillar: '{theme}' ({count} classified occurrences), which suggests repetition risk."
        )

    return insights[:5]

def build_weekly_brief(creative, longevity, shifts, saturation, strategy, gaps):
    lines = []
    lines.append("Competitor Ad War Room — Weekly Brief")
    lines.append("")

    lines.append("3 Creative Trends")
    for i, item in enumerate((creative + shifts)[:3], start=1):
        lines.append(f"{i}. {item}")
    lines.append("")

    lines.append("2 Winning Formats")
    wins = longevity[:2] if len(longevity) >= 2 else longevity
    for i, item in enumerate(wins[:2], start=1):
        lines.append(f"{i}. {item}")
    lines.append("")

    lines.append("2 Strategic Insights")
    for i, item in enumerate(strategy[:2], start=1):
        lines.append(f"{i}. {item}")
    lines.append("")

    lines.append("2 Opportunity Gaps")
    for i, item in enumerate(gaps[:2], start=1):
        lines.append(f"{i}. {item}")

    return "\n".join(lines)

def make_json_serializable(value):
    if isinstance(value, pd.Timestamp):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, (list, dict, str, int, float, bool)) or value is None:
        return value
    return str(value)

def main():
    df = load_data()
    themes_df = explode_themes(df)
    scored_df = score_ads(df)

    creative = creative_trends(df, themes_df)
    longevity = longevity_signals(df, themes_df)
    shifts = format_shifts(df)
    saturation = message_saturation(themes_df)
    gaps = gap_detection(df, themes_df)
    strategy = strategic_insights(df, themes_df, scored_df)

    top_ads = scored_df[[
        "brand", "category", "format", "primary_theme",
        "ad_age_days", "performance_proxy_score", "platform", "url", "ad_text"
    ]].head(25).copy()

    overview = {
        "total_ads": int(len(df)),
        "brands_tracked": int(df["brand"].nunique()),
        "categories_tracked": int(df["category"].nunique()),
        "avg_ad_age_days": round(float(df["ad_age_days"].mean()), 1) if len(df) else 0,
        "top_format": df["format"].value_counts().idxmax() if len(df) else "N/A",
        "top_theme": themes_df["theme"].value_counts().idxmax() if len(themes_df) else "N/A",
    }

    brief = build_weekly_brief(creative, longevity, shifts, saturation, strategy, gaps)

    insights_payload = {
        "overview": {k: make_json_serializable(v) for k, v in overview.items()},
        "creative_trends": creative,
        "longevity_signals": longevity,
        "format_shifts": shifts,
        "message_saturation": saturation,
        "strategic_insights": strategy,
        "gap_detection": gaps,
        "weekly_brief": brief
    }

    os.makedirs("data", exist_ok=True)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(insights_payload, f, indent=2, ensure_ascii=False)

    top_ads.to_csv(OUTPUT_TOP_ADS, index=False)

    with open(OUTPUT_BRIEF, "w", encoding="utf-8") as f:
        f.write(brief)

    print("Done.")
    print(f"Saved insights JSON to {OUTPUT_JSON}")
    print(f"Saved top scored ads to {OUTPUT_TOP_ADS}")
    print(f"Saved weekly brief to {OUTPUT_BRIEF}")
    print("\nWeekly Brief Preview:\n")
    print(brief)

if __name__ == "__main__":
    main()

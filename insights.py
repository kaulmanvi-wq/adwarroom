import pandas as pd


def ensure_classified(df):

    if "theme" not in df.columns:
        df["theme"] = "unknown"

    if "ad_text" not in df.columns:
        df["ad_text"] = ""

    return df


def run_full_analysis(df):

    insights = []

    if df.empty:
        return ["No data available"]

    top_format = df["format"].value_counts().idxmax()
    insights.append(f"Most used creative format: {top_format}")

    top_theme = df["theme"].value_counts().idxmax()
    insights.append(f"Most common message theme: {top_theme}")

    longest = df["days_running"].max()
    insights.append(f"Longest running ad: {int(longest)} days")

    brands = df["brand"].nunique()
    insights.append(f"{brands} brands are actively advertising")

    return insights

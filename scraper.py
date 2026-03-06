"""
scraper.py
Fetch ads from Meta Ad Library for tracked competitors
"""

import requests
import pandas as pd
from datetime import datetime

# Competitors
BRANDS = [
    "Traya",
    "Man Matters",
    "Be Bodywise",
    "Gynoveda",
    "Mamaearth",
    "The Moms Co",
    "Sirona",
    "Carmesi",
    "Bombay Shaving Company",
    "Beardo"
]

META_URL = "https://graph.facebook.com/v18.0/ads_archive"

def get_ads_for_brand(brand, token):

    params = {
        "access_token": token,
        "search_terms": brand,
        "ad_reached_countries": "IN",
        "ad_type": "ALL",
        "fields": "ad_creative_body,ad_creative_link_caption,ad_delivery_start_time,ad_delivery_stop_time,page_name,publisher_platforms",
        "limit": 50
    }

    r = requests.get(META_URL, params=params)
    data = r.json()

    ads = []

    for ad in data.get("data", []):

        start = ad.get("ad_delivery_start_time")

        if start:
            start_date = datetime.fromisoformat(start.replace("Z", ""))
            days_running = (datetime.now() - start_date).days
        else:
            days_running = 0

        text = ad.get("ad_creative_body", "")

        ads.append({
            "brand": brand,
            "category": "Wellness",
            "format": detect_format(ad),
            "theme": detect_theme(text),
            "ad_text": text,
            "days_running": days_running,
            "platform": ",".join(ad.get("publisher_platforms", [])),
            "is_active": "Yes",
            "url": "https://www.facebook.com/ads/library/"
        })

    return ads


def detect_format(ad):

    platforms = ad.get("publisher_platforms", [])

    if "instagram" in platforms or "facebook" in platforms:
        return "Video"

    return "Static Image"


def detect_theme(text):

    text = text.lower()

    if "hair" in text or "hairfall" in text:
        return "hair_loss"

    if "pcos" in text or "hormone" in text:
        return "hormonal_health"

    if "doctor" in text:
        return "doctor_authority"

    if "discount" in text or "offer" in text:
        return "discount_offer"

    if "sleep" in text or "stress" in text:
        return "stress_sleep"

    return "ugc_testimonial"


def load_data(access_token=None):

    # If no token → return demo data
    if not access_token:

        data = []

        for brand in BRANDS:

            data.append({
                "brand": brand,
                "category": "Wellness",
                "format": "Video",
                "theme": "hair_loss",
                "ad_text": f"{brand} solution for hair fall",
                "days_running": 90,
                "platform": "Facebook,Instagram",
                "is_active": "Yes",
                "url": "https://facebook.com"
            })

        return pd.DataFrame(data)

    # Fetch real ads
    all_ads = []

    for brand in BRANDS:

        try:
            ads = get_ads_for_brand(brand, access_token)
            all_ads.extend(ads)

        except Exception as e:
            print("Error fetching", brand, e)

    df = pd.DataFrame(all_ads)

    if len(df) == 0:
        return pd.DataFrame()

    return df

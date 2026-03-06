"""
scraper.py
Seed competitor ad dataset generator
"""

import pandas as pd
import random

BRANDS = [
    {"brand": "Traya", "category": "Men's Wellness"},
    {"brand": "Man Matters", "category": "Men's Wellness"},
    {"brand": "Be Bodywise", "category": "Women's Wellness"},
    {"brand": "Gynoveda", "category": "Women's Wellness"},
    {"brand": "Mamaearth", "category": "Baby Care"},
    {"brand": "The Moms Co", "category": "Baby Care"},
    {"brand": "Sirona", "category": "Women's Wellness"},
    {"brand": "Carmesi", "category": "Women's Wellness"},
    {"brand": "Bombay Shaving Company", "category": "Men's Wellness"},
    {"brand": "Beardo", "category": "Men's Wellness"}
]

FORMATS = [
    "Video",
    "Carousel",
    "Static Image"
]

THEMES = [
    "hair_loss",
    "hormonal_health",
    "testosterone",
    "acne_treatment",
    "doctor_authority",
    "ugc_testimonial",
    "discount_offer",
    "emotional_story",
    "stress_sleep"
]

PLATFORMS = [
    "Facebook",
    "Instagram",
    "Facebook, Instagram"
]

AD_TEXT_SAMPLES = [
    "Still struggling with hair fall? Doctors recommend this routine.",
    "90 day transformation using natural ingredients.",
    "Real users share their hair regrowth journey.",
    "Stop hormonal acne naturally.",
    "Doctors reveal the real cause of hair loss.",
    "Flat 30% off this week only.",
    "Sleep better and reduce stress naturally.",
    "Parents trust this baby care routine.",
    "Ayurvedic formula backed by research.",
    "Thousands of happy customers already switched."
]


def generate_ads():

    rows = []

    for b in BRANDS:

        brand = b["brand"]
        category = b["category"]

        num_ads = random.randint(20,40)

        for i in range(num_ads):

            ad_text = random.choice(AD_TEXT_SAMPLES)

            row = {
                "brand": brand,
                "category": category,
                "format": random.choice(FORMATS),
                "theme": random.choice(THEMES),
                "platform": random.choice(PLATFORMS),
                "days_running": random.randint(5,120),
                "is_active": random.choice(["Yes","No"]),
                "ad_text": ad_text,
                "url": "https://facebook.com/ads/library"
            }

            rows.append(row)

    df = pd.DataFrame(rows)

    return df


def load_data(access_token=None):

    df = generate_ads()

    return df

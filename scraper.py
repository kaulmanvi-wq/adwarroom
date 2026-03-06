import pandas as pd


def load_data():

    data = [
        {
            "brand": "Traya",
            "category": "Men Wellness",
            "format": "Video",
            "theme": "hair_loss",
            "ad_text": "Stop hair loss in 90 days with doctor backed treatment",
            "days_running": 120
        },
        {
            "brand": "Be Bodywise",
            "category": "Women Wellness",
            "format": "Video",
            "theme": "hormonal_health",
            "ad_text": "Hormonal acne treatment by dermatologists",
            "days_running": 95
        },
        {
            "brand": "The Derma Co",
            "category": "Skin Care",
            "format": "Carousel",
            "theme": "acne",
            "ad_text": "Salicylic acid for acne free skin",
            "days_running": 60
        },
        {
            "brand": "Mamaearth",
            "category": "Baby Care",
            "format": "Image",
            "theme": "parenting",
            "ad_text": "Safe products for your baby",
            "days_running": 150
        }
    ]

    return pd.DataFrame(data)

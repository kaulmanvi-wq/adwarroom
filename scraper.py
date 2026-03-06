import os
import pandas as pd

# Brands list
BRANDS = {
    "Man Matters": {"category": "Men's Wellness"},
    "Traya Health": {"category": "Men's Wellness"},
    "Bombay Shaving Co": {"category": "Men's Wellness"},
    "Beardo": {"category": "Men's Wellness"},
    "The Man Company": {"category": "Men's Wellness"},
    "Hims": {"category": "Men's Wellness"},
    "Bebodywise": {"category": "Women's Wellness"},
    "Gynoveda": {"category": "Women's Wellness"},
    "andMe": {"category": "Women's Wellness"},
    "Nua Woman": {"category": "Women's Wellness"},
    "Carmesi": {"category": "Women's Wellness"},
    "Sirona": {"category": "Women's Wellness"},
    "Mamaearth": {"category": "Baby Care"},
    "The Moms Co": {"category": "Baby Care"},
    "Little Joys": {"category": "Baby Care"},
}

def load_data(access_token=None):

    data = []

    df = pd.DataFrame(data)

    csv_path = os.path.join(os.path.dirname(__file__), "ads_data.csv")

    df.to_csv(csv_path, index=False)

    return df

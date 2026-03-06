import os
import re
import time
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SEARCHAPI_KEY")
BASE_URL = "https://www.searchapi.io/api/v1/search"

BRANDS = [
    {"brand": "Traya", "query": "Traya Health"},
    {"brand": "Bold Care", "query": "Bold Care"},
    {"brand": "Mars by GHC", "query": "Mars by GHC"},
    {"brand": "ForMen Health", "query": "ForMen Health"},
    {"brand": "Power Gummies", "query": "Power Gummies"},
    {"brand": "Sirona", "query": "Sirona"},
    {"brand": "Sanfe", "query": "Sanfe"},
    {"brand": "Nua", "query": "Nua Woman"},
    {"brand": "Mother Sparsh", "query": "Mother Sparsh"},
    {"brand": "BabyOrgano", "query": "BabyOrgano"},
]

def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (text or "").lower())

def safe_get(url, params):
    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()
    return response.json()

def search_page(query: str):
    params = {
        "engine": "meta_ad_library_page_search",
        "q": query,
        "country": "ALL",
        "ad_type": "all",
        "api_key": API_KEY,
    }
    return safe_get(BASE_URL, params)

def choose_best_page(brand_name: str, page_results: list):
    if not page_results:
        return None

    target = normalize(brand_name)
    scored = []

    for page in page_results:
        name = page.get("name", "")
        alias = page.get("page_alias", "")
        score = 0

        if normalize(name) == target or normalize(alias) == target:
            score += 100
        if target in normalize(name) or target in normalize(alias):
            score += 50
        if page.get("verification") == "VERIFIED":
            score += 5

        likes = page.get("likes", 0) or 0
        try:
            score += min(int(likes) // 10000, 10)
        except:
            pass

        scored.append((score, page))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0][1]

def fetch_ads_for_page(page_id: str, max_pages: int = 1):
    all_ads = []
    next_page_token = None

    for page_num in range(max_pages):
        params = {
            "engine": "meta_ad_library",
            "page_id": page_id,
            "country": "ALL",
            "ad_type": "all",
            "active_status": "active",
            "api_key": API_KEY,
        }

        if next_page_token:
            params["next_page_token"] = next_page_token

        data = safe_get(BASE_URL, params)
        ads = data.get("ads", [])
        all_ads.extend(ads)

        next_page_token = data.get("pagination", {}).get("next_page_token")
        if not next_page_token:
            break

        time.sleep(1)

    return all_ads

def detect_format(ad: dict) -> str:
    snapshot = ad.get("snapshot", {}) or {}
    display_format = (snapshot.get("display_format") or "").upper()

    videos = snapshot.get("videos") or []
    images = snapshot.get("images") or []

    if "VIDEO" in display_format or len(videos) > 0:
        return "video"
    if "MULTI" in display_format or len(images) > 1:
        return "carousel"
    if "IMAGE" in display_format or len(images) == 1:
        return "static image"

    return "unknown"

def build_snapshot_url(ad_archive_id: str) -> str:
    if not ad_archive_id:
        return ""
    return f"https://www.facebook.com/ads/library/?id={ad_archive_id}"

def extract_record(requested_brand: str, matched_page: dict, ad: dict) -> dict:
    snapshot = ad.get("snapshot", {}) or {}
    body = snapshot.get("body", {}) or {}

    return {
        "brand_name": requested_brand,
        "matched_page_name": ad.get("page_name") or matched_page.get("name", ""),
        "page_id": ad.get("page_id") or matched_page.get("page_id", ""),
        "ad_text": body.get("text", ""),
        "ad_start_date": ad.get("start_date", ""),
        "ad_creative_type": detect_format(ad),
        "platform": ", ".join(ad.get("publisher_platform", [])),
        "ad_snapshot_url": build_snapshot_url(ad.get("ad_archive_id")),
        "ad_archive_id": ad.get("ad_archive_id", ""),
        "raw_display_format": snapshot.get("display_format", ""),
    }

def main():
    if not API_KEY:
        raise ValueError("SEARCHAPI_KEY not found. Put it in your .env file.")

    all_rows = []
    page_matches = []

    for item in BRANDS:
        brand = item["brand"]
        query = item["query"]

        print(f"\nSearching page for: {brand}")
        page_data = search_page(query)
        page_results = page_data.get("page_results", [])

        best_page = choose_best_page(brand, page_results)

        if not best_page:
            print(f"No page found for {brand}")
            continue

        page_matches.append({
            "brand": brand,
            "query": query,
            "matched_page_name": best_page.get("name", ""),
            "page_id": best_page.get("page_id", ""),
            "verification": best_page.get("verification", ""),
            "likes": best_page.get("likes", ""),
        })

        print(f"Matched page: {best_page.get('name')} | page_id={best_page.get('page_id')}")

        ads = fetch_ads_for_page(best_page.get("page_id"), max_pages=1)
        print(f"Fetched {len(ads)} ads for {brand}")

        for ad in ads:
            all_rows.append(extract_record(brand, best_page, ad))

        time.sleep(1)

    os.makedirs("data", exist_ok=True)

    ads_df = pd.DataFrame(all_rows)
    matches_df = pd.DataFrame(page_matches)

    ads_df.to_csv("data/raw_ads.csv", index=False)
    matches_df.to_csv("data/page_matches.csv", index=False)

    print("\nDone.")
    print(f"Saved ads to: data/raw_ads.csv")
    print(f"Saved page matches to: data/page_matches.csv")
    print(f"Total ads collected: {len(ads_df)}")

if __name__ == "__main__":
    main()

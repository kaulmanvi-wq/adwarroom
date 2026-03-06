# Competitor Ad War Room

A D2C competitive intelligence dashboard that analyzes competitor ads from Meta Ad Library and transforms raw ad data into actionable insights for marketing teams.

## What it does

- Tracks **15 competitor brands** across Men's Wellness, Women's Wellness, and Baby Care
- Fetches real ads from **Meta Ad Library API** (with seed data fallback)
- **AI classifies** ads by creative format and message theme
- Generates **competitive intelligence** insights
- Detects **strategic gap opportunities** competitors are missing
- Produces a **Weekly Intelligence Brief** for marketing teams

## Project Structure

```
adwarroom/
├── app.py              # Streamlit dashboard
├── scraper.py          # Meta Ad Library data collector
├── insights.py         # Intelligence & gap analysis engine
├── requirements.txt    # Python dependencies
├── .streamlit/
│   └── config.toml     # Streamlit theme config
└── data/
    └── ads_data.csv    # Auto-generated data cache
```

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Cloud (FREE)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set `app.py` as the main file
5. Click Deploy — get a live public URL in 2 minutes

## Optional: Connect Live Meta Data

1. Go to [developers.facebook.com](https://developers.facebook.com)
2. Create an app → Tools → Graph API Explorer
3. Generate an access token
4. Paste it in the sidebar "Meta API Token" field

## Brands Tracked

**Men's Wellness:** Man Matters, Traya Health, Bombay Shaving Co, Beardo, The Man Company, Hims

**Women's Wellness:** Bebodywise, Gynoveda, andMe, Nua Woman, Carmesi, Sirona

**Baby Care:** Mamaearth, The Moms Co, Little Joys

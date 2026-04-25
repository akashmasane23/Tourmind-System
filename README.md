# TourMind AI 🌍

A hybrid rule-based + ML travel intelligence app built with Streamlit.

## Features

| Feature | Description |
|---|---|
| 🏖️ Place Recommendations | Search tourist destinations with Unsplash photos & Wikipedia info |
| ⭐ Reviews & Ratings | Community travel reviews stored in Google Sheets |
| 🗓️ Itinerary Planner | AI-generated day-by-day travel plans (OpenAI) |
| 💬 Chatbot Assistant | AI travel assistant with rule-based fallback |
| 🌤️ Destination & Weather | Live weather forecasts via OpenWeatherMap |
| ⏰ Peak Hours & Nearby | **Hybrid ML** crowd prediction + ML-ranked nearby attractions |

## ML System (Hybrid Rule-Based + ML)

The app uses a **two-layer system** — the original rule engine is always active; ML adds enhancements on top.

### Crowd Prediction
- **Rule engine**: `time_score × day_score × weather_factor → crowd level`
- **ML layer**: RandomForestClassifier trained on 3,000 synthetic samples; uses `rule_score` as a feature
- **UI**: Shows both predictions side-by-side with ML confidence %

### Place Ranking
- **Rule engine**: Haversine distance sort + OpenStreetMap fallback
- **ML layer**: RandomForestRegressor ranks by `distance`, `rating`, `activity_match`, `hour_relevance`
- **UI**: Each card shows `🤖 ML Score` and rank badge

## Quick Start

```bash
# 1. Clone and install
pip install -r requirements.txt

# 2. Train ML models (one-time)
python models/ml_model.py

# 3. Run the app
streamlit run app.py
```

## API Keys

Add to `.streamlit/secrets.toml`:

```toml
OPENAI_API_KEY      = "sk-..."
UNSPLASH_ACCESS_KEY = "your_key"
OPENWEATHER_API_KEY = "your_key"

# Optional — for persistent reviews & itineraries
GOOGLE_SHEET_URL    = "https://docs.google.com/spreadsheets/d/..."
[gcp_service_account]
# paste your GCP service account JSON fields here
```

## Project Structure

```
TourMind-AI/
├── app.py                    # Main Streamlit app + navigation
├── config.py                 # API keys, constants, settings
├── requirements.txt
├── models/
│   ├── ml_model.py           # Dataset generation + RF training script
│   ├── crowd_rf_model.joblib # Auto-generated (run ml_model.py)
│   └── ranking_rf_model.joblib
├── services/
│   └── ml_service.py         # Runtime ML singleton (eager-loaded)
├── utils/
│   ├── realtime_crowd.py     # Hybrid crowd prediction
│   ├── realtime_places.py    # Hybrid nearby attraction finder
│   ├── api_handlers.py       # Unsplash, Wikipedia, OpenWeatherMap
│   ├── data_handlers.py      # Google Sheets + CSV data layer
│   ├── chatbot_handler.py    # OpenAI chatbot handler
│   └── pdf_generator.py      # Itinerary PDF export
├── pages/
│   ├── peak_hours_nearby.py  # Peak hours + ML comparison UI
│   ├── place_recommendations.py
│   ├── reviews_and_ratings.py
│   ├── itinerary_planner.py
│   ├── destination_info.py
│   └── chatbot_assistant.py
└── data/
    ├── places.csv            # 100 Pune tourist places with coordinates
    └── peak_hours_nearby.csv # Crowd timing data per place
```

## Tech Stack

- **Frontend**: Streamlit + custom CSS (glassmorphism, animations)
- **ML**: scikit-learn RandomForest (classifier + regressor), joblib
- **Data**: pandas, numpy, synthetic dataset generation
- **APIs**: OpenAI GPT-4o-mini, Unsplash, OpenWeatherMap, Wikipedia, OSM Overpass
- **Storage**: Google Sheets (primary) + CSV fallback

---
Built with ❤️ for travellers | © 2026 TourMind AI

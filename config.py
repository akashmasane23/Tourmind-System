"""
TourMind AI — Configuration
All app-wide constants, settings, and API key loading live here.

Improvements:
  - API key loader checks ALL locations every utils file uses:
      st.secrets["KEY"], st.secrets["api_keys"]["KEY"], os.getenv("KEY")
  - Consistent key names (uppercase) across secrets + env
  - check_api_keys() / get_missing_keys() updated to include OpenAI
  - Cache TTLs, limits, and constants grouped clearly
  - Removed redundant fallback strings that masked misconfiguration
"""

import os
import streamlit as st

# ============================================
# SECURE API KEY LOADING
# ============================================

def _load_key(
    flat_name: str,
    nested_name: str | None = None,
    env_name: str | None = None,
    fallback: str = "",
) -> str:
    """
    Universal key loader — checks in order:
      1. st.secrets["FLAT_NAME"]
      2. st.secrets["api_keys"]["NESTED_NAME"]   (if nested_name provided)
      3. os.environ["ENV_NAME"]                  (if env_name provided)
      4. fallback string

    This matches the lookup order used in every utils file.
    """
    try:
        if flat_name in st.secrets:
            return st.secrets[flat_name]
    except Exception:
        pass

    try:
        if nested_name and "api_keys" in st.secrets:
            val = st.secrets["api_keys"].get(nested_name)
            if val:
                return val
    except Exception:
        pass

    if env_name:
        val = os.getenv(env_name)
        if val:
            return val

    return fallback


# Load all keys
UNSPLASH_ACCESS_KEY = _load_key(
    "UNSPLASH_ACCESS_KEY",
    nested_name="unsplash_access_key",
    env_name="UNSPLASH_ACCESS_KEY",
    fallback="YOUR_UNSPLASH_ACCESS_KEY",
)

OPENWEATHER_API_KEY = _load_key(
    "OPENWEATHER_API_KEY",
    nested_name="openweather_api_key",
    env_name="OPENWEATHER_API_KEY",
    fallback="YOUR_OPENWEATHER_API_KEY",
)

OPENAI_API_KEY = _load_key(
    "OPENAI_API_KEY",
    nested_name="openai_api_key",
    env_name="OPENAI_API_KEY",
    fallback="",
)

GOOGLE_PLACES_API_KEY = _load_key(
    "GOOGLE_PLACES_API_KEY",
    nested_name="google_places_api_key",
    env_name="GOOGLE_PLACES_API_KEY",
    fallback="",
)

GOOGLE_SHEET_URL = _load_key(
    "GOOGLE_SHEET_URL",
    env_name="GOOGLE_SHEET_URL",
    fallback="",
)

# ============================================
# API ENDPOINTS
# ============================================

UNSPLASH_API_URL    = "https://api.unsplash.com/search/photos"
OPENWEATHER_API_URL = "https://api.openweathermap.org/data/2.5"

# ============================================
# APP SETTINGS
# ============================================

APP_TITLE             = "TourMind AI"
APP_ICON              = "🌍"
APP_VERSION           = "2.1.0"    # 2.1.0 — Hybrid ML enhancement layer
DEFAULT_RESULTS_LIMIT = 10

# ============================================
# CACHE TTLs (seconds)
# ============================================

CACHE_TTL_SHORT  = 1800    # 30 min  — weather, live crowd
CACHE_TTL_MEDIUM = 3600    # 1 hour  — places, peak hours
CACHE_TTL_LONG   = 86400   # 24 hrs  — Wikipedia, Unsplash images

# ============================================
# ML MODEL PATHS
# ============================================

import os as _os
_MODELS_DIR              = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "models")
ML_CROWD_MODEL_PATH      = _os.path.join(_MODELS_DIR, "crowd_rf_model.joblib")
ML_CROWD_ENCODER_PATH    = _os.path.join(_MODELS_DIR, "crowd_label_encoder.joblib")
ML_RANKING_MODEL_PATH    = _os.path.join(_MODELS_DIR, "ranking_rf_model.joblib")

# ============================================
# WIKIPEDIA
# ============================================

WIKI_USER_AGENT = "TourMindAI/2.0 (tourmind@example.com)"
WIKI_LANGUAGE   = "en"

# ============================================
# TIME SLOTS
# ============================================

TIME_SLOTS = [
    "Early Morning (5–8 AM)",
    "Morning (8–11 AM)",
    "Afternoon (11 AM–2 PM)",
    "Evening (2–6 PM)",
    "Night (6–10 PM)",
]

# ============================================
# TRIP TYPES & PREFERENCES
# ============================================

TRIP_TYPES = [
    "Relaxation",
    "Adventure",
    "Cultural",
    "Family",
    "Solo",
    "Romantic",
    "Business",
    "Spiritual",
]

TRAVEL_PREFERENCES = [
    "Historical Sites",
    "Beaches",
    "Mountains",
    "Food Tours",
    "Shopping",
    "Wildlife",
    "Photography",
    "Nightlife",
    "Spiritual",
    "Architecture",
    "Museums",
    "Adventure Sports",
]

# ============================================
# RATINGS
# ============================================

MIN_RATING = 1
MAX_RATING = 5
RATING_LABELS = {
    1: "😞 Poor",
    2: "😕 Fair",
    3: "😐 Good",
    4: "😊 Very Good",
    5: "🤩 Excellent",
}

# ============================================
# MAP
# ============================================

DEFAULT_MAP_ZOOM = 12
MAP_TILE_STYLE   = "OpenStreetMap"

# ============================================
# IMAGE SIZES
# ============================================

IMAGE_WIDTH      = 800
IMAGE_HEIGHT     = 600
THUMBNAIL_WIDTH  = 400
THUMBNAIL_HEIGHT = 300
ITEMS_PER_PAGE   = 10

# ============================================
# RULE-BASED CHATBOT KEYWORDS
# (used as fallback when OpenAI is unavailable)
# ============================================

CHATBOT_KEYWORDS = {
    "weather": (
        "I can help with weather! 🌤️ Go to **Destination Info** and enter "
        "a city name to see current conditions and a 5-day forecast."
    ),
    "itinerary": (
        "Planning a trip? 🗓️ Visit **Itinerary Planner**, enter your destination, "
        "duration, and preferences — I'll generate a day-by-day plan for you!"
    ),
    "place": (
        "Looking for places? 🏖️ Head to **Place Recommendations** and search "
        "by city or state to discover top destinations with photos."
    ),
    "review": (
        "For reviews ⭐ check the **Reviews & Ratings** page — read fellow "
        "travellers' experiences or leave your own."
    ),
    "peak hours": (
        "Find the best visiting times ⏰ on the **Peak Hours & Nearby** page — "
        "see crowd levels, optimal timing, and nearby attractions."
    ),
    "nearby": (
        "Discover nearby attractions 📍 on the **Peak Hours & Nearby** page. "
        "Search for a place and we'll show what's close by!"
    ),
    "budget": (
        "For budget tips 💰 use the **Itinerary Planner** — it includes an "
        "estimated cost breakdown per person for your trip."
    ),
    "food": (
        "Hungry for local flavours? 🍜 Use the **Itinerary Planner** with "
        "'Food Tours' in preferences — I'll include restaurant & street food tips."
    ),
    "hello": (
        "Hello! 👋 I'm your TourMind assistant. Ask me about places, "
        "weather, itineraries, reviews, or the best times to visit!"
    ),
    "hi": (
        "Hi there! 🌿 Ready to plan your next adventure? Ask me anything "
        "about destinations across India!"
    ),
    "help": (
        "I can assist with:\n"
        "🏖️ Finding tourist places\n"
        "🗓️ Planning itineraries\n"
        "🌤️ Checking weather\n"
        "⭐ Reading & writing reviews\n"
        "⏰ Best visiting times & crowd levels\n"
        "💬 General travel tips\n\n"
        "What would you like help with?"
    ),
    "thanks": (
        "You're welcome! 😊 Happy travels and have a wonderful trip! 🌍✈️"
    ),
}

DEFAULT_CHATBOT_RESPONSE = (
    "I'm here to help with your travel plans! 🌍 "
    "Try asking about destinations, weather, itineraries, "
    "reviews, or the best times to visit an attraction."
)

# ============================================
# ERROR & SUCCESS MESSAGES
# ============================================

ERROR_MESSAGES = {
    "api_key_missing":  "⚠️ API key not configured. Add it to .streamlit/secrets.toml",
    "api_error":        "⚠️ API request failed. Please try again later.",
    "no_results":       "😔 No results found. Try a different search term.",
    "network_error":    "🌐 Network error. Check your internet connection.",
    "invalid_input":    "❌ Invalid input. Please check your entry and try again.",
}

SUCCESS_MESSAGES = {
    "review_saved":    "✅ Review submitted successfully. Thank you!",
    "itinerary_saved": "✅ Itinerary saved successfully!",
    "data_loaded":     "✅ Data loaded successfully!",
}

HELP_TEXT = {
    "place_search":     "Enter a city or state name — e.g. Goa, Rajasthan, Mumbai",
    "review_rating":    "Rate 1–5 stars. Be honest and helpful for fellow travellers!",
    "itinerary_days":   "Select trip duration: 1–14 days",
    "weather_forecast": "Enter a city name for current weather and 5-day forecast",
    "peak_hours":       "Find best visiting times and avoid peak crowds",
}

# ============================================
# API SETUP GUIDE (shown in UI)
# ============================================

API_SETUP_INSTRUCTIONS = """
### 🔑 How to Get Free API Keys

#### 1. Unsplash API (Images)
- Visit: https://unsplash.com/developers
- Create a new application → copy your **Access Key**
- Free tier: 50 requests/hour

#### 2. OpenWeatherMap API (Weather)
- Visit: https://openweathermap.org/appid
- Sign up and check email for your **API Key**
- Free tier: 1,000 calls/day

#### 3. OpenAI API (Chatbot + Itinerary)
- Visit: https://platform.openai.com/api-keys
- Create a new key and add billing
- Model used: `gpt-4o-mini` (very affordable)

#### 4. Wikipedia API — ✅ No key needed

---

Add all keys to `.streamlit/secrets.toml`:

```toml
OPENAI_API_KEY       = "sk-..."
UNSPLASH_ACCESS_KEY  = "your_key"
OPENWEATHER_API_KEY  = "your_key"
```
"""

# ============================================
# HELPER FUNCTIONS
# ============================================

def check_api_keys() -> dict[str, bool]:
    """Return which API keys are properly configured."""
    # Check Google Sheets separately (needs both URL + service account)
    try:
        sheets_ok = bool(
            st.secrets.get("gcp_service_account") and
            st.secrets.get("GOOGLE_SHEET_URL")
        )
    except Exception:
        sheets_ok = False

    return {
        "unsplash":    (
            bool(UNSPLASH_ACCESS_KEY) and
            UNSPLASH_ACCESS_KEY not in ("YOUR_UNSPLASH_ACCESS_KEY", "")
        ),
        "openweather": (
            bool(OPENWEATHER_API_KEY) and
            OPENWEATHER_API_KEY not in ("YOUR_OPENWEATHER_API_KEY", "")
        ),
        "openai":      bool(OPENAI_API_KEY),
        "wikipedia":   True,
        "sheets":      sheets_ok,
    }


def get_missing_keys() -> list[str]:
    """Return list of missing (non-configured) API key names."""
    status  = check_api_keys()
    missing = []
    if not status["unsplash"]:
        missing.append("Unsplash (destination photos)")
    if not status["openweather"]:
        missing.append("OpenWeatherMap (weather forecasts)")
    if not status["openai"]:
        missing.append("OpenAI (AI chatbot & itinerary planner)")
    if not status["sheets"]:
        missing.append("Google Sheets (persistent reviews & itineraries)")
    return missing
"""
TourMind — Live Crowd Predictor (Hybrid Rule-Based + ML)
Used by: pages/peak_hours_nearby.py

Original rule-based system (unchanged):
  - Holiday/festival calendar boosts crowd on public holidays
  - Finer time-of-day scoring (dawn/night correctly = Low)
  - Weather factor checks both nested & flat secrets
  - Confidence label returned alongside level
  - Returns structured dict so callers get richer data
  - predict_live_crowd() still returns plain string (backward compat)

ML Enhancement (added on top — does NOT replace rule logic):
  - RandomForestClassifier trained on synthetic data
  - Uses rule_score as a feature (along with hour, weekday, etc.)
  - Adds 'ml_prediction' and 'ml_confidence' keys to returned dict
  - Falls back silently if model files not present
"""

from datetime import date, datetime
from typing import Optional
import requests
import streamlit as st


# ============================================
# INDIAN PUBLIC HOLIDAYS (approximate fixed dates)
# Add / remove as needed
# ============================================

_HOLIDAYS: set[tuple[int, int]] = {
    (1,  26),   # Republic Day
    (8,  15),   # Independence Day
    (10,  2),   # Gandhi Jayanti
    (11,  1),   # Diwali region (approximate)
    (12, 25),   # Christmas
    (1,   1),   # New Year
    (3,  25),   # Holi (approximate)
    (4,  14),   # Dr. Ambedkar Jayanti
}


def _is_holiday(d: date | None = None) -> bool:
    """Return True if the date falls on a known Indian public holiday."""
    d = d or date.today()
    return (d.month, d.day) in _HOLIDAYS


# ============================================
# WEATHER FACTOR
# ============================================

def _get_api_key_weather() -> Optional[str]:
    """Fetch OpenWeatherMap key from flat or nested secrets, then env."""
    import os
    try:
        if "OPENWEATHER_API_KEY" in st.secrets:
            return st.secrets["OPENWEATHER_API_KEY"]
        if "api_keys" in st.secrets:
            k = st.secrets["api_keys"].get("OPENWEATHER_API_KEY")
            if k:
                return k
    except Exception:
        pass
    return os.getenv("OPENWEATHER_API_KEY")


@st.cache_data(ttl=1800)
def get_weather_factor(city: str = "Pune") -> tuple[float, str]:
    """
    Fetch live weather and return (factor, description).
    factor > 1  → more people likely out
    factor < 1  → fewer people likely out
    """
    key = _get_api_key_weather()
    if key:
        try:
            resp = requests.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={"q": city, "appid": key},
                timeout=5,
            )
            if resp.status_code == 200:
                data        = resp.json()
                weather     = data["weather"][0]["main"].lower()
                description = data["weather"][0]["description"].capitalize()
                temp_c      = round(data["main"]["temp"] - 273.15, 1)

                if "thunderstorm" in weather: return 0.5, f"{description} ({temp_c}°C)"
                if "rain" in weather or "drizzle" in weather: return 0.7, f"{description} ({temp_c}°C)"
                if "snow" in weather or "fog" in weather or "mist" in weather: return 0.8, f"{description} ({temp_c}°C)"
                if "clear" in weather: return 1.2, f"{description} ({temp_c}°C)"
                return 1.0, f"{description} ({temp_c}°C)"
        except Exception:
            pass

    # Fallback to Open-Meteo (No API key required)
    try:
        geo_resp = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1", timeout=5)
        if geo_resp.status_code == 200:
            geo_data = geo_resp.json().get("results", [])
            if geo_data:
                lat, lon = geo_data[0]["latitude"], geo_data[0]["longitude"]
                weather_resp = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true", timeout=5)
                if weather_resp.status_code == 200:
                    w_data = weather_resp.json().get("current_weather", {})
                    code = w_data.get("weathercode", 0)
                    temp = w_data.get("temperature", 25)
                    
                    if code in [95, 96, 99]: return 0.5, f"Thunderstorm ({temp}°C)"
                    if code in [51, 53, 55, 61, 63, 65, 66, 67]: return 0.7, f"Rain ({temp}°C)"
                    if code in [45, 48, 71, 73, 75, 77]: return 0.8, f"Fog/Snow ({temp}°C)"
                    if code == 0: return 1.2, f"Clear Sky ({temp}°C)"
                    return 1.0, f"Cloudy ({temp}°C)"
    except Exception:
        pass

    return 1.0, "Unknown"


# ============================================
# SCORING ENGINE
# ============================================

def _time_score(hour: int) -> tuple[float, str]:
    """Return a base score and time-slot label for the given hour."""
    if   0  <= hour <= 5:   return 0.2, "Late Night"
    elif 6  <= hour <= 8:   return 0.5, "Early Morning"
    elif 9  <= hour <= 11:  return 0.9, "Morning"
    elif 12 <= hour <= 14:  return 1.2, "Midday"
    elif 15 <= hour <= 16:  return 1.0, "Afternoon"
    elif 17 <= hour <= 19:  return 1.5, "Evening Rush"
    elif 20 <= hour <= 21:  return 1.3, "Night"
    else:                   return 0.6, "Late Evening"


def _day_score(weekday: int, is_holiday: bool) -> tuple[float, str]:
    """
    Return a day multiplier and label.
    weekday: 0=Mon … 6=Sun
    """
    if is_holiday:
        return 1.8, "Public Holiday"
    if weekday == 6:    # Sunday
        return 1.6, "Sunday"
    if weekday == 5:    # Saturday
        return 1.4, "Saturday"
    if weekday == 4:    # Friday
        return 1.1, "Friday"
    return 1.0, "Weekday"


def _score_to_level(score: float) -> tuple[str, str]:
    """Map numeric score to (level, confidence)."""
    if   score < 1.2:  return "Low",       "High"
    elif score < 2.2:  return "Medium",    "High"
    elif score < 3.2:  return "High",      "Medium"
    else:              return "Very High", "Medium"


# ============================================
# PUBLIC API
# ============================================

def predict_crowd_detail(city: str = "Pune", hour: int = None) -> dict:
    """
    Full crowd prediction with all contributing factors.

    Returns:
        {
          "level":         str   — "Low" / "Medium" / "High" / "Very High"  (rule-based)
          "score":         float — raw numeric score
          "confidence":    str   — "High" / "Medium"  (rule-based confidence label)
          "time_slot":     str   — e.g. "Evening Rush"
          "day_type":      str   — e.g. "Sunday" / "Public Holiday"
          "weather_desc":  str   — e.g. "Clear sky"
          "factors": {
              "time":    float,
              "day":     float,
              "weather": float,
          }
          # ── ML Enhancement fields (None if model not loaded) ──
          "rule_based":    str   — same as "level" (explicit label for UI comparison)
          "ml_prediction": str | None  — ML model output
          "ml_confidence": float | None — probability of the predicted class
        }
    """
    now      = datetime.now()
    current_hour = now.hour if hour is None else hour
    weekday  = now.weekday()
    holiday  = _is_holiday(now.date())

    time_sc,    time_slot    = _time_score(current_hour)
    day_sc,     day_type     = _day_score(weekday, holiday)
    weather_sc, weather_desc = get_weather_factor(city)

    score = time_sc * day_sc * weather_sc
    level, confidence = _score_to_level(score)

    # ── ML Enhancement: call ml_service if available ──────────────────
    # Imported here (lazy) to avoid circular imports and keep startup fast.
    ml_prediction = None
    ml_confidence = None
    try:
        from services.ml_service import ml_service
        ml_result = ml_service.predict_crowd_ml(
            hour=current_hour,
            weekday=weekday,
            is_holiday=int(holiday),
            weather_factor=weather_sc,
            rule_score=score,
        )
        if ml_result:
            ml_prediction = ml_result["ml_prediction"]
            ml_confidence = ml_result["confidence"]
    except Exception:
        pass  # silently fall back — rule-based result is always returned
    # ─────────────────────────────────────────────────────────────────

    return {
        # ── Original keys (unchanged — backward compatible) ──
        "level":        level,
        "score":        round(score, 3),
        "confidence":   confidence,
        "time_slot":    time_slot,
        "day_type":     day_type,
        "weather_desc": weather_desc,
        "factors": {
            "time":    round(time_sc,    2),
            "day":     round(day_sc,     2),
            "weather": round(weather_sc, 2),
        },
        # ── ML Enhancement keys (new) ──
        "rule_based":    level,
        "ml_prediction": ml_prediction,
        "ml_confidence": ml_confidence,
    }


def predict_live_crowd(city: str = "Pune") -> str:
    """
    Backward-compatible wrapper — returns plain crowd level string.
    Used by peak_hours_nearby.py exactly as before.
    """
    return predict_crowd_detail(city)["level"]
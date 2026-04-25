"""
TourMind — Data Handlers
Deployment-ready: reviews & itineraries use Google Sheets (persistent).
Static data (places, peak hours) loads from local CSV files (in repo).

Setup:
  1. Create a Google Sheet with two tabs: "Reviews" and "Itineraries"
  2. Create a GCP Service Account, download JSON key
  3. Share the sheet with the service account email
  4. Add credentials to .streamlit/secrets.toml (see secrets_template.toml)
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st

log = logging.getLogger("tourmind.data")

# ── File paths (static data only) ────────────
DATA_DIR    = "data"
PEAK_FILE   = os.path.join(DATA_DIR, "peak_hours_nearby.csv")
PLACES_FILE = os.path.join(DATA_DIR, "places.csv")
ENCODINGS   = ["utf-8", "utf-8-sig", "cp1252", "latin1"]

REVIEWS_COLUMNS   = ["place", "user_name", "rating", "comment", "date"]
ITINERARY_COLUMNS = ["key", "destination", "days", "trip_type",
                     "preferences", "itinerary", "created_at"]


# ============================================
# GOOGLE SHEETS CONNECTION
# ============================================

@st.cache_resource(show_spinner=False)
def _get_gsheet_client():
    """
    Return an authenticated gspread client using service account
    credentials stored in st.secrets["gcp_service_account"].
    Returns None if credentials are not configured.
    """
    try:
        import gspread
        from google.oauth2.service_account import Credentials

        creds_dict = dict(st.secrets["gcp_service_account"])
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds  = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        log.warning("Google Sheets not configured: %s", e)
        return None


def _get_worksheet(tab_name: str):
    """
    Open a worksheet by tab name from the configured Google Sheet.
    Tries exact match first, then case-insensitive match.
    Sheet URL/ID comes from st.secrets["GOOGLE_SHEET_URL"].
    Returns worksheet or None.
    """
    try:
        client = _get_gsheet_client()
        if not client:
            return None
        sheet_url = st.secrets.get("GOOGLE_SHEET_URL", "")
        if not sheet_url:
            return None
        sheet = client.open_by_url(sheet_url)

        # Try exact match first
        try:
            return sheet.worksheet(tab_name)
        except Exception:
            pass

        # Try case-insensitive + stripped match
        available = sheet.worksheets()
        tab_lower = tab_name.lower().strip()
        for ws in available:
            if ws.title.lower().strip() == tab_lower:
                log.info("Matched tab '%s' to '%s'", tab_name, ws.title)
                return ws

        # Log available tabs to help diagnose
        names = [ws.title for ws in available]
        log.error(
            "_get_worksheet: tab '%s' not found. Available tabs: %s",
            tab_name, names
        )
        # Show in Streamlit so user can see it
        import streamlit as _st
        _st.warning(
            f"⚠️ Google Sheet tab **'{tab_name}'** not found.\n\n"
            f"Available tabs in your sheet: **{names}**\n\n"
            f"Please rename one tab to exactly `Reviews` and another to `Itineraries`."
        )
        return None

    except Exception as e:
        log.error("_get_worksheet(%s) failed: %s", tab_name, e)
        return None


def _sheets_available() -> bool:
    """Quick check — True if Google Sheets is configured."""
    try:
        return bool(
            st.secrets.get("gcp_service_account") and
            st.secrets.get("GOOGLE_SHEET_URL")
        )
    except Exception:
        return False


# ============================================
# DIRECTORY + CSV HELPERS (static files)
# ============================================

def ensure_data_directory() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)


def _read_csv_safe(filepath: str, **kwargs) -> pd.DataFrame:
    for enc in ENCODINGS:
        try:
            df = pd.read_csv(filepath, encoding=enc, **kwargs)
            df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
            return df
        except UnicodeDecodeError:
            continue
        except Exception as e:
            log.error("Failed reading %s: %s", filepath, e)
            return pd.DataFrame()
    return pd.DataFrame()


# ============================================
# REVIEWS  (Google Sheets primary, CSV fallback)
# ============================================

def load_reviews() -> pd.DataFrame:
    """
    Load all reviews.
    Primary:  Google Sheets tab "Reviews"
    Fallback: data/reviews.csv  (local dev or if Sheets not configured)
    """
    # ── Google Sheets ─────────────────────────
    if _sheets_available():
        try:
            ws      = _get_worksheet("Reviews")
            if ws is None:
                raise ValueError("Worksheet not found")
            records = ws.get_all_records()
            if not records:
                return pd.DataFrame(columns=REVIEWS_COLUMNS)
            df = pd.DataFrame(records)
            # Normalise
            for col in REVIEWS_COLUMNS:
                if col not in df.columns:
                    df[col] = ""
            df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0).astype(int)
            return df[REVIEWS_COLUMNS]
        except Exception as e:
            log.error("load_reviews (Sheets) failed: %s — falling back to CSV", e)

    # ── CSV fallback ──────────────────────────
    ensure_data_directory()
    reviews_file = os.path.join(DATA_DIR, "reviews.csv")
    if not os.path.exists(reviews_file):
        empty = pd.DataFrame(columns=REVIEWS_COLUMNS)
        empty.to_csv(reviews_file, index=False)
        return empty
    df = _read_csv_safe(reviews_file)
    if df.empty:
        return pd.DataFrame(columns=REVIEWS_COLUMNS)
    for col in REVIEWS_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0).astype(int)
    return df[REVIEWS_COLUMNS]


def save_review(place: str, user_name: str, rating: int, comment: str) -> bool:
    """
    Save a new review.
    Primary:  Append row to Google Sheets tab "Reviews"
    Fallback: Append to data/reviews.csv
    """
    place     = place.strip()
    user_name = user_name.strip()
    comment   = comment.strip()

    if not all([place, user_name, comment]):
        log.warning("save_review: empty field")
        return False
    if not (1 <= int(rating) <= 5):
        log.warning("save_review: invalid rating %s", rating)
        return False

    from datetime import datetime, timezone, timedelta
    ist_tz = timezone(timedelta(hours=5, minutes=30))
    new_row = {
        "place":     place,
        "user_name": user_name,
        "rating":    int(rating),
        "comment":   comment,
        "date":      datetime.now(ist_tz).strftime("%Y-%m-%d %H:%M:%S"),
    }

    # ── Google Sheets ─────────────────────────
    if _sheets_available():
        try:
            ws = _get_worksheet("Reviews")
            if ws is None:
                raise ValueError("Worksheet not found")

            # If sheet is empty, write header first
            if ws.row_count <= 1 and not ws.get_all_values():
                ws.append_row(REVIEWS_COLUMNS)

            ws.append_row([new_row[c] for c in REVIEWS_COLUMNS])
            st.cache_data.clear()
            return True
        except Exception as e:
            log.error("save_review (Sheets) failed: %s — falling back to CSV", e)

    # ── CSV fallback ──────────────────────────
    try:
        ensure_data_directory()
        reviews_file = os.path.join(DATA_DIR, "reviews.csv")
        df = load_reviews()
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(reviews_file, index=False, encoding="utf-8")
        st.cache_data.clear()
        return True
    except Exception as e:
        log.error("save_review (CSV fallback) failed: %s", e)
        return False


def get_place_reviews(place: str) -> pd.DataFrame:
    df = load_reviews()
    if df.empty:
        return df
    return df[df["place"].str.lower() == place.lower()]


def get_average_rating(place: str) -> Optional[float]:
    reviews = get_place_reviews(place)
    if reviews.empty:
        return None
    return round(float(reviews["rating"].mean()), 2)


def get_review_count(place: str) -> int:
    return len(get_place_reviews(place))


# ============================================
# ITINERARIES  (Google Sheets primary, JSON fallback)
# ============================================

def save_itinerary(destination: str, days: int, itinerary_data: Dict) -> bool:
    """
    Save a generated itinerary.
    Primary:  Append row to Google Sheets tab "Itineraries"
    Fallback: Append to data/itineraries.json
    """
    from datetime import datetime, timezone, timedelta
    ist_tz = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(ist_tz)
    key        = f"{destination.strip()}_{days}_{now.strftime('%Y%m%d_%H%M%S')}"
    created_at = now.strftime("%Y-%m-%d %H:%M:%S")
    prefs      = itinerary_data.get("preferences", [])
    prefs_str  = ", ".join(prefs) if isinstance(prefs, list) else str(prefs)

    # ── Google Sheets ─────────────────────────
    if _sheets_available():
        try:
            ws = _get_worksheet("Itineraries")
            if ws is None:
                raise ValueError("Worksheet not found")

            if ws.row_count <= 1 and not ws.get_all_values():
                ws.append_row(ITINERARY_COLUMNS)

            ws.append_row([
                key,
                destination.strip(),
                int(days),
                itinerary_data.get("trip_type", ""),
                prefs_str,
                itinerary_data.get("itinerary", ""),
                created_at,
            ])
            return True
        except Exception as e:
            log.error("save_itinerary (Sheets) failed: %s — falling back to JSON", e)

    # ── JSON fallback ─────────────────────────
    try:
        ensure_data_directory()
        itin_file = os.path.join(DATA_DIR, "itineraries.json")
        try:
            with open(itin_file, "r", encoding="utf-8") as f:
                itineraries = json.load(f)
        except Exception:
            itineraries = {}

        itineraries[key] = {
            **itinerary_data,
            "destination": destination.strip(),
            "days":        int(days),
            "created_at":  created_at,
        }
        with open(itin_file, "w", encoding="utf-8") as f:
            json.dump(itineraries, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        log.error("save_itinerary (JSON fallback) failed: %s", e)
        return False


def get_saved_itineraries(limit: int = 10) -> List[Dict]:
    """Load recent saved itineraries (Sheets primary, JSON fallback)."""
    if _sheets_available():
        try:
            ws      = _get_worksheet("Itineraries")
            if ws is None:
                raise ValueError("Worksheet not found")
            records = ws.get_all_records()
            if not records:
                return []
            items = sorted(records, key=lambda x: x.get("created_at",""), reverse=True)
            return items[:limit]
        except Exception as e:
            log.error("get_saved_itineraries (Sheets) failed: %s", e)

    try:
        itin_file = os.path.join(DATA_DIR, "itineraries.json")
        if not os.path.exists(itin_file):
            return []
        with open(itin_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        items = [{"key": k, **v} for k, v in data.items() if "created_at" in v]
        return sorted(items, key=lambda x: x["created_at"], reverse=True)[:limit]
    except Exception:
        return []


# ============================================
# STATISTICS
# ============================================

def get_review_statistics() -> Dict:
    df = load_reviews()
    if df.empty:
        return {
            "total_reviews":  0,
            "average_rating": 0,
            "total_places":   0,
            "top_rated":      None,
            "most_reviewed":  None,
        }
    stats = (
        df.groupby("place")["rating"]
        .agg(["mean", "count"])
        .reset_index()
        .rename(columns={"mean": "avg", "count": "cnt"})
    )
    return {
        "total_reviews":  len(df),
        "average_rating": round(float(df["rating"].mean()), 2),
        "total_places":   df["place"].nunique(),
        "top_rated": {
            "place":  stats.sort_values("avg",  ascending=False).iloc[0]["place"],
            "rating": round(float(stats.sort_values("avg", ascending=False).iloc[0]["avg"]), 2),
        },
        "most_reviewed": {
            "place": stats.sort_values("cnt", ascending=False).iloc[0]["place"],
            "count": int(stats.sort_values("cnt", ascending=False).iloc[0]["cnt"]),
        },
    }


def get_popular_destinations(limit: int = 5) -> List[Tuple[str, int]]:
    df = load_reviews()
    if df.empty:
        return []
    return list(df["place"].value_counts().head(limit).items())


# ============================================
# PEAK HOURS  (static CSV — in repo)
# ============================================

@st.cache_data(ttl=600)
def load_peak_hours() -> pd.DataFrame:
    ensure_data_directory()
    if not os.path.exists(PEAK_FILE):
        return pd.DataFrame()
    df = _read_csv_safe(PEAK_FILE)
    if "place" not in df.columns:
        log.error("'place' column missing in %s", PEAK_FILE)
        return pd.DataFrame()
    return df


def get_place_peak_hours(place: str) -> Optional[Dict]:
    df = load_peak_hours()
    if df.empty or "place" not in df.columns:
        return None
    exact = df[df["place"].str.lower() == place.lower()]
    if not exact.empty:
        return exact.iloc[0].to_dict()
    partial = df[df["place"].str.lower().str.contains(place.lower(), na=False, regex=False)]
    if not partial.empty:
        return partial.iloc[0].to_dict()
    return None


# ============================================
# PLACES  (static CSV — in repo)
# ============================================

@st.cache_data(ttl=3600)
def load_places() -> pd.DataFrame:
    if not os.path.exists(PLACES_FILE):
        return pd.DataFrame()
    return _read_csv_safe(PLACES_FILE)


def search_places(
    city: str          = None,
    state: str         = None,
    activity_type: str = None,
    keyword: str       = None,
) -> pd.DataFrame:
    df = load_places()
    if df.empty:
        return df
    if city:
        df = df[df["city"].str.lower().str.contains(city.strip().lower(), na=False, regex=False)]
    if state:
        df = df[df["state"].str.lower().str.contains(state.strip().lower(), na=False, regex=False)]
    if activity_type:
        df = df[df["activity_type"].str.lower().str.contains(activity_type.strip().lower(), na=False, regex=False)]
    if keyword:
        kw   = keyword.strip().lower()
        mask = (
            df["place_name"].str.lower().str.contains(kw, na=False, regex=False) |
            df["description_keyword"].str.lower().str.contains(kw, na=False, regex=False)
        )
        df = df[mask]
    return df.reset_index(drop=True)
"""
API Handler Functions — TourMind
Handles Unsplash, OpenWeatherMap, Wikipedia APIs
Improvements: retry logic, specific error handling,
              deprecated URL fixes, richer responses
"""

import time
import requests
import streamlit as st
import wikipediaapi
from typing import Optional, Dict, List
from config import *


# ============================================
# INTERNAL HELPER — RETRY REQUEST
# ============================================

def _get_with_retry(
    url: str,
    params: dict = None,
    headers: dict = None,
    retries: int = 2,
    timeout: int = 10,
    backoff: float = 0.6
) -> Optional[requests.Response]:
    """
    GET request with automatic retry + exponential backoff.
    Returns Response on success, None on all failures.
    """
    for attempt in range(retries + 1):
        try:
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=timeout
            )
            if response.status_code == 200:
                return response
            # 429 = rate limited — wait longer before retry
            if response.status_code == 429:
                time.sleep(backoff * (attempt + 2))
            elif response.status_code >= 500:
                time.sleep(backoff * (attempt + 1))
            else:
                # 4xx client error — no point retrying
                return None
        except requests.exceptions.Timeout:
            if attempt < retries:
                time.sleep(backoff)
        except requests.exceptions.ConnectionError:
            if attempt < retries:
                time.sleep(backoff * (attempt + 1))
        except requests.exceptions.RequestException:
            return None
    return None


# ============================================
# UNSPLASH API
# ============================================

# ── Curated activity-type fallback search terms ──────────────
# When a specific place name returns no results, we fall back
# to a generic landscape image matching the place's category.
_ACTIVITY_FALLBACKS = {
    "historical":  ["ancient fort india", "historical monument india", "heritage architecture india"],
    "forts":       ["indian fort architecture", "maratha fort", "hilltop fort india"],
    "religious":   ["hindu temple india", "temple architecture india", "indian shrine"],
    "spiritual":   ["spiritual temple india", "pilgrimage india", "sacred place india"],
    "nature":      ["india nature landscape", "scenic india outdoors", "green hills india"],
    "adventure":   ["adventure tourism india", "paragliding india", "trekking india mountains"],
    "cultural":    ["indian culture heritage", "india cultural festival", "traditional india"],
    "shopping":    ["india bazaar market", "colorful market india", "shopping street india"],
    "food":        ["indian street food", "india food market", "traditional indian cuisine"],
    "city":        ["pune city india", "india urban cityscape", "modern india city"],
    "camping":     ["camping nature india", "lakeside camping india", "outdoor camping"],
    "mountains":   ["western ghats india", "india hill station", "mountain landscape india"],
    "wildlife":    ["indian wildlife sanctuary", "india nature wildlife", "indian animals"],
    "sports":      ["cricket stadium india", "sports india", "india sports ground"],
    "family":      ["india family tourism", "garden park india", "india attraction"],
    "mall":        ["india shopping mall", "modern mall india", "retail india"],
    "water park":  ["water park india", "amusement water slides", "fun water park"],
}

_CITY_FALLBACKS = {
    "pune":     ["pune india", "pune city maharashtra", "pune landmark"],
    "mumbai":   ["mumbai india", "mumbai gateway", "mumbai cityscape"],
    "goa":      ["goa beach india", "goa tourism", "goa coastal"],
    "jaipur":   ["jaipur rajasthan india", "jaipur pink city", "jaipur palace"],
    "delhi":    ["delhi india monument", "new delhi tourism", "india gate delhi"],
    "agra":     ["agra taj mahal", "agra india tourism"],
    "kerala":   ["kerala backwaters india", "kerala nature tourism"],
}


def _unsplash_fallback(query: str, count: int = 1,
                        activity: str = None, city: str = None) -> List[Dict]:
    """
    Last-resort fallback using Wikipedia Commons public domain travel images.
    Only reached when Wikipedia page search also returns nothing.
    """
    import hashlib
    # Wikipedia Commons public-domain travel images
    placeholders = [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9d/India_Gate_in_New_Delhi_03-2016.jpg/960px-India_Gate_in_New_Delhi_03-2016.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bd/Taj_Mahal%2C_Agra%2C_India_edit3.jpg/960px-Taj_Mahal%2C_Agra%2C_India_edit3.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Rotating_earth_%28large%29.gif/200px-Rotating_earth_%28large%29.gif",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/24701-nature-natural-beauty.jpg/960px-24701-nature-natural-beauty.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/280px-PNG_transparency_demonstration_1.png",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Bihu_dance_in_Assam.jpg/960px-Bihu_dance_in_Assam.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/480px-No_image_available.svg.png",
    ]

    seed_hash = hashlib.md5(query.lower().strip().encode("utf-8")).hexdigest()
    seed = int(seed_hash, 16) % len(placeholders)

    return [
        {
            "url": placeholders[(seed + i) % len(placeholders)],
            "alt": f"Travel destination {i+1}",
            "photographer": "Wikipedia Commons",
            "photographer_url": "https://commons.wikimedia.org"
        }
        for i in range(count)
    ]



def get_wikipedia_images_robust(query: str, count: int = 3) -> List[Dict]:
    """
    Search Wikipedia for matching pages, score them based on overlap with the query,
    sort by score, and retrieve their main thumbnails.
    """
    import re
    search_url = "https://en.wikipedia.org/w/api.php"
    search_params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "srlimit": count * 3
    }
    headers = {"User-Agent": WIKI_USER_AGENT}
    
    try:
        response = _get_with_retry(search_url, params=search_params, headers=headers)
        if not response:
            return []
            
        results = response.json().get("query", {}).get("search", [])
        if not results:
            return []
        
        # Clean and tokenize query
        noise_words = {
            "temple", "fort", "market", "peth", "pune", "mumbai", "india", 
            "tourist", "attraction", "historical", "monument", "lake", "garden", 
            "park", "museum", "palace", "caves", "hill", "of", "and", "the", "in"
        }
        
        def tokenize(text):
            text = text.lower()
            text = re.sub(r'ganpati|ganapathi', 'ganapati', text)
            words = re.findall(r'[a-z0-9]+', text)
            return [w for w in words if w not in noise_words]
        
        query_tokens = tokenize(query)
        if not query_tokens:
            query_tokens = re.findall(r'[a-z0-9]+', query.lower())
            
        scored_pages = []
        for r_item in results:
            title = r_item["title"]
            title_tokens = tokenize(title)
            
            # Score overlap
            overlap = set(query_tokens).intersection(set(title_tokens))
            score = len(overlap)
            
            # Start word bonus
            if query_tokens and title_tokens and query_tokens[0] == title_tokens[0]:
                score += 0.5
                
            # Title length penalty
            score -= len(title_tokens) * 0.05
            
            scored_pages.append((score, title))
            
        scored_pages.sort(key=lambda x: x[0], reverse=True)
        top_titles = [title for _, title in scored_pages]
        
        if not top_titles:
            return []
            
        # Get thumbnails
        img_params = {
            "action": "query",
            "prop": "pageimages",
            "format": "json",
            "piprop": "thumbnail",
            "pithumbsize": 800,
            "titles": "|".join(top_titles[:count * 2]),
            "redirects": 1,
        }
        r_img = _get_with_retry(search_url, params=img_params, headers=headers)
        if not r_img:
            return []
            
        pages = r_img.json().get("query", {}).get("pages", {})
        title_to_img = {}
        for pid, pinfo in pages.items():
            t = pinfo.get("title")
            img_url = pinfo.get("thumbnail", {}).get("source")
            if img_url:
                title_to_img[t] = {
                    "url": img_url,
                    "title": t
                }
                
        images = []
        for t in top_titles:
            if t in title_to_img:
                images.append(title_to_img[t])
                if len(images) >= count:
                    break
                    
        return images
    except Exception:
        return []


def _wikipedia_image_fallback(query: str, count: int = 1) -> List[Dict]:
    """
    Fallback using Wikipedia page images, with a secondary fallback to static placeholders.
    """
    wiki_images = get_wikipedia_images_robust(query, count)
    
    formatted_images = []
    for img in wiki_images:
        title = img["title"]
        url = img["url"]
        formatted_images.append({
            "url":              url,
            "thumb":            url,
            "alt":              f"Wikipedia image for {title}",
            "photographer":     "Wikipedia Contributors",
            "photographer_url": f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}",
            "unsplash_link":    f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}",
            "query_used":       title,
        })
        
    if len(formatted_images) >= count:
        return formatted_images[:count]
        
    needed = count - len(formatted_images)
    placeholders = _unsplash_fallback(query, needed)
    formatted_images.extend(placeholders)
    return formatted_images[:count]


def _build_search_variations(place_name: str,
                               activity_type: str = None,
                               city: str = None) -> List[str]:
    """
    Build a smart, ordered list of search queries for a place name.
    """
    variations = []
    name = place_name.strip()

    # Remove qualifiers like "(Near Pune)", "(Lonavala)" etc.
    import re
    clean_name = re.sub(r"\s*[(][^)]*[)]", "", name).strip()

    # 1. Exact name
    variations.append(name)

    # 2. Clean name
    if clean_name != name:
        variations.append(clean_name)

    # 3. Clean name + city
    if city:
        city_l = city.lower()
        if city_l not in clean_name.lower():
            variations.append(f"{clean_name} {city_l}")
        
        # City-only fallback terms
        for c_key, c_terms in _CITY_FALLBACKS.items():
            if c_key in city_l:
                variations.extend(c_terms[:2])
                break

    # 4. Activity-type generic terms
    if activity_type:
        act_l = activity_type.lower()
        for a_key, a_terms in _ACTIVITY_FALLBACKS.items():
            if a_key in act_l:
                variations.extend(a_terms[:2])
                break

    # 5. Last resort generic fallback
    variations.append(f"{clean_name} landmark travel")

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for v in variations:
        if v not in seen:
            seen.add(v)
            unique.append(v)
    return unique


@st.cache_data(ttl=86400)  # 24 hours
def get_unsplash_image(query: str, count: int = 1,
                        activity_type: str = None,
                        city: str = None) -> List[Dict]:
    """
    Fetch images — always uses Wikipedia for accurate, place-specific images.
    Unsplash is bypassed to avoid random/incorrect images on free-tier rate limits.
    """
    return _wikipedia_image_fallback(query, count)



# ============================================
# WIKIPEDIA API
# ============================================

@st.cache_data(ttl=604800)  # 7 days — Wikipedia content rarely changes
def get_wikipedia_summary(
    place_name: str,
    max_chars: int = 600
) -> Optional[Dict]:
    """
    Fetch Wikipedia summary with auto-disambiguation fallback.
    Tries the exact name first, then appends context words on failure.
    """
    try:
        wiki = wikipediaapi.Wikipedia(
            user_agent=WIKI_USER_AGENT,
            language=WIKI_LANGUAGE
        )

        # Try variations if exact match fails
        attempts = [
            place_name,
            f"{place_name} (city)",
            f"{place_name} (India)",
            f"{place_name} tourist attraction",
        ]

        for attempt in attempts:
            page = wiki.page(attempt)
            if page.exists() and len(page.summary.strip()) > 50:
                summary = page.summary
                if len(summary) > max_chars:
                    # Cut at sentence boundary
                    trimmed = summary[:max_chars]
                    last_dot = trimmed.rfind(".")
                    summary = trimmed[:last_dot + 1] if last_dot > 0 else trimmed + "…"

                return {
                    "title":   page.title,
                    "summary": summary,
                    "url":     page.fullurl,
                    "exists":  True,
                }

        return {
            "title":   place_name,
            "summary": f"No detailed Wikipedia article found for '{place_name}'.",
            "url":     None,
            "exists":  False,
        }

    except Exception as e:
        return {
            "title":   place_name,
            "summary": "Wikipedia information is temporarily unavailable.",
            "url":     None,
            "exists":  False,
            "error":   str(e),
        }


@st.cache_data(ttl=CACHE_TTL_LONG)
def search_wikipedia_places(query: str, max_results: int = 10) -> List[str]:
    """Search Wikipedia for place names matching a query."""
    try:
        import wikipedia
        wikipedia.set_lang(WIKI_LANGUAGE)
        return wikipedia.search(query, results=max_results)
    except Exception:
        return []


# ============================================
# OPENWEATHERMAP API
# ============================================

@st.cache_data(ttl=CACHE_TTL_SHORT)
def get_weather_forecast(city: str, days: int = 5) -> Optional[Dict]:
    """
    Fetch current weather + multi-day forecast.
    Returns structured dict or None on failure.
    """
    if not OPENWEATHER_API_KEY or OPENWEATHER_API_KEY == "YOUR_OPENWEATHER_API_KEY":
        return None

    base_params = {
        "q":     city,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
    }

    # ── Current weather ──────────────────────
    current_resp = _get_with_retry(
        f"{OPENWEATHER_API_URL}/weather",
        params=base_params,
    )

    if not current_resp:
        return None

    current_data = current_resp.json()

    # ── Forecast ─────────────────────────────
    forecast_resp = _get_with_retry(
        f"{OPENWEATHER_API_URL}/forecast",
        params={**base_params, "cnt": min(days * 8, 40)},
    )

    # Build current conditions
    weather_main = current_data["weather"][0]
    current = {
        "temp":        round(current_data["main"]["temp"], 1),
        "feels_like":  round(current_data["main"]["feels_like"], 1),
        "description": weather_main["description"].capitalize(),
        "humidity":    current_data["main"]["humidity"],
        "wind_speed":  round(current_data["wind"]["speed"], 1),
        "icon":        weather_main["icon"],
        "icon_url":    get_weather_icon_url(weather_main["icon"]),
        "city":        current_data["name"],
        "country":     current_data["sys"].get("country", ""),
        "visibility":  round(current_data.get("visibility", 0) / 1000, 1),  # km
    }

    # Build daily forecast
    daily_forecast: List[Dict] = []
    seen_dates: set = set()

    if forecast_resp:
        for item in forecast_resp.json().get("list", []):
            date = item["dt_txt"].split()[0]
            if date in seen_dates:
                continue
            seen_dates.add(date)

            fw = item["weather"][0]
            daily_forecast.append({
                "date":        date,
                "temp_max":    round(item["main"]["temp_max"], 1),
                "temp_min":    round(item["main"]["temp_min"], 1),
                "description": fw["description"].capitalize(),
                "icon":        fw["icon"],
                "icon_url":    get_weather_icon_url(fw["icon"]),
                "humidity":    item["main"]["humidity"],
                "wind_speed":  round(item["wind"]["speed"], 1),
            })

            if len(daily_forecast) >= days:
                break

    return {
        "current":  current,
        "forecast": daily_forecast,
        "success":  True,
    }


# ============================================
# CHATBOT FALLBACK (Rule-based)
# ============================================

def get_chatbot_response(user_message: str) -> str:
    """
    Rule-based chatbot fallback when OpenAI is unavailable.
    Matches keywords defined in config.CHATBOT_KEYWORDS.
    """
    message_lower = user_message.lower().strip()

    # Longest-match first to avoid partial keyword collisions
    matched = None
    matched_len = 0
    for keyword, response in CHATBOT_KEYWORDS.items():
        if keyword in message_lower and len(keyword) > matched_len:
            matched = response
            matched_len = len(keyword)

    return matched if matched else DEFAULT_CHATBOT_RESPONSE


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_weather_icon_url(icon_code: str) -> str:
    """Return HTTPS URL for an OpenWeatherMap icon (2x resolution)."""
    return f"https://openweathermap.org/img/wn/{icon_code}@2x.png"


def format_temperature(temp: float, unit: str = "C") -> str:
    """Format temperature with degree symbol."""
    return f"{round(temp, 1)}°{unit}"


def get_google_maps_url(place_name: str) -> str:
    """Build a Google Maps search URL for a place name."""
    query = requests.utils.quote(place_name)
    return f"https://www.google.com/maps/search/?api=1&query={query}"


def check_api_health() -> Dict[str, bool]:
    """
    Quick health check — verifies API keys are non-default.
    Does NOT make live calls (avoids wasting quota on startup).
    """
    return {
        "unsplash":     bool(UNSPLASH_ACCESS_KEY)    and UNSPLASH_ACCESS_KEY    != "YOUR_UNSPLASH_ACCESS_KEY",
        "openweather":  bool(OPENWEATHER_API_KEY)    and OPENWEATHER_API_KEY    != "YOUR_OPENWEATHER_API_KEY",
        "wikipedia":    True,   # No key needed
    }
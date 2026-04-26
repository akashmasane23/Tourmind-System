"""
TourMind AI — ML Service (Runtime Layer)
==========================================
Singleton that loads trained models once and exposes two methods:

  ml_service.predict_crowd_ml(...)   → crowd level + confidence
  ml_service.rank_places_ml(...)     → places sorted by ML score

Design principles:
  - Eager loading at import time — models loaded once when singleton is created
  - Graceful fallback — if models missing, returns None / unchanged list
  - No crash — all errors are caught; rule-based system takes over
  - Simple & explainable — no hidden magic, easy to describe in interviews

Interview talking point:
  "We trained two Random Forest models on synthetic data generated from
   our own rule engine. The crowd model uses the rule-based score as a
   feature, so it learns the same patterns plus additional interactions.
   The ranking model learns from distance, rating, user preference match,
   and time-of-day relevance. Both models are loaded once at startup and
   used as enhancement layers — the original logic stays intact as a fallback."
"""

import os
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

# ── model file paths ────────────────────────────────────────────────────────
_BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MODELS_DIR  = os.path.join(_BASE_DIR, "models")

_CROWD_MODEL_PATH   = os.path.join(_MODELS_DIR, "crowd_rf_model.joblib")
_ENCODER_PATH       = os.path.join(_MODELS_DIR, "crowd_label_encoder.joblib")
_RANKING_MODEL_PATH = os.path.join(_MODELS_DIR, "ranking_rf_model.joblib")

# Activity types and their peak hour windows (mirrors ml_model.py)
_ACTIVITY_HOURS: dict[str, tuple[int, int]] = {
    "nature":      (6,  18),
    "historical":  (9,  17),
    "religious":   (5,  21),
    "adventure":   (8,  16),
    "shopping":    (10, 21),
    "food":        (10, 22),
    "cultural":    (10, 19),
    "forts":       (7,  17),
    "mountains":   (6,  16),
    "camping":     (6,  20),
    "family":      (9,  20),
    "city":        (10, 22),
    "sports":      (6,  20),
    "spiritual":   (5,  20),
}


def _hour_relevance(activity_type: str, hour: int) -> float:
    lo, hi = _ACTIVITY_HOURS.get(str(activity_type).lower(), (8, 20))
    if hour < lo or hour > hi:
        return 0.1
    mid  = (lo + hi) / 2
    dist = abs(hour - mid) / ((hi - lo) / 2 + 1e-6)
    return round(max(0.1, 1.0 - dist * 0.6), 3)


# ============================================================
# ML SERVICE CLASS
# ============================================================

class MLService:
    """
    Lazy-loading ML service for TourMind AI.

    Usage:
        from services.ml_service import ml_service

        result = ml_service.predict_crowd_ml(hour=14, weekday=5,
                     is_holiday=0, weather_factor=1.0, rule_score=1.68)
        # → {"ml_prediction": "High", "confidence": 0.82}

        places = ml_service.rank_places_ml(places, user_hour=14,
                     user_preference="nature")
        # → same list with "ml_score" added, sorted descending
    """

    def __init__(self):
        self._crowd_model   = None
        self._label_encoder = None
        self._ranking_model = None

        self.crowd_model_loaded   = False
        self.ranking_model_loaded = False

        self._load_models()

    # ── private loader ───────────────────────────────────────

    def _load_models(self):
        """Try to load all joblib models. Silently skip if files missing."""
        try:
            import joblib
        except ImportError:
            logger.warning("joblib not installed — ML features disabled.")
            return

        # Crowd model
        if os.path.exists(_CROWD_MODEL_PATH) and os.path.exists(_ENCODER_PATH):
            try:
                self._crowd_model   = joblib.load(_CROWD_MODEL_PATH)
                self._label_encoder = joblib.load(_ENCODER_PATH)
                self.crowd_model_loaded = True
                logger.info("✅ Crowd ML model loaded.")
            except Exception as e:
                logger.warning(f"Could not load crowd model: {e}")

        # Ranking model
        if os.path.exists(_RANKING_MODEL_PATH):
            try:
                self._ranking_model  = joblib.load(_RANKING_MODEL_PATH)
                self.ranking_model_loaded = True
                logger.info("✅ Ranking ML model loaded.")
            except Exception as e:
                logger.warning(f"Could not load ranking model: {e}")

    # ── public API ───────────────────────────────────────────

    def predict_crowd_ml(
        self,
        hour: int,
        weekday: int,
        is_holiday: int,
        weather_factor: float,
        rule_score: float,
    ) -> Optional[dict]:
        """
        Predict crowd level using the trained RandomForest classifier.

        Args:
            hour           : 0–23
            weekday        : 0=Monday … 6=Sunday
            is_holiday     : 0 or 1
            weather_factor : 0.5–1.2 (from realtime_crowd.py)
            rule_score     : the raw score from existing rule engine

        Returns:
            {"ml_prediction": str, "confidence": float}
            or None if model not loaded (caller falls back to rule-based)
        """
        if not self.crowd_model_loaded:
            return None

        try:
            import pandas as pd
            X = pd.DataFrame([{
                "hour":           hour,
                "weekday":        weekday,
                "is_holiday":     is_holiday,
                "weather_factor": weather_factor,
                "rule_score":     rule_score,
            }])
            pred_enc   = self._crowd_model.predict(X)[0]
            proba      = self._crowd_model.predict_proba(X)[0]
            confidence = round(float(proba.max()), 3)
            label      = self._label_encoder.inverse_transform([pred_enc])[0]

            return {
                "ml_prediction": label,
                "confidence":    confidence,
            }
        except Exception as e:
            logger.warning(f"Crowd ML prediction failed: {e}")
            return None

    def get_crowd_feature_importance(self) -> dict:
        """
        Get feature importances from the trained crowd RandomForest model.
        Returns a dictionary mapping feature names to their importance scores.
        """
        if not self.crowd_model_loaded or self._crowd_model is None:
            return {}
        try:
            importances = self._crowd_model.feature_importances_
            features = ["hour", "weekday", "is_holiday", "weather_factor", "rule_score"]
            if len(importances) == len(features):
                return dict(zip(features, importances))
            return {}
        except Exception as e:
            logger.warning(f"Failed to get feature importances: {e}")
            return {}

    def rank_places_ml(
        self,
        places: list[dict],
        user_hour: Optional[int] = None,
        user_preference: str = "",
    ) -> list[dict]:
        """
        Add 'ml_score' to each place and return sorted list (best first).

        Falls back to distance-only sort if ranking model not loaded.

        Args:
            places          : list of place dicts from get_nearby_attractions()
            user_hour       : hour of day (0–23); defaults to current hour
            user_preference : user-selected activity type (e.g. "nature")

        Returns:
            Same list with 'ml_score' (float 0–1) added, sorted descending.
        """
        if user_hour is None:
            from datetime import timezone as _tz, timedelta as _td
            _ist = _tz(_td(hours=5, minutes=30))
            user_hour = datetime.now(_ist).hour

        user_pref = (user_preference or "").strip().lower()

        # Guard: nothing to rank
        if not places:
            return places

        # If model missing → add default ml_score and sort by distance
        if not self.ranking_model_loaded:
            for p in places:
                p["ml_score"] = 0.0
            return sorted(places, key=lambda x: x.get("distance_km", 999))

        try:
            import numpy as np
            import pandas as pd

            rows = []
            for p in places:
                dist = float(p.get("distance_km", 5.0))

                # rating: handle "N/A" or missing
                raw_rating = p.get("rating", "N/A")
                try:
                    rating = float(raw_rating)
                    rating = max(1.0, min(5.0, rating))  # clamp to model training range
                except (ValueError, TypeError):
                    rating = 3.0  # neutral default

                activity_type  = str(p.get("activity", "")).strip().lower()
                activity_match = 1 if (user_pref and user_pref == activity_type) else 0
                hour_rel       = _hour_relevance(activity_type, user_hour)

                rows.append({
                    "distance_km":    dist,
                    "rating":         rating,
                    "activity_match": activity_match,
                    "hour_relevance": hour_rel,
                })

            X      = pd.DataFrame(rows)
            scores = self._ranking_model.predict(X)
            scores = np.clip(scores, 0.0, 1.0)

            for p, score in zip(places, scores):
                p["ml_score"] = round(float(score), 3)

            # Sort by ML score descending
            return sorted(places, key=lambda x: x.get("ml_score", 0.0), reverse=True)

        except Exception as e:
            logger.warning(f"ML ranking failed: {e}")
            for p in places:
                p.setdefault("ml_score", 0.0)
            return places


# ============================================================
# MODULE-LEVEL SINGLETON
# ============================================================

ml_service = MLService()

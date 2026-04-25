"""
TourMind AI — ML Model Training Script
========================================
Generates synthetic datasets and trains:
  1. RandomForestClassifier  → crowd level prediction
  2. RandomForestRegressor   → place ranking score

Run once from the project root:
    python models/ml_model.py

Outputs (saved to models/):
    crowd_rf_model.joblib
    crowd_label_encoder.joblib
    ranking_rf_model.joblib

Interview note:
    The crowd model uses our rule-based score as a FEATURE, not a
    replacement. This means the ML model learns the same patterns
    the rule engine knows, PLUS additional interactions between
    features that a simple multiply can't capture.
"""

import os
import random
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, mean_squared_error
import joblib

# ── paths ──────────────────────────────────────────────────────────────────
MODELS_DIR = os.path.dirname(os.path.abspath(__file__))
CROWD_MODEL_PATH    = os.path.join(MODELS_DIR, "crowd_rf_model.joblib")
ENCODER_PATH        = os.path.join(MODELS_DIR, "crowd_label_encoder.joblib")
RANKING_MODEL_PATH  = os.path.join(MODELS_DIR, "ranking_rf_model.joblib")


# ============================================================
# HELPERS — mirrors realtime_crowd.py scoring so the synthetic
# data is grounded in the same logic the app already uses.
# ============================================================

def _time_score(hour: int) -> float:
    if   0  <= hour <= 5:   return 0.2
    elif 6  <= hour <= 8:   return 0.5
    elif 9  <= hour <= 11:  return 0.9
    elif 12 <= hour <= 14:  return 1.2
    elif 15 <= hour <= 16:  return 1.0
    elif 17 <= hour <= 19:  return 1.5
    elif 20 <= hour <= 21:  return 1.3
    else:                   return 0.6


def _day_score(weekday: int, is_holiday: int) -> float:
    if is_holiday:  return 1.8
    if weekday == 6: return 1.6
    if weekday == 5: return 1.4
    if weekday == 4: return 1.1
    return 1.0


def _score_to_label(score: float) -> str:
    if   score < 1.2: return "Low"
    elif score < 2.2: return "Medium"
    elif score < 3.2: return "High"
    else:             return "Very High"


# ============================================================
# FEATURE 1 — CROWD DATASET
# ============================================================

def generate_crowd_dataset(n_samples: int = 3000, random_state: int = 42) -> pd.DataFrame:
    """
    Generate a synthetic crowd-level dataset.

    Each row represents one realistic observation.
    Noise is intentionally added (~10% label flip) so the ML model
    learns slightly more than the pure rule-engine — making the
    comparison between the two interesting.

    Columns:
        hour           int     0–23
        weekday        int     0–6
        is_holiday     int     0 or 1
        weather_factor float   0.5–1.2
        rule_score     float   time * day * weather  (existing logic)
        crowd_level    str     Low / Medium / High / Very High  (target)
    """
    rng = random.Random(random_state)
    np.random.seed(random_state)

    rows = []
    for _ in range(n_samples):
        hour       = rng.randint(0, 23)
        weekday    = rng.randint(0, 6)
        is_holiday = 1 if rng.random() < 0.10 else 0

        # Realistic weather factor distribution
        weather_factor = round(rng.choice([0.5, 0.7, 0.8, 1.0, 1.0, 1.0, 1.2]) +
                               np.random.normal(0, 0.05), 2)
        weather_factor = max(0.4, min(1.3, weather_factor))

        ts = _time_score(hour)
        ds = _day_score(weekday, is_holiday)
        rule_score = round(ts * ds * weather_factor, 3)

        label = _score_to_label(rule_score)

        # ── introduce ~10% noise so ML diverges slightly from rules ──
        if rng.random() < 0.10:
            choices = ["Low", "Medium", "High", "Very High"]
            choices.remove(label)
            label = rng.choice(choices)

        rows.append({
            "hour":           hour,
            "weekday":        weekday,
            "is_holiday":     is_holiday,
            "weather_factor": weather_factor,
            "rule_score":     rule_score,
            "crowd_level":    label,
        })

    return pd.DataFrame(rows)


def train_crowd_model(verbose: bool = True) -> dict:
    """
    Train a RandomForestClassifier for crowd level prediction.

    Returns a dict with evaluation metrics.
    """
    print("[Crowd Model] Generating dataset ...")
    df = generate_crowd_dataset()

    X = df[["hour", "weekday", "is_holiday", "weather_factor", "rule_score"]]
    y = df["crowd_level"]

    # Encode labels
    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.2, random_state=42, stratify=y_enc
    )

    print("[Crowd Model] Training RandomForestClassifier ...")
    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1,
    )
    clf.fit(X_train, y_train)

    # Evaluate
    y_pred = clf.predict(X_test)
    report = classification_report(y_test, y_pred,
                                   target_names=le.classes_,
                                   output_dict=True)
    acc = report["accuracy"]

    if verbose:
        print(f"[Crowd Model] Accuracy: {acc:.3f}")
        print(classification_report(y_test, y_pred, target_names=le.classes_))

    # Save
    joblib.dump(clf, CROWD_MODEL_PATH)
    joblib.dump(le,  ENCODER_PATH)
    print(f"[Crowd Model] Saved -> {CROWD_MODEL_PATH}")
    print(f"[Crowd Model] Encoder -> {ENCODER_PATH}")

    return {"accuracy": acc, "classes": list(le.classes_)}


# ============================================================
# FEATURE 2 — PLACE RANKING DATASET
# ============================================================

# Activity types and which hours they are most relevant
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
    """Return 0–1 score for how relevant an activity is at a given hour."""
    lo, hi = _ACTIVITY_HOURS.get(activity_type, (8, 20))
    if hour < lo or hour > hi:
        return 0.1
    # Peak relevance in the middle of the active window
    mid = (lo + hi) / 2
    dist = abs(hour - mid) / ((hi - lo) / 2 + 1e-6)
    return round(max(0.1, 1.0 - dist * 0.6), 3)


def generate_ranking_dataset(n_samples: int = 2000, random_state: int = 42) -> pd.DataFrame:
    """
    Generate a synthetic place-ranking dataset.

    Target: ml_score (0–1) representing "how good this recommendation is
    for the user right now". Higher = should rank first.

    Columns:
        distance_km      float  0.1–10
        rating           float  1.0–5.0 (N/A → 3.0 default)
        activity_match   int    1 if user preference matches place type
        hour_relevance   float  0–1
        ml_score         float  0–1  (target)
    """
    rng = random.Random(random_state)
    np.random.seed(random_state)

    activity_types = list(_ACTIVITY_HOURS.keys())

    rows = []
    for _ in range(n_samples):
        distance_km    = round(rng.uniform(0.1, 10.0), 2)
        rating         = round(rng.uniform(2.5, 5.0), 1)
        activity_type  = rng.choice(activity_types)
        hour           = rng.randint(0, 23)
        activity_match = rng.choice([0, 1])
        hour_rel       = _hour_relevance(activity_type, hour)

        # Ground-truth score formula (weighted)
        base_score = (
            0.35 * max(0, 1 - distance_km / 10) +  # closer is better
            0.30 * ((rating - 1) / 4) +             # higher rating is better
            0.20 * activity_match +                  # pref match bonus
            0.15 * hour_rel                          # time relevance
        )
        # Add small noise
        noise = np.random.normal(0, 0.04)
        ml_score = round(min(1.0, max(0.0, base_score + noise)), 3)

        rows.append({
            "distance_km":    distance_km,
            "rating":         rating,
            "activity_match": activity_match,
            "hour_relevance": hour_rel,
            "ml_score":       ml_score,
        })

    return pd.DataFrame(rows)


def train_ranking_model(verbose: bool = True) -> dict:
    """
    Train a RandomForestRegressor for place ranking.

    Returns evaluation metrics dict.
    """
    print("[Ranking Model] Generating dataset ...")
    df = generate_ranking_dataset()

    X = df[["distance_km", "rating", "activity_match", "hour_relevance"]]
    y = df["ml_score"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print("[Ranking Model] Training RandomForestRegressor ...")
    reg = RandomForestRegressor(
        n_estimators=100,
        max_depth=8,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1,
    )
    reg.fit(X_train, y_train)

    y_pred = reg.predict(X_test)
    rmse   = float(np.sqrt(mean_squared_error(y_test, y_pred)))

    if verbose:
        print(f"[Ranking Model] RMSE: {rmse:.4f}")

    joblib.dump(reg, RANKING_MODEL_PATH)
    print(f"[Ranking Model] Saved -> {RANKING_MODEL_PATH}")

    return {"rmse": rmse}


# ============================================================
# ENTRY POINT — run from project root:
#   python models/ml_model.py
# ============================================================

if __name__ == "__main__":
    print("=" * 55)
    print("  TourMind AI — ML Model Training")
    print("=" * 55)

    crowd_metrics   = train_crowd_model(verbose=True)
    ranking_metrics = train_ranking_model(verbose=True)

    print()
    print("=" * 55)
    print("  Training Complete")
    print(f"  Crowd   accuracy : {crowd_metrics['accuracy']:.3f}")
    print(f"  Ranking RMSE     : {ranking_metrics['rmse']:.4f}")
    print("=" * 55)

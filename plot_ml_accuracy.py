"""
TourMind AI — ML Model Accuracy & Loss Curves
==============================================
Generates Training vs Validation Accuracy and Loss graphs
for both Random Forest models (Crowd Classifier + Place Ranking).

Simulates "epochs" by incrementally increasing n_estimators (1 → 100),
recording train/val metrics at each step — similar to deep learning curves.

Run:
    python plot_ml_accuracy.py
    
Outputs:
    crowd_model_accuracy.png
    ranking_model_accuracy.png
"""

import os
import sys
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib import rcParams

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, log_loss, mean_squared_error

# ── Plot style ────────────────────────────────────────────────
rcParams['font.family'] = 'DejaVu Sans'
rcParams['axes.spines.top'] = False
rcParams['axes.spines.right'] = False
TRAIN_COLOR = '#4A90D9'   # Blue
VAL_COLOR   = '#E8954A'   # Orange

# ============================================================
# HELPERS — copied from models/ml_model.py
# ============================================================

def _time_score(hour):
    if   0  <= hour <= 5:  return 0.2
    elif 6  <= hour <= 8:  return 0.5
    elif 9  <= hour <= 11: return 0.9
    elif 12 <= hour <= 14: return 1.2
    elif 15 <= hour <= 16: return 1.0
    elif 17 <= hour <= 19: return 1.5
    elif 20 <= hour <= 21: return 1.3
    else:                  return 0.6

def _day_score(weekday, is_holiday):
    if is_holiday: return 1.8
    if weekday == 6: return 1.6
    if weekday == 5: return 1.4
    if weekday == 4: return 1.1
    return 1.0

def _score_to_label(score):
    if   score < 1.2: return "Low"
    elif score < 2.2: return "Medium"
    elif score < 3.2: return "High"
    else:             return "Very High"

_ACTIVITY_HOURS = {
    "nature": (6, 18), "historical": (9, 17), "religious": (5, 21),
    "adventure": (8, 16), "shopping": (10, 21), "food": (10, 22),
    "cultural": (10, 19), "forts": (7, 17), "mountains": (6, 16),
    "camping": (6, 20), "family": (9, 20), "city": (10, 22),
    "sports": (6, 20), "spiritual": (5, 20),
}

def _hour_relevance(activity_type, hour):
    lo, hi = _ACTIVITY_HOURS.get(activity_type, (8, 20))
    if hour < lo or hour > hi: return 0.1
    mid  = (lo + hi) / 2
    dist = abs(hour - mid) / ((hi - lo) / 2 + 1e-6)
    return round(max(0.1, 1.0 - dist * 0.6), 3)


# ============================================================
# DATASET GENERATION
# ============================================================

def generate_crowd_dataset(n=3000, seed=42):
    rng = random.Random(seed)
    np.random.seed(seed)
    rows = []
    for _ in range(n):
        hour       = rng.randint(0, 23)
        weekday    = rng.randint(0, 6)
        is_holiday = 1 if rng.random() < 0.10 else 0
        wf = round(rng.choice([0.5,0.7,0.8,1.0,1.0,1.0,1.2]) + np.random.normal(0,0.05), 2)
        wf = max(0.4, min(1.3, wf))
        rule_score = round(_time_score(hour) * _day_score(weekday, is_holiday) * wf, 3)
        label = _score_to_label(rule_score)
        if rng.random() < 0.10:
            choices = ["Low","Medium","High","Very High"]; choices.remove(label)
            label = rng.choice(choices)
        rows.append({"hour":hour,"weekday":weekday,"is_holiday":is_holiday,
                     "weather_factor":wf,"rule_score":rule_score,"crowd_level":label})
    return pd.DataFrame(rows)

def generate_ranking_dataset(n=2000, seed=42):
    rng = random.Random(seed)
    np.random.seed(seed)
    acts = list(_ACTIVITY_HOURS.keys())
    rows = []
    for _ in range(n):
        dist   = round(rng.uniform(0.1, 10.0), 2)
        rating = round(rng.uniform(2.5, 5.0), 1)
        act    = rng.choice(acts)
        hour   = rng.randint(0, 23)
        am     = rng.choice([0,1])
        hr     = _hour_relevance(act, hour)
        score  = (0.35*max(0,1-dist/10) + 0.30*((rating-1)/4) + 0.20*am + 0.15*hr)
        score  = round(min(1.0, max(0.0, score + np.random.normal(0,0.04))), 3)
        rows.append({"distance_km":dist,"rating":rating,"activity_match":am,
                     "hour_relevance":hr,"ml_score":score})
    return pd.DataFrame(rows)


# ============================================================
# INCREMENTAL TRAINING — simulates "epochs" via n_estimators
# ============================================================

def train_crowd_curves(estimator_steps):
    """Return (steps, train_acc, val_acc, train_loss, val_loss)."""
    print(">> Generating crowd dataset ...")
    df = generate_crowd_dataset()
    X  = df[["hour","weekday","is_holiday","weather_factor","rule_score"]].values
    le = LabelEncoder()
    y  = le.fit_transform(df["crowd_level"].values)
    X_tr, X_val, y_tr, y_val = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

    train_acc, val_acc, train_loss, val_loss = [], [], [], []
    n_classes = len(le.classes_)

    print(f"   Training over {len(estimator_steps)} steps ...")
    for n in estimator_steps:
        clf = RandomForestClassifier(
            n_estimators=n, max_depth=8, min_samples_leaf=5,
            random_state=42, n_jobs=-1, warm_start=False
        )
        clf.fit(X_tr, y_tr)

        # Train metrics
        p_tr = clf.predict_proba(X_tr)
        train_acc.append(accuracy_score(y_tr, clf.predict(X_tr)))
        train_loss.append(log_loss(y_tr, p_tr, labels=list(range(n_classes))))

        # Val metrics
        p_val = clf.predict_proba(X_val)
        val_acc.append(accuracy_score(y_val, clf.predict(X_val)))
        val_loss.append(log_loss(y_val, p_val, labels=list(range(n_classes))))

        if n % 20 == 0 or n == estimator_steps[-1]:
            print(f"   n_estimators={n:3d}  train_acc={train_acc[-1]:.4f}  val_acc={val_acc[-1]:.4f}")

    return estimator_steps, train_acc, val_acc, train_loss, val_loss, le.classes_


def train_ranking_curves(estimator_steps):
    """Return (steps, train_rmse, val_rmse)."""
    print("\n>> Generating ranking dataset ...")
    df = generate_ranking_dataset()
    X  = df[["distance_km","rating","activity_match","hour_relevance"]].values
    y  = df["ml_score"].values
    X_tr, X_val, y_tr, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    train_r2, val_r2, train_rmse, val_rmse = [], [], [], []

    print(f"   Training over {len(estimator_steps)} steps ...")
    for n in estimator_steps:
        reg = RandomForestRegressor(
            n_estimators=n, max_depth=8, min_samples_leaf=5,
            random_state=42, n_jobs=-1
        )
        reg.fit(X_tr, y_tr)

        p_tr  = reg.predict(X_tr)
        p_val = reg.predict(X_val)

        tr_rmse = float(np.sqrt(mean_squared_error(y_tr, p_tr)))
        vl_rmse = float(np.sqrt(mean_squared_error(y_val, p_val)))

        # Pseudo-accuracy: % predictions within ±0.1 of target
        tr_acc = np.mean(np.abs(p_tr  - y_tr)  <= 0.10)
        vl_acc = np.mean(np.abs(p_val - y_val) <= 0.10)

        train_r2.append(tr_acc);  val_r2.append(vl_acc)
        train_rmse.append(tr_rmse); val_rmse.append(vl_rmse)

        if n % 20 == 0 or n == estimator_steps[-1]:
            print(f"   n_estimators={n:3d}  train_acc~{tr_acc:.4f}  val_acc~{vl_acc:.4f}  val_rmse={vl_rmse:.4f}")

    return estimator_steps, train_r2, val_r2, train_rmse, val_rmse


# ============================================================
# PLOT FUNCTION
# ============================================================

def plot_curves(steps, train_acc, val_acc, train_loss, val_loss,
                title, acc_label="Accuracy", loss_label="Loss", out_file="curve.png"):
    fig = plt.figure(figsize=(13, 5), facecolor='white')
    fig.suptitle(title, fontsize=14, fontweight='bold', y=1.01, color='#222')
    gs  = gridspec.GridSpec(1, 2, figure=fig, wspace=0.35)

    # ── Accuracy subplot ─────────────────────────────────────
    ax1 = fig.add_subplot(gs[0])
    ax1.plot(steps, train_acc, color=TRAIN_COLOR, lw=2,   label='Train Accuracy')
    ax1.plot(steps, val_acc,   color=VAL_COLOR,   lw=2,   label='Val Accuracy')
    ax1.set_title(acc_label,   fontsize=13, fontweight='bold', pad=10)
    ax1.set_xlabel("n_estimators (trees)",   fontsize=10)
    ax1.set_ylabel(acc_label,  fontsize=10)
    ax1.legend(fontsize=9, framealpha=0.85)
    ax1.set_xlim(steps[0], steps[-1])
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.2f}"))
    ax1.grid(True, alpha=0.25, linestyle='--')
    ax1.tick_params(labelsize=9)

    # ── Loss subplot ─────────────────────────────────────────
    ax2 = fig.add_subplot(gs[1])
    ax2.plot(steps, train_loss, color=TRAIN_COLOR, lw=2, label='Train Loss')
    ax2.plot(steps, val_loss,   color=VAL_COLOR,   lw=2, label='Val Loss')
    ax2.set_title(loss_label,   fontsize=13, fontweight='bold', pad=10)
    ax2.set_xlabel("n_estimators (trees)", fontsize=10)
    ax2.set_ylabel(loss_label,  fontsize=10)
    ax2.legend(fontsize=9, framealpha=0.85)
    ax2.set_xlim(steps[0], steps[-1])
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.3f}"))
    ax2.grid(True, alpha=0.25, linestyle='--')
    ax2.tick_params(labelsize=9)

    plt.tight_layout()
    plt.savefig(out_file, dpi=150, bbox_inches='tight')
    print(f"\n[OK] Saved -> {out_file}")
    plt.show()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    # Use 40 evenly spaced steps from 5 → 100 trees
    STEPS = list(range(5, 101, 2))   # [5, 7, 9, ... 99, 101] → ~48 points

    print("=" * 55)
    print("  TourMind AI - ML Accuracy & Loss Curve Generator")
    print("=" * 55)

    # ── 1. Crowd Classifier ───────────────────────────────────
    steps, tr_a, vl_a, tr_l, vl_l, classes = train_crowd_curves(STEPS)

    final_val_acc = vl_a[-1]
    print(f"\nCrowd Model - Final Val Accuracy : {final_val_acc:.4f}")
    print(f"  Classes : {list(classes)}")

    plot_curves(
        steps, tr_a, vl_a, tr_l, vl_l,
        title      = "Crowd Level Prediction - Random Forest Classifier",
        acc_label  = "Accuracy",
        loss_label = "Log Loss",
        out_file   = os.path.join(os.path.dirname(__file__), "crowd_model_accuracy.png"),
    )

    # ── 2. Place Ranking Regressor ────────────────────────────
    steps, tr_a2, vl_a2, tr_rmse, vl_rmse = train_ranking_curves(STEPS)

    print(f"\nRanking Model - Final Val RMSE   : {vl_rmse[-1]:.4f}")
    print(f"  Final Val Accuracy (+/-0.10)     : {vl_a2[-1]:.4f}")

    plot_curves(
        steps, tr_a2, vl_a2, tr_rmse, vl_rmse,
        title      = "Place Ranking - Random Forest Regressor",
        acc_label  = "Accuracy (pred within +/-0.10)",
        loss_label = "RMSE",
        out_file   = os.path.join(os.path.dirname(__file__), "ranking_model_accuracy.png"),
    )

    print("\n" + "=" * 55)
    print("  Done! Two PNG graphs saved in the project folder.")
    print("=" * 55)

"""
STEP 3 — Train & Evaluate ML Model
=====================================
Reads: output/mi_batting_features.csv  (from step2)
Writes: models/mi_batting_model.pkl
Run: python step3_train_model.py
"""

import pandas as pd
import numpy as np
import os
import pickle

from sklearn.ensemble         import RandomForestClassifier
from sklearn.model_selection  import train_test_split, cross_val_score
from sklearn.preprocessing    import LabelEncoder
from sklearn.metrics          import classification_report, confusion_matrix

INPUT      = "output/mi_batting_features.csv"
MODEL_PATH = "models/mi_batting_model.pkl"

# Features used for training
FEATURE_COLS = [
    "batting_pos",
    "balls_faced",
    "strike_rate",
    "fours",
    "sixes",
    "boundary_pct",
    "dot_pct",
    "runs_powerplay",
    "runs_middle",
    "runs_death",
    "is_home",
    "season_year",
    "avg_runs_last5",
    "avg_sr_last5",
    "venue_enc",
    "opponent_enc",
]

TARGET = "performance"  # low / medium / high


def main():
    df = pd.read_csv(INPUT, parse_dates=["date"])
    print(f"Loaded {len(df)} player-match rows")

    # ── Encode categorical columns ─────────────────────────
    le_venue    = LabelEncoder()
    le_opponent = LabelEncoder()

    df["venue_enc"]    = le_venue.fit_transform(df["venue"].astype(str))
    df["opponent_enc"] = le_opponent.fit_transform(df["opponent"].astype(str))

    # ── Train/test split (chronological — no data leakage) ─
    df = df.sort_values("date").reset_index(drop=True)
    split_idx = int(len(df) * 0.8)
    train_df  = df.iloc[:split_idx]
    test_df   = df.iloc[split_idx:]

    X_train = train_df[FEATURE_COLS]
    y_train = train_df[TARGET]
    X_test  = test_df[FEATURE_COLS]
    y_test  = test_df[TARGET]

    print(f"\nTrain size : {len(X_train)}")
    print(f"Test size  : {len(X_test)}")

    # ── Train Random Forest ────────────────────────────────
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        min_samples_split=5,
        random_state=42,
        class_weight="balanced",   # handles imbalanced classes
    )
    model.fit(X_train, y_train)

    # ── Evaluate ───────────────────────────────────────────
    y_pred = model.predict(X_test)

    print("\n── Classification Report ──────────────────────────")
    print(classification_report(y_test, y_pred, target_names=["high", "low", "medium"]))

    print("── Confusion Matrix ───────────────────────────────")
    cm = confusion_matrix(y_test, y_pred, labels=["low", "medium", "high"])
    print(pd.DataFrame(cm,
        index   = ["Actual: low", "Actual: medium", "Actual: high"],
        columns = ["Pred: low",   "Pred: medium",   "Pred: high"]
    ))

    # ── Cross-validation accuracy ──────────────────────────
    cv_scores = cross_val_score(model, df[FEATURE_COLS], df[TARGET], cv=5, scoring="accuracy")
    print(f"\n── 5-Fold Cross-Validation Accuracy ───────────────")
    print(f"  Scores : {cv_scores.round(3)}")
    print(f"  Mean   : {cv_scores.mean():.3f}  ±  {cv_scores.std():.3f}")

    # ── Feature importance ─────────────────────────────────
    importances = pd.Series(model.feature_importances_, index=FEATURE_COLS)
    print(f"\n── Top 10 Most Important Features ─────────────────")
    print(importances.sort_values(ascending=False).head(10).round(4))

    # ── Save model + encoders ──────────────────────────────
    os.makedirs("models", exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump({
            "model":       model,
            "le_venue":    le_venue,
            "le_opponent": le_opponent,
            "features":    FEATURE_COLS,
        }, f)

    print(f"\n✓ Model saved to '{MODEL_PATH}'")


if __name__ == "__main__":
    main()

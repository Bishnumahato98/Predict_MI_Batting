"""
STEP 4 — Predict Batting Performance for Upcoming Match
=========================================================
Reads: models/mi_batting_model.pkl  (from step3)
       output/mi_batting_features.csv  (for player history)
Run: python step4_predict.py
"""

import pickle
import pandas as pd
import numpy as np

MODEL_PATH   = "models/mi_batting_model.pkl"
FEATURES_CSV = "output/mi_batting_features.csv"

# ── CONFIGURE YOUR UPCOMING MATCH HERE ────────────────────
UPCOMING_MATCH = {
    "venue":    "Wankhede Stadium, Mumbai",   # change as needed
    "opponent": "Chennai Super Kings",         # change as needed
    "season":   2025,
}

# MI batting lineup for the upcoming match (expected order)
MI_LINEUP = [
    {"batter": "RG Sharma",     "batting_pos": 1},
    {"batter": "Ishan Kishan",  "batting_pos": 2},
    {"batter": "SA Yadav",      "batting_pos": 3},
    {"batter": "TH David",      "batting_pos": 4},
    {"batter": "HH Pandya",     "batting_pos": 5},
    {"batter": "KH Pandya",     "batting_pos": 6},
    {"batter": "TL Seifert",    "batting_pos": 7},
]
# ──────────────────────────────────────────────────────────


def get_player_history(features_df, batter):
    """Get last 5 match averages for a player."""
    player = features_df[features_df["batter"] == batter].sort_values("date")
    if len(player) == 0:
        return {"avg_runs_last5": 20.0, "avg_sr_last5": 120.0}  # default for new players
    last5 = player.tail(5)
    return {
        "avg_runs_last5": round(last5["runs"].mean(), 2),
        "avg_sr_last5":   round(last5["strike_rate"].mean(), 2),
    }


def predict_lineup(lineup, match_info, model_bundle, features_df):
    model       = model_bundle["model"]
    le_venue    = model_bundle["le_venue"]
    le_opponent = model_bundle["le_opponent"]
    feature_cols = model_bundle["features"]

    venue    = match_info["venue"]
    opponent = match_info["opponent"]
    season   = match_info["season"]
    is_home  = 1 if "Wankhede" in venue else 0

    # Encode venue/opponent (handle unseen labels gracefully)
    try:
        venue_enc = le_venue.transform([venue])[0]
    except ValueError:
        venue_enc = 0

    try:
        opponent_enc = le_opponent.transform([opponent])[0]
    except ValueError:
        opponent_enc = 0

    results = []
    for player in lineup:
        batter      = player["batter"]
        batting_pos = player["batting_pos"]
        history     = get_player_history(features_df, batter)

        # Build input row (use historical averages as proxies for upcoming match)
        row = {
            "batting_pos":    batting_pos,
            "balls_faced":    history["avg_runs_last5"] * 0.8,   # rough proxy
            "strike_rate":    history["avg_sr_last5"],
            "fours":          max(0, round(history["avg_runs_last5"] / 12)),
            "sixes":          max(0, round(history["avg_runs_last5"] / 25)),
            "boundary_pct":   20.0,
            "dot_pct":        40.0,
            "runs_powerplay": history["avg_runs_last5"] * 0.3,
            "runs_middle":    history["avg_runs_last5"] * 0.4,
            "runs_death":     history["avg_runs_last5"] * 0.3,
            "is_home":        is_home,
            "season_year":    season,
            "avg_runs_last5": history["avg_runs_last5"],
            "avg_sr_last5":   history["avg_sr_last5"],
            "venue_enc":      venue_enc,
            "opponent_enc":   opponent_enc,
        }

        X = pd.DataFrame([row])[feature_cols]
        prediction    = model.predict(X)[0]
        probabilities = model.predict_proba(X)[0]
        classes       = model.classes_

        prob_dict = dict(zip(classes, probabilities))

        results.append({
            "batter":         batter,
            "batting_pos":    batting_pos,
            "avg_runs_last5": history["avg_runs_last5"],
            "avg_sr_last5":   history["avg_sr_last5"],
            "prediction":     prediction.upper(),
            "prob_low":       round(prob_dict.get("low", 0) * 100, 1),
            "prob_medium":    round(prob_dict.get("medium", 0) * 100, 1),
            "prob_high":      round(prob_dict.get("high", 0) * 100, 1),
        })

    return pd.DataFrame(results)


def main():
    # Load model
    with open(MODEL_PATH, "rb") as f:
        model_bundle = pickle.load(f)

    # Load features for player history
    features_df = pd.read_csv(FEATURES_CSV, parse_dates=["date"])

    print("=" * 55)
    print("  MUMBAI INDIANS — BATTING PERFORMANCE PREDICTION")
    print("=" * 55)
    print(f"  Venue    : {UPCOMING_MATCH['venue']}")
    print(f"  Opponent : {UPCOMING_MATCH['opponent']}")
    print(f"  Season   : {UPCOMING_MATCH['season']}")
    print("=" * 55)

    results = predict_lineup(MI_LINEUP, UPCOMING_MATCH, model_bundle, features_df)

    print(results.to_string(index=False))
    print("\n  Prediction key:  LOW < 20 runs | MEDIUM 20–49 | HIGH 50+")

    results.to_csv("output/mi_predictions.csv", index=False)
    print("\n✓ Predictions saved to 'output/mi_predictions.csv'")


if __name__ == "__main__":
    main()

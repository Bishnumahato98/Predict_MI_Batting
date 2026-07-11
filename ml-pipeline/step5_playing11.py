"""
STEP 5 — Playing XI Selector & Player Ranker
==============================================
Reads: models/mi_batting_model.pkl
       output/mi_batting_features.csv
Writes: output/mi_playing11_recommendation.csv
Run: python step5_playing11.py
"""

import pickle
import pandas as pd
import numpy as np

MODEL_PATH   = "models/mi_batting_model.pkl"
FEATURES_CSV = "output/mi_batting_features.csv"
OUTPUT_FILE  = "output/mi_playing11_recommendation.csv"

# ── CONFIGURE YOUR NEXT MATCH ─────────────────────────
NEXT_MATCH = {
    "venue":    "Wankhede Stadium, Mumbai",
    "opponent": "Chennai Super Kings",
    "season":   2025,
    "is_home":  True,
}

# ── FULL MI SQUAD (change as needed per season) ───────
MI_SQUAD = [
    {"name": "RG Sharma",        "role": "BAT",   "batting_pos": 1},
    {"name": "Ishan Kishan",     "role": "WK",    "batting_pos": 2},
    {"name": "SA Yadav",         "role": "BAT",   "batting_pos": 3},
    {"name": "TH David",         "role": "BAT",   "batting_pos": 4},
    {"name": "HH Pandya",        "role": "ALLR",  "batting_pos": 5},
    {"name": "KH Pandya",        "role": "ALLR",  "batting_pos": 6},
    {"name": "TL Seifert",       "role": "WK",    "batting_pos": 7},
    {"name": "RD Gaikwad",       "role": "BAT",   "batting_pos": 3},
    {"name": "N Wadhera",        "role": "BAT",   "batting_pos": 4},
    {"name": "Naman Dhir",       "role": "ALLR",  "batting_pos": 6},
    {"name": "Shubman Gill",     "role": "BAT",   "batting_pos": 1},
    {"name": "JJ Bumrah",        "role": "BOWL",  "batting_pos": 10},
    {"name": "Mohammad Nabi",    "role": "ALLR",  "batting_pos": 7},
    {"name": "Romario Shepherd", "role": "ALLR",  "batting_pos": 8},
    {"name": "Nuwan Thushara",   "role": "BOWL",  "batting_pos": 11},
    {"name": "Akash Madhwal",    "role": "BOWL",  "batting_pos": 11},
]

# ── PLAYING XI CONSTRAINTS ────────────────────────────
CONSTRAINTS = {
    "min_batsmen":    4,   # pure BAT
    "min_allrounders": 2,  # ALLR
    "min_bowlers":    4,   # BOWL
    "min_wk":         1,   # WK
    "total":         11,
}
# ──────────────────────────────────────────────────────


def get_player_stats(features_df, name):
    """Get comprehensive player stats from historical data."""
    player = features_df[features_df["batter"] == name].sort_values("date")
    if len(player) == 0:
        return None

    last5  = player.tail(5)
    last10 = player.tail(10)

    # Home vs away performance
    home_matches = player[player["is_home"] == 1]
    away_matches = player[player["is_home"] == 0]

    # Performance label distribution
    high_pct   = (player["performance"] == "high").mean() * 100
    medium_pct = (player["performance"] == "medium").mean() * 100
    low_pct    = (player["performance"] == "low").mean() * 100

    return {
        "matches":          len(player),
        "total_runs":       int(player["runs"].sum()),
        "avg_runs":         round(player["runs"].mean(), 2),
        "avg_sr":           round(player["strike_rate"].mean(), 2),
        "avg_runs_last5":   round(last5["runs"].mean(), 2),
        "avg_sr_last5":     round(last5["strike_rate"].mean(), 2),
        "avg_runs_last10":  round(last10["runs"].mean(), 2),
        "best_score":       int(player["runs"].max()),
        "fifties":          int((player["runs"] >= 50).sum()),
        "thirties":         int((player["runs"] >= 30).sum()),
        "home_avg":         round(home_matches["runs"].mean(), 2) if len(home_matches) > 0 else 0,
        "away_avg":         round(away_matches["runs"].mean(), 2) if len(away_matches) > 0 else 0,
        "high_pct":         round(high_pct, 1),
        "medium_pct":       round(medium_pct, 1),
        "low_pct":          round(low_pct, 1),
        "consistency":      round(100 - player["runs"].std(), 2),
    }


def compute_player_score(stats, match_info, prediction, prob_high, prob_medium):
    """
    Compute a composite score (0–100) for player selection.
    Weights:
      - ML prediction probability  40%
      - Recent form (last 5)       25%
      - Overall average            15%
      - Home/away bonus            10%
      - Consistency                10%
    """
    if stats is None:
        return 30.0  # default for unknown players

    # ML probability score (40%)
    ml_score = (prob_high * 1.0 + prob_medium * 0.5) * 40

    # Recent form score (25%) — normalize last5 avg to 0–100
    form_score = min(stats["avg_runs_last5"] / 50 * 100, 100) * 0.25

    # Overall average score (15%)
    avg_score = min(stats["avg_runs"] / 50 * 100, 100) * 0.15

    # Home/away bonus (10%)
    if match_info["is_home"]:
        venue_score = min(stats["home_avg"] / 50 * 100, 100) * 0.10
    else:
        venue_score = min(stats["away_avg"] / 50 * 100, 100) * 0.10

    # Consistency score (10%) — more matches + lower std = better
    consistency_score = min(stats["matches"] / 50 * 100, 100) * 0.10

    total = ml_score + form_score + avg_score + venue_score + consistency_score
    return round(min(total, 100), 2)


def select_playing11(ranked_players):
    """
    Select best 11 from ranked players respecting role constraints.
    Priority: highest composite score first, within constraints.
    """
    selected  = []
    remaining = ranked_players.copy()

    counts = {"BAT": 0, "WK": 0, "ALLR": 0, "BOWL": 0}

    # First pass: fill minimum requirements
    for role, min_count in [
        ("WK",   CONSTRAINTS["min_wk"]),
        ("BAT",  CONSTRAINTS["min_batsmen"]),
        ("BOWL", CONSTRAINTS["min_bowlers"]),
        ("ALLR", CONSTRAINTS["min_allrounders"]),
    ]:
        role_players = remaining[remaining["role"] == role].head(min_count)
        for _, p in role_players.iterrows():
            if len(selected) < 11:
                selected.append(p)
                counts[role] += 1
                remaining = remaining[remaining["name"] != p["name"]]

    # Second pass: fill remaining spots with highest scorers
    spots_left = 11 - len(selected)
    top_rest   = remaining.head(spots_left)
    for _, p in top_rest.iterrows():
        selected.append(p)

    return pd.DataFrame(selected).reset_index(drop=True)


def predict_for_player(player, match_info, model_bundle, features_df):
    """Run ML model prediction for one player."""
    model        = model_bundle["model"]
    le_venue     = model_bundle["le_venue"]
    le_opponent  = model_bundle["le_opponent"]
    feature_cols = model_bundle["features"]

    stats = get_player_stats(features_df, player["name"])

    if stats:
        avg_runs = stats["avg_runs_last5"]
        avg_sr   = stats["avg_sr_last5"]
    else:
        avg_runs = 15.0
        avg_sr   = 110.0

    try:
        venue_enc = le_venue.transform([match_info["venue"]])[0]
    except ValueError:
        venue_enc = 0
    try:
        opponent_enc = le_opponent.transform([match_info["opponent"]])[0]
    except ValueError:
        opponent_enc = 0

    row = {
        "batting_pos":    player["batting_pos"],
        "balls_faced":    avg_runs * 0.8,
        "strike_rate":    avg_sr,
        "fours":          max(0, round(avg_runs / 12)),
        "sixes":          max(0, round(avg_runs / 25)),
        "boundary_pct":   20.0,
        "dot_pct":        40.0,
        "runs_powerplay": avg_runs * 0.3,
        "runs_middle":    avg_runs * 0.4,
        "runs_death":     avg_runs * 0.3,
        "is_home":        int(match_info["is_home"]),
        "season_year":    match_info["season"],
        "avg_runs_last5": avg_runs,
        "avg_sr_last5":   avg_sr,
        "venue_enc":      venue_enc,
        "opponent_enc":   opponent_enc,
    }

    X          = pd.DataFrame([row])[feature_cols]
    prediction = model.predict(X)[0]
    probs      = dict(zip(model.classes_, model.predict_proba(X)[0]))

    return prediction, probs, stats


def main():
    # Load model and features
    with open(MODEL_PATH, "rb") as f:
        model_bundle = pickle.load(f)

    features_df = pd.read_csv(FEATURES_CSV, parse_dates=["date"])

    print("=" * 65)
    print("  MUMBAI INDIANS — PLAYING XI SELECTOR")
    print("=" * 65)
    print(f"  Venue    : {NEXT_MATCH['venue']}")
    print(f"  Opponent : {NEXT_MATCH['opponent']}")
    print(f"  Season   : {NEXT_MATCH['season']}")
    print(f"  Home     : {'Yes' if NEXT_MATCH['is_home'] else 'No'}")
    print("=" * 65)

    # ── Score every squad member ───────────────────────
    results = []
    for player in MI_SQUAD:
        prediction, probs, stats = predict_for_player(
            player, NEXT_MATCH, model_bundle, features_df
        )

        prob_high   = probs.get("high", 0)
        prob_medium = probs.get("medium", 0)
        prob_low    = probs.get("low", 0)

        score = compute_player_score(
            stats, NEXT_MATCH, prediction, prob_high, prob_medium
        )

        results.append({
            "name":           player["name"],
            "role":           player["role"],
            "batting_pos":    player["batting_pos"],
            "prediction":     prediction.upper(),
            "prob_high":      round(prob_high * 100, 1),
            "prob_medium":    round(prob_medium * 100, 1),
            "prob_low":       round(prob_low * 100, 1),
            "avg_runs_last5": stats["avg_runs_last5"] if stats else 0,
            "avg_sr_last5":   stats["avg_sr_last5"] if stats else 0,
            "home_avg":       stats["home_avg"] if stats else 0,
            "matches":        stats["matches"] if stats else 0,
            "fifties":        stats["fifties"] if stats else 0,
            "composite_score": score,
        })

    ranked = pd.DataFrame(results).sort_values(
        "composite_score", ascending=False
    ).reset_index(drop=True)

    # ── Print full squad ranking ───────────────────────
    print("\n ALL SQUAD MEMBERS RANKED")
    print("-" * 65)
    print(f"{'#':<3} {'Name':<22} {'Role':<5} {'Predict':<8} {'Score':<7} {'Last5 Avg':<10} {'50s'}")
    print("-" * 65)
    for i, row in ranked.iterrows():
        print(
            f"{i+1:<3} {row['name']:<22} {row['role']:<5} "
            f"{row['prediction']:<8} {row['composite_score']:<7} "
            f"{row['avg_runs_last5']:<10} {row['fifties']}"
        )

    # ── Select Playing XI ──────────────────────────────
    playing11 = select_playing11(ranked)

    print("\n\n RECOMMENDED PLAYING XI")
    print("=" * 65)
    print(f"{'#':<3} {'Name':<22} {'Role':<5} {'Prediction':<10} {'Score':<7} {'Prob High'}")
    print("-" * 65)
    for i, row in playing11.iterrows():
        marker = " *" if row["prediction"] == "HIGH" else ""
        print(
            f"{i+1:<3} {row['name']:<22} {row['role']:<5} "
            f"{row['prediction']:<10} {row['composite_score']:<7} "
            f"{row['prob_high']}%{marker}"
        )

    # ── Role summary ───────────────────────────────────
    role_counts = playing11["role"].value_counts()
    print("\n  Team composition:")
    for role, count in role_counts.items():
        print(f"    {role}: {count}")

    # ── Top performer prediction ───────────────────────
    top = playing11.iloc[0]
    print(f"\n  Top pick: {top['name']} (score: {top['composite_score']})")
    print(f"  Predicted: {top['prediction']} | "
          f"High chance: {top['prob_high']}% | "
          f"Last 5 avg: {top['avg_runs_last5']}")

    print("\n  * = predicted HIGH (50+ runs)")
    print("  Prediction key: LOW < 20 | MEDIUM 20–49 | HIGH 50+")

    # ── Save outputs ───────────────────────────────────
    playing11.to_csv(OUTPUT_FILE, index=False)
    ranked.to_csv("output/mi_squad_ranking.csv", index=False)

    print(f"\n✓ Playing XI saved to '{OUTPUT_FILE}'")
    print(f"✓ Full squad ranking saved to 'output/mi_squad_ranking.csv'")


if __name__ == "__main__":
    main()

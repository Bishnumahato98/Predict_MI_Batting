"""
ML Predictor — loads trained Random Forest model and serves predictions.
"""

import os
import pickle
import pandas as pd

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH   = os.path.join(BASE_DIR, "mi_batting_model.pkl")
FEATURES_CSV = os.path.join(BASE_DIR, "mi_batting_features.csv")

# ── Load once at startup ──────────────────────────────
with open(MODEL_PATH, "rb") as f:
    _bundle = pickle.load(f)

MODEL        = _bundle["model"]
LE_VENUE     = _bundle["le_venue"]
LE_OPPONENT  = _bundle["le_opponent"]
FEATURE_COLS = _bundle["features"]

FEATURES_DF = pd.read_csv(FEATURES_CSV, parse_dates=["date"])


def get_player_stats(name: str):
    """Full historical stats for one player."""
    player = FEATURES_DF[FEATURES_DF["batter"] == name].sort_values("date")
    if len(player) == 0:
        return None

    last5 = player.tail(5)
    home  = player[player["is_home"] == 1]
    away  = player[player["is_home"] == 0]

    return {
        "name":            name,
        "matches":         int(len(player)),
        "total_runs":      int(player["runs"].sum()),
        "avg_runs":        round(float(player["runs"].mean()), 2),
        "avg_sr":          round(float(player["strike_rate"].mean()), 2),
        "avg_runs_last5":  round(float(last5["runs"].mean()), 2),
        "avg_sr_last5":    round(float(last5["strike_rate"].mean()), 2),
        "best_score":      int(player["runs"].max()),
        "fifties":         int((player["runs"] >= 50).sum()),
        "home_avg":        round(float(home["runs"].mean()), 2) if len(home) else 0,
        "away_avg":        round(float(away["runs"].mean()), 2) if len(away) else 0,
    }


def list_all_players():
    """All MI batters with summary stats, sorted by total runs."""
    summary = (
        FEATURES_DF.groupby("batter")
        .agg(
            matches=("date", "nunique"),
            total_runs=("runs", "sum"),
            avg_runs=("runs", "mean"),
            avg_sr=("strike_rate", "mean"),
            fifties=("runs", lambda x: int((x >= 50).sum())),
        )
        .reset_index()
        .sort_values("total_runs", ascending=False)
    )
    summary["avg_runs"] = summary["avg_runs"].round(2)
    summary["avg_sr"]   = summary["avg_sr"].round(2)
    return summary.to_dict(orient="records")


def season_summary():
    """Season-wise MI batting summary."""
    s = (
        FEATURES_DF.groupby("season_year")
        .agg(
            total_runs=("runs", "sum"),
            avg_runs=("runs", "mean"),
            avg_sr=("strike_rate", "mean"),
            players=("batter", "nunique"),
        )
        .reset_index()
        .sort_values("season_year")
    )
    s["avg_runs"] = s["avg_runs"].round(2)
    s["avg_sr"]   = s["avg_sr"].round(2)
    return s.to_dict(orient="records")


def predict_player(name: str, batting_pos: int, venue: str, opponent: str,
                   season: int, is_home: bool):
    """Predict LOW/MEDIUM/HIGH for one player in an upcoming match."""
    stats = get_player_stats(name)

    avg_runs = stats["avg_runs_last5"] if stats else 15.0
    avg_sr   = stats["avg_sr_last5"] if stats else 110.0

    try:
        venue_enc = LE_VENUE.transform([venue])[0]
    except ValueError:
        venue_enc = 0
    try:
        opponent_enc = LE_OPPONENT.transform([opponent])[0]
    except ValueError:
        opponent_enc = 0

    row = {
        "batting_pos":    batting_pos,
        "balls_faced":    avg_runs * 0.8,
        "strike_rate":    avg_sr,
        "fours":          max(0, round(avg_runs / 12)),
        "sixes":          max(0, round(avg_runs / 25)),
        "boundary_pct":   20.0,
        "dot_pct":        40.0,
        "runs_powerplay": avg_runs * 0.3,
        "runs_middle":    avg_runs * 0.4,
        "runs_death":     avg_runs * 0.3,
        "is_home":        int(is_home),
        "season_year":    season,
        "avg_runs_last5": avg_runs,
        "avg_sr_last5":   avg_sr,
        "venue_enc":      venue_enc,
        "opponent_enc":   opponent_enc,
    }

    X     = pd.DataFrame([row])[FEATURE_COLS]
    pred  = MODEL.predict(X)[0]
    probs = dict(zip(MODEL.classes_, MODEL.predict_proba(X)[0]))

    return {
        "name":        name,
        "batting_pos": batting_pos,
        "prediction":  pred.upper(),
        "prob_low":    round(float(probs.get("low", 0)) * 100, 1),
        "prob_medium": round(float(probs.get("medium", 0)) * 100, 1),
        "prob_high":   round(float(probs.get("high", 0)) * 100, 1),
        "avg_runs_last5": avg_runs,
        "avg_sr_last5":   avg_sr,
        "has_history": stats is not None,
    }


def composite_score(stats, prob_high, prob_medium, is_home):
    """Selection score 0-100. Weights: ML 40%, form 25%, avg 15%, venue 10%, experience 10%."""
    if stats is None:
        return 30.0

    ml_score   = (prob_high / 100 * 1.0 + prob_medium / 100 * 0.5) * 40
    form_score = min(stats["avg_runs_last5"] / 50 * 100, 100) * 0.25
    avg_score  = min(stats["avg_runs"] / 50 * 100, 100) * 0.15
    venue_avg  = stats["home_avg"] if is_home else stats["away_avg"]
    venue_score = min(venue_avg / 50 * 100, 100) * 0.10
    exp_score  = min(stats["matches"] / 50 * 100, 100) * 0.10

    return round(min(ml_score + form_score + avg_score + venue_score + exp_score, 100), 2)


def select_playing11(squad: list, venue: str, opponent: str, season: int, is_home: bool,
                     constraints=None):
    """
    Rank the full squad and select a valid Playing XI.
    squad: list of {"name", "role", "batting_pos"}
    """
    if constraints is None:
        constraints = {"min_wk": 1, "min_batsmen": 4, "min_bowlers": 4, "min_allrounders": 2}

    results = []
    for p in squad:
        pred  = predict_player(p["name"], p["batting_pos"], venue, opponent, season, is_home)
        stats = get_player_stats(p["name"])
        score = composite_score(stats, pred["prob_high"], pred["prob_medium"], is_home)
        results.append({**p, **pred, "composite_score": score})

    ranked = sorted(results, key=lambda r: r["composite_score"], reverse=True)

    selected, selected_names = [], set()

    # Fill role minimums first
    for role, key in [("WK", "min_wk"), ("BAT", "min_batsmen"),
                      ("BOWL", "min_bowlers"), ("ALLR", "min_allrounders")]:
        needed = constraints[key]
        for r in ranked:
            if needed == 0 or len(selected) >= 11:
                break
            if r["role"] == role and r["name"] not in selected_names:
                selected.append(r)
                selected_names.add(r["name"])
                needed -= 1

    # Fill remaining with best scores
    for r in ranked:
        if len(selected) >= 11:
            break
        if r["name"] not in selected_names:
            selected.append(r)
            selected_names.add(r["name"])

    return {"ranking": ranked, "playing11": selected}

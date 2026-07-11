"""
STEP 2 — Feature Engineering
==============================
Reads: output/mi_batting_raw.csv  (from step1)
Writes: output/mi_batting_features.csv  (ready for ML)
Run: python step2_features.py
"""

import pandas as pd
import numpy as np

INPUT  = "output/mi_batting_raw.csv"
OUTPUT = "output/mi_batting_features.csv"


def build_features(df):
    # ── Per match per batter aggregation ──────────────────
    grouped = df[~df["is_wide"]].groupby(["date", "season", "venue", "opponent", "batter", "batting_pos"])

    agg = grouped.agg(
        runs        = ("runs_batter", "sum"),
        balls_faced = ("runs_batter", "count"),
        fours       = ("runs_batter", lambda x: (x == 4).sum()),
        sixes       = ("runs_batter", lambda x: (x == 6).sum()),
        dots        = ("runs_batter", lambda x: (x == 0).sum()),
        mi_won      = ("mi_won", "first"),
    ).reset_index()

    # Strike rate
    agg["strike_rate"] = (agg["runs"] / agg["balls_faced"] * 100).round(2)

    # Boundary %
    agg["boundary_pct"] = ((agg["fours"] + agg["sixes"]) / agg["balls_faced"] * 100).round(2)

    # Dot ball %
    agg["dot_pct"] = (agg["dots"] / agg["balls_faced"] * 100).round(2)

    # ── Phase runs (powerplay / middle / death) ────────────
    phase_df = df[~df["is_wide"]].groupby(["date", "batter", "phase"])["runs_batter"].sum().unstack(fill_value=0).reset_index()
    for col in ["powerplay", "middle", "death"]:
        if col not in phase_df.columns:
            phase_df[col] = 0
    phase_df = phase_df.rename(columns={
        "powerplay": "runs_powerplay",
        "middle":    "runs_middle",
        "death":     "runs_death"
    })
    agg = agg.merge(phase_df[["date", "batter", "runs_powerplay", "runs_middle", "runs_death"]], on=["date", "batter"], how="left")

    # ── Dismissal info ─────────────────────────────────────
    dismissals = df[df["is_wicket"]].groupby(["date", "batter"])["dismissal_kind"].first().reset_index()
    agg = agg.merge(dismissals, on=["date", "batter"], how="left")
    agg["was_dismissed"] = agg["dismissal_kind"].notna().astype(int)

    # ── Is home match (Wankhede) ───────────────────────────
    agg["is_home"] = agg["venue"].str.contains("Wankhede", case=False, na=False).astype(int)

    # ── Season as integer ──────────────────────────────────
    agg["season_year"] = agg["season"].astype(str).str[:4].astype(int)

    # ── Sort by batter + date for rolling features ─────────
    agg = agg.sort_values(["batter", "date"]).reset_index(drop=True)

    # ── Rolling last-5-match form per batter ───────────────
    agg["avg_runs_last5"] = (
        agg.groupby("batter")["runs"]
        .transform(lambda x: x.shift(1).rolling(5, min_periods=1).mean())
        .round(2)
    )
    agg["avg_sr_last5"] = (
        agg.groupby("batter")["strike_rate"]
        .transform(lambda x: x.shift(1).rolling(5, min_periods=1).mean())
        .round(2)
    )

    # ── Target label: performance category ────────────────
    def performance_label(runs):
        if runs < 20:   return "low"
        elif runs < 50: return "medium"
        else:           return "high"

    agg["performance"] = agg["runs"].apply(performance_label)

    # ── Clean up ───────────────────────────────────────────
    feature_cols = [
        "date", "season", "season_year", "venue", "is_home",
        "opponent", "batter", "batting_pos",
        "runs", "balls_faced", "strike_rate",
        "fours", "sixes", "dots", "boundary_pct", "dot_pct",
        "runs_powerplay", "runs_middle", "runs_death",
        "dismissal_kind", "was_dismissed",
        "avg_runs_last5", "avg_sr_last5",
        "mi_won", "performance"
    ]

    agg = agg[feature_cols].fillna(0)
    return agg


def main():
    df = pd.read_csv(INPUT, parse_dates=["date"])
    print(f"Loaded {len(df)} ball-by-ball rows")

    features = build_features(df)
    features.to_csv(OUTPUT, index=False)

    print(f"\n✓ Feature dataset saved to '{OUTPUT}'")
    print(f"  Rows (player-match): {len(features)}")
    print(f"  Columns            : {len(features.columns)}")
    print(f"  Unique batters     : {features['batter'].nunique()}")
    print(f"\nPerformance label distribution:")
    print(features["performance"].value_counts())
    print(f"\nSample features:")
    print(features.head())


if __name__ == "__main__":
    main()

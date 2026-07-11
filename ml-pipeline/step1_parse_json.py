"""
STEP 1 — Parse Cricsheet IPL JSON files
========================================
Place all your .json files from ipl_json.zip inside the 'data/' folder.
Run: python step1_parse_json.py
Output: output/mi_batting_raw.csv
"""

import json
import os
import pandas as pd

# ── CONFIG ──────────────────────────────────────────────
JSON_FOLDER = "data/"          # folder where your .json files are
OUTPUT_FILE = "output/mi_batting_raw.csv"
MI_NAME     = "Mumbai Indians"
# ────────────────────────────────────────────────────────


def parse_match(filepath):
    with open(filepath, encoding="utf-8") as f:
        match = json.load(f)

    info    = match.get("info", {})
    teams   = info.get("teams", [])
    season  = info.get("season", "Unknown")
    venue   = info.get("venue", "Unknown")
    date    = info.get("dates", ["Unknown"])[0]
    winner  = info.get("outcome", {}).get("winner", "No result")
    city    = info.get("city", "Unknown")

    # Only process matches where MI played
    if MI_NAME not in teams:
        return []

    opponent = [t for t in teams if t != MI_NAME]
    opponent = opponent[0] if opponent else "Unknown"

    rows = []
    for innings in match.get("innings", []):
        batting_team = innings.get("team", "")
        if batting_team != MI_NAME:
            continue  # only MI batting innings

        # Track batting position per batter
        batting_order = {}
        position_counter = 1

        for over_data in innings.get("overs", []):
            over_num = over_data.get("over", 0)

            # Classify phase
            if over_num < 6:
                phase = "powerplay"
            elif over_num < 15:
                phase = "middle"
            else:
                phase = "death"

            for delivery in over_data.get("deliveries", []):
                batter  = delivery.get("batter", "Unknown")
                bowler  = delivery.get("bowler", "Unknown")
                runs    = delivery.get("runs", {})

                # Assign batting position (first time we see a batter)
                if batter not in batting_order:
                    batting_order[batter] = position_counter
                    position_counter += 1

                # Wicket info
                wickets     = delivery.get("wickets", [])
                is_wicket   = len(wickets) > 0
                dismissal   = wickets[0].get("kind", None) if is_wicket else None

                # Extras
                extras      = delivery.get("extras", {})
                extras_type = list(extras.keys())[0] if extras else None
                is_wide     = "wides" in extras
                is_noball   = "noballs" in extras

                row = {
                    "season":         season,
                    "date":           date,
                    "venue":          venue,
                    "city":           city,
                    "batting_team":   batting_team,
                    "opponent":       opponent,
                    "batter":         batter,
                    "bowler":         bowler,
                    "batting_pos":    batting_order[batter],
                    "over":           over_num,
                    "phase":          phase,
                    "runs_batter":    runs.get("batter", 0),
                    "runs_extras":    runs.get("extras", 0),
                    "runs_total":     runs.get("total", 0),
                    "is_wide":        is_wide,
                    "is_noball":      is_noball,
                    "is_wicket":      is_wicket,
                    "dismissal_kind": dismissal,
                    "match_winner":   winner,
                    "mi_won":         winner == MI_NAME,
                }
                rows.append(row)

    return rows


def main():
    all_rows = []
    files    = [f for f in os.listdir(JSON_FOLDER) if f.endswith(".json")]

    if not files:
        print(f"No JSON files found in '{JSON_FOLDER}'. Please put your Cricsheet JSON files there.")
        return

    print(f"Found {len(files)} JSON files. Parsing...")

    for i, filename in enumerate(files, 1):
        path = os.path.join(JSON_FOLDER, filename)
        rows = parse_match(path)
        all_rows.extend(rows)
        if i % 100 == 0:
            print(f"  Processed {i}/{len(files)} files...")

    if not all_rows:
        print("No Mumbai Indians data found in these files.")
        return

    df = pd.DataFrame(all_rows)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["date", "over"]).reset_index(drop=True)

    os.makedirs("output", exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"\n✓ Done! Saved {len(df)} ball-by-ball rows to '{OUTPUT_FILE}'")
    print(f"  Seasons covered  : {sorted(df['season'].unique())}")
    print(f"  Unique batters   : {df['batter'].nunique()}")
    print(f"  Total matches    : {df.groupby('date')['date'].count().shape[0]}")
    print(f"\nSample (first 5 rows):")
    print(df.head())


if __name__ == "__main__":
    main()

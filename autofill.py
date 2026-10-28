"""
Auto-fill weekly stat lines for every leg from nflverse's free weekly player stats.

    python autofill.py            # writes data.json in place
    python autofill.py --dry-run  # prints what it would add

Rules
  * Only weeks not already in data.json are added, so hand-written notes and
    corrections are never overwritten.
  * A week counts only once the player's team has played it in the feed.
    If the team played and the player has no row, it's logged as 0 with an
    "O" tag (that is how the tracker counts a missed game). Bye weeks are skipped.
  * Players the feed can't find are listed in the log for manual entry.
"""
from __future__ import annotations

import csv
import io
import json
import sys
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone

SEASON = 2026
FEED = f"https://github.com/nflverse/nflverse-data/releases/download/stats_player/stats_player_week_{SEASON}.csv"

# leg id -> (player name in the feed, how to compute the leg's stat from a feed row)
def col(*names):
    return lambda r: sum(float(r.get(n) or 0) for n in names)

LEGS = {
    "bowers":   ("Brock Bowers",     col("receiving_yards")),
    "herbert":  ("Justin Herbert",   col("passing_tds")),
    "moore":    ("DJ Moore",         col("receiving_yards")),
    "flowers":  ("Zay Flowers",      col("receiving_tds")),
    "evans":    ("Mike Evans",       col("receiving_tds")),
    "lamar":    ("Lamar Jackson",    col("passing_yards", "rushing_yards")),
    "bijan":    ("Bijan Robinson",   col("receptions")),
    "johnston": ("Quentin Johnston", col("receiving_tds")),
    "dak":      ("Dak Prescott",     col("passing_yards")),
    "waddle":   ("Jaylen Waddle",    col("receiving_yards")),
    "nacua":    ("Puka Nacua",       col("rushing_tds")),
    "fox":      ("Jack Fox",         col("passing_yards")),
    "chase":    ("Ja'Marr Chase",    col("rushing_yards")),
    "zayrush":  ("Zay Flowers",      col("rushing_yards")),
    "mclaurin": ("Terry McLaurin",   col("receiving_tds")),
    "dart":     ("Jaxson Dart",      col("passing_yards")),
}
TEAM_FIX = {"LA": "LAR"}   # feed abbreviation -> tracker abbreviation


def load_feed() -> list[dict]:
    req = urllib.request.Request(FEED, headers={"User-Agent": "fantasy-tracker-autofill"})
    with urllib.request.urlopen(req, timeout=60) as r:
        text = r.read().decode("utf-8", "replace")
    return [row for row in csv.DictReader(io.StringIO(text)) if row.get("season_type", "REG") == "REG"]


def main(dry: bool = False) -> None:
    rows = load_feed()
    played: dict[int, dict[str, str]] = {}          # week -> team -> "vs OPP" / "at OPP"
    for r in rows:
        wk = int(r["week"])
        gid = r.get("game_id") or ""               # 2026_07_AWAY_HOME
        parts = gid.split("_")
        away, home = (parts[2], parts[3]) if len(parts) >= 4 else ("", "")
        team, opp = r["team"], r["opponent_team"]
        where = "vs" if team == home else "at" if team == away else "vs"
        played.setdefault(wk, {})[team] = f"{where} {TEAM_FIX.get(opp, opp)}"
    last_week = max(played) if played else 0

    data = json.load(open("data.json"))
    legs = data.setdefault("legs", {})
    added, missing = [], []
    for lid, (name, stat) in LEGS.items():
        mine = [r for r in rows if r["player_display_name"] == name]
        if not mine:
            missing.append(name)
            continue
        team = Counter(r["team"] for r in mine).most_common(1)[0][0]
        by_week = {int(r["week"]): r for r in mine}
        leg = legs.setdefault(lid, {"inj": "", "injNote": "", "weeks": {}})
        weeks = leg.setdefault("weeks", {})
        if leg.get("settled"):
            continue
        for wk in range(1, last_week + 1):
            if str(wk) in weeks or team not in played.get(wk, {}):
                continue                            # already logged, or a bye
            r = by_week.get(wk)
            val = round(stat(r), 1) if r else 0
            if float(val).is_integer():
                val = int(val)
            entry = {"val": val, "opp": played[wk][team],
                     "note": "Auto-filled from nflverse weekly stats." if r else "Auto-filled: no stat line, so logged as a missed game."}
            if not r:
                entry["inj"] = "O"
            weeks[str(wk)] = entry
            added.append(f"{lid} wk{wk}={val}")

    if added:
        data["throughWeek"] = max(int(data.get("throughWeek") or 0), last_week)
        et = datetime.now(timezone(timedelta(hours=-4)))
        data["updated"] = et.strftime("%Y-%m-%d")
    print(f"feed through week {last_week}; added {len(added)}: {', '.join(added) or 'nothing'}")
    if missing:
        print("not in feed, enter by hand:", ", ".join(missing))
    if not dry:
        with open("data.json", "w") as f:
            json.dump(data, f, indent=1, ensure_ascii=False)
            f.write("\n")


if __name__ == "__main__":
    main(dry="--dry-run" in sys.argv)

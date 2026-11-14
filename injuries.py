"""
Refresh each live leg's injury tag from ESPN's public NFL injury report.

    python injuries.py            # writes data.json in place
    python injuries.py --dry-run  # prints the changes only

Sets legs[<id>].inj to O / D / Q / IR / PUP (or clears it) and injNote to ESPN's
short comment. Legs already settled are skipped. A tag you set on your phone still
wins on your phone; this keeps the published tag current for everyone else.
"""
from __future__ import annotations

import json
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

from autofill import LEGS

FEED = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/injuries"
CODE = {"out": "O", "doubtful": "D", "questionable": "Q", "injured reserve": "IR",
        "physically unable to perform": "PUP", "suspension": "O"}


def tag(status: str) -> str:
    s = (status or "").strip().lower()
    for k, v in CODE.items():
        if s.startswith(k):
            return v
    return ""


def load() -> dict[str, dict]:
    req = urllib.request.Request(FEED, headers={"User-Agent": "fantasy-tracker-injuries"})
    with urllib.request.urlopen(req, timeout=40) as r:
        d = json.load(r)
    out = {}
    for team in d.get("injuries", []):
        for i in team.get("injuries", []):
            name = (i.get("athlete") or {}).get("displayName")
            if name:
                out[name] = {"inj": tag(i.get("status")), "note": (i.get("shortComment") or "").strip()[:240]}
    return out


def apply(data: dict, report: dict[str, dict]) -> list[str]:
    changes = []
    legs = data.setdefault("legs", {})
    for lid, (name, _) in LEGS.items():
        leg = legs.setdefault(lid, {"inj": "", "injNote": "", "weeks": {}})
        if leg.get("settled"):
            continue
        r = report.get(name, {"inj": "", "note": ""})
        new_inj, new_note = r["inj"], (r["note"] if r["inj"] else "")
        if leg.get("inj", "") != new_inj or leg.get("injNote", "") != new_note:
            changes.append(f"{lid}: {leg.get('inj') or 'OK'} -> {new_inj or 'OK'}")
            leg["inj"], leg["injNote"] = new_inj, new_note
    return changes


def main(dry: bool = False) -> None:
    data = json.load(open("data.json"))
    changes = apply(data, load())
    print("injury changes:", ", ".join(changes) or "none")
    if changes and not dry:
        data["injuriesUpdated"] = datetime.now(timezone(timedelta(hours=-5))).strftime("%Y-%m-%d %H:%M ET")
        with open("data.json", "w") as f:
            json.dump(data, f, indent=1, ensure_ascii=False)
            f.write("\n")


if __name__ == "__main__":
    main(dry="--dry-run" in sys.argv)

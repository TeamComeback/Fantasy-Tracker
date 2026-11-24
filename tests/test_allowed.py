"""HQ item p20261119nfl: per-leg 'what the next opponent allows' block written by autofill.py."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import autofill


def row(player, team, opp, wk, pos, yds):
    return {"player_display_name": player, "team": team, "opponent_team": opp, "week": str(wk), "position": pos,
            "receiving_yards": str(yds), "passing_tds": "0"}


def test_allowed_per_game_and_rank():
    rows = [row("Brock Bowers", "LV", "DEN", 1, "TE", 50), row("Other TE", "KC", "DEN", 1, "TE", 70),
            row("Brock Bowers", "LV", "LA", 2, "TE", 30), row("Other WR", "KC", "LA", 2, "WR", 999)]
    out = autofill.allowed_block(rows, {})["bowers"]
    assert out["pos"] == "TE"
    assert out["teams"]["DEN"] == [120.0, 1]          # 50 + 70 in one game
    assert out["teams"]["LAR"] == [30.0, 2]           # LA is the feed's name for LAR; WRs don't count against a TE

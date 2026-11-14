import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import injuries


def test_tags():
    assert injuries.tag("Out") == "O" and injuries.tag("Doubtful") == "D" and injuries.tag("Questionable") == "Q"
    assert injuries.tag("Injured Reserve") == "IR" and injuries.tag("Active") == ""


def test_apply_sets_and_clears_and_skips_settled():
    data = {"legs": {"evans": {"inj": "D", "injNote": "", "weeks": {}},
                     "waddle": {"inj": "Q", "injNote": "old", "weeks": {}},
                     "bowers": {"inj": "O", "injNote": "", "weeks": {}, "settled": "win"}}}
    ch = injuries.apply(data, {"Mike Evans": {"inj": "O", "note": "Achilles, ruled out"}})
    assert data["legs"]["evans"] == {"inj": "O", "injNote": "Achilles, ruled out", "weeks": {}}
    assert data["legs"]["waddle"]["inj"] == "" and data["legs"]["waddle"]["injNote"] == ""
    assert data["legs"]["bowers"]["inj"] == "O"          # settled legs are left alone
    assert any(c.startswith("evans") for c in ch)

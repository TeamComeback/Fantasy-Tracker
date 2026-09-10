# Fantasy Tracker

Season-long NFL parlay tracker for three 2026 slips: Goat Whale, New Systems, Fun.

Required rate recalculates against games actually remaining, so a slow start visibly
raises the bar instead of hiding behind a season average. Over legs show the rate still
needed. The under leg shows the rate that can still be afforded. Binary legs (over 0.5)
just wait for one play.

## Deploy

1. Create a public repo, e.g. `fantasy-tracker`.
2. Upload every file in this folder to the repo root.
3. Settings → Pages → Source: **Deploy from a branch**, branch `main`, folder `/ (root)`.
4. Wait for the green check, then open `https://<user>.github.io/fantasy-tracker/`.

## Add to the iPhone home screen

Open the Pages URL **in Safari** (not Chrome — only Safari can install).
Share → Add to Home Screen. It launches full screen with no browser chrome.

## Where data lives

Two layers, merged at load:

| Layer | File | Written by |
|---|---|---|
| Published | `data.json` in the repo | the weekly job, or by hand |
| Personal | browser storage on the device | tapping **Save week** |

**Local always wins, field by field.** A published stat never overwrites a note you
typed, and a correction you make is never clobbered by the next publish. `Clear this
slip` only wipes local edits; published data stays.

## data.json format

```json
{
  "updated": "2026-09-15",
  "throughWeek": 1,
  "legs": {
    "bowers": {
      "inj": "O",
      "injNote": "Meniscus trim Sep 8.",
      "weeks": {
        "1": { "val": 0, "opp": "vs MIA", "inj": "O", "note": "Sat out." }
      }
    }
  }
}
```

- `val` — the stat for that week in the leg's own unit (yards, TDs, receptions).
  Log `0` for a game missed; the season total will not grow but games-remaining still
  drops, which is what actually happens to the bet.
- `opp` — optional; falls back to the schedule baked into `index.html`.
- `inj` — one of `""`, `Q`, `D`, `O`, `IR`, `PUP`.
- `note` — the matchup read shown in the "Last game" block.

Leg IDs: `bowers herbert moore flowers` (Goat Whale) ·
`evans lamar bijan johnston dak waddle` (New Systems) ·
`nacua fox chase zayrush mclaurin dart` (Fun).

`zayrush` is Zay Flowers' rushing-yards leg in Fun. `flowers` is his receiving-TD leg
in Goat Whale. Same player, two legs, two slips — one injury hits both.

## Automating the weekly update

Not built yet. The plan is a GitHub Actions cron that fires Tuesday morning ET (after
Monday night finalizes), pulls the week's player stat lines, and commits `data.json`.
Pages redeploys and the app has the week already logged.

Two things to verify before building it:

- **The data source.** [nflverse](https://github.com/nflverse/nflverse-data) publishes
  weekly player stats as open files, no API key. Confirm the current release URL and
  that the fields needed are present.
- **Cron reliability.** Scheduled workflows get delayed under load and are disabled
  after 60 days of repo inactivity. Add `workflow_dispatch` so it can be run manually.

The matchup notes are not in any stat feed and stay a manual or model-written field.

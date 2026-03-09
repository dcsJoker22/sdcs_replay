# SDCS Campaign Replay

Interactive web-based replay viewer for Strategic DCS campaign sessions.
Hosted at strategic-dcs.com.

## Stack

- **Parser**: Python (`parse_acmi.py`) — converts .acmi Tacview files to JSON
- **Watcher**: Python (`watch_acmi.py`) — monitors folders, auto-imports new sessions
- **Viewer**: Vanilla HTML/JS + Leaflet.js (`public/sdcs_replay.html`)
- **Registry**: `campaigns.json` — maps campaigns to sessions, auto-managed by watcher
- **Data**: Parsed session JSONs in `public/data/` (one per session)

---

## Project Layout

```
sdcs-replay/
├── parse_acmi.py               ACMI parser
├── watch_acmi.py               Folder watcher & importer
├── campaigns.json              Campaign/session registry (auto-managed)
├── raw/                        Drop raw ACMI files here (one subfolder per campaign)
│   ├── germany_v1/
│   ├── germany_v2/
│   └── caucasus_v1/
└── public/
    ├── sdcs_replay.html        Viewer (single file, all JS/CSS inline)
    └── data/                   Parsed session JSONs
        ├── session_20260226_074617.json
        └── ...
```

---

## Data Pipeline

### Automatic (recommended)

1. Create a subfolder under `raw/` for each campaign (e.g. `raw\germany_v1\`)
2. Start the watcher:
   ```
   python watch_acmi.py watch
   ```
3. The first time a new subfolder is detected, you'll be prompted once to name
   the campaign and confirm the map. After that, just drop `.acmi` files in and
   they are parsed and registered automatically with no further input.

### Manual (single file)

```
python watch_acmi.py import raw\germany_v1\20260301_080845.zip.acmi
```

---

## Watcher Commands

```
python watch_acmi.py watch          Watch raw/ subfolders continuously
python watch_acmi.py import FILE    Import a single file (interactive)
python watch_acmi.py list           Show all campaigns and sessions
python watch_acmi.py campaigns      Manage campaigns (rename, rebind, delete)
```

---

## campaigns.json Structure

Auto-managed by `watch_acmi.py`. Manual edits to `name` and `map` fields are safe.
Do not edit `sessions` or `folder_bindings` by hand.

```json
{
  "campaigns": [
    {
      "id": "germany_v1_campaign",
      "name": "Germany v1 Campaign",
      "map": "Germany",
      "sessions": [
        {
          "file": "session_20260226_074617.json",
          "label": "26 Feb 2026 · 07:46z  (6.0h)",
          "date": "2026-02-26T07:46:17Z",
          "duration_hours": 5.99,
          "players": ["Darkstar1", "Papst", "Joker22", "Savage2"],
          "kill_count": 12
        }
      ]
    }
  ],
  "folder_bindings": {
    "germany_v1": "germany_v1_campaign"
  }
}
```

---

## Viewer Features

- **Satellite map** (Esri) with dark label overlay
- **Aircraft icons** — Tacview-style top-down silhouettes per type (F-16, FA-18,
  F-15, F-14, MiG-29, Su-27, Su-25, A-10, AH-64, Mi-8, Mi-24, Ka-50, CH-47, UH-60 etc.)
- **Ground vehicles** — team-coloured diamonds; static emplacements shown from
  first contact to end of session; units with `Base` in callsign excluded
- **Base/objective overlay** — Shelter3-driven ownership, updates in real-time;
  10nm circles for all objectives, FARPs, and factories
- **FLOT** — forward line of troops derived from ground unit positions
- **Kill feed** — player kills panel with PvP flash animation
- **Timeline scrubber** — with kill/death pips coloured by pilot team
- **Speed controls** — 1× 2× 5× 10× 30× 100× 300×
- **Player sidebar** — flight history, kill log, click-to-seek
- **Two dropdowns** — Campaign → Session, loaded from `campaigns.json` at startup

---

## Key Concepts

- **ACMI format**: Tacview's text format; objects identified by hex IDs (`b1017` etc.)
  Filenames follow `YYYYMMDD_HHMMSS.zip.acmi` convention.
- **Coalitions**: `Friendlies` = Blue/NATO · `Hostiles` = Red/PACT
- **Shelter3**: One per named base; coalition = current owner. Ownership change
  signalled by `Shelter3Construction` appearing for the opposing side.
- **Shelter3FARP**: Completed FARPs (shown as double-diamond icons).
- **Factory / FactoryBuild**: Factory structures (shown as square+cross icons).
- **Campaign**: one map variant with one or more sessions (server restarts).
- **Map detection**: Geographic centroid of waypoints matched against known
  theatre bounding boxes (Germany, Caucasus, Syria, Persian Gulf, Sinai,
  Normandy, Marianas, South Atlantic).

---

## Supported Maps

| Map | Approx. Coverage |
|---|---|
| Germany | 49–54 N, 7–14 E |
| Caucasus | 41–44 N, 40–46 E |
| Syria | 33–38 N, 35–41 E |
| Persian Gulf | 24–28 N, 50–57 E |
| Sinai | 28–32 N, 32–37 E |
| Normandy | 49–51 N, 4W–2 E |
| Marianas | 13–16 N, 144–147 E |
| South Atlantic | 49–55 S, 57–67 W |

To add a new theatre, append an entry to `MAP_DEFS` in `watch_acmi.py`.

---

## File Reference

| File | Purpose |
|---|---|
| `parse_acmi.py` | ACMI → JSON parser. Key fn: `parse_acmi()` |
| `watch_acmi.py` | Watcher, importer, campaign manager |
| `campaigns.json` | Registry of campaigns, sessions, folder bindings |
| `public/sdcs_replay.html` | Viewer — all logic in one file |
| `public/data/session_*.json` | Parsed session data |
| `raw/<folder>/` | Raw ACMI input, one subfolder per campaign |
| `.seen_acmi` | Internal dedup log (auto-managed, do not edit) |

---

## Planned / Future

- Embed into strategic-dcs.com (Django/Flask upload endpoint + `/api/campaigns`)
- Multi-session campaign timeline (sessions concatenated end-to-end)
- Base ownership history graph
- Trail gradient fade (canvas overlay)
- Shelter3 kill event detection for mid-session ownership changes

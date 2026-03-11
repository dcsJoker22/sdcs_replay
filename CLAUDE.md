# CLAUDE.md — SDCS Replay Viewer

Operational context for Claude sessions. Read this before touching anything.

---

## What This Is

Single-file HTML replay viewer for Strategic DCS campaign sessions at strategic-dcs.com.
Parser converts Tacview `.acmi` files to session JSON. Viewer is self-contained HTML + Leaflet.js.

**Repo:** `https://github.com/dcsJoker22/sdcs_replay.git` (HTTPS + PAT auth)

---

## File Locations

| File | Purpose |
|------|---------|
| `public/sdcs_replay_v1.xx.html` | Versioned releases — current is `v1.52`. Never overwrite old versions. |
| `parse_acmi.py` | ACMI → session JSON (batch or single-file) |
| `build_campaigns.py` | Scans `public/data/` and builds `public/campaigns.json` |
| `watch_acmi.py` | Live watcher — calls parse_acmi.py + build_campaigns.py on new files |
| `download_campaign.py` | Downloads ACMI files from remote |
| `public/campaigns.json` | Campaign index loaded by viewer on startup |
| `public/data/<campaign>/session_*.json` | Per-session data files |

**Version policy:** Never overwrite an existing versioned HTML file. Bump to next version (`v1.54` etc.) and write a new file.

---

## Folder Structure

```
H:\SDCS_replay\
├── public\
│   ├── sdcs_replay_v1.52.html    ← current production HTML
│   ├── campaigns.json
│   ├── Logo_4.1.png              ← actual logo filename (dot, not underscore)
│   └── data\
│       ├── 2026-01-24 Syria\
│       ├── 2026-02-03 Persian Gulf\
│       ├── 2026-02-09 CaucasusInverted\
│       ├── 2026-02-21 GermanyInverted\
│       └── 2026-02-26 Germany\
├── raw\
│   ├── 2026-01-24 Syria\
│   ├── 2026-02-03 Persian Gulf\
│   ├── 2026-02-09 CaucasusInverted\
│   ├── 2026-02-21 GermanyInverted\
│   └── 2026-02-26 Germany\
├── parse_acmi.py
├── build_campaigns.py
├── watch_acmi.py
└── download_campaign.py
```

---

## Data Pipeline

```
raw/<campaign>/*.acmi  →  parse_acmi.py  →  public/data/<campaign>/session_*.json
                                                        ↓
                                            build_campaigns.py
                                                        ↓
                                            public/campaigns.json
                                                        ↓
                                              sdcs_replay_v1.xx.html
```

---

## parse_acmi.py — Modes

```powershell
# Batch: reparse ALL campaigns (run from H:\SDCS_replay)
python parse_acmi.py

# Single file (output auto-derived from folder name)
python parse_acmi.py "raw\2026-02-26 Germany\20260226_074617.zip.acmi"

# Single file, explicit output
python parse_acmi.py input.acmi output.json
```

Input filenames may be `*.acmi` or `*.zip.acmi` — both handled correctly.
Output: `public/data/<campaign_folder>/session_<stem>.json` where stem strips `.zip.acmi` or `.acmi`.

---

## Local Dev

```powershell
python -m http.server 8080 --directory public/
# Open: http://localhost:8080/sdcs_replay_v1.52.html
```

---

## Campaign / Map IDs

| campaign_id | Theatre | Notes |
|-------------|---------|-------|
| 189 | Persian Gulf | |
| 190 | Caucasus | Standard Tacview lat/lon |
| 192 | Germany | |
| 193 | Syria (Caucasus Inverted) | |
| `syria_map` | Syria (Syria engine) | fe/fn TBD |

---

## Projection System (lon_0 / fe / fn per map)

| Map | campaign_id | lon_0 | fe | fn |
|-----|-------------|-------|-----|-----|
| Persian Gulf | 189 | 57 | 67756.00 | -2894933.00 |
| Caucasus | 190, 193 | 33 | -99161.74 | -4998101.62 |
| Germany | 192 | 21 | 26627.49 | -6062477.12 |
| Syria | syria_map | 39 | 282801.00 | -3879866.00 |

---

## Key Constants in Viewer

```javascript
const SDCS_API = null;   // map API endpoint — null until strategic-dcs.com is wired
const SCORE_EXCLUDE_KEYS = new Set(['LA44','QE40']);  // Ramstein + Laage excluded
const AI_AIRCRAFT_NAMES  = new Set(['E2-D','KC-135']);
```

**MAP_CENTRES:**
```javascript
189: {lat:26.5,  lon:55.5,  zoom:7},  // Persian Gulf
190: {lat:43.2,  lon:42.0,  zoom:7},  // Caucasus
192: {lat:51.68, lon:10.5,  zoom:7},  // Germany
193: {lat:35.5,  lon:37.5,  zoom:7},  // Syria
```

---

## Session JSON Schema

```json
{
  "meta": {
    "source_file": "20260226_074617.zip.acmi",
    "reference_time": "2026-02-26T07:46:17Z",
    "duration_seconds": 21600.0,
    "duration_hours": 6.0,
    "sample_interval": 5.0,
    "object_count": 912,
    "track_count": 418,
    "kill_count": 47,
    "player_count": 8
  },
  "objects": {
    "b1017": {
      "name": "F-16C_50",
      "category": "player_air",
      "coalition": "Friendlies",
      "color": "Blue",
      "pilot": "Joker22",
      "is_human": true,
      "first_seen": 0.0,
      "last_seen": 21600.0,
      "visible_off_t": null
    }
  },
  "tracks": {
    "b1017": [{"t": 0.0, "lat": 52.1, "lon": 10.5, "alt": 5000.0, "hdg": 270.0}]
  },
  "events": [
    {
      "type": "kill", "t": 1200.0,
      "killer": "Joker22", "weapon": "AIM-120C",
      "victim_id": "b2034", "victim_name": "Su-27", "victim_pilot": null,
      "victim_coalition": "Enemies", "victim_category": "ai_air",
      "lat": 52.3, "lon": 10.8, "alt": 7000.0
    }
  ],
  "statics": [{"id": "b0012", "name": "MA74: Frankfurt AB", "lat": 50.095, "lon": 8.703}],
  "players": {
    "Joker22": {"callsign": "Joker22", "flights": [...], "kills": [...], "deaths": 0}
  }
}
```

**`visible_off_t`** — game-time (seconds) of first `Visible=0` line for this unit, or `null` if never set. Used by the HTML viewer to fade/hide ground units that were removed from the simulation (retreated, despawned, scripted removal). More reliable than track end. Kill events are separate and still drive explosion animations.

**object categories:** `player_air`, `ai_air`, `player_weapon`, `ground`, `naval`, `navaid`, `other`

---

## Aircraft Icon System

9 icon keys, 64×64 viewBox, nose-up, rotated at runtime by heading:

| Key | Aircraft |
|-----|---------|
| `modernFW` | F-16, F/A-18, F-15, Su-27/33, MiG-29, JF-17, M-2000, F-14, J-11 |
| `legacyFW` | Su-25, MiG-21/15/19, F-4E, F-5E, Mirage F1, AJS37, C-101, L-39, MB-339, F-86, AV-8B, A-10 |
| `prop` | TF-51D, P-51D |
| `transport` | An-30, KC-30, C-130, IL-76, KC-135 |
| `awacs` | E-2D |
| `attackRW` | Ka-50, AH-64D, Mi-24P, SA342, OH-58 |
| `CH47` | CH-47 |
| `Mi8` | Mi-8MT, Mi-8MSB |
| `huey` | UH-1H |

Player icons: `stroke-width=4`, size 36px. AI icons: `stroke-width=2.5`, size 28px.

---

## DCS ACMI Naming Quirks

| Aircraft | ACMI name |
|----------|-----------|
| F/A-18C | `FA-18C_hornet` |
| F-16C block 50 | `F-16C_50` |
| AV-8B N/A | `AV8BNA` |
| E-2D Hawkeye | `E2-D` |
| AH-64D Block II | `AH-64D_BLK_II` |
| Mi-8MT | `Mi-8MT` |
| CH-47F block 1 | `CH-47Fbl1` |
| AJS-37 | `AJS37` |
| Mirage F1 variants | `MirageF1CE`, `MirageF1EE`, `MirageF1BE` |

---

## Shelter3 / Base Architecture

- Bases and objectives always rendered at `CAMPAIGN_GEODATA` coordinates (DB coords)
- Colour driven by `baseOwnerAt(key, t)` → current Shelter3 owner → last known → Neutral
- `buildShelterMap()` matches Shelter3 ACMI units to known DB locations by proximity (10nm radius)
- FARPs and Factories: ACMI-driven location, colour does not change
- `SCORE_EXCLUDE_KEYS` excludes Ramstein (`LA44`) and Laage (`QE40`) from objective count

---

## FLOT

Currently **disabled** in the HTML. Code is intact. Re-enable by restoring the `f-flot` checkbox label in the sidebar and uncommenting the `updateFLOT()` call in the render loop.

Constants when re-enabled: `CLUSTER_MIN=6`, `CLUSTER_PUSH_M=22000`, `CLUSTER_WEIGHT=14`.

---

## Known TODOs / Pending

- [ ] Wire `SDCS_API` endpoint when strategic-dcs.com map API is ready
- [ ] Re-enable FLOT when ground track data is sufficient
- [ ] Syria campaign — wire `syria_map` to correct campaign_id; calibrate fe/fn
- [ ] Embed viewer into strategic-dcs.com
- [ ] Push to GitHub

---

## Git Workflow

```powershell
git add -A
git commit -m "v1.xx - description"
git push origin main
```

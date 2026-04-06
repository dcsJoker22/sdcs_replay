# CLAUDE.md — SDCS Replay Viewer

Operational context for Claude sessions. Read this before touching anything.

---

## What This Is

Two-viewer HTML replay system for Strategic DCS campaign sessions at strategic-dcs.com.
Parser converts Tacview `.acmi` files to session JSON. Both viewers are static HTML + Leaflet.js with no build step.

**Repo:** `https://github.com/dcsJoker22/sdcs_replay` (GitHub Pages, served from root)

---

## File Locations

| File | Location | Purpose |
| --- | --- | --- |
| `index.html` | root | Session viewer — full aircraft tracks, all unit types |
| `sdcs_campaign_v1.0.html` | root | Campaign viewer — ground units only, multi-session |
| `sdcs_shared.js` | root | Shared JS library loaded by both viewers |
| `parse_acmi.py` | root | ACMI → session JSON |
| `build_campaigns.py` | root | Scans `public/data/` → `public/campaigns.json` |
| `campaign_viewer_build.py` | root | Builds per-session and index JSON for campaign viewer |
| `watch_acmi.py` | root | Live watcher — calls parse + build on new files |
| `download_campaign.py` | root | Downloads ACMI files from strategic-dcs.com |
| `public/campaigns.json` | public/ | Campaign index loaded by both viewers on startup |
| `public/Logo_4.1.png` | public/ | Logo (note: dot not underscore) |
| `public/data/<campaign>/session_*.json` | public/ | Full session data (parser output) |
| `public/data/<campaign>/campaign_session_*.json` | public/ | Stripped per-session data (campaign viewer) |
| `public/data/<campaign>/campaign_index_*.json` | public/ | Lightweight campaign index (campaign viewer) |

---

## Folder Structure

```
H:\SDCS_replay\
├── index.html
├── sdcs_campaign_v1.0.html
├── sdcs_shared.js
├── parse_acmi.py
├── build_campaigns.py
├── campaign_viewer_build.py
├── watch_acmi.py
├── download_campaign.py
├── CLAUDE.md
├── README.md
└── public\
    ├── campaigns.json
    ├── Logo_4.1.png
    └── data\
        ├── 2026-01-24 Syria\
        │   ├── session_*.json
        │   ├── campaign_session_*.json
        │   └── campaign_index_2026-01-24 Syria.json
        ├── 2026-02-03 Persian Gulf\
        ├── 2026-02-09 CaucasusInverted\
        ├── 2026-02-21 GermanyInverted\
        ├── 2026-02-26 Germany\
        └── 2026-03-05 Caucasus\
```

---

## Architecture — Two Viewers

### `index.html` — Session Viewer
- Loads one session at a time from `public/campaigns.json` + `public/data/<campaign>/session_*.json`
- Full aircraft tracks, weapon tracks, ground units, bases, kill feed, kill heatmap
- URL persistence: `?campIdx=N&sessIdx=N` restored on reload
- Shared functions loaded from `sdcs_shared.js`

### `sdcs_campaign_v1.0.html` — Campaign Viewer
- Loads `campaign_index_<folder>.json` first (lightweight), then all `campaign_session_*.json` in parallel
- Per-session architecture: no cross-session ID stitching — each session is isolated
- Ground units + SAM units + Shelter3/FARP/Factory + kills only (no aircraft)
- Active session swapped as playback crosses session boundaries via `activateSession()`
- Kill heatmap uses `_allEvents` from the campaign index (all kills across all sessions)
- Bases reinit on every session switch (FARPs change between sessions)
- Shared functions loaded from `sdcs_shared.js`

---

## `sdcs_shared.js` — What Lives Here

Constants and functions shared between both viewers:
- `CAMPAIGN_GEODATA` — base/objective DB coordinates per campaign
- `SCORE_EXCLUDE_KEYS` — bases excluded from objective count (keyed as `'airbase_<Name>'`)
- `MAP_CENTRES` — default map centre/zoom per campaign_id
- `AC_ICONS` — aircraft name → icon key mapping
- `iconKey()`, `makeGroundDiamond()`, `makeACSVG()`, `leafletIcon()`
- `trackIdxAt()`, `haverKm()`, `fmtT()`, `fmtDur()`, `pad()`, `setLoad()`
- `NM10` constant
- `buildShelterMap()`, `buildGroundKillTimes()`, `baseOwnerAt()`
- `STRUCT_NAMES`, `isSAMUnit()`, `samDisplayName()`, `isGroundVehicle()`, `isNamedAircraft()`
- `initBases()`, `drawBase()`
- `isWpn()`, `addKillFeedEntry()`, `updateKillFeed()`, `spawnExp()`

`UI_SCALE` is NOT in shared.js — each viewer manages its own.

---

## Build Pipeline

```
# Parse new ACMI files
python parse_acmi.py

# Rebuild campaign index (required after parse)
python build_campaigns.py

# Build campaign viewer files
python campaign_viewer_build.py
# or single campaign:
python campaign_viewer_build.py --campaign "2026-03-05 Caucasus"
```

`campaign_viewer_build.py` outputs:
- `campaign_session_YYYYMMDD_HHMMSS.json` — one per session, stripped data
- `campaign_index_<folder>.json` — lightweight index with session metadata + all kill events

---

## Campaign / Map IDs

| campaign_id | Theatre |
| --- | --- |
| 185 | Syria |
| 189 | Persian Gulf |
| 190 | Caucasus |
| 192 | Germany |
| 193 | Caucasus Inverted |

---

## Key Constants

```js
const SDCS_API = null;          // map API — null until strategic-dcs.com is wired
const SCORE_EXCLUDE_KEYS = new Set([  // excluded from objective count
  'airbase_Ramstein', 'airbase_Laage',           // Germany
  'airbase_Vaziani', 'airbase_Anapa-Vityazevo',  // Caucasus
  'airbase_Jiroft', 'airbase_Liwa AFB',          // Persian Gulf
  'airbase_Gaziantep', 'airbase_Ben Gurion',     // Syria
]);
const AI_AIRCRAFT_NAMES  = new Set(['E2-D','KC-135']);
const NM10 = 18.52;             // 10 nautical miles in km
```

MAP_CENTRES (in sdcs_shared.js):
```js
189: {lat:26.5,  lon:55.5,  zoom:7},   // Persian Gulf
190: {lat:43.2,  lon:42.0,  zoom:7},   // Caucasus
192: {lat:51.68, lon:10.5,  zoom:7},   // Germany
193: {lat:35.5,  lon:37.5,  zoom:7},   // Syria
```

---

## Session JSON Schema

```json
{
  "meta": {
    "source_file": "20260305_065846.zip.acmi",
    "reference_time": "2026-03-05T06:58:46Z",
    "duration_seconds": 21604.0,
    "sample_interval": 5.0,
    "object_count": 1027,
    "kill_count": 93,
    "player_count": 12
  },
  "objects": {
    "b1017": {
      "name": "F-16C_50",
      "category": "player_air",
      "coalition": "Friendlies",
      "pilot": "Joker22",
      "is_human": true,
      "first_seen": 0.0,
      "last_seen": 21600.0,
      "visible_off_t": null
    }
  },
  "tracks": { "b1017": [{"t":0.0,"lat":43.2,"lon":42.0,"alt":5000.0,"hdg":270.0}] },
  "events": [
    {
      "type": "kill", "t": 1200.0,
      "killer": "Joker22", "weapon": "AIM-120C",
      "victim_id": "b2034", "victim_name": "Su-27",
      "victim_coalition": "Hostiles", "victim_category": "ai_air",
      "lat": 43.3, "lon": 42.1, "alt": 7000.0
    }
  ],
  "statics": [{"id":"b0012","name":"MA74: Tbilisi","lat":41.669,"lon":44.954}],
  "players": { "Joker22": {"callsign":"Joker22","flights":[],"kills":[],"deaths":0} }
}
```

**`visible_off_t`** — game-time seconds of first `Visible=0` for this unit, or null. Used to fade/hide ground units that despawned or retreated.

**Object categories:** `player_air`, `ai_air`, `player_weapon`, `ground`, `naval`, `navaid`, `other`

**Coalitions:** `Friendlies` (Blue), `Hostiles` (Red)

---

## Campaign Session JSON Schema

Stripped version written by `campaign_viewer_build.py`:

```json
{
  "meta": {"offset": 0.0, "duration": 21604.0},
  "objects": { "b1017": { ... } },
  "tracks":  { "b1017": [{"t":0.0,"lat":43.2,"lon":42.0}] },
  "events":  [ { "type":"kill", "t":1200.0, ... } ],
  "statics": [ { "name":"MA74: Tbilisi", "lat":41.669, "lon":44.954 } ]
}
```

Ground tracks subsampled to 60s intervals, 4 decimal place precision.
Only ground vehicles, SAM units, Shelter3/FARP/Factory, and kills are included.

---

## Campaign Index JSON Schema

```json
{
  "total_duration": 475174.0,
  "session_index": [
    {
      "file": "data/2026-03-05 Caucasus/campaign_session_20260305_065846.json",
      "label": "session_20260305_065846.json",
      "date": "2026-03-05",
      "offset": 0.0,
      "duration": 21604.0,
      "reference_time": "2026-03-05T06:58:46Z",
      "player_kills_blue": 93,
      "player_kills_red": 0
    }
  ],
  "events": [ { "type":"kill", "t":1200.0, "lat":43.3, "lon":42.1, ... } ]
}
```

---

## Shelter3 / Base Architecture

- Bases and objectives always rendered at `CAMPAIGN_GEODATA` coordinates (DB coords)
- Colour driven by `baseOwnerAt(key, t)` → current Shelter3 owner → last known → Neutral
- `buildShelterMap()` matches Shelter3 ACMI units to DB locations by proximity (10nm radius)
- FARPs: ACMI-driven location, appear/disappear by `first_seen`/`visible_off_t`
- Factories: same as FARPs
- `SCORE_EXCLUDE_KEYS` excludes specific bases per theatre from objective count (keyed as `'airbase_<Name>'`)
- Campaign viewer reinits bases on every session switch

---

## Aircraft Icon System

9 icon keys, 64×64 viewBox, nose-up, rotated at runtime by heading:

| Key | Aircraft |
| --- | --- |
| `modernFW` | F-16, F/A-18, F-15, Su-27/33, MiG-29, JF-17, M-2000, F-14, J-11 |
| `legacyFW` | Su-25, MiG-21/15/19, F-4E, F-5E, Mirage F1, AJS37, A-10, AV-8B |
| `prop` | TF-51D, P-51D |
| `transport` | An-30, KC-30, C-130, IL-76, KC-135 |
| `awacs` | E-2D |
| `attackRW` | Ka-50, AH-64D, Mi-24P, SA342, OH-58 |
| `CH47` | CH-47 |
| `Mi8` | Mi-8MT |
| `huey` | UH-1H |

---

## FLOT

Currently **disabled**. Code intact in `index.html`. Re-enable by restoring `f-flot` checkbox and uncommenting `updateFLOT(t)` in the render loop. Constants: `CLUSTER_MIN=6`, `CLUSTER_PUSH_M=22000`, `CLUSTER_WEIGHT=14`.

---

## Known TODOs

- Wire `SDCS_API` endpoint when strategic-dcs.com map API is ready
- Re-enable FLOT when ground track data is sufficient
- Syria campaign — calibrate `campaign_id` and fe/fn projection
- Embed viewers into strategic-dcs.com
- Performance optimisation pass (deferred)

---

## Git Workflow

```
git add -A
git commit -m "description of changes"
git push
```

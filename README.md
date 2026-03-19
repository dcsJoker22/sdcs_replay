# SDCS Campaign Replay Viewer

Interactive web-based replay of [Strategic DCS](https://strategic-dcs.com) campaign sessions. Displays aircraft tracks, ground units, base ownership, kill events, kill heatmap, objective progress, and pilot telemetry on a live map.

## Live Demo

Hosted at [strategic-dcs.com](https://strategic-dcs.com) — currently in development.

---

## Stack

| Component | Technology |
| --- | --- |
| Parser | Python 3 — converts Tacview `.acmi` files to session JSON |
| Session Viewer | `index.html` — single-session replay with full aircraft tracks |
| Campaign Viewer | `sdcs_campaign_v1.0.html` — multi-session campaign overview, ground units only |
| Shared Library | `sdcs_shared.js` — constants and functions shared between both viewers |
| Data | Pre-processed JSON files served statically |
| Hosting | GitHub Pages (root) |

---

## Project Structure

```
sdcs_replay/                          ← root (GitHub Pages serves from here)
├── index.html                        ← session viewer
├── sdcs_campaign_v1.0.html           ← campaign viewer
├── sdcs_shared.js                    ← shared JS library (loaded by both viewers)
├── parse_acmi.py                     ← converts .acmi → session JSON
├── build_campaigns.py                ← scans public/data/ → writes campaigns.json
├── build_campaign_viewer.py          ← builds campaign_session_*.json + campaign_index_*.json
├── watch_acmi.py                     ← auto-parses new .acmi files on save
├── download_campaign.py              ← downloads campaign files from strategic-dcs.com
├── CLAUDE.md                         ← Claude project instructions
├── .gitignore
├── README.md
└── public/
    ├── campaigns.json                ← campaign index (generated)
    ├── Logo_4.1.png
    └── data/
        └── YYYY-MM-DD CampaignName/
            ├── session_*.json                       ← full session data (parser output)
            ├── campaign_session_YYYYMMDD_HHMMSS.json ← stripped per-session (campaign viewer)
            └── campaign_index_YYYY-MM-DD CampaignName.json ← lightweight campaign index
```

---

## Setup

### Requirements

```
pip install watchdog   # for watch_acmi.py only — no other dependencies
```

---

## Full Pipeline (new campaign)

### 1. Download raw ACMI files

```
python download_campaign.py
```

At the prompt enter the campaign URL from `https://strategic-dcs.com/tacview/`. Files are saved to `raw/<campaign folder>/`.

### 2. Parse ACMI files

```
# Batch — parses everything in raw/ and writes to public/data/
python parse_acmi.py

# Single file
python parse_acmi.py "raw\2026-03-05 Caucasus\20260305_065846.zip.acmi"
```

Both `.acmi` and `.zip.acmi` formats are handled. Output: `public/data/<campaign>/session_<stem>.json`

### 3. Build campaign index

```
python build_campaigns.py
```

Scans all `public/data/*/session_*.json` and writes `public/campaigns.json`.

### 4. Build campaign viewer files

```
# All campaigns
python build_campaign_viewer.py

# Single campaign
python build_campaign_viewer.py --campaign "2026-03-05 Caucasus"
```

Writes one `campaign_session_<stem>.json` per session and one `campaign_index_<folder>.json` per campaign into each campaign folder.

---

## Adding a New Campaign

1. Run `python download_campaign.py` and enter the campaign URL
2. Run `python parse_acmi.py` (batch)
3. Run `python build_campaigns.py`
4. Run `python build_campaign_viewer.py`

Folder name auto-detection:

| Folder contains | Theatre | campaign_id |
| --- | --- | --- |
| `Caucasus` | Caucasus | 190 |
| `Germany` | Germany | 192 |
| `Syria` | Syria | 185 |
| `Gulf` or `Persian` | Persian Gulf | 189 |

---

## Data Pipeline

```
raw/<campaign>/*.zip.acmi
        │
        ▼
  parse_acmi.py
        │
        ▼
public/data/<campaign>/session_<stem>.json
        │
        ├──► build_campaigns.py ──► public/campaigns.json
        │                                    │
        │                               index.html
        │
        └──► build_campaign_viewer.py
                    │
                    ├──► campaign_session_<stem>.json  (one per session)
                    └──► campaign_index_<folder>.json  (one per campaign)
                                    │
                             sdcs_campaign_v1.0.html
```

---

## Viewer Features

### Session Viewer (`index.html`)
- Campaign and session selectors, newest session pre-selected, URL persistence on reload
- 9 SVG aircraft silhouettes with heading rotation and smooth interpolation
- Altitude and Mach telemetry labels
- Air-launched weapon tracks (missiles, bombs, rockets)
- Kill events with explosion animations and PvP highlighting in kill feed
- Kill heatmap (3hr fade, toggleable)
- Ground unit diamonds with fade on despawn
- Base and objective ownership tracking via Shelter3 events
- Objective progress bars (blue vs red)
- Player detail panel with kill log, closes on map click
- Filters: player aircraft, AI aircraft, ground units, labels, trails, kills, heatmap, bases, FARPs, weapons
- UI scale slider

### Campaign Viewer (`sdcs_campaign_v1.0.html`)
- Per-session architecture — no cross-session ID stitching, clean unit data per session
- Ground units and SAM systems only (no aircraft tracks)
- Base and objective ownership tracking
- Kill heatmap across entire campaign (3hr fade)
- Kill feed and player list (sorted A-Z or by kills)
- Session boundary markers on timeline scrubber
- Campaign kill counter increments live with playback
- Speed options up to 1000×
- Links to Live Map and session viewer

---

## Local Dev

Open either HTML file with VS Code Live Server from the project root.

---

## Git Workflow

```
git add -A
git commit -m "description of changes"
git push
```

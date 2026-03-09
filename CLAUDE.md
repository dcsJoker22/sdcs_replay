# CLAUDE.md — SDCS Replay Viewer

Operational context for Claude Code sessions. Read this before touching anything.

---

## What This Is

Single-file HTML replay viewer for Strategic DCS campaign sessions at strategic-dcs.com.
Parser converts Tacview `.acmi` files to session JSON. Viewer is self-contained HTML + Leaflet.js.

**Repo:** `https://github.com/dcsJoker22/sdcs_replay.git` (HTTPS + PAT auth)

---

## File Locations

| File | Purpose |
|------|---------|
| `public/sdcs_replay_current.html` | Working copy — always edit this, never a versioned copy |
| `public/sdcs_replay_v1.xx.html` | Versioned release copies — output only |
| `parser/parse_acmi.py` | ACMI → session JSON |
| `parser/watch_acmi.py` | v1.1 live watcher |
| `parser/build_campaigns.py` | Builds campaigns.json index |
| `data/campaigns.json` | Campaign index loaded by viewer on startup |
| `data/session_*.json` | Session data files |

**Version bumping:** Edit version strings inside `sdcs_replay_current.html`, then `cp` to `sdcs_replay_v1.xx.html`. Never rename the working file.

---

## Campaign IDs

| ID | Theatre | Notes |
|----|---------|-------|
| 189 | Persian Gulf | |
| 190 | Caucasus | |
| 192 | Germany | Custom map — Syria engine with affine transform |
| 193 | Syria | Custom map — Caucasus engine with affine transform |

---

## Coordinate Transforms (DCS U/V → WGS84)

**Germany (campaign 192):**
```
lat = 1.26495422e-06*u + 8.84543105e-06*v + 55.06735108
lon = 1.42836218e-05*u + -2.10144742e-06*v + 19.90626026
```

Other theatres (Caucasus, PG, Syria) use standard Tacview lat/lon — no transform needed.

---

## Key Constants in Viewer

```javascript
const SDCS_API = null;                    // map API endpoint — null = use hardcoded data
const SCORE_EXCLUDE_KEYS = new Set(['LA44','QE40']);  // Ramstein + Laage excluded from obj count
```

**Filters default state:**
```javascript
{ playerAir:true, aiAir:true, ground:true, groundLabels:false,
  trails:true, kills:true, bases:true, flot:true }
```

**FLOT** is currently disabled (`CLUSTER_MIN=6`, `CLUSTER_PUSH_M=22000`, `CLUSTER_WEIGHT=14` when re-enabled).

---

## Aircraft Icon System

**9 icon keys** (all 64×64 viewBox, nose-up, rotated at runtime):

| Key | Aircraft |
|-----|---------|
| `modernFW` | F-16, F/A-18, F-15, Su-27, Su-33, MiG-29, JF-17, M-2000, F-14, J-11 |
| `legacyFW` | Su-25, MiG-21/15/19, F-4E, F-5E, Mirage F1, AJS37, C-101, L-39, MB-339, F-86, AV-8B, A-10 |
| `prop` | TF-51D, P-51D |
| `transport` | An-30, KC-30, C-130, IL-76, KC-135 |
| `awacs` | E-2D (ACMI name: `E2-D`, `E2 A xxx`) |
| `attackRW` | Ka-50, AH-64D, Mi-24P, SA342, OH-58 |
| `CH47` | CH-47D, CH-47Fbl1 |
| `Mi8` | Mi-8MT, Mi-8MSB |
| `huey` | UH-1H |

**Rendering:** Both player and AI icons get black outline. Player: `stroke-width=4`, AI: `stroke-width=2.5`. Outline group must set `style="color:#000"` to override `currentColor` inheritance.

**Icon sizes:** Player `36px`, AI `28px`.

**Label sizes:** Player name `16px`, AI name `12px`. AI anchor is 4px lower than player (`iconAnchor:[-20,38]` vs `[-20,34]`).

---

## DCS Naming Quirks (ACMI)

These differ from what you'd expect — confirmed from real session data:

| Aircraft | ACMI name |
|----------|-----------|
| F/A-18C | `FA-18C_hornet` (underscore, no slash) |
| F-16C block 50 | `F-16C_50` |
| AV-8B N/A | `AV8BNA` (no hyphens or spaces) |
| E-2D Hawkeye | `E2-D` (no hyphen between E and 2) |
| E-2 AI orbit | `E2 A 270/15 FL300` (bearing/alt suffix) |
| AH-64D Block II | `AH-64D_BLK_II` |
| Mi-8MT | `Mi-8MT` |
| CH-47F block 1 | `CH-47Fbl1` |
| AJS-37 | `AJS37` (no hyphen) |
| Mirage F1 variants | `MirageF1CE`, `MirageF1EE`, `MirageF1BE` (no space/hyphen) |

`iconKey()` is lowercase `.includes()` based. **Order matters** — su-25 before su-27, mig-15/19/21 before mig-29, f-15 before any f-5 risk.

---

## SAM / AI Unit Detection

SAM units are `ai_air` category in DCS. Detection logic (`isSAMUnit()`):
- If name is in `SAM_STANDALONE` set → SAM
- If name has a dash-prefix that's NOT in `AIRCRAFT_PREFIXES` → SAM
- `AI_AIRCRAFT_NAMES = new Set(['E2-D','KC-135'])` — explicit allowlist for edge cases

`AIRCRAFT_PREFIXES = ['FA','CH','An','UH','AH','Mi','Ka','Su','MiG','Tu','IL','A','B']`

---

## Pilot Name Sanitisation

DCS sometimes appends `- interpolated` to pilot names. Stripped in two places:
1. Player key lookup during `mergeSessions()`
2. Pass over all `obj.pilot` fields after merge

Pattern: `/\s*-\s*interpolated\s*$/i`

Also strip `\s*\(\d+\)$` (duplicate numbering suffix).

---

## Base / Objective Data

Hardcoded in `CAMPAIGN_GEODATA` in the viewer. Coordinates for campaign 192 (Germany) are derived via affine transform from the DB `pos_u`/`pos_v` columns. All 18 Germany bases are verified correct. 9 objectives were corrected in v1.29 from bad manual coords.

**DB source columns:** `airbase.pos_u`, `airbase.pos_v`, `campaign_objectives.pos_u`, `campaign_objectives.pos_v`

`ORPHAN_BASE_NAMES` handles Shelter3 units with no named static nearby (Germany campaign only).

---

## Session JSON Schema (abbreviated)

```json
{
  "objects": {
    "b1017": {
      "name": "F-16C_50",
      "category": "player_air",
      "coalition": "Friendlies",
      "pilot": "Callsign",
      "is_human": true,
      "first_seen": 0.0,
      "last_seen": 3600.0
    }
  },
  "tracks": {
    "b1017": [{"t": 0.0, "lat": 52.1, "lon": 10.5, "alt": 5000, "hdg": 270}]
  },
  "events": [
    {"type": "kill", "t": 1200.0, "killer_id": "b1017", "victim_id": "b2034",
     "killer_pilot": "Callsign", "victim_pilot": null,
     "killer_name": "F-16C_50", "victim_name": "Su-27",
     "killer_category": "player_air", "victim_category": "ai_air",
     "lat": 52.3, "lon": 10.8}
  ],
  "statics": [{"name": "MA74: Frankfurt AB", "lat": 50.095, "lon": 8.703}],
  "players": {
    "Callsign": {"callsign": "Callsign", "flights": [...], "kills": [...], "deaths": 0}
  }
}
```

---

## Local Dev

```bash
python3 -m http.server 8080 --directory public/
# Open: http://localhost:8080/sdcs_replay_current.html
```

Load session data by editing `SESSIONS` array in the viewer, or point `SDCS_API` at a local endpoint.

---

## Git Workflow

```bash
git add -A
git commit -m "v1.xx - description"
git push origin main
# HTTPS auth with PAT
```

---

## Known TODOs

- Wire `SDCS_API` endpoint when strategic-dcs.com map API is ready
- Re-enable FLOT (`CLUSTER_MIN=6`, `CLUSTER_PUSH_M=22000`, `CLUSTER_WEIGHT=14`)
- Improve coordinate transforms for Caucasus, Syria, Persian Gulf
- Embed viewer into strategic-dcs.com

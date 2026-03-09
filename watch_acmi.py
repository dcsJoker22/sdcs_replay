#!/usr/bin/env python3
"""
SDCS ACMI Watcher & Importer
─────────────────────────────
Monitors subfolders of raw/ for new ACMI files. Each subfolder maps to one
campaign — set up once interactively, then fully automatic thereafter.

Usage
─────
  python watch_acmi.py watch          Watch raw/ subfolders continuously
  python watch_acmi.py import FILE    Import a single file (prompted)
  python watch_acmi.py list           Show all campaigns and sessions
  python watch_acmi.py campaigns      Manage campaigns (rename / delete)

Folder layout
─────────────
  sdcs-replay/
  ├── watch_acmi.py
  ├── parse_acmi.py
  ├── campaigns.json          auto-managed registry
  ├── raw/
  │   ├── germany_v1/         one subfolder = one campaign
  │   │   ├── 20260226_074617.zip.acmi
  │   │   └── 20260301_080845.zip.acmi
  │   ├── germany_v2/
  │   └── caucasus_v1/
  └── public/
      └── data/               parsed session JSONs

First time the watcher sees a new subfolder it asks you to name the campaign
and confirm the map. Every file dropped in after that is imported automatically
with no prompts — just drop and go.

Map detection
─────────────
Detected from geographic centroid of waypoints. Extend MAP_DEFS for new theatres:
  Germany, Caucasus, Syria, Persian Gulf, Sinai, Normandy, Marianas, South Atlantic
"""

import os
import sys
import io
import json
import time
import zipfile
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# Force UTF-8 output on Windows (cp1252 can't print ✓ ✗ → etc.)
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

if sys.version_info < (3, 6):
    sys.exit('Python 3.6+ required.')

# ─────────────────────────────────────────────────────────────────────────────
#  Paths
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent.resolve()
RAW_DIR     = BASE_DIR / 'raw'
DATA_DIR    = BASE_DIR / 'public' / 'data'
CAMPAIGNS_F = BASE_DIR / 'public' / 'campaigns.json'   # served alongside the viewer
PARSER_F    = BASE_DIR / 'parse_acmi.py'
SEEN_F      = BASE_DIR / '.seen_acmi'

# ─────────────────────────────────────────────────────────────────────────────
#  Known map / theatre bounding boxes  (lat_min, lat_max, lon_min, lon_max)
# ─────────────────────────────────────────────────────────────────────────────
MAP_DEFS = [
    ('Germany',        49,  54,   7,  14),
    ('Caucasus',       41,  44,  40,  46),
    ('Syria',          33,  38,  35,  41),
    ('Persian Gulf',   24,  28,  50,  57),
    ('Sinai',          28,  32,  32,  37),
    ('Normandy',       49,  51,  -4,   2),
    ('Marianas',       13,  16, 144, 147),
    ('South Atlantic',-55, -49, -67, -57),
]

# ─────────────────────────────────────────────────────────────────────────────
#  Terminal colours
# ─────────────────────────────────────────────────────────────────────────────
_C = {
    'reset':'\033[0m','bold':'\033[1m','dim':'\033[2m',
    'blue':'\033[34m','cyan':'\033[36m','green':'\033[32m',
    'yellow':'\033[33m','red':'\033[31m',
}
def c(colour, text):
    return _C.get(colour, '') + str(text) + _C['reset']

def banner():
    print()
    print(c('cyan', '╔══════════════════════════════════════════╗'))
    print(c('cyan', '║') + c('bold', '   SDCS ACMI Watcher & Importer  v1.1   ') + c('cyan', '║'))
    print(c('cyan', '╚══════════════════════════════════════════╝'))
    print()

# ─────────────────────────────────────────────────────────────────────────────
#  campaigns.json  helpers
# ─────────────────────────────────────────────────────────────────────────────
def load_campaigns():
    if CAMPAIGNS_F.exists():
        with open(CAMPAIGNS_F, encoding='utf-8') as f:
            return json.load(f)
    return {'campaigns': [], 'folder_bindings': {}}

def save_campaigns(data):
    CAMPAIGNS_F.parent.mkdir(parents=True, exist_ok=True)
    with open(CAMPAIGNS_F, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(c('green', '  ✓ campaigns.json updated'))

def get_campaign(data, campaign_id):
    for camp in data['campaigns']:
        if camp['id'] == campaign_id:
            return camp
    return None

def session_exists(data, json_filename):
    for camp in data['campaigns']:
        for sess in camp.get('sessions', []):
            if sess['file'] == json_filename:
                return True
    return False

# folder_bindings maps  subfolder-name → campaign_id
def get_binding(data, folder_name):
    return data.get('folder_bindings', {}).get(folder_name)

def set_binding(data, folder_name, campaign_id):
    data.setdefault('folder_bindings', {})[folder_name] = campaign_id

# ─────────────────────────────────────────────────────────────────────────────
#  .seen_acmi  dedup tracking
# ─────────────────────────────────────────────────────────────────────────────
def load_seen():
    if SEEN_F.exists():
        with open(SEEN_F, encoding='utf-8') as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def mark_seen(path_str):
    with open(SEEN_F, 'a', encoding='utf-8') as f:
        f.write(path_str + '\n')

# ─────────────────────────────────────────────────────────────────────────────
#  Map detection
# ─────────────────────────────────────────────────────────────────────────────
def detect_map(acmi_path):
    """Returns (map_name, confidence 0-1) from geographic centroid of waypoints."""
    lines = _read_lines(acmi_path, max_lines=2000)
    lats, lons = [], []
    for line in lines:
        if ('Waypoint' not in line and 'Navaid' not in line) or 'T=' not in line:
            continue
        try:
            t_part = line.split('T=')[1].split(',')[0]
            parts = t_part.split('|')
            lon_v = float(parts[0]) if parts[0] else None
            lat_v = float(parts[1]) if len(parts) > 1 and parts[1] else None
            if lon_v is not None and lat_v is not None:
                lats.append(lat_v); lons.append(lon_v)
        except (IndexError, ValueError):
            pass
    if not lats:
        return ('Unknown', 0.0)
    clat = sum(lats) / len(lats)
    clon = sum(lons) / len(lons)
    best_name, best_score = 'Unknown', 0.0
    for name, la, lb, lo, lp in MAP_DEFS:
        if la <= clat <= lb and lo <= clon <= lp:
            score = 1.0
        else:
            dlat = max(0, la - clat, clat - lb)
            dlon = max(0, lo - clon, clon - lp)
            score = max(0.0, 1.0 - (dlat + dlon) / 10.0)
        if score > best_score:
            best_score = score; best_name = name
    return (best_name, round(best_score, 2))

def _read_lines(path, max_lines=None):
    path = Path(path)
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            raw = z.read(z.namelist()[0]).decode('utf-8', errors='replace')
    else:
        raw = path.read_text(encoding='utf-8', errors='replace')
    lines = raw.splitlines()
    return lines[:max_lines] if max_lines else lines

# ─────────────────────────────────────────────────────────────────────────────
#  Filename → datetime
# ─────────────────────────────────────────────────────────────────────────────
def parse_filename_dt(filename):
    """Handle 20260301_080845.zip.acmi / .zip / .acmi / _zip.acmi variants."""
    stem = Path(filename).stem
    stem = re.sub(r'\.zip$', '', stem)
    stem = re.sub(r'_zip$',  '', stem)
    m = re.match(r'^(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})$', stem)
    if m:
        yr, mo, dy, hr, mn, sc = (int(x) for x in m.groups())
        return datetime(yr, mo, dy, hr, mn, sc, tzinfo=timezone.utc)
    return None

def session_label(dt, duration_hours):
    if dt:
        dur = f'{duration_hours:.1f}h' if duration_hours else ''
        base = dt.strftime('%d %b %Y · %H:%Mz')
        return f'{base}  ({dur})' if dur else base
    return 'Unknown Session'

# ─────────────────────────────────────────────────────────────────────────────
#  Parser subprocess
# ─────────────────────────────────────────────────────────────────────────────
def run_parser(acmi_path, out_path):
    if not PARSER_F.exists():
        raise FileNotFoundError(f'parse_acmi.py not found at {PARSER_F}')
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(c('dim', '  → Running parse_acmi.py…'))
    result = subprocess.run(
        [sys.executable, str(PARSER_F), str(acmi_path), str(out_path)],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    if result.returncode != 0:
        print(c('red', '  Parser stderr:'))
        print(result.stderr[-2000:])
        raise RuntimeError(f'parse_acmi.py exited with code {result.returncode}')
    for line in result.stdout.splitlines():
        print(c('dim', f'    {line}'))
    with open(out_path, encoding='utf-8') as f:
        return json.load(f)

# ─────────────────────────────────────────────────────────────────────────────
#  File detection
# ─────────────────────────────────────────────────────────────────────────────
def is_acmi_file(path):
    path = Path(path)
    name = path.name.lower()
    if not (name.endswith('.acmi') or name.endswith('.zip')):
        return False
    if zipfile.is_zipfile(path):
        try:
            with zipfile.ZipFile(path) as z:
                return any(n.endswith('.acmi') for n in z.namelist())
        except Exception:
            return False
    return name.endswith('.acmi')

def file_stable(path, wait=2.0):
    path = Path(path)
    try:
        s1 = path.stat().st_size
        time.sleep(wait)
        return path.stat().st_size == s1 and s1 > 0
    except FileNotFoundError:
        return False

def clean_stem(filename):
    """Strip all ACMI-related extensions to get bare YYYYMMDD_HHMMSS."""
    stem = Path(filename).stem
    stem = re.sub(r'\.zip$', '', stem)
    stem = re.sub(r'_zip$',  '', stem)
    return stem

# ─────────────────────────────────────────────────────────────────────────────
#  Interactive: create a new campaign
# ─────────────────────────────────────────────────────────────────────────────
def create_campaign(data, suggested_map='Unknown', suggested_name=''):
    """Prompt for name + map, append to data['campaigns'], return the new camp dict."""
    print()
    print(c('bold', '  New campaign'))
    print()

    # Map selection
    map_names = [m[0] for m in MAP_DEFS] + ['Other']
    print(c('dim', '  Available maps:'))
    for i, m in enumerate(map_names, 1):
        tag = c('yellow', '  <- detected') if m == suggested_map else ''
        print(f"    {c('cyan', str(i))}.  {m}{tag}")
    print()

    map_choice = suggested_map
    while True:
        raw = input(f'  Map [1-{len(map_names)}] (Enter = {suggested_map}): ').strip()
        if not raw:
            break
        if raw.isdigit() and 1 <= int(raw) <= len(map_names):
            map_choice = map_names[int(raw) - 1]
            if map_choice == 'Other':
                map_choice = input('  Map name: ').strip() or 'Unknown'
            break

    # Campaign name
    default_name = suggested_name or f'{map_choice} Campaign'
    name = input(f'  Campaign name [{default_name}]: ').strip() or default_name

    # Optional version tag
    version = input('  Version/descriptor (e.g. v2, REDFOR Push) [blank to skip]: ').strip()
    if version:
        name = f'{name} – {version}'

    # Generate unique id
    new_id = re.sub(r'[^a-z0-9_]', '_', name.lower())[:40]
    existing = {c_['id'] for c_ in data['campaigns']}
    base, n = new_id, 2
    while new_id in existing:
        new_id = f'{base}_{n}'; n += 1

    camp = {'id': new_id, 'name': name, 'map': map_choice, 'sessions': []}
    data['campaigns'].append(camp)
    print(c('green', f'  ✓ Created campaign: {name}'))
    return camp

# ─────────────────────────────────────────────────────────────────────────────
#  Interactive: bind a new subfolder to a campaign (or create one)
# ─────────────────────────────────────────────────────────────────────────────
def setup_folder_binding(data, folder_name, suggested_map):
    """
    Called the first time the watcher sees a new subfolder.
    Asks the user to pick or create a campaign, saves the binding, returns camp.
    """
    print()
    print(c('cyan',  '  ┌─────────────────────────────────────────────┐'))
    print(c('cyan',  '  │') + c('bold', f'  New folder detected: raw/{folder_name:<28}') + c('cyan', '│'))
    print(c('cyan',  '  └─────────────────────────────────────────────┘'))
    print()
    print(c('dim',   f'  Detected map: {suggested_map}'))
    print()
    print(c('bold',  '  Which campaign should files in this folder belong to?'))
    print()

    campaigns = data['campaigns']
    for i, camp in enumerate(campaigns, 1):
        scount = len(camp.get('sessions', []))
        map_tag = c('dim', '[' + camp['map'] + ']')
        sess_tag = c('dim', str(scount) + (' sessions' if scount != 1 else ' session'))
        print(f"    {c('cyan', str(i))}.  {camp['name']}  {map_tag}  {sess_tag}")

    print(f"    {c('cyan', str(len(campaigns) + 1))}.  {c('yellow', 'Create new campaign…')}")
    print()

    while True:
        raw = input(f'  Choice [1-{len(campaigns) + 1}]: ').strip()
        if not raw.isdigit():
            continue
        choice = int(raw)
        if 1 <= choice <= len(campaigns):
            camp = campaigns[choice - 1]
            break
        if choice == len(campaigns) + 1:
            # Suggest a name based on the folder name (replace underscores/hyphens)
            suggested_name = folder_name.replace('_', ' ').replace('-', ' ').title()
            camp = create_campaign(data, suggested_map, suggested_name)
            break

    set_binding(data, folder_name, camp['id'])
    save_campaigns(data)
    print()
    print(c('green', f'  ✓ Folder raw/{folder_name}  →  campaign: {camp["name"]}'))
    print(c('dim',   '    Future files here will be imported automatically.'))
    print()
    return camp

# ─────────────────────────────────────────────────────────────────────────────
#  Core import
# ─────────────────────────────────────────────────────────────────────────────
def import_file(acmi_path, campaign_id=None):
    """
    Parse one ACMI file and register it.
    campaign_id: if given, skip the chooser prompt (used by watch_mode).
    Returns True on success.
    """
    acmi_path = Path(acmi_path).resolve()
    if not acmi_path.exists():
        print(c('red', f'  File not found: {acmi_path}'))
        return False

    print()
    print(c('bold', f'  Importing: {acmi_path.name}'))

    dt = parse_filename_dt(acmi_path.name)
    if dt:
        print(c('dim', f'  Session time: {dt.strftime("%Y-%m-%d %H:%M:%S UTC")}'))

    # Map detection — always run it (shown for info even in auto mode)
    print(c('dim', '  Detecting map…'))
    map_name, confidence = detect_map(acmi_path)
    conf_str = f'{confidence*100:.0f}%'
    col = 'green' if confidence >= 0.9 else 'yellow' if confidence >= 0.5 else 'red'
    print(c(col, f'  Map: {map_name}  (confidence {conf_str})'))

    # Output JSON path
    stem     = clean_stem(acmi_path.name)
    json_name = f'session_{stem}.json'
    json_path = DATA_DIR / json_name

    # Duplicate check
    cdata = load_campaigns()
    if session_exists(cdata, json_name):
        print(c('yellow', f'  Already registered: {json_name} — skipping'))
        return False

    # Parse
    print()
    try:
        session_data = run_parser(acmi_path, json_path)
    except Exception as e:
        print(c('red', f'  ✗ Parse failed: {e}'))
        return False

    dur_h   = session_data['meta'].get('duration_hours', 0)
    players = list(session_data.get('players', {}).keys())
    print(c('green', f'  ✓ Parsed  {dur_h}h  ·  {len(players)} players: {", ".join(players[:6])}'))

    # Campaign resolution
    cdata = load_campaigns()
    if campaign_id:
        camp = get_campaign(cdata, campaign_id)
        if not camp:
            print(c('red', f'  Campaign id "{campaign_id}" not found — prompting'))
            camp = _choose_campaign(cdata, map_name)
    else:
        camp = _choose_campaign(cdata, map_name)

    # Build and insert session entry (chronological order)
    entry = {
        'file':           json_name,
        'label':          session_label(dt, dur_h),
        'date':           dt.strftime('%Y-%m-%dT%H:%M:%SZ') if dt else None,
        'duration_hours': dur_h,
        'players':        players,
        'kill_count':     session_data['meta'].get('kill_count', 0),
    }
    sessions = camp.setdefault('sessions', [])
    sessions.append(entry)
    sessions.sort(key=lambda s: s.get('date') or '')

    save_campaigns(cdata)
    print()
    print(c('green', f'  ✓ Registered in: {camp["name"]}'))
    print(c('dim',   f'    → {json_path}'))
    print()
    return True

def _choose_campaign(data, suggested_map):
    """Interactive chooser used by manual import (no folder binding)."""
    campaigns = data['campaigns']
    print()
    print(c('bold', '  Assign to campaign:'))
    print()
    for i, camp in enumerate(campaigns, 1):
        scount = len(camp.get('sessions', []))
        map_tag  = c('dim', '[' + camp['map'] + ']')
        sess_tag = c('dim', str(scount) + (' sessions' if scount != 1 else ' session'))
        print(f"    {c('cyan', str(i))}.  {camp['name']}  {map_tag}  {sess_tag}")
    print(f"    {c('cyan', str(len(campaigns) + 1))}.  {c('yellow', 'Create new campaign…')}")
    print()
    while True:
        raw = input(f'  Choice [1-{len(campaigns) + 1}]: ').strip()
        if not raw.isdigit():
            continue
        choice = int(raw)
        if 1 <= choice <= len(campaigns):
            return campaigns[choice - 1]
        if choice == len(campaigns) + 1:
            return create_campaign(data, suggested_map)

# ─────────────────────────────────────────────────────────────────────────────
#  Watch mode  — polls raw/ subfolders
# ─────────────────────────────────────────────────────────────────────────────
def watch_mode():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    seen = load_seen()

    print(c('cyan', f'  Watching subfolders of: {RAW_DIR}'))
    print(c('dim',  f'  Output:   {DATA_DIR}'))
    print(c('dim',  f'  Registry: {CAMPAIGNS_F}'))
    print()
    print(c('bold', '  Folder structure:'))
    print(c('dim',  '    raw/'))
    print(c('dim',  '    ├── germany_v1/       ← one subfolder per campaign'))
    print(c('dim',  '    ├── germany_v2/'))
    print(c('dim',  '    └── caucasus_v1/'))
    print()
    print(c('dim',  '  New subfolders trigger a one-time setup prompt.'))
    print(c('dim',  '  After that, drop files in and they import automatically.'))
    print(c('dim',  '  Press Ctrl-C to stop.'))
    print()

    # Show existing bindings on startup
    cdata = load_campaigns()
    bindings = cdata.get('folder_bindings', {})
    if bindings:
        print(c('dim', '  Folder bindings:'))
        for folder, cid in sorted(bindings.items()):
            camp = get_campaign(cdata, cid)
            camp_name = camp['name'] if camp else c('red', f'[missing: {cid}]')
            print(c('dim', f'    raw/{folder}  →  {camp_name}'))
        print()

    while True:
        try:
            _watch_tick(seen)
            time.sleep(2)
        except KeyboardInterrupt:
            print()
            print(c('cyan', '  Watcher stopped.'))
            break

def _watch_tick(seen):
    """One poll cycle — scan all subfolders for new ACMI files."""
    if not RAW_DIR.exists():
        return

    for subfolder in sorted(RAW_DIR.iterdir()):
        if not subfolder.is_dir():
            # Files directly in raw/ are not supported in watch mode
            continue

        folder_name = subfolder.name

        # Ensure this folder is bound to a campaign
        cdata = load_campaigns()
        campaign_id = get_binding(cdata, folder_name)

        if not campaign_id:
            # Check if there are any ACMI files before asking for setup
            acmi_files = [f for f in subfolder.iterdir() if f.is_file() and is_acmi_file(f)]
            if not acmi_files:
                continue  # Empty or non-ACMI folder — ignore silently
            # Detect map from first file for the setup prompt
            map_name, _ = detect_map(acmi_files[0])
            camp = setup_folder_binding(cdata, folder_name, map_name)
            campaign_id = camp['id']

        # Scan for new ACMI files in this subfolder
        for fpath in sorted(subfolder.iterdir()):
            if not fpath.is_file():
                continue
            key = str(fpath)
            if key in seen:
                continue
            if not is_acmi_file(fpath):
                continue

            print(c('yellow', f'  [{folder_name}]  New file: {fpath.name}'))
            print(c('dim', '  Waiting for file to stabilise…'))
            if not file_stable(fpath):
                print(c('dim', '  Still copying — will retry next cycle'))
                continue

            import_file(fpath, campaign_id=campaign_id)
            mark_seen(key)
            seen.add(key)

# ─────────────────────────────────────────────────────────────────────────────
#  List command
# ─────────────────────────────────────────────────────────────────────────────
def cmd_list():
    data = load_campaigns()
    camps = data.get('campaigns', [])
    bindings = data.get('folder_bindings', {})

    if not camps:
        print(c('yellow', '  No campaigns registered yet.'))
        py = 'py' if sys.platform == 'win32' else 'python3'
        print(c('dim', f'  Create raw/ subfolders and run:  {py} watch_acmi.py watch'))
        return

    # Invert bindings for display
    folders_by_campaign = {}
    for folder, cid in bindings.items():
        folders_by_campaign.setdefault(cid, []).append(folder)

    for camp in camps:
        sessions = camp.get('sessions', [])
        folders  = folders_by_campaign.get(camp['id'], [])
        folder_str = '  [' + ', '.join(f'raw/{f}' for f in folders) + ']' if folders else ''
        print()
        print(c('bold', f'  {camp["name"]}') + c('dim', f'  [{camp["map"]}]{folder_str}'))
        if not sessions:
            print(c('dim', '    (no sessions)'))
            continue
        for s in sessions:
            players_str = ', '.join(s.get('players', [])[:4])
            if len(s.get('players', [])) > 4:
                players_str += f' +{len(s["players"]) - 4}'
            print(f'    {c("cyan", "→")} {s["label"]}')
            print(c('dim', f'       {s["file"]}  ·  {s.get("kill_count", 0)} kills  ·  {players_str}'))
    print()

# ─────────────────────────────────────────────────────────────────────────────
#  Campaigns management
# ─────────────────────────────────────────────────────────────────────────────
def cmd_campaigns():
    while True:
        data  = load_campaigns()
        camps = data.get('campaigns', [])
        bindings = data.get('folder_bindings', {})
        folders_by_campaign = {}
        for folder, cid in bindings.items():
            folders_by_campaign.setdefault(cid, []).append(folder)

        print()
        print(c('bold', '  Campaign Management'))
        print()
        for i, camp in enumerate(camps, 1):
            scount = len(camp.get('sessions', []))
            folders = folders_by_campaign.get(camp['id'], [])
            map_tag  = c('dim', '[' + camp['map'] + ']')
            sess_tag = c('dim', str(scount) + (' sessions' if scount != 1 else ' session'))
            fold_tag = c('dim', '  folders: ' + ', '.join(folders)) if folders else ''
            print(f"    {c('cyan', str(i))}.  {camp['name']}  {map_tag}  {sess_tag}{fold_tag}")
        print()
        print(f"    {c('cyan', 'n')}.  {c('yellow', 'New campaign')}")
        print(f"    {c('cyan', 'b')}.  {c('yellow', 'Rebind a folder to a different campaign')}")
        print(f"    {c('cyan', 'q')}.  Quit")
        print()

        choice = input('  > ').strip().lower()

        if choice == 'q':
            break

        elif choice == 'n':
            data = load_campaigns()
            create_campaign(data, 'Unknown')
            save_campaigns(data)

        elif choice == 'b':
            data = load_campaigns()
            bnd  = data.get('folder_bindings', {})
            if not bnd:
                print(c('yellow', '  No folder bindings yet.'))
                continue
            print()
            folder_list = sorted(bnd.keys())
            for i, f in enumerate(folder_list, 1):
                cid  = bnd[f]
                camp = get_campaign(data, cid)
                cname = camp['name'] if camp else f'[missing: {cid}]'
                print(f"    {c('cyan', str(i))}.  raw/{f}  →  {cname}")
            print()
            raw = input('  Choose folder to rebind: ').strip()
            if raw.isdigit() and 1 <= int(raw) <= len(folder_list):
                folder_name = folder_list[int(raw) - 1]
                map_name, _ = detect_map(RAW_DIR / folder_name / next(
                    (f.name for f in (RAW_DIR / folder_name).iterdir() if is_acmi_file(f)),
                    Path('.')))
                camp = setup_folder_binding(data, folder_name, map_name)

        elif choice.isdigit() and 1 <= int(choice) <= len(camps):
            idx  = int(choice) - 1
            camp = camps[idx]
            print()
            print(f"    {c('cyan', 'r')}.  Rename  ({camp['name']})")
            print(f"    {c('cyan', 'm')}.  Change map  ({camp['map']})")
            print(f"    {c('cyan', 'd')}.  Delete (removes registry entry, keeps JSON files)")
            print(f"    {c('cyan', 'b')}.  Back")
            print()
            sub = input('  > ').strip().lower()

            if sub == 'r':
                new_name = input(f'  New name [{camp["name"]}]: ').strip()
                if new_name:
                    camp['name'] = new_name
                    save_campaigns(data)
            elif sub == 'm':
                new_map = input(f'  New map [{camp["map"]}]: ').strip()
                if new_map:
                    camp['map'] = new_map
                    save_campaigns(data)
            elif sub == 'd':
                confirm = input(f'  Delete "{camp["name"]}"? [y/N]: ').strip().lower()
                if confirm == 'y':
                    data['campaigns'].pop(idx)
                    # Remove folder bindings pointing to this campaign
                    data['folder_bindings'] = {
                        f: cid for f, cid in data.get('folder_bindings', {}).items()
                        if cid != camp['id']
                    }
                    save_campaigns(data)
                    print(c('green', '  ✓ Deleted'))

# ─────────────────────────────────────────────────────────────────────────────
#  Clean command  —  remove registry entries whose JSON file is missing
# ─────────────────────────────────────────────────────────────────────────────
def cmd_clean():
    data  = load_campaigns()
    camps = data.get('campaigns', [])

    orphans = []  # list of (camp_index, sess_index, camp_name, sess_label, json_name)

    for ci, camp in enumerate(camps):
        for si, sess in enumerate(camp.get('sessions', [])):
            json_path = DATA_DIR / sess['file']
            if not json_path.exists():
                orphans.append((ci, si, camp['name'], sess['label'], sess['file']))

    if not orphans:
        print(c('green', '  ✓ All good — every session in campaigns.json has its JSON file.'))
        return

    print()
    print(c('yellow', f'  Found {len(orphans)} missing session file{"s" if len(orphans) != 1 else ""}:'))
    print()
    for _, _, camp_name, label, json_name in orphans:
        print(f'    {c("red", "✗")}  [{camp_name}]  {label}')
        print(c('dim', f'         missing: {DATA_DIR / json_name}'))
    print()

    confirm = input('  Remove these entries from campaigns.json? [y/N]: ').strip().lower()
    if confirm != 'y':
        print(c('dim', '  Aborted — nothing changed.'))
        return

    # Remove in reverse index order so indices stay valid as we delete
    # Group by campaign index first
    by_camp = {}
    for ci, si, *_ in orphans:
        by_camp.setdefault(ci, []).append(si)

    removed = 0
    for ci, sess_indices in sorted(by_camp.items()):
        camp = camps[ci]
        for si in sorted(sess_indices, reverse=True):
            camp['sessions'].pop(si)
            removed += 1

    # Also clean .seen_acmi entries for missing raw files (optional tidy-up)
    seen_cleaned = 0
    if SEEN_F.exists():
        with open(SEEN_F, encoding='utf-8') as f:
            seen_lines = [l.strip() for l in f if l.strip()]
        still_valid = [l for l in seen_lines if Path(l).exists()]
        seen_cleaned = len(seen_lines) - len(still_valid)
        if seen_cleaned > 0:
            with open(SEEN_F, 'w', encoding='utf-8') as f:
                f.write('\n'.join(still_valid) + ('\n' if still_valid else ''))

    save_campaigns(data)
    print(c('green', f'  ✓ Removed {removed} session {"entry" if removed == 1 else "entries"} from campaigns.json.'))
    if seen_cleaned > 0:
        print(c('dim', f'  Also cleaned {seen_cleaned} stale {"entry" if seen_cleaned == 1 else "entries"} from .seen_acmi.'))
    print()


def main():
    banner()
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'help'
    py  = 'py' if sys.platform == 'win32' else 'python3'
    sep = '\\' if sys.platform == 'win32' else '/'

    if cmd == 'watch':
        watch_mode()

    elif cmd == 'import':
        if len(sys.argv) < 3:
            print(c('red', f'  Usage: {py} watch_acmi.py import <file>'))
            sys.exit(1)
        for path in sys.argv[2:]:
            import_file(path)

    elif cmd == 'list':
        cmd_list()

    elif cmd == 'campaigns':
        cmd_campaigns()

    elif cmd == 'clean':
        cmd_clean()

    elif cmd in ('help', '--help', '-h'):
        print(c('bold', '  Commands:'))
        print()
        print(f"    {c('cyan', 'watch')}        Watch raw/ subfolders (continuous, auto-import)")
        print(f"    {c('cyan', 'import')} FILE   Import one file manually (interactive)")
        print(f"    {c('cyan', 'list')}          Show all campaigns and sessions")
        print(f"    {c('cyan', 'campaigns')}     Manage campaigns (rename, rebind folders, delete)")
        print(f"    {c('cyan', 'clean')}         Remove registry entries for deleted session files")
        print()
        print(c('dim', '  Quick start:'))
        print(c('dim', f'    1.  Create subfolders:  raw{sep}germany_v1{sep}  raw{sep}caucasus{sep}'))
        print(c('dim', f'    2.  Run:  {py} watch_acmi.py watch'))
        print(c('dim',  '    3.  Drop .acmi files into the subfolders — done.'))
        print()

    else:
        print(c('red', f'  Unknown command: {cmd}'))
        print(c('dim', f'  Run:  {py} watch_acmi.py --help'))
        sys.exit(1)


if __name__ == '__main__':
    main()

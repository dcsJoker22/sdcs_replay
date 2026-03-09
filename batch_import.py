#!/usr/bin/env python3
"""
One-off batch importer for the two new campaign folders.
Runs parse_acmi.py on every ACMI file and registers results in campaigns.json.
Usage: py batch_import.py
"""
import sys, io
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import json, subprocess, re
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR    = Path(__file__).parent.resolve()
RAW_DIR     = BASE_DIR / 'raw'
DATA_DIR    = BASE_DIR / 'public' / 'data'
CAMPAIGNS_F = BASE_DIR / 'public' / 'campaigns.json'
PARSER_F    = BASE_DIR / 'parse_acmi.py'

BATCH = [
    {
        'folder':  '2026-02-09 CaucasusInverted',
        'name':    '2026-02-09 Caucasus (Inverted)',
        'map':     'Caucasus',
        'id':      '2026_02_09_caucasus_inverted',
    },
    {
        'folder':  '2026-02-21 GermanyInverted',
        'name':    '2026-02-21 Germany (Inverted)',
        'map':     'Germany',
        'id':      '2026_02_21_germany_inverted',
    },
]

def load_campaigns():
    if CAMPAIGNS_F.exists():
        with open(CAMPAIGNS_F, encoding='utf-8') as f:
            return json.load(f)
    return {'campaigns': [], 'folder_bindings': {}}

def save_campaigns(data):
    with open(CAMPAIGNS_F, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print('  ✓ campaigns.json saved')

def parse_filename_dt(filename):
    stem = Path(filename).stem
    stem = re.sub(r'\.zip$', '', stem)
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

def clean_stem(filename):
    stem = Path(filename).stem
    stem = re.sub(r'\.zip$', '', stem)
    return stem

def session_exists(data, json_filename):
    for camp in data['campaigns']:
        for sess in camp.get('sessions', []):
            if sess['file'] == json_filename:
                return True
    return False

def run_parser(acmi_path, out_path):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [sys.executable, str(PARSER_F), str(acmi_path), str(out_path)],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    for line in result.stdout.splitlines():
        print(f'    {line}')
    if result.returncode != 0:
        print(f'  PARSER ERROR (exit {result.returncode}):')
        print(result.stderr[-1000:])
        return None
    with open(out_path, encoding='utf-8') as f:
        return json.load(f)

def main():
    data = load_campaigns()

    # Ensure both campaigns exist in campaigns.json
    for spec in BATCH:
        existing = next((c for c in data['campaigns'] if c['id'] == spec['id']), None)
        if not existing:
            data['campaigns'].append({'id': spec['id'], 'name': spec['name'], 'map': spec['map'], 'sessions': []})
            print(f"  + Created campaign: {spec['name']}")
        # Set folder binding
        data.setdefault('folder_bindings', {})[spec['folder']] = spec['id']

    save_campaigns(data)

    # Process each folder
    for spec in BATCH:
        folder = RAW_DIR / spec['folder']
        if not folder.exists():
            print(f'\n  SKIP — folder not found: {folder}')
            continue

        acmi_files = sorted(f for f in folder.iterdir() if f.suffix.lower() in ('.acmi', '.zip'))
        print(f'\n{"="*60}')
        print(f'  Campaign: {spec["name"]}')
        print(f'  Folder:   {folder.name}')
        print(f'  Files:    {len(acmi_files)} ACMI files')
        print(f'{"="*60}')

        for i, acmi_path in enumerate(acmi_files, 1):
            stem = clean_stem(acmi_path.name)
            json_name = f'session_{stem}.json'
            json_path = DATA_DIR / json_name

            # Reload each iteration to stay consistent
            data = load_campaigns()

            if session_exists(data, json_name):
                print(f'  [{i}/{len(acmi_files)}] SKIP (already imported): {acmi_path.name}')
                continue

            print(f'\n  [{i}/{len(acmi_files)}] {acmi_path.name}')
            dt = parse_filename_dt(acmi_path.name)

            session_data = run_parser(acmi_path, json_path)
            if session_data is None:
                print(f'  ✗ Failed — skipping')
                continue

            dur_h   = session_data['meta'].get('duration_hours', 0)
            players = list(session_data.get('players', {}).keys())
            print(f'  ✓ {dur_h}h · {len(players)} players: {", ".join(players[:6])}')

            entry = {
                'file':           json_name,
                'label':          session_label(dt, dur_h),
                'date':           dt.strftime('%Y-%m-%dT%H:%M:%SZ') if dt else None,
                'duration_hours': dur_h,
                'players':        players,
                'kill_count':     session_data['meta'].get('kill_count', 0),
            }

            data = load_campaigns()
            camp = next(c for c in data['campaigns'] if c['id'] == spec['id'])
            camp.setdefault('sessions', []).append(entry)
            camp['sessions'].sort(key=lambda s: s.get('date') or '')
            save_campaigns(data)

    print('\n\nAll done.')

if __name__ == '__main__':
    main()

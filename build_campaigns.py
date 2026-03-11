#!/usr/bin/env python3
"""
build_campaigns.py  —  scans the raw/ folder structure and builds campaigns.json.

New folder structure:
    raw/
      2026-02-09 CaucasusInverted/
        *.acmi
        data/
          session_*.json
      2026-02-21 GermanyInverted/
        ...

Usage (run from project root, i.e. the folder containing raw/ and public/):
    python build_campaigns.py

Or specify paths:
    python build_campaigns.py --raw raw/ --output public/campaigns.json
"""
import json, os, re, sys, argparse

def clean_players(raw_players: dict) -> list:
    """Deduplicate pilot names: strip trailing (N), - NPC, - interpolated, etc."""
    seen, out = set(), []
    for p in raw_players:
        base = re.sub(r'\s*(-\s*(NPC|interpolated|\d+)|[\(\s]\d+\)?)\s*$', '', p, flags=re.I).strip()
        if base and base not in seen:
            seen.add(base)
            out.append(base)
    out.sort(key=str.lower)
    return out

def session_label(filename: str) -> str:
    # Viewer derives its own label from sess.date — this is just a fallback
    m = re.search(r'session_(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})', filename)
    if m:
        yr,mo,dy,hh,mm,_ = m.groups()
        return f"{yr}/{mo}/{dy} {hh}:{mm}"
    return filename

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='public/campaigns.json', help='Output path for campaigns.json')
    args = parser.parse_args()

    # Map name keywords -> campaign_id
    # Inverted variants get a different campaign_id (coalitions are swapped)
    MAP_IDS = {
        'caucasusinverted': 193, 'georgiaInverted': 193,
        'caucasus': 190, 'georgia': 190,
        'germanyinverted': 192,  # same map, coalitions swapped
        'germany': 192,
        'syria': 185,
        'persiangulf': 189, 'gulf': 189,
        'nevada': 194, 'nttr': 194,
        'marianas': 195,
        'southatlantic': 196, 'falklands': 196,
    }

    def guess_campaign_id(folder_name):
        """Guess campaign_id from folder name keywords."""
        n = folder_name.lower().replace(' ', '').replace('-', '').replace('_', '')
        # Check longer/more-specific keys first so 'caucasusinverted' matches before 'caucasus'
        for key in sorted(MAP_IDS, key=len, reverse=True):
            if key in n:
                return MAP_IDS[key]
        return 0

    def guess_map(folder_name):
        n = folder_name.lower()
        if 'caucasus' in n: return 'Caucasus'
        if 'germany' in n: return 'Germany'
        if 'syria' in n: return 'Syria'
        if 'gulf' in n or 'persian' in n: return 'Persian Gulf'
        if 'nevada' in n or 'nttr' in n: return 'Nevada'
        if 'marianas' in n: return 'Marianas'
        if 'atlantic' in n or 'falkland' in n: return 'South Atlantic'
        return folder_name

    # Scan public/data/ for campaign subfolders
    public_data = os.path.join(os.path.dirname(args.output), 'data')
    if not os.path.isdir(public_data):
        print(f"No public/data/ folder found. Run parse_acmi.py on your ACMI files first.", file=sys.stderr)
        sys.exit(1)

    campaign_folders = sorted(
        d for d in os.listdir(public_data)
        if os.path.isdir(os.path.join(public_data, d))
    )

    if not campaign_folders:
        print(f"No campaign subfolders found in {public_data}", file=sys.stderr)
        sys.exit(1)

    campaigns = []
    for folder in campaign_folders:
        data_dir = os.path.join(public_data, folder)
        session_files = sorted(
            f for f in os.listdir(data_dir)
            if f.startswith('session_') and f.endswith('.json')
        )
        if not session_files:
            print(f"  ! {folder}: no session_*.json files, skipping")
            continue

        print(f"\n{folder}  ({len(session_files)} sessions)")
        sessions = []
        for fname in session_files:
            path = os.path.join(data_dir, fname)
            try:
                with open(path, encoding='utf-8') as f:
                    d = json.load(f)
                meta = d.get('meta', {})
                players = clean_players(list(d.get('players', {}).keys()))
                m = re.search(r'session_(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})', fname)
                date_str = f"{m.group(1)}-{m.group(2)}-{m.group(3)}T{m.group(4)}:{m.group(5)}:{m.group(6)}Z" if m else None
                # File path relative to public/ — viewer fetches data/<folder>/session_*.json
                rel_file = f"data/{folder}/{fname}"
                sessions.append({
                    "file":           rel_file,
                    "label":          session_label(fname),
                    "date":           date_str,
                    "duration_hours": round(meta.get('duration_hours', 0), 2),
                    "players":        players,
                    "kill_count":     meta.get('kill_count', 0),
                })
                print(f"  ✓ {fname}  ({meta.get('duration_hours',0):.2f}h, {meta.get('kill_count',0)} kills, {len(players)} players)")
            except Exception as e:
                print(f"  ✗ {fname}: {e}", file=sys.stderr)

        # Derive campaign date from first session
        first_date = None
        if sessions and sessions[0]['date']:
            first_date = sessions[0]['date'][:10]  # YYYY-MM-DD

        camp_id = re.sub(r'^\d{4}-\d{2}-\d{2}\s*', '', folder).lower().replace(' ', '_')
        campaigns.append({
            "id":          camp_id,
            "campaign_id": guess_campaign_id(folder),
            "name":        re.sub(r'^\d{4}-\d{2}-\d{2}\s*', '', folder),
            "map":         guess_map(folder),
            "date":        first_date,
            "sessions":    sessions,
        })

    out = {
        "_comment": "SDCS Campaign Registry — generated by build_campaigns.py",
        "campaigns": campaigns,
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    total = sum(len(c['sessions']) for c in campaigns)
    print(f"\n✓ Written {len(campaigns)} campaigns, {total} sessions → {args.output}")

if __name__ == '__main__':
    main()

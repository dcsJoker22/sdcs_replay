#!/usr/bin/env python3
"""
build_campaign_viewer.py
────────────────────────
Reads all session_*.json files for every campaign in public/data/ and writes:

  1. campaign_session_<stem>.json  — one per session, stripped data only:
       - ground unit objects + tracks (no aircraft, no weapons)
       - Shelter3/FARP/Factory objects + tracks (base ownership)
       - kill events (for heatmap and kill feed)
       - statics (base/FARP name labels)

  2. campaign_index_<folder>.json  — one per campaign, lightweight index:
       - session_index (offsets, durations, reference times, kill totals)
       - list of campaign_session file paths
       - all kill events (for heatmap across whole campaign)

No cross-session stitching — each session is self-contained.
The viewer loads all campaign_session files upfront on campaign load.

Usage:
    python build_campaign_viewer.py
    python build_campaign_viewer.py --campaign "2026-03-05 Caucasus"
"""

import json, os, re, sys, argparse

STRUCT_NAMES = {
    'FARPWatchtower','FARP Flag','FARP Tanker','Shelter3','Shelter3FARP',
    'Shelter3Construction','Shelter3Crate','Windsock','JTACTower',
    'FARPAmmoStatic','FatCowFuelTruck','COMP RELOAD',
    'Factory3','FactoryBuild','FactoryBuild3',
}
AIRCRAFT_PREFIXES = {'FA','CH','An','UH','AH','Mi','Ka','Su','MiG','Tu','IL','A','B'}
SAM_STANDALONE = {
    '55G6 EWR','Dog Ear radar','SA-2 Fan Song','Flat Face radar',
    'P-19 Flat Face B','Spoon Rest','Side Net',
}
AI_AIRCRAFT_NAMES = {'E2-D','KC-135'}
OWNERSHIP_NAMES   = {'Shelter3', 'Shelter3FARP', 'Factory3'}


def is_sam_unit(obj):
    if not obj.get('name'): return False
    if obj.get('category') != 'ai_air': return False
    if obj.get('is_human'): return False
    nm = obj['name']
    if 'truck build' in nm.lower(): return False
    if nm in AI_AIRCRAFT_NAMES: return False
    if nm in SAM_STANDALONE: return True
    dash = nm.find('-')
    if dash < 1: return False
    prefix = nm[:dash]
    if prefix in AIRCRAFT_PREFIXES: return False
    if re.match(r'^[A-Z]-?$', prefix): return False
    return True

def is_ground_vehicle(obj):
    if not obj.get('name'): return False
    if is_sam_unit(obj): return True
    if obj.get('category') != 'ground': return False
    nm = obj['name']
    if nm in STRUCT_NAMES: return False
    if nm.startswith('BD') or nm.startswith('SA11-') or nm.startswith('SA10-'): return False
    return True

def is_ownership_unit(obj):
    return obj.get('name') in OWNERSHIP_NAMES

def keep_object(obj):
    return is_ground_vehicle(obj) or is_ownership_unit(obj)

def keep_static(st):
    nm = st.get('name', '')
    if not nm: return False
    if nm.startswith('JTAC:'): return False
    if nm.startswith('P:') or nm.startswith('P :'): return False
    if re.search(r'within \d+m', nm): return False
    if nm in ('group', 'ww1', 'cargo util', 'CSAR RED\\'): return False
    if nm.startswith('CSAR '): return False
    return True


def process_session(data, time_offset):
    raw_objects = data.get('objects', {})
    raw_tracks  = data.get('tracks',  {})
    raw_events  = data.get('events',  [])
    raw_statics = data.get('statics', [])

    objects = {}
    tracks  = {}

    for oid, obj in raw_objects.items():
        if not keep_object(obj):
            continue
        track = raw_tracks.get(oid)
        if not track and not is_ownership_unit(obj):
            continue

        o = dict(obj)
        for field in ('first_seen', 'last_seen', 'visible_off_t'):
            if o.get(field) is not None:
                o[field] = round(o[field] + time_offset, 1)
        objects[oid] = o

        if track:
            INTERVAL = 60.0
            if is_ownership_unit(obj):
                sampled = track
            else:
                sampled, last_t = [], -INTERVAL
                for pt in track:
                    if not sampled or pt['t'] - last_t >= INTERVAL:
                        sampled.append(pt)
                        last_t = pt['t']
                if track and (not sampled or sampled[-1] is not track[-1]):
                    sampled.append(track[-1])

            shifted = []
            for pt in sampled:
                sp = {'t': round(pt['t'] + time_offset, 1)}
                if pt.get('lat') is not None: sp['lat'] = round(pt['lat'], 4)
                if pt.get('lon') is not None: sp['lon'] = round(pt['lon'], 4)
                if pt.get('alt') is not None: sp['alt'] = round(pt['alt'], 0)
                if pt.get('hdg') is not None: sp['hdg'] = round(pt['hdg'], 0)
                shifted.append(sp)
            tracks[oid] = shifted

    events = []
    for ev in raw_events:
        if ev.get('type') not in ('kill', 'crashed', 'pilot dead'):
            continue
        e = dict(ev)
        e['t'] = round(e['t'] + time_offset, 1)
        events.append(e)

    statics = [s for s in raw_statics if keep_static(s)]
    return objects, tracks, events, statics


def acmi_stem(filename):
    m = re.search(r'session_(\d{8}_\d{6})', filename)
    return m.group(1) if m else re.sub(r'\.json$', '', filename)


def build_campaign(campaign_folder, campaigns_data=None):
    session_files = sorted(
        f for f in os.listdir(campaign_folder)
        if f.startswith('session_') and f.endswith('.json')
    )
    if not session_files:
        print(f'  ! No session files found in {campaign_folder}')
        return

    folder_name = os.path.basename(campaign_folder)

    camp_meta_sessions = {}
    if campaigns_data:
        for camp in campaigns_data.get('campaigns', []):
            for s in camp.get('sessions', []):
                stem = os.path.basename(s['file'])
                camp_meta_sessions[stem] = s

    print(f'\n  Processing {len(session_files)} sessions…')

    session_index = []
    time_offset   = 0.0
    all_events    = []

    for fname in session_files:
        path = os.path.join(campaign_folder, fname)
        try:
            with open(path, encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f'    ✗ {fname}: {e}', file=sys.stderr)
            continue

        meta  = data.get('meta', {})
        dur   = meta.get('duration_seconds', 0)
        cmeta = camp_meta_sessions.get(fname, {})

        objects, tracks, events, statics = process_session(data, time_offset)
        all_events.extend(events)

        # Write per-session file
        stem     = acmi_stem(fname)
        out_name = f'campaign_session_{stem}.json'
        out_path = os.path.join(campaign_folder, out_name)

        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump({
                'objects': objects,
                'tracks':  tracks,
                'events':  events,
                'statics': statics,
                'meta':    {'offset': round(time_offset, 1), 'duration': round(dur, 1)},
            }, f, separators=(',', ':'))

        size_kb = os.path.getsize(out_path) / 1024

        session_index.append({
            'file':              f'data/{folder_name}/{out_name}',
            'label':             cmeta.get('label') or fname,
            'date':              cmeta.get('date') or meta.get('reference_time', '')[:10],
            'offset':            round(time_offset, 1),
            'duration':          round(dur, 1),
            'reference_time':    meta.get('reference_time'),
            'player_kills_blue': cmeta.get('player_kills_blue', 0),
            'player_kills_red':  cmeta.get('player_kills_red',  0),
        })

        print(f'    OK {out_name}  {size_kb:.0f}KB  '
              f'offset={time_offset:.0f}s  dur={dur/3600:.2f}h  '
              f'kills={len(events)}  objs={len(objects)}')

        time_offset += dur

    all_events.sort(key=lambda e: e['t'])

    # Write campaign index
    index_name = f'campaign_index_{folder_name}.json'
    index_path = os.path.join(campaign_folder, index_name)
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump({
            '_comment':       'Campaign index — generated by build_campaign_viewer.py',
            'total_duration': round(time_offset, 1),
            'session_index':  session_index,
            'events':         all_events,
        }, f, separators=(',', ':'))

    index_kb = os.path.getsize(index_path) / 1024
    print(f'\n  OK Index -> {index_name}  ({index_kb:.0f}KB)')
    print(f'    {time_offset/3600:.1f}h  |  {len(session_index)} sessions  |  {len(all_events)} events')


def find_new_campaign_folders(data_root):
    """Return folders that are missing their campaign_index or any campaign_session file."""
    new_folders = []
    for folder_name in sorted(os.listdir(data_root)):
        folder = os.path.join(data_root, folder_name)
        if not os.path.isdir(folder):
            continue
        session_files = [f for f in os.listdir(folder)
                         if f.startswith('session_') and f.endswith('.json')]
        if not session_files:
            continue
        index_name = f'campaign_index_{folder_name}.json'
        if not os.path.isfile(os.path.join(folder, index_name)):
            new_folders.append(folder_name)
            continue
        # Check each session has a corresponding campaign_session file
        for fname in session_files:
            stem = acmi_stem(fname)
            if not os.path.isfile(os.path.join(folder, f'campaign_session_{stem}.json')):
                new_folders.append(folder_name)
                break
    return new_folders


def prompt_new_only(new_folders, all_folders):
    """Prompt user; return list of folder names to process."""
    if not new_folders:
        print('All campaigns already built (campaign_index + campaign_session files present).')
        ans = input('Build all campaigns anyway? [y/N] ').strip().lower()
        return all_folders if ans == 'y' else []

    print(f'\nNew / updated campaigns detected ({len(new_folders)}):')
    for f in new_folders:
        print(f'  + {f}')
    ans = input('\nBuild only new campaigns? [Y/n] ').strip().lower()
    return new_folders if ans != 'n' else all_folders


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--campaign', default=None)
    parser.add_argument('--data', default='public/data')
    parser.add_argument('--campaigns-json', default='public/campaigns.json')
    parser.add_argument('--all', action='store_true', help='Skip prompt and build all campaigns')
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_root  = os.path.join(script_dir, args.data)

    if not os.path.isdir(data_root):
        print(f'ERROR: {data_root} not found', file=sys.stderr); sys.exit(1)

    campaigns_data = None
    cjson_path = os.path.join(script_dir, args.campaigns_json)
    if os.path.isfile(cjson_path):
        try:
            with open(cjson_path, encoding='utf-8') as f:
                campaigns_data = json.load(f)
            print('Loaded campaigns.json')
        except Exception as e:
            print(f'Warning: {e}', file=sys.stderr)

    if args.campaign:
        # Explicit --campaign: build exactly that one, no prompt
        folder = os.path.join(data_root, args.campaign)
        if not os.path.isdir(folder):
            print(f'ERROR: {folder} not found', file=sys.stderr); sys.exit(1)
        print(f'\n=== {args.campaign} ===')
        build_campaign(folder, campaigns_data)
    else:
        all_folders = sorted(
            d for d in os.listdir(data_root)
            if os.path.isdir(os.path.join(data_root, d))
            and any(f.startswith('session_') and f.endswith('.json')
                    for f in os.listdir(os.path.join(data_root, d)))
        )

        if args.all:
            folders_to_build = all_folders
        else:
            new_folders = find_new_campaign_folders(data_root)
            folders_to_build = prompt_new_only(new_folders, all_folders)
            if not folders_to_build:
                print('Nothing to build.')
                sys.exit(0)

        total = 0
        for folder_name in folders_to_build:
            folder = os.path.join(data_root, folder_name)
            print(f'\n=== {folder_name} ===')
            build_campaign(folder, campaigns_data)
            total += 1
        print(f'\nDone - {total} campaign(s).')


if __name__ == '__main__':
    main()

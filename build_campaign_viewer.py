#!/usr/bin/env python3
"""
build_campaign_viewer.py
────────────────────────
Reads all session_*.json files for every campaign in public/data/ and writes
a single campaign_viewer.json into each campaign folder.

The output contains only data needed by sdcs_campaign_v1.0.html:
  - kills (all, with lat/lon/coalition/time)
  - ground unit objects + tracks  (no aircraft, no weapons)
  - Shelter3 objects + tracks     (base ownership)
  - Shelter3FARP objects + tracks (FARP visibility)
  - Factory3 objects + tracks     (factory visibility)
  - statics                       (base/FARP name labels)
  - session_index                 (timing info so viewer can stitch timeline)

All timestamps are offset so session 2 starts where session 1 ends, etc.
Ground units that share an ID across sessions are merged into one continuous
track so movement appears seamless.

Usage (run from project root):
    python build_campaign_viewer.py

Or for a single campaign folder:
    python build_campaign_viewer.py --campaign "2026-01-24 Syria"
"""

import json, os, re, sys, argparse, math
from collections import defaultdict

# ── Unit classification helpers (mirrors index.html logic) ──────────────────

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

# Names we always keep regardless of category (base ownership markers)
OWNERSHIP_NAMES = {'Shelter3', 'Shelter3FARP', 'Factory3'}


def is_sam_unit(obj):
    """Mirror of isSAMUnit() in index.html."""
    if not obj.get('name'):
        return False
    if obj.get('category') != 'ai_air':
        return False
    if obj.get('is_human'):
        return False
    nm = obj['name']
    if 'truck build' in nm.lower():
        return False
    if nm in AI_AIRCRAFT_NAMES:
        return False
    if nm in SAM_STANDALONE:
        return True
    dash = nm.find('-')
    if dash < 1:
        return False
    prefix = nm[:dash]
    if prefix in AIRCRAFT_PREFIXES:
        return False
    if re.match(r'^[A-Z]-?$', prefix):
        return False
    return True


def is_ground_vehicle(obj):
    """Mirror of isGroundVehicle() in index.html."""
    if not obj.get('name'):
        return False
    if is_sam_unit(obj):
        return True
    if obj.get('category') != 'ground':
        return False
    nm = obj['name']
    if nm in STRUCT_NAMES:
        return False
    if nm.startswith('BD') or nm.startswith('SA11-') or nm.startswith('SA10-'):
        return False
    return True


def is_ownership_unit(obj):
    """Shelter3, Shelter3FARP, Factory3 — needed for base ownership rules."""
    return obj.get('name') in OWNERSHIP_NAMES


def keep_object(obj):
    """Return True if this object should appear in campaign_viewer.json."""
    return is_ground_vehicle(obj) or is_ownership_unit(obj)


# ── Geometry helper ──────────────────────────────────────────────────────────

def haver_km(lat1, lon1, lat2, lon2):
    R = 6371
    p = math.pi / 180
    dlat = (lat2 - lat1) * p
    dlon = (lon2 - lon1) * p
    a = math.sin(dlat/2)**2 + math.cos(lat1*p)*math.cos(lat2*p)*math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ── Session processing ────────────────────────────────────────────────────────

def process_session(data, time_offset):
    """
    Extract ground/ownership objects, their tracks, kill events, and statics
    from one session JSON. All timestamps are shifted by time_offset.
    Returns (objects, tracks, events, statics).
    """
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
        if not track:
            # Ownership units (Shelter3) may not have tracks in raw_tracks
            # but we still need their object record
            if not is_ownership_unit(obj):
                continue

        # Shift timestamps on the object record
        o = dict(obj)
        if o.get('first_seen') is not None:
            o['first_seen'] = round(o['first_seen'] + time_offset, 1)
        if o.get('last_seen') is not None:
            o['last_seen']  = round(o['last_seen']  + time_offset, 1)
        if o.get('visible_off_t') is not None:
            o['visible_off_t'] = round(o['visible_off_t'] + time_offset, 1)
        objects[oid] = o

        if track:
            # Subsample ground unit tracks to 60s intervals for the campaign viewer.
            # Ground units move slowly — 60s resolution is imperceptible at campaign scale.
            # Ownership units (Shelter3 etc) keep all points (they are few and static).
            GROUND_SAMPLE_INTERVAL = 60.0
            if is_ownership_unit(obj):
                sampled = track  # keep all points for ownership units
            else:
                sampled = []
                last_t = -GROUND_SAMPLE_INTERVAL
                for pt in track:
                    if not sampled or pt['t'] - last_t >= GROUND_SAMPLE_INTERVAL:
                        sampled.append(pt)
                        last_t = pt['t']
                # Always include the last point
                if track and (not sampled or sampled[-1] is not track[-1]):
                    sampled.append(track[-1])

            shifted = []
            for pt in sampled:
                sp = {'t': round(pt['t'] + time_offset, 1)}
                # 4 decimal places = ~11m precision — sufficient for campaign scale
                if pt.get('lat') is not None: sp['lat'] = round(pt['lat'], 4)
                if pt.get('lon') is not None: sp['lon'] = round(pt['lon'], 4)
                if pt.get('alt') is not None: sp['alt'] = round(pt['alt'], 0)
                if pt.get('hdg') is not None: sp['hdg'] = round(pt['hdg'], 0)
                shifted.append(sp)
            tracks[oid] = shifted

    # Kill events — keep all (including air kills — needed for heatmap/FLOT)
    events = []
    for ev in raw_events:
        if ev.get('type') not in ('kill', 'crashed', 'pilot dead'):
            continue
        e = dict(ev)
        e['t'] = round(e['t'] + time_offset, 1)
        events.append(e)

    # Filter statics — keep only FARP labels and named airfield/objective markers.
    # Drop P: intel waypoints, JTAC proximity alerts, and range strings — these
    # are server-side GM tools, not map features needed by the campaign viewer.
    def keep_static(st):
        nm = st.get('name', '')
        if not nm:
            return False
        # Always drop: JTAC proximity strings, P: intel, range strings
        if nm.startswith('JTAC:'):
            return False
        if nm.startswith('P:') or nm.startswith('P :'):
            return False
        if re.search(r'within \d+m', nm):
            return False
        # Drop generic noise names
        if nm in ('group', 'ww1', 'cargo util', 'CSAR RED\\'):
            return False
        if nm.startswith('CSAR '):
            return False
        return True

    filtered_statics = [s for s in raw_statics if keep_static(s)]
    return objects, tracks, events, filtered_statics


# ── Cross-session ground track stitching ─────────────────────────────────────

def stitch_ground_tracks(all_session_data):
    """
    Ground units restart each session with the same ID.  Merge their tracks
    across sessions into one continuous track per ID.

    all_session_data: list of (objects_dict, tracks_dict) per session, in order.
    Returns merged_objects, merged_tracks.
    """
    merged_objects = {}
    merged_tracks  = defaultdict(list)

    for objects, tracks in all_session_data:
        for oid, obj in objects.items():
            if oid not in merged_objects:
                merged_objects[oid] = obj
            else:
                # Keep the earliest first_seen and latest last_seen across sessions
                existing = merged_objects[oid]
                if obj.get('first_seen') is not None and existing.get('first_seen') is not None:
                    existing['first_seen'] = min(existing['first_seen'], obj['first_seen'])
                if obj.get('last_seen') is not None and existing.get('last_seen') is not None:
                    existing['last_seen'] = max(existing['last_seen'], obj['last_seen'])
                # visible_off_t: take the latest across sessions (last time unit disappeared)
                vot_new = obj.get('visible_off_t')
                vot_ex  = existing.get('visible_off_t')
                if vot_new is not None:
                    if vot_ex is None or vot_new > vot_ex:
                        existing['visible_off_t'] = vot_new

        for oid, track in tracks.items():
            merged_tracks[oid].extend(track)

    # Sort all tracks by time (should already be sorted, but be safe)
    for oid in merged_tracks:
        merged_tracks[oid].sort(key=lambda p: p['t'])

    return merged_objects, dict(merged_tracks)


# ── Statics deduplication ────────────────────────────────────────────────────

def merge_statics(all_statics):
    """Deduplicate statics by name (same rule as mergeSessions in index.html)."""
    seen = set()
    out  = []
    for st in all_statics:
        nm = st.get('name','')
        if nm and nm not in seen:
            seen.add(nm)
            out.append(st)
    return out


# ── Session index ─────────────────────────────────────────────────────────────

def build_session_index(session_metas):
    """
    Build the session_index array: each entry records label, offset, duration,
    and reference_time so the viewer can show real-world wall-clock time and
    draw session boundary markers on the timeline.
    """
    index = []
    for m in session_metas:
        index.append({
            'label':          m.get('label', ''),
            'date':           m.get('date'),
            'offset':         m['offset'],
            'duration':       m['duration'],
            'reference_time': m.get('reference_time'),
            'player_kills_blue': m.get('player_kills_blue', 0),
            'player_kills_red':  m.get('player_kills_red',  0),
        })
    return index


# ── Main build function ───────────────────────────────────────────────────────

def build_campaign(campaign_folder, data_dir, campaigns_data=None):
    session_files = sorted(
        f for f in os.listdir(campaign_folder)
        if f.startswith('session_') and f.endswith('.json')
    )
    if not session_files:
        print(f'  ! No session files found in {campaign_folder}')
        return

    # Get supplementary metadata from campaigns.json if available
    camp_meta_sessions = {}
    if campaigns_data:
        folder_name = os.path.basename(campaign_folder)
        for camp in campaigns_data.get('campaigns', []):
            # Match by checking if any session file path contains the folder name
            for s in camp.get('sessions', []):
                stem = os.path.basename(s['file'])
                camp_meta_sessions[stem] = s

    print(f'\n  Processing {len(session_files)} sessions…')

    all_objects_tracks = []   # list of (objects, tracks) per session for stitching
    all_events         = []   # all kill events, time-shifted
    all_statics        = []   # statics from all sessions (will deduplicate)
    session_metas      = []   # timing metadata per session
    time_offset        = 0.0

    for fname in session_files:
        path = os.path.join(campaign_folder, fname)
        try:
            with open(path, encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f'    ✗ {fname}: {e}', file=sys.stderr)
            continue

        meta = data.get('meta', {})
        dur  = meta.get('duration_seconds', 0)

        # Pull per-session kill counts from campaigns.json meta if available
        cmeta = camp_meta_sessions.get(fname, {})

        objects, tracks, events, statics = process_session(data, time_offset)

        all_objects_tracks.append((objects, tracks))
        all_events.extend(events)
        all_statics.extend(statics)
        session_metas.append({
            'label':             cmeta.get('label') or fname,
            'date':              cmeta.get('date')  or meta.get('reference_time', '')[:10],
            'offset':            round(time_offset, 1),
            'duration':          round(dur, 1),
            'reference_time':    meta.get('reference_time'),
            'player_kills_blue': cmeta.get('player_kills_blue', 0),
            'player_kills_red':  cmeta.get('player_kills_red',  0),
        })

        print(f'    ✓ {fname}  offset={time_offset:.0f}s  dur={dur/3600:.2f}h  '
              f'kills={len(events)}  ground_objs={len(objects)}')

        time_offset += dur

    if not all_objects_tracks:
        print('  ! No sessions loaded, skipping.')
        return

    # Stitch ground tracks across sessions
    merged_objects, merged_tracks = stitch_ground_tracks(all_objects_tracks)

    # Sort all events by time
    all_events.sort(key=lambda e: e['t'])

    # Deduplicate statics
    merged_statics = merge_statics(all_statics)

    # Build session index
    session_index = build_session_index(session_metas)

    total_duration = time_offset  # sum of all session durations

    output = {
        '_comment':       'Campaign viewer data — generated by build_campaign_viewer.py. '
                          'Contains ground units, kills, base ownership, no aircraft tracks.',
        'total_duration': round(total_duration, 1),
        'session_index':  session_index,
        'objects':        merged_objects,
        'tracks':         merged_tracks,
        'events':         all_events,
        'statics':        merged_statics,
    }

    out_path = os.path.join(campaign_folder, 'campaign_viewer.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, separators=(',', ':'))  # compact — same as session JSONs

    size_kb = os.path.getsize(out_path) / 1024
    print(f'  ✓ Written → {out_path}')
    print(f'    {size_kb:.1f} KB  |  {total_duration/3600:.1f}h total  |  '
          f'{len(all_events)} events  |  {len(merged_objects)} objects  |  '
          f'{len(merged_statics)} statics')


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Build campaign_viewer.json for each campaign.')
    parser.add_argument('--campaign', default=None,
                        help='Single campaign folder name (e.g. "2026-01-24 Syria"). '
                             'Omit to process all campaigns.')
    parser.add_argument('--data', default='public/data',
                        help='Path to public/data directory (default: public/data)')
    parser.add_argument('--campaigns-json', default='public/campaigns.json',
                        help='Path to campaigns.json for supplementary metadata')
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_root  = os.path.join(script_dir, args.data)

    if not os.path.isdir(data_root):
        print(f'ERROR: data directory not found: {data_root}', file=sys.stderr)
        sys.exit(1)

    # Load campaigns.json for supplementary metadata (label, date, kill counts)
    campaigns_data = None
    cjson_path = os.path.join(script_dir, args.campaigns_json)
    if os.path.isfile(cjson_path):
        try:
            with open(cjson_path, encoding='utf-8') as f:
                campaigns_data = json.load(f)
            print(f'Loaded campaigns.json from {cjson_path}')
        except Exception as e:
            print(f'Warning: could not load campaigns.json: {e}', file=sys.stderr)

    if args.campaign:
        # Single campaign mode
        folder = os.path.join(data_root, args.campaign)
        if not os.path.isdir(folder):
            print(f'ERROR: campaign folder not found: {folder}', file=sys.stderr)
            sys.exit(1)
        print(f'\n=== {args.campaign} ===')
        build_campaign(folder, data_root, campaigns_data)
    else:
        # Batch mode — all campaigns
        folders = sorted(
            d for d in os.listdir(data_root)
            if os.path.isdir(os.path.join(data_root, d))
        )
        if not folders:
            print(f'No campaign folders found in {data_root}', file=sys.stderr)
            sys.exit(1)

        total_camps = 0
        for folder_name in folders:
            folder = os.path.join(data_root, folder_name)
            # Skip if no session files (e.g. stray folders)
            if not any(f.startswith('session_') and f.endswith('.json')
                       for f in os.listdir(folder)):
                continue
            print(f'\n=== {folder_name} ===')
            build_campaign(folder, data_root, campaigns_data)
            total_camps += 1

        print(f'\n✓ Done — processed {total_camps} campaign(s).')


if __name__ == '__main__':
    main()

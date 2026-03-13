#!/usr/bin/env python3
"""
ACMI Tacview Parser for Strategic DCS Campaign Replay
Converts .acmi (zipped or plain) files into structured JSON for web visualization.

Output structure:
- meta: session info, time range, reference time
- objects: all units with their full property definitions
- tracks: position snapshots sampled every N seconds (for efficient web playback)
- events: kills, crashes, messages, pilot connect/disconnect
- players: human pilot summary with flights and kills
"""

import sys, io
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import zipfile
import re
import json
import os
from collections import defaultdict
from datetime import datetime, timedelta

# ── Config ────────────────────────────────────────────────────────────────────
SAMPLE_INTERVAL = 5.0   # seconds between track snapshots (5s = smooth enough, small file)
# ─────────────────────────────────────────────────────────────────────────────


def open_acmi(path):
    """Open .acmi file - handles both zipped and plain text."""
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path, 'r') as z:
            name = z.namelist()[0]
            return z.read(name).decode('utf-8', errors='replace').splitlines()
    else:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read().splitlines()


def parse_T_field(t_str):
    """Parse T= field: lon|lat|alt|roll|pitch|yaw|u|v|speed (empty = unchanged)."""
    parts = t_str.split('|')
    def val(i):
        return float(parts[i]) if i < len(parts) and parts[i] != '' else None
    return {
        'lon': val(0),
        'lat': val(1),
        'alt': val(2),   # meters
        'roll': val(3),
        'pitch': val(4),
        'yaw': val(5),   # heading in degrees
    }


def parse_props(raw):
    """Parse key=value pairs from an object definition line (after T= field)."""
    props = {}
    # Split on commas that are NOT inside values (values don't contain commas in ACMI)
    for token in raw.split(','):
        if '=' in token:
            k, _, v = token.partition('=')
            props[k.strip()] = v.strip()
    return props


def classify_object(obj_type, name, pilot):
    """Determine if object is player aircraft, AI aircraft, ground unit, weapon, etc."""
    t = obj_type or ''
    if 'Weapon' in t or 'Missile' in t or 'Bomb' in t or 'Rocket' in t:
        if is_human_pilot(pilot):
            return 'player_weapon'
        return 'weapon'
    if 'Air' in t:
        if is_human_pilot(pilot):
            return 'player_air'
        return 'ai_air'
    if 'Ground' in t or 'Anti' in t:
        return 'ground'
    if 'Navaid' in t or 'Waypoint' in t:
        return 'navaid'
    if 'Sea' in t:
        return 'naval'
    return 'other'


def clean_pilot_name(pilot_str):
    """Extract clean callsign from pilot field like 'Joker22 - 14ups' or 'Papst (2030)'."""
    if not pilot_str:
        return None
    # Strip tracking suffixes like " - 14ups", " - interpolated - 0ups"
    name = re.sub(r'\s*-\s*\d+ups$', '', pilot_str).strip()
    name = re.sub(r'\s*-\s*interpolated\s*-?\s*\d*ups?$', '', name).strip()
    # Strip ID numbers in parens: "Joker22 (16791298)"
    name = re.sub(r'\s*\(\d+\)\s*$', '', name).strip()
    # Strip radar track suffixes
    name = re.sub(r'\s*-\s*(RT|VT|ET) by .*$', '', name).strip()
    name = re.sub(r'\s*-\s*jamming$', '', name).strip()
    return name if name else None

def is_human_pilot(pilot_str):
    """True if pilot string looks like a human player rather than AI unit ID."""
    if not pilot_str:
        return False
    clean = clean_pilot_name(pilot_str)
    if not clean:
        return False
    # AI units always start with a purely numeric ID >= 5000
    first_token = clean.split()[0].rstrip(',-|')
    if re.match(r'^\d+$', first_token) and int(first_token) >= 5000:
        return False
    return True


def parse_acmi(path, sample_interval=SAMPLE_INTERVAL):
    lines = open_acmi(path)
    print(f"  Loaded {len(lines):,} lines")

    # ── Pass 1: Build object registry & collect all timestamped updates ───────
    ref_time = None
    current_time = 0.0
    objects = {}          # id -> {props dict, first seen, last seen, category}
    raw_updates = defaultdict(list)   # id -> [(time, T_parsed)]
    events = []
    kill_messages = []    # raw kill event strings with timestamps

    for line in lines:
        line = line.rstrip()
        if not line:
            continue

        # Global header
        if line.startswith('FileType=') or line.startswith('FileVersion='):
            continue

        # Timestamp
        if line.startswith('#'):
            try:
                current_time = float(line[1:])
            except ValueError:
                pass
            continue

        # Global events (id=0)
        if line.startswith('0,'):
            rest = line[2:]
            if rest.startswith('ReferenceTime='):
                ref_time = rest[14:]
            elif rest.startswith('Event=Message|'):
                msg = rest[14:]
                events.append({'t': current_time, 'type': 'message', 'text': msg})
                if 'Killed by' in msg:
                    kill_messages.append({'t': current_time, 'raw': msg})
                elif 'crashed' in msg or 'pilot dead' in msg:
                    kill_messages.append({'t': current_time, 'raw': msg})
            continue

        # Object line: id,T=...,Key=Val,...
        m = re.match(r'^(b[0-9a-f]+|[0-9a-f]+),(.+)$', line, re.IGNORECASE)
        if not m:
            continue

        obj_id = m.group(1)
        rest = m.group(2)

        # Extract T= field
        t_data = None
        if rest.startswith('T='):
            t_end = rest.find(',', 2)
            t_str = rest[2:t_end] if t_end != -1 else rest[2:]
            t_data = parse_T_field(t_str)
            rest_props = rest[t_end+1:] if t_end != -1 else ''
        else:
            rest_props = rest

        # Parse remaining properties
        props = parse_props(rest_props)

        # Initialize or update object registry
        if obj_id not in objects:
            objects[obj_id] = {
                'id': obj_id,
                'type': None,
                'name': None,
                'coalition': None,
                'color': None,
                'pilot': None,
                'pilot_clean': None,
                'category': None,
                'first_seen': current_time,
                'last_seen': current_time,
                'visible_off_t': None,   # timestamp of first Visible=0 line
            }

        obj = objects[obj_id]
        obj['last_seen'] = current_time

        # Update props if present in this line
        if 'Type' in props:
            obj['type'] = props['Type']
        if 'Name' in props:
            obj['name'] = props['Name']
        if 'Coalition' in props:
            obj['coalition'] = props['Coalition']
        if 'Color' in props:
            obj['color'] = props['Color']
        if 'Pilot' in props:
            obj['pilot'] = props['Pilot']
            obj['pilot_clean'] = clean_pilot_name(props['Pilot'])

        # Capture Visible=0 (unit removed from sim — more reliable than track end)
        if 'Visible' in props and props['Visible'] == '0':
            if obj['visible_off_t'] is None:   # record first occurrence only
                obj['visible_off_t'] = current_time

        # Categorize once we have type info
        if obj['type'] and not obj['category']:
            obj['category'] = classify_object(obj['type'], obj['name'], obj['pilot'])

        # Store position update (only if we have lat/lon)
        if t_data and (t_data['lat'] is not None or t_data['lon'] is not None):
            raw_updates[obj_id].append((current_time, t_data))

    print(f"  Found {len(objects):,} objects, {sum(len(v) for v in raw_updates.values()):,} raw position updates")

    # ── Pass 2: Finalize categories & filter ──────────────────────────────────
    for obj_id, obj in objects.items():
        if not obj['category']:
            obj['category'] = classify_object(obj['type'], obj['name'], obj['pilot'])
        # Mark human players
        obj['is_human'] = is_human_pilot(obj['pilot'])

    # ── Pass 3: Sample tracks at fixed interval ───────────────────────────────
    # For each object, interpolate/subsample positions
    tracks = {}

    for obj_id, updates in raw_updates.items():
        if not updates:
            continue
        obj = objects.get(obj_id, {})
        cat = obj.get('category', 'other')

        # Skip AI weapons (too many, short lived). Keep player_weapon for map rendering.
        if cat == 'weapon':
            continue
        # Skip navaids (static, handled separately)
        if cat == 'navaid':
            continue

        # Build a continuous position by carrying forward last known values
        # Sort by time
        updates.sort(key=lambda x: x[0])

        sampled = []
        last_lat = None
        last_lon = None
        last_alt = None
        last_yaw = None
        next_sample = updates[0][0]  # first sample at first appearance
        # Player weapons are short-lived — keep every raw update, no subsampling
        is_player_wpn = (cat == 'player_weapon')

        for (t, pos) in updates:
            # Carry forward
            if pos['lat'] is not None: last_lat = pos['lat']
            if pos['lon'] is not None: last_lon = pos['lon']
            if pos['alt'] is not None: last_alt = pos['alt']
            if pos['yaw'] is not None: last_yaw = pos['yaw']

            if (is_player_wpn or t >= next_sample) and last_lat is not None and last_lon is not None:
                sampled.append({
                    't': round(t, 1),
                    'lat': round(last_lat, 6),
                    'lon': round(last_lon, 6),
                    'alt': round(last_alt, 1) if last_alt is not None else None,
                    'hdg': round(last_yaw, 1) if last_yaw is not None else None,
                })
                if not is_player_wpn:
                    next_sample = t + sample_interval

        if sampled:
            tracks[obj_id] = sampled

    print(f"  Sampled {len(tracks):,} object tracks ({sample_interval}s interval)")

    # ── Pass 4: Parse kill events ─────────────────────────────────────────────
    parsed_kills = []
    for km in kill_messages:
        raw = km['raw']
        t = km['t']

        # Format: "b1042|Killed by Joker22 with YakB_12_7"
        m = re.match(r'(b[0-9a-f]+)\|Killed by (.+) with (.+)', raw)
        if m:
            victim_id = m.group(1)
            killer_name = m.group(2).strip()
            weapon = m.group(3).strip()
            victim_obj = objects.get(victim_id, {})
            parsed_kills.append({
                't': round(t, 1),
                'type': 'kill',
                'victim_id': victim_id,
                'victim_name': victim_obj.get('name', '?'),
                'victim_pilot': victim_obj.get('pilot_clean'),
                'victim_coalition': victim_obj.get('coalition'),
                'victim_category': victim_obj.get('category'),
                'killer': killer_name,
                'weapon': weapon,
                # Position of victim at time of kill
                'lat': None,
                'lon': None,
            })
            continue

        # Format: "b1037|Papst (2030) crashed"
        m = re.match(r'(b[0-9a-f]+)\|(.+?) \(\d+\) (crashed|pilot dead|killed)', raw)
        if m:
            victim_id = m.group(1)
            pilot = m.group(2).strip()
            cause = m.group(3)
            victim_obj = objects.get(victim_id, {})
            parsed_kills.append({
                't': round(t, 1),
                'type': cause,
                'victim_id': victim_id,
                'victim_name': victim_obj.get('name', '?'),
                'victim_pilot': pilot,
                'victim_coalition': victim_obj.get('coalition'),
                'victim_category': victim_obj.get('category'),
                'killer': None,
                'weapon': None,
                'lat': None,
                'lon': None,
            })

    # Attach kill positions from tracks
    for kill in parsed_kills:
        vid = kill.get('victim_id')
        if vid and vid in tracks:
            # Find closest track point to kill time
            t_kill = kill['t']
            closest = min(tracks[vid], key=lambda p: abs(p['t'] - t_kill))
            kill['lat'] = closest['lat']
            kill['lon'] = closest['lon']
            kill['alt'] = closest.get('alt')

    print(f"  Parsed {len(parsed_kills):,} kill/crash events")

    # ── Pass 5: Build player summaries ────────────────────────────────────────
    players = {}

    for obj_id, obj in objects.items():
        if not obj['is_human']:
            continue
        # Weapons fired by players are tracked separately — not flights
        if obj.get('category') == 'player_weapon':
            continue
        callsign = obj['pilot_clean']
        if not callsign:
            continue

        if callsign not in players:
            players[callsign] = {
                'callsign': callsign,
                'flights': [],
                'kills': [],
                'deaths': 0,
            }

        p = players[callsign]
        flight = {
            'obj_id': obj_id,
            'aircraft': obj['name'],
            'coalition': obj['coalition'],
            'start_t': round(obj['first_seen'], 1),
            'end_t': round(obj['last_seen'], 1),
            'duration_min': round((obj['last_seen'] - obj['first_seen']) / 60, 1),
        }
        p['flights'].append(flight)

    # Attach kills to players
    for kill in parsed_kills:
        killer = kill.get('killer')
        if killer and killer in players:
            players[killer]['kills'].append({
                't': kill['t'],
                'victim': kill['victim_name'],
                'victim_pilot': kill['victim_pilot'],
                'weapon': kill['weapon'],
                'lat': kill['lat'],
                'lon': kill['lon'],
            })
        # Deaths
        pilot = kill.get('victim_pilot')
        if pilot and pilot in players:
            players[pilot]['deaths'] += 1

    print(f"  Found {len(players):,} human players: {', '.join(players.keys())}")

    # ── Pass 6: Assemble static objects (bases, navaids) ──────────────────────
    statics = []
    for obj_id, obj in objects.items():
        if obj['category'] in ('navaid',) and obj['name']:
            first_updates = raw_updates.get(obj_id, [])
            if first_updates:
                t0, pos = first_updates[0]
                if pos['lat'] and pos['lon']:
                    statics.append({
                        'id': obj_id,
                        'name': obj['name'],
                        'coalition': obj['coalition'],
                        'color': obj['color'],
                        'lat': round(pos['lat'], 6),
                        'lon': round(pos['lon'], 6),
                        'alt': round(pos['alt'], 1) if pos['alt'] else None,
                    })

    print(f"  Extracted {len(statics):,} static waypoints/bases")

    # ── Assemble final output ─────────────────────────────────────────────────
    duration = current_time

    output = {
        'meta': {
            'source_file': os.path.basename(path),
            'reference_time': ref_time,
            'duration_seconds': round(duration, 1),
            'duration_hours': round(duration / 3600, 2),
            'sample_interval': sample_interval,
            'object_count': len(objects),
            'track_count': len(tracks),
            'kill_count': len(parsed_kills),
            'player_count': len(players),
        },
        'objects': {
            oid: {
                'id': oid,
                'name': obj['name'],
                'type': obj['type'],
                'category': obj['category'],
                'coalition': obj['coalition'],
                'color': obj['color'],
                'pilot': obj['pilot_clean'],
                'is_human': obj['is_human'],
                'first_seen': round(obj['first_seen'], 1),
                'last_seen': round(obj['last_seen'], 1),
                'visible_off_t': round(obj['visible_off_t'], 1) if obj['visible_off_t'] is not None else None,
            }
            for oid, obj in objects.items()
            if obj['category'] not in ('weapon',)  # skip AI weapons (player_weapon retained)
        },
        'tracks': tracks,
        'events': parsed_kills,
        'statics': statics,
        'players': players,
    }

    return output


def acmi_stem(filename):
    """Strip .zip.acmi or .acmi suffix to get clean stem for output filename.

    Handles both '20260226_074617.zip.acmi' and '20260226_074617.acmi'.
    Result: '20260226_074617' in both cases.
    """
    stem = re.sub(r'\.zip\.acmi$', '', filename, flags=re.I)
    stem = re.sub(r'\.acmi$', '', stem, flags=re.I)
    return stem


def parse_and_write(acmi_path, out_path):
    """Parse one .acmi file and write compact JSON to out_path."""
    print(f"\nParsing: {acmi_path}")
    data = parse_acmi(acmi_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    print(f"Writing: {out_path}")
    with open(out_path, 'w') as f:
        json.dump(data, f, separators=(',', ':'))  # compact JSON
    size = os.path.getsize(out_path)
    print(f"  \u2713 {size/1024:.1f} KB  |  {data['meta']['duration_hours']}h  |  "
          f"{data['meta']['kill_count']} kills  |  "
          f"{data['meta']['player_count']} players: {', '.join(data['players'].keys())}")
    return data


def main():
    # No args:   batch mode — reparse ALL campaigns under raw/
    # One arg:   parse single file, auto-derive output path
    # Two args:  parse single file to explicit output path
    #
    # Batch mode walks:  raw/<campaign_folder>/*.acmi
    # and writes to:     public/data/<campaign_folder>/session_<stem>.json
    # Both paths are relative to the directory containing this script.

    script_dir = os.path.dirname(os.path.abspath(__file__))

    if len(sys.argv) == 1:
        # ── Batch mode ────────────────────────────────────────────────────────
        raw_root = os.path.join(script_dir, 'raw')
        if not os.path.isdir(raw_root):
            print(f"ERROR: raw/ directory not found at {raw_root}")
            sys.exit(1)

        total = 0
        for campaign_folder in sorted(os.listdir(raw_root)):
            campaign_dir = os.path.join(raw_root, campaign_folder)
            if not os.path.isdir(campaign_dir):
                continue

            acmi_files = sorted(
                f for f in os.listdir(campaign_dir)
                if re.search(r'\.acmi$', f, re.I)
            )
            if not acmi_files:
                print(f"\n(no .acmi files in {campaign_folder})")
                continue

            print(f"\n=== {campaign_folder} ({len(acmi_files)} files) ===")
            for fname in acmi_files:
                acmi_path = os.path.join(campaign_dir, fname)
                stem = acmi_stem(fname)
                out_path = os.path.join(script_dir, 'public', 'data',
                                        campaign_folder, f'session_{stem}.json')
                parse_and_write(acmi_path, out_path)
                total += 1

        print(f"\n\u2713 Batch complete \u2014 {total} sessions parsed.")

    else:
        # ── Single-file mode ──────────────────────────────────────────────────
        acmi_path = sys.argv[1]
        if len(sys.argv) > 2:
            out_path = sys.argv[2]
        else:
            acmi_dir = os.path.dirname(os.path.abspath(acmi_path))
            campaign_folder = os.path.basename(acmi_dir)
            stem = acmi_stem(os.path.basename(acmi_path))
            out_path = os.path.join(script_dir, 'public', 'data',
                                    campaign_folder, f'session_{stem}.json')
        parse_and_write(acmi_path, out_path)


if __name__ == '__main__':
    main()

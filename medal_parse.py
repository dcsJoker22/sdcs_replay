#!/usr/bin/env python3
"""
ACMI Medal Parser for Strategic DCS
Reads all .acmi files in a campaign folder and aggregates per-player stats
into campaign_medals.json.

Usage:
    python medal_parse.py "2026-03-28 Caucasus Inverted"   # single campaign
    python medal_parse.py                                   # all campaigns under raw/
"""

import sys, io
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import zipfile, re, json, os
from collections import defaultdict
from datetime import datetime


MAX_SESSION_SECONDS = 21_600

FARP_NAMES = {'FARP Flag', 'FARPWatchtower', 'Shelter3FARP'}
ARTY_SLOT_RE = re.compile(r'^artillery_commander_')


# ── Utilities (mirrored from parse_acmi.py) ───────────────────────────────────

def open_acmi(path):
    """Open .acmi file — handles both zipped and plain text."""
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path, 'r') as z:
            name = z.namelist()[0]
            return z.read(name).decode('utf-8', errors='replace').splitlines()
    else:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read().splitlines()


def parse_props(raw):
    """Parse key=value pairs from an object definition line."""
    props = {}
    for token in raw.split(','):
        if '=' in token:
            k, _, v = token.partition('=')
            props[k.strip()] = v.strip()
    return props


def clean_pilot_name(pilot_str):
    """Extract clean callsign from a raw Pilot= value or message name."""
    if not pilot_str:
        return None
    name = re.sub(r'\s*-\s*\d+ups$', '', pilot_str).strip()
    name = re.sub(r'\s*-\s*interpolated\s*-?\s*\d*ups?$', '', name).strip()
    name = re.sub(r'\s*\(\d+\).*$', '', name).strip()
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
    first_token = clean.split()[0].rstrip(',-|')
    if re.match(r'^\d+$', first_token) and int(first_token) >= 5000:
        return False
    return True


def is_air_type(type_str):
    # Must start with 'Air' — avoids matching 'Ground+AntiAircraft' substring
    return bool(type_str and type_str.startswith('Air'))


# ── Per-session parser ────────────────────────────────────────────────────────

def parse_session(path):
    """
    Parse one .acmi file.
    Returns: dict { player_name -> stats_dict }
    """
    lines = open_acmi(path)
    print(f"  Loaded {len(lines):,} lines")

    objects = {}       # obj_id -> {type, name, coalition, pilot, pilot_clean}
    farp_seen = set()  # obj_ids already processed for FARP attribution

    # Player state tracking within this session
    player_slot = {}        # player_name -> current slot string (or None)
    player_coalition = {}   # player_name -> 'Friendlies' | 'Hostiles'
    pending_unpacks = []    # [{t, player, coalition, unit_id}] — awaiting FARP spawn

    stats = _new_stats_store()
    current_time = 0.0

    for line in lines:
        line = line.rstrip()
        if not line:
            continue
        if line.startswith('FileType=') or line.startswith('FileVersion='):
            continue

        # Timestamp
        if line.startswith('#'):
            try:
                t = float(line[1:])
                if t > MAX_SESSION_SECONDS and (t - current_time) > MAX_SESSION_SECONDS:
                    print(f"  WARNING: Corrupted timestamp #{t:.0f}, truncating at {current_time:.1f}s")
                    break
                current_time = t
            except ValueError:
                pass
            continue

        # Global events (id=0)
        if line.startswith('0,'):
            rest = line[2:]
            if rest.startswith('Event=Message|'):
                _handle_message(rest[14:], current_time, stats,
                                player_slot, player_coalition, objects, pending_unpacks)
            continue

        # Object line: bXXXX,...
        m = re.match(r'^(b[0-9a-f]+),(.+)$', line, re.IGNORECASE)
        if not m:
            continue

        obj_id = m.group(1)
        rest = m.group(2)

        # Skip T= positional data (not needed for medals)
        if rest.startswith('T='):
            t_end = rest.find(',', 2)
            rest_props = rest[t_end + 1:] if t_end != -1 else ''
        else:
            rest_props = rest

        props = parse_props(rest_props)

        if obj_id not in objects:
            objects[obj_id] = {
                'type': None, 'name': None, 'coalition': None,
                'pilot': None, 'pilot_clean': None,
            }

        obj = objects[obj_id]
        if 'Type'      in props: obj['type']        = props['Type']
        if 'Name'      in props: obj['name']         = props['Name']
        if 'Coalition' in props: obj['coalition']    = props['Coalition']
        if 'Pilot'     in props:
            obj['pilot']       = props['Pilot']
            obj['pilot_clean'] = clean_pilot_name(props['Pilot'])

        # FARP spawn: first time we see this FARP-type object
        if obj_id not in farp_seen and obj.get('name') in FARP_NAMES:
            farp_seen.add(obj_id)
            _attribute_farp(obj, current_time, pending_unpacks, stats)

    kills = sum(s['aa_kills_human'] + s['aa_kills_ai'] + s['ag_kills'] + s['gg_kills']
                for s in stats.values())
    print(f"  {len(stats):,} players tracked, {kills} kills attributed")
    return stats


def _new_stats_store():
    return defaultdict(lambda: {
        'aa_kills_human': 0,
        'aa_kills_ai':    0,
        'ag_kills':       0,
        'gg_kills':       0,
        'routes_set':     0,
        'farps_built':    0,
        'flights':        0,
        'weapons_fired':  defaultdict(int),
    })


def _handle_message(msg, t, stats, player_slot, player_coalition, objects, pending_unpacks):
    """Dispatch a single 0,Event=Message| payload to the appropriate handler."""

    # Skip server broadcast messages (fast path)
    if msg.startswith('[ALL] server') or msg.startswith('[BLUE] server') or msg.startswith('[RED] server'):
        return

    # ── Slot change: "PlayerName (id) changed slot: SLOT" ─────────────────────
    m = re.match(r'^(.+?) \(\d+\) changed slot: (.+)$', msg)
    if m:
        player = clean_pilot_name(m.group(1).strip())
        slot = m.group(2).strip()
        if not player:
            return
        player_slot[player] = slot
        if slot != 'spectators' and not ARTY_SLOT_RE.match(slot):
            stats[player]['flights'] += 1
        if slot.startswith('artillery_commander_blue'):
            player_coalition[player] = 'Friendlies'
        elif slot.startswith('artillery_commander_red'):
            player_coalition[player] = 'Hostiles'
        return

    # ── Disconnect: optional "bXXXX|" prefix, "PlayerName (id) disconnected" ──
    m = re.match(r'^(?:b[0-9a-f]+\|)?(.+?) \(\d+\) disconnected$', msg, re.IGNORECASE)
    if m:
        player = clean_pilot_name(m.group(1).strip())
        if player:
            player_slot[player] = None
        return

    # ── Kill: "bVICTIM|Killed by KILLER with WEAPON" ──────────────────────────
    m = re.match(r'^(b[0-9a-f]+)\|Killed by (.+?) with (.+)$', msg)
    if m:
        victim_id  = m.group(1)
        killer_raw = m.group(2).strip()
        # weapon   = m.group(3).strip()  # available if needed later

        if not is_human_pilot(killer_raw):
            return  # AI or numeric unit ID — not a player kill
        killer = clean_pilot_name(killer_raw)
        if not killer:
            return

        victim_obj  = objects.get(victim_id, {})
        victim_type = victim_obj.get('type') or ''
        victim_pilot = victim_obj.get('pilot') or ''
        slot = player_slot.get(killer) or ''

        if ARTY_SLOT_RE.match(slot):
            stats[killer]['gg_kills'] += 1
        elif is_air_type(victim_type):
            if is_human_pilot(victim_pilot):
                stats[killer]['aa_kills_human'] += 1
            else:
                stats[killer]['aa_kills_ai'] += 1
        else:
            stats[killer]['ag_kills'] += 1
        return

    # ── Route set: "bXXXX|UnitName (unit_id) route set by PlayerName (player_id)" ──
    m = re.match(r'^b[0-9a-f]+\|.+ route set by (.+?) \(\d+\)$', msg)
    if m:
        player = clean_pilot_name(m.group(1).strip())
        if player:
            stats[player]['routes_set'] += 1
        return

    # ── Fired: "bXXXX|UnitName (PlayerName) Fired WeaponType (weapon_id)" ─────
    # Guns appear as "started/stopped shooting" — not a Fired event, so all
    # Fired events are missiles, bombs, rockets, or tank rounds.
    m = re.match(r'^b[0-9a-f]+\|.+? \((.+?)\) Fired (.+?) \(\d+\)$', msg)
    if m:
        pilot_raw = m.group(1)
        weapon    = m.group(2).strip()
        if is_human_pilot(pilot_raw):
            player = clean_pilot_name(pilot_raw)
            if player:
                stats[player]['weapons_fired'][weapon] += 1
        return

    # ── Unpack: "[COALITION] PlayerName (id): -unpack [unit_id]" ──────────────
    m = re.match(r'^\[(\w+)\] (.+?) \(\d+\): -?unpack(?: (\d+))?$', msg)
    if m:
        coalition_tag = m.group(1).upper()
        player  = clean_pilot_name(m.group(2).strip())
        unit_id = m.group(3)  # may be None
        if not player:
            return
        coalition = ('Friendlies' if coalition_tag == 'BLUE'
                     else 'Hostiles' if coalition_tag == 'RED'
                     else player_coalition.get(player))
        if coalition:
            player_coalition[player] = coalition
        pending_unpacks.append({
            't':         t,
            'player':    player,
            'coalition': coalition or player_coalition.get(player),
            'unit_id':   unit_id,
        })
        return


def _attribute_farp(farp_obj, t, pending_unpacks, stats):
    """
    Try to attribute a newly-spawned FARP cluster to the player who built it.
    Matches the most recent -unpack event within 30s with the same coalition.
    Consuming the unpack prevents the rest of the spawn cluster from double-counting.
    """
    farp_coalition = farp_obj.get('coalition')

    candidates = [
        u for u in pending_unpacks
        if 0 <= (t - u['t']) <= 30
        and (u['coalition'] == farp_coalition or u['coalition'] is None)
    ]
    if not candidates:
        return

    best = max(candidates, key=lambda u: u['t'])
    stats[best['player']]['farps_built'] += 1
    pending_unpacks.remove(best)


# ── Aggregation ───────────────────────────────────────────────────────────────

def merge_stats(totals, session_stats):
    """Accumulate per-session stats into campaign totals."""
    for player, s in session_stats.items():
        t = totals[player]
        t['aa_kills_human'] += s['aa_kills_human']
        t['aa_kills_ai']    += s['aa_kills_ai']
        t['ag_kills']       += s['ag_kills']
        t['gg_kills']       += s['gg_kills']
        t['routes_set']     += s['routes_set']
        t['farps_built']    += s['farps_built']
        t['flights']        += s['flights']
        for weapon, count in s['weapons_fired'].items():
            t['weapons_fired'][weapon] += count


# ── Campaign runner ───────────────────────────────────────────────────────────

def process_campaign(campaign_folder, raw_dir, out_dir):
    campaign_dir = os.path.join(raw_dir, campaign_folder)
    if not os.path.isdir(campaign_dir):
        print(f"ERROR: not found: {campaign_dir}")
        return

    acmi_files = sorted(
        f for f in os.listdir(campaign_dir)
        if re.search(r'\.acmi$', f, re.I)
    )
    if not acmi_files:
        print(f"  No .acmi files in {campaign_folder}")
        return

    print(f"\n=== {campaign_folder} ({len(acmi_files)} sessions) ===")

    campaign_totals = _new_stats_store()

    for fname in acmi_files:
        path = os.path.join(campaign_dir, fname)
        print(f"\nParsing: {fname}")
        session_stats = parse_session(path)
        merge_stats(campaign_totals, session_stats)

    # Serialise — convert defaultdicts to plain dicts, sort weapons alphabetically
    output_players = {}
    for player, s in sorted(campaign_totals.items()):
        wf = dict(sorted(s['weapons_fired'].items()))
        output_players[player] = {
            'flights':        s['flights'],
            'aa_kills_human': s['aa_kills_human'],
            'aa_kills_ai':    s['aa_kills_ai'],
            'ag_kills':       s['ag_kills'],
            'gg_kills':       s['gg_kills'],
            'routes_set':     s['routes_set'],
            'farps_built':    s['farps_built'],
            'weapons_fired':  wf,
            'weapons_total':  sum(wf.values()),
        }

    output = {
        'campaign':  campaign_folder,
        'generated': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'sessions':  len(acmi_files),
        'players':   output_players,
    }

    out_path = os.path.join(out_dir, campaign_folder, 'campaign_medals.json')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    total_kills = sum(
        p['aa_kills_human'] + p['aa_kills_ai'] + p['ag_kills'] + p['gg_kills']
        for p in output_players.values()
    )
    print(f"\n  Players: {len(output_players)}")
    print(f"  Total kills across campaign: {total_kills}")
    print(f"  Written: {out_path}")
    return output


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    raw_root = os.path.join(script_dir, 'raw')
    out_root = os.path.join(script_dir, 'public', 'data')

    if not os.path.isdir(raw_root):
        print(f"ERROR: raw/ directory not found at {raw_root}")
        sys.exit(1)

    if len(sys.argv) >= 2:
        process_campaign(sys.argv[1], raw_root, out_root)
    else:
        for campaign_folder in sorted(os.listdir(raw_root)):
            if os.path.isdir(os.path.join(raw_root, campaign_folder)):
                process_campaign(campaign_folder, raw_root, out_root)


if __name__ == '__main__':
    main()

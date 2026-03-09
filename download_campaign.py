#!/usr/bin/env python3
"""
download_campaign.py — Download ACMI files from a strategic-dcs.com tacview directory,
then optionally parse and rebuild campaigns.json.

Usage (run from project root — the folder containing raw/ and public/):
    python download_campaign.py https://strategic-dcs.com/tacview/2026-02-03-1649-PersianGulf/
"""

import os
import re
import sys
import hashlib
import subprocess
import urllib.request
import urllib.error
from html.parser import HTMLParser


# ── Helpers ───────────────────────────────────────────────────────────────────

class LinkParser(HTMLParser):
    """Extract href links from an HTML directory listing."""
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for k, v in attrs:
                if k == 'href' and v:
                    self.links.append(v)


def folder_name_from_url(url):
    """
    Convert a tacview URL folder name to the raw/ folder naming convention.

    '2026-02-03-1649-PersianGulf'  →  '2026-02-03 Persian Gulf'
    '2026-02-21-0900-GermanyInverted'  →  '2026-02-21 Germany Inverted'
    """
    # Strip trailing slash, take last path component
    slug = url.rstrip('/').split('/')[-1]

    # Extract date: YYYY-MM-DD
    m = re.match(r'^(\d{4}-\d{2}-\d{2})-\d{4}-(.+)$', slug)
    if not m:
        # Fallback: just use slug as-is
        return slug

    date_part = m.group(1)          # 2026-02-03
    name_part = m.group(2)          # PersianGulf  or  GermanyInverted

    # Insert spaces before capital letters (CamelCase → Title Case)
    spaced = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', name_part)

    return f"{date_part} {spaced}"


def human_size(n):
    for unit in ['B','KB','MB','GB']:
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def download_file(url, dest_path, expected_size=None):
    """Download url → dest_path with a simple progress indicator."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'sdcs-downloader/1.0'})
        with urllib.request.urlopen(req, timeout=60) as resp:
            total = int(resp.headers.get('Content-Length', 0))
            downloaded = 0
            chunk = 65536
            with open(dest_path, 'wb') as f:
                while True:
                    data = resp.read(chunk)
                    if not data:
                        break
                    f.write(data)
                    downloaded += len(data)
                    if total:
                        pct = downloaded / total * 100
                        bar = '█' * int(pct / 5) + '░' * (20 - int(pct / 5))
                        print(f"\r    [{bar}] {pct:5.1f}%  {human_size(downloaded)}", end='', flush=True)
            print()  # newline after progress
        return downloaded
    except urllib.error.HTTPError as e:
        print(f"\n    ✗ HTTP {e.code}: {e.reason}")
        return None
    except Exception as e:
        print(f"\n    ✗ Error: {e}")
        return None


def verify_file(path):
    """Basic integrity check — file exists, non-zero, readable."""
    if not os.path.exists(path):
        return False, "file missing"
    size = os.path.getsize(path)
    if size == 0:
        return False, "zero bytes"
    # Try reading first and last 1KB
    try:
        with open(path, 'rb') as f:
            f.read(1024)
            f.seek(max(0, size - 1024))
            f.read(1024)
    except Exception as e:
        return False, str(e)
    return True, f"{human_size(size)}"


def already_parsed(acmi_path, project_root):
    """
    Check whether a session JSON already exists in public/data/<campaign>/ for this ACMI.
    """
    acmi_dir = os.path.dirname(os.path.abspath(acmi_path))
    campaign_folder = os.path.basename(acmi_dir)
    stem = os.path.basename(acmi_path)
    stem = re.sub(r'(\.zip)?\.acmi$', '', stem, flags=re.I)
    json_path = os.path.join(project_root, 'public', 'data', campaign_folder, f'session_{stem}.json')
    return os.path.exists(json_path), json_path


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    # ── 1. Get URL ────────────────────────────────────────────────────────────
    if len(sys.argv) > 1:
        url = sys.argv[1].rstrip('/')
    else:
        url = input("Paste tacview directory URL: ").strip().rstrip('/')

    if not url.startswith('http'):
        print("ERROR: URL must start with http:// or https://")
        sys.exit(1)

    print(f"\nFetching directory listing: {url}/")

    # ── 2. Parse directory listing ────────────────────────────────────────────
    try:
        req = urllib.request.Request(url + '/', headers={'User-Agent': 'sdcs-downloader/1.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        print(f"ERROR: Could not fetch directory listing: {e}")
        sys.exit(1)

    parser = LinkParser()
    parser.feed(html)

    # Filter to ACMI files only (any .acmi or .zip.acmi link)
    acmi_links = [
        l for l in parser.links
        if re.search(r'\.(zip\.acmi|acmi)$', l, re.I)
        and not l.startswith('?')
        and not l.startswith('/')
        and not l.startswith('http')
    ]

    if not acmi_links:
        print("ERROR: No ACMI files found in directory listing.")
        print("       Check the URL is a valid tacview directory.")
        sys.exit(1)

    acmi_links.sort()
    print(f"Found {len(acmi_links)} ACMI file(s).")

    # ── 3. Derive folder name ─────────────────────────────────────────────────
    project_root = os.path.abspath('.')
    folder_name = folder_name_from_url(url)
    raw_dir = os.path.join(project_root, 'raw', folder_name)

    print(f"\nCampaign folder: raw/{folder_name}/")

    if not os.path.exists(raw_dir):
        os.makedirs(raw_dir)
        print(f"  Created: {raw_dir}")
    else:
        print(f"  Already exists.")

    # ── 4. Download ───────────────────────────────────────────────────────────
    print(f"\nDownloading {len(acmi_links)} file(s)...\n")

    downloaded_ok = []
    skipped = []
    failed = []

    for link in acmi_links:
        # Build full URL
        file_url = f"{url}/{link}" if not link.startswith('http') else link
        dest = os.path.join(raw_dir, link)

        if os.path.exists(dest):
            ok, info = verify_file(dest)
            if ok:
                print(f"  ↷  {link}  (already downloaded, {info})")
                skipped.append(dest)
                continue
            else:
                print(f"  ⚠  {link}  (exists but {info}, re-downloading)")

        print(f"  ↓  {link}")
        size = download_file(file_url, dest)

        if size is None:
            failed.append(link)
            continue

        ok, info = verify_file(dest)
        if ok:
            print(f"    ✓  {info}")
            downloaded_ok.append(dest)
        else:
            print(f"    ✗  Verification failed: {info}")
            failed.append(link)

    # ── 5. Summary ────────────────────────────────────────────────────────────
    print(f"\n{'─'*60}")
    print(f"  Downloaded:  {len(downloaded_ok)}")
    print(f"  Skipped:     {len(skipped)}  (already present)")
    print(f"  Failed:      {len(failed)}")
    if failed:
        print(f"\n  Failed files:")
        for f in failed:
            print(f"    • {f}")
        print("\n  Re-run the script to retry failed downloads.")

    if failed:
        sys.exit(1)

    all_acmi = sorted([
        os.path.join(raw_dir, f) for f in os.listdir(raw_dir)
        if re.search(r'\.(zip\.acmi|acmi)$', f, re.I)
    ])

    # ── 6. Prompt to parse ────────────────────────────────────────────────────
    print(f"\n{'═'*60}")
    print(f"  All files verified. {len(all_acmi)} ACMI file(s) in raw/{folder_name}/")
    print(f"{'═'*60}")

    # Check which ones haven't been parsed yet
    to_parse = []
    already_done = []
    for acmi in all_acmi:
        done, json_path = already_parsed(acmi, project_root)
        if done:
            already_done.append((acmi, json_path))
        else:
            to_parse.append(acmi)

    if already_done:
        print(f"\n  Already parsed: {len(already_done)} session(s) — skipping these.")

    if not to_parse:
        print("\n  ✓ All files already parsed. Skipping to build_campaigns.\n")
    else:
        print(f"\n  {len(to_parse)} session(s) need parsing.")
        answer = input(f"\n  Parse now? [Y/n] ").strip().lower()
        if answer not in ('', 'y', 'yes'):
            print("\n  Skipped. Run parse_acmi.py manually when ready.")
            sys.exit(0)

        print()
        parse_ok = []
        parse_fail = []
        for i, acmi in enumerate(to_parse, 1):
            fname = os.path.basename(acmi)
            print(f"  [{i}/{len(to_parse)}] {fname}")
            result = subprocess.run(
                [sys.executable, 'parse_acmi.py', acmi],
                capture_output=False
            )
            if result.returncode == 0:
                parse_ok.append(acmi)
            else:
                parse_fail.append(acmi)
                print(f"    ✗ parse_acmi.py failed for {fname}")

        print(f"\n  Parsed: {len(parse_ok)}  Failed: {len(parse_fail)}")
        if parse_fail:
            print("  Some files failed to parse — check output above.")

    # ── 7. Prompt to rebuild campaigns.json ───────────────────────────────────
    print(f"\n{'─'*60}")
    answer = input("  Rebuild campaigns.json now? [Y/n] ").strip().lower()
    if answer in ('', 'y', 'yes'):
        print()
        result = subprocess.run(
            [sys.executable, 'build_campaigns.py'],
            capture_output=False
        )
        if result.returncode == 0:
            print("\n  ✓ campaigns.json updated.")
        else:
            print("\n  ✗ build_campaigns.py failed — check output above.")
    else:
        print("\n  Skipped. Run build_campaigns.py manually when ready.")

    print(f"\nDone!\n")


if __name__ == '__main__':
    main()

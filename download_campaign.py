#!/usr/bin/env python3
"""
download_campaign.py -- Download ACMI files from a strategic-dcs.com tacview directory,
then optionally parse and rebuild campaigns.json.

Usage (run from project root -- the folder containing raw/ and public/):
    python download_campaign.py https://strategic-dcs.com/tacview/2026-03-05-0657-Caucasus/

Multiple URLs can be passed as arguments:
    python download_campaign.py <url1> <url2> <url3> ...

Or paste multiple URLs interactively (one per line, blank line to finish).

Files smaller than MIN_ACMI_BYTES (default 1 MB) are treated as junk and skipped.
"""

import os
import re
import sys
import subprocess
import urllib.request
import urllib.error
from html.parser import HTMLParser


# Files under this size are considered junk (aborted/crashed sessions).
# The smallest legitimate session seen so far is ~1.4 MB; junk files are <100 KB.
MIN_ACMI_BYTES = 1_048_576  # 1 MB


# -- Helpers ------------------------------------------------------------------

class LinkParser(HTMLParser):
    """
    Extract href links and their file sizes from an HTML directory listing.

    Apache/nginx listings look like:
        <a href="foo.zip.acmi">foo.zip.acmi</a>   05-Mar-2026 12:58   10007147

    We capture links as before, and also build a sizes dict {filename -> int bytes}
    by reading the text node that follows each ACMI <a> tag.
    """
    def __init__(self):
        super().__init__()
        self.links = []
        self.sizes = {}        # filename -> int bytes
        self._last_href = None

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for k, v in attrs:
                if k == 'href' and v:
                    self.links.append(v)
                    if re.search(r'\.(zip\.acmi|acmi)$', v, re.I):
                        self._last_href = v

    def handle_data(self, data):
        if self._last_href:
            stripped = data.strip()
            if stripped:
                tokens = stripped.split()
                last = tokens[-1]
                if re.fullmatch(r'\d+', last):
                    self.sizes[self._last_href] = int(last)
                self._last_href = None  # consumed regardless


def folder_name_from_url(url):
    """
    Convert a tacview URL folder name to the raw/ folder naming convention.

    '2026-02-03-1649-PersianGulf'      ->  '2026-02-03 Persian Gulf'
    '2026-02-21-0900-GermanyInverted'  ->  '2026-02-21 Germany Inverted'
    """
    slug = url.rstrip('/').split('/')[-1]
    m = re.match(r'^(\d{4}-\d{2}-\d{2})-\d{4}-(.+)$', slug)
    if not m:
        return slug
    date_part = m.group(1)
    name_part = m.group(2)
    spaced = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', name_part)
    return f"{date_part} {spaced}"


def human_size(n):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def get_remote_size(url):
    """HEAD request to get Content-Length. Returns 0 on failure."""
    try:
        req = urllib.request.Request(
            url, method='HEAD',
            headers={'User-Agent': 'sdcs-downloader/1.0'}
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            return int(r.headers.get('Content-Length', 0))
    except Exception:
        return 0


def download_file(url, dest_path):
    """Download url -> dest_path with a simple progress indicator."""
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
                        bar = '\u2588' * int(pct / 5) + '\u2591' * (20 - int(pct / 5))
                        print(f"\r    [{bar}] {pct:5.1f}%  {human_size(downloaded)}", end='', flush=True)
            print()
        return downloaded
    except urllib.error.HTTPError as e:
        print(f"\n    \u2717 HTTP {e.code}: {e.reason}")
        return None
    except Exception as e:
        print(f"\n    \u2717 Error: {e}")
        return None


def verify_file(path):
    """Basic integrity check -- file exists, non-zero, readable."""
    if not os.path.exists(path):
        return False, "file missing"
    size = os.path.getsize(path)
    if size == 0:
        return False, "zero bytes"
    try:
        with open(path, 'rb') as f:
            f.read(1024)
            f.seek(max(0, size - 1024))
            f.read(1024)
    except Exception as e:
        return False, str(e)
    return True, f"{human_size(size)}"


def acmi_stem(filename):
    """Strip .zip.acmi or .acmi suffix -- must match parse_acmi.py logic exactly."""
    stem = re.sub(r'\.zip\.acmi$', '', filename, flags=re.I)
    stem = re.sub(r'\.acmi$', '', stem, flags=re.I)
    return stem


def already_parsed(acmi_path, project_root):
    """
    Check whether a session JSON already exists in public/data/<campaign>/ for this ACMI.
    """
    acmi_dir = os.path.dirname(os.path.abspath(acmi_path))
    campaign_folder = os.path.basename(acmi_dir)
    stem = acmi_stem(os.path.basename(acmi_path))
    json_path = os.path.join(project_root, 'public', 'data', campaign_folder, f'session_{stem}.json')
    return os.path.exists(json_path), json_path


def process_url(url, project_root):
    """
    Fetch directory listing, skip junk files, download valid ACMI files for one URL.
    Returns (all_acmi_paths, folder_name, had_failures).
    """
    print(f"\n{'='*60}")
    print(f"  Fetching directory listing: {url}/")
    print(f"{'='*60}")

    try:
        req = urllib.request.Request(url + '/', headers={'User-Agent': 'sdcs-downloader/1.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        print(f"  ERROR: Could not fetch directory listing: {e}")
        return [], None, True

    parser = LinkParser()
    parser.feed(html)

    all_links = sorted([
        l for l in parser.links
        if re.search(r'\.(zip\.acmi|acmi)$', l, re.I)
        and not l.startswith('?')
        and not l.startswith('/')
        and not l.startswith('http')
    ])

    if not all_links:
        print("  ERROR: No ACMI files found in directory listing.")
        print("         Check the URL is a valid tacview directory.")
        return [], None, True

    # Separate good files from junk based on size.
    # Size comes from the HTML listing; fall back to a HEAD request if not parsed.
    acmi_links = []
    junk_links = []
    for link in all_links:
        size = parser.sizes.get(link)
        if size is None:
            size = get_remote_size(f"{url}/{link}")
        if size < MIN_ACMI_BYTES:
            junk_links.append((link, size))
        else:
            acmi_links.append(link)

    print(f"  Found {len(all_links)} ACMI file(s).")
    if junk_links:
        print(f"  Skipping {len(junk_links)} junk file(s) under {human_size(MIN_ACMI_BYTES)}:")
        for name, sz in junk_links:
            print(f"    \u2205  {name}  ({human_size(sz)})")

    if not acmi_links:
        print("  ERROR: No valid ACMI files remain after junk filter.")
        return [], None, True

    folder_name = folder_name_from_url(url)
    raw_dir = os.path.join(project_root, 'raw', folder_name)

    print(f"\n  Campaign folder: raw/{folder_name}/")
    if not os.path.exists(raw_dir):
        os.makedirs(raw_dir)
        print(f"  Created: {raw_dir}")
    else:
        print(f"  Already exists.")

    print(f"\n  Downloading {len(acmi_links)} file(s)...\n")

    downloaded_ok = []
    skipped = []
    failed = []

    for link in acmi_links:
        file_url = f"{url}/{link}"
        dest = os.path.join(raw_dir, link)

        if os.path.exists(dest):
            ok, info = verify_file(dest)
            if ok:
                print(f"  \u21b7  {link}  (already downloaded, {info})")
                skipped.append(dest)
                continue
            else:
                print(f"  \u26a0  {link}  (exists but {info}, re-downloading)")

        print(f"  \u2193  {link}")
        size = download_file(file_url, dest)

        if size is None:
            failed.append(link)
            continue

        ok, info = verify_file(dest)
        if ok:
            print(f"    \u2713  {info}")
            downloaded_ok.append(dest)
        else:
            print(f"    \u2717  Verification failed: {info}")
            failed.append(link)

    print(f"\n  {'-'*56}")
    print(f"  Downloaded:  {len(downloaded_ok)}")
    print(f"  Skipped:     {len(skipped)}  (already present)")
    print(f"  Junk:        {len(junk_links)}  (too small, ignored)")
    print(f"  Failed:      {len(failed)}")
    if failed:
        print(f"\n  Failed files:")
        for f in failed:
            print(f"    - {f}")

    all_acmi = sorted([
        os.path.join(raw_dir, f) for f in os.listdir(raw_dir)
        if re.search(r'\.(zip\.acmi|acmi)$', f, re.I)
    ])

    return all_acmi, folder_name, bool(failed)


# -- Main ---------------------------------------------------------------------

def main():
    project_root = os.path.abspath('.')

    # -- 1. Collect URLs ------------------------------------------------------
    if len(sys.argv) > 1:
        urls = [u.rstrip('/') for u in sys.argv[1:]]
    else:
        print("Paste tacview directory URL(s), one per line.")
        print("Press Enter on a blank line when done.\n")
        urls = []
        while True:
            line = input("  URL: ").strip().rstrip('/')
            if not line:
                if urls:
                    break
                print("  (Enter at least one URL)")
            else:
                urls.append(line)

    bad = [u for u in urls if not u.startswith('http')]
    if bad:
        for u in bad:
            print(f"ERROR: URL must start with http:// or https://  ->  {u}")
        sys.exit(1)

    print(f"\n{len(urls)} URL(s) queued.")

    # -- 2. Download all URLs -------------------------------------------------
    all_acmi_paths = []
    any_failures = False

    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] {url}")
        acmi_paths, folder_name, had_failures = process_url(url, project_root)
        all_acmi_paths.extend(acmi_paths)
        if had_failures:
            any_failures = True

    if any_failures:
        print("\n\u26a0  Some downloads failed -- re-run to retry.")

    if not all_acmi_paths:
        print("\nNo ACMI files available. Exiting.")
        sys.exit(1)

    # -- 3. Prompt to parse ---------------------------------------------------
    to_parse = []
    already_done = []
    for acmi in all_acmi_paths:
        done, json_path = already_parsed(acmi, project_root)
        if done:
            already_done.append((acmi, json_path))
        else:
            to_parse.append(acmi)

    print(f"\n{'='*60}")
    print(f"  Total ACMI files across all campaigns: {len(all_acmi_paths)}")
    if already_done:
        print(f"  Already parsed: {len(already_done)} session(s) -- skipping these.")
    print(f"{'='*60}")

    if not to_parse:
        print("\n  \u2713 All files already parsed. Skipping to build_campaigns.\n")
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
                print(f"    \u2717 parse_acmi.py failed for {fname}")

        print(f"\n  Parsed: {len(parse_ok)}  Failed: {len(parse_fail)}")
        if parse_fail:
            print("  Some files failed to parse -- check output above.")

    # -- 4. Prompt to rebuild campaigns.json ----------------------------------
    print(f"\n{'-'*60}")
    answer = input("  Rebuild campaigns.json now? [Y/n] ").strip().lower()
    if answer in ('', 'y', 'yes'):
        print()
        result = subprocess.run(
            [sys.executable, 'build_campaigns.py'],
            capture_output=False
        )
        if result.returncode == 0:
            print("\n  \u2713 campaigns.json updated.")
        else:
            print("\n  \u2717 build_campaigns.py failed -- check output above.")
    else:
        print("\n  Skipped. Run build_campaigns.py manually when ready.")

    print(f"\nDone!\n")


if __name__ == '__main__':
    main()

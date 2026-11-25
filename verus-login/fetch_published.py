"""Download PDD Kit's page script and extract the published verified/src/login.rs from it.

The page renders the file from a JavaScript array of source lines. This script fetches that
asset, refuses to continue if its hash differs from the one recorded on 2026-11-24, and
writes the extracted file (LF line endings) for study.py to read.

Usage:
    python fetch_published.py [--out PATH]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path

from study import ASSET_SHA256, ASSET_URL, DEFAULT_PUBLISHED, PUBLISHED_SHA256

LINE = re.compile(r'\s*(`(?:[^`\\]|\\.)*`|"(?:[^"\\]|\\.)*")\s*(,|\])', re.S)


def extract(body: str) -> str:
    start = body.index("//! The async login flow")
    position = body.rfind("[", 0, start) + 1
    lines = []
    while True:
        match = LINE.match(body, position)
        if not match:
            raise ValueError("source array ended unexpectedly")
        literal = match.group(1)
        if literal.startswith("`"):
            lines.append(literal[1:-1].replace("\\`", "`").replace("\\\\", "\\"))
        else:
            lines.append(json.loads(literal))
        position = match.end()
        if match.group(2) == "]":
            return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=DEFAULT_PUBLISHED)
    args = parser.parse_args()
    with urllib.request.urlopen(ASSET_URL, timeout=30) as response:
        raw = response.read()
    if hashlib.sha256(raw).hexdigest() != ASSET_SHA256:
        print("the page script changed since 2026-11-24; refusing to extract", file=sys.stderr)
        return 2
    source = extract(raw.decode("utf-8"))
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
    if digest != PUBLISHED_SHA256:
        print(f"extracted file hash {digest} differs from {PUBLISHED_SHA256}", file=sys.stderr)
        return 2
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(source.encode("utf-8"))
    print("extracted", len(source.splitlines()), "lines, sha256", digest)
    return 0


if __name__ == "__main__":
    sys.exit(main())

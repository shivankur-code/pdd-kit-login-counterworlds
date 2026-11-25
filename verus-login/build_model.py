"""Rebuild login_model.rs from login_model.template.rs and PDD Kit's published login.rs.

The template holds the stand-ins and proved bodies written for this study. Each line
`//@published A-B` stands for published lines A to B, with the type-path substitutions
and regroupings listed in study.py applied. The rebuilt file must match the model hash
recorded in the saved evidence.

Usage:
    python fetch_published.py
    python build_model.py [--published PATH]
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

from study import DEFAULT_PUBLISHED, MODEL, PUBLISHED_SHA256, normalize_published

TEMPLATE = Path(__file__).resolve().parent / "login_model.template.rs"
MODEL_SHA256 = "cbdfd3c97f4a7981c94b6835dcfb59115edcfa5ec4702b544880342dbfe5f965"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--published", type=Path, default=DEFAULT_PUBLISHED)
    args = parser.parse_args()
    published = args.published.read_bytes().replace(b"\r\n", b"\n")
    if hashlib.sha256(published).hexdigest() != PUBLISHED_SHA256:
        print("published file differs from the one studied; run fetch_published.py", file=sys.stderr)
        return 2
    lines = [normalize_published(line) for line in published.decode("utf-8").splitlines()]
    model = []
    for line in TEMPLATE.read_text(encoding="utf-8").splitlines():
        reference = re.fullmatch(r"//@published (\d+)-(\d+)", line)
        model.extend(lines[int(reference.group(1)) - 1:int(reference.group(2))] if reference else [line])
    # The studied model file had Windows line endings, and the recorded hash covers those bytes.
    data = ("\r\n".join(model) + "\r\n").encode("utf-8")
    digest = hashlib.sha256(data).hexdigest()
    if digest != MODEL_SHA256:
        print(f"rebuilt model hash {digest} differs from {MODEL_SHA256}", file=sys.stderr)
        return 2
    MODEL.write_bytes(data)
    print("rebuilt", MODEL.name, "sha256", digest)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Download, verify, query, and cite an OPK SQLite release using only stdlib."""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import urllib.request
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("base_url", help="Release asset base URL ending in /")
    parser.add_argument("--output", type=Path, default=Path("opk.sqlite"))
    args = parser.parse_args()
    with urllib.request.urlopen(args.base_url + "manifest.json", timeout=30) as response:
        manifest = json.load(response)
    artifact = next(
        item for item in manifest["artifacts"] if item["path"].endswith("open-provenance-knowledge.sqlite")
    )
    with urllib.request.urlopen(args.base_url + Path(artifact["path"]).name, timeout=30) as response:
        payload = response.read()
    if hashlib.sha256(payload).hexdigest() != artifact["sha256"]:
        raise SystemExit("checksum mismatch")
    args.output.write_bytes(payload)
    connection = sqlite3.connect(f"file:{args.output}?mode=ro", uri=True)
    rows = connection.execute(
        "SELECT subject_id, predicate, object_id, status FROM relationships "
        "WHERE status = 'disputed' OR predicate = 'not-equivalent-to' ORDER BY id"
    )
    for subject, predicate, object_id, status in rows:
        print(f"{subject} {predicate} {object_id} [{status}; release {manifest['release']}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

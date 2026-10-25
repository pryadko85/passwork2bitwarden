#!/usr/bin/env python3
"""Run both converters on sample/sample.json and verify the output."""

import csv
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "sample" / "sample.json"


def run(cmd):
    print("$", " ".join(str(c) for c in cmd))
    subprocess.run(cmd, check=True)


def main():
    src = json.loads(SRC.read_text())
    n = len(src["passwords"])

    # JSON converter
    run([sys.executable, str(HERE / "convert.py"), str(SRC), str(HERE / "vault-export.json")])
    out = json.loads((HERE / "vault-export.json").read_text())
    assert len(out["items"]) == n, f"expected {n} items, got {len(out['items'])}"
    assert all(it["type"] == 1 for it in out["items"])
    folder_ids = {f["id"] for f in out["folders"]}
    assert all(it["folderId"] in folder_ids or it["folderId"] is None for it in out["items"]), \
        "dangling folderId"

    # CSV converter
    run([sys.executable, str(HERE / "convert_csv.py"), str(SRC), str(HERE / "vault-export.csv")])
    with open(HERE / "vault-export.csv", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == n, f"expected {n} csv rows, got {len(rows)}"

    print(f"OK: {n} entries converted to both formats, all checks passed")


if __name__ == "__main__":
    main()

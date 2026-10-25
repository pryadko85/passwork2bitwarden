#!/usr/bin/env python3
"""Passwork JSON → Bitwarden CSV (Vaultwarden-ready)."""

import csv
import json
import sys
from pathlib import Path

# --- Passwork → Bitwarden field mapping ----------------------------------------
#   Passwork fields          Bitwarden CSV column
#   fields.name             name
#   fields.login            username
#   fields.password         password
#   fields.url              urL
#   fields.note             notes
#   path[] (full chain)     folder
#   fields.custom[]         notes (appended as key: value)

# --- Bitwarden CSV header (exact column order) --------------------------------
BW_HEADER = ["favorite", "folder", "name", "notes", "username", "password", "urL", "totp", "bitwarden:autofill_compatibility"]


def build_folder_path(entry):
    """Reconstruct folder chain: vault name prepended (Bitwarden CSV folders are flat)."""
    names = [node["name"] for node in entry.get("path", []) if node.get("name")]
    vault = entry.get("vaultName", "")
    parts = ([vault] if vault else []) + names
    return " / ".join(parts)


def build_notes(entry):
    """Combine note field, tags, and custom fields into one notes string."""
    fields = entry.get("fields", {})
    parts = []
    if fields.get("note"):
        parts.append(fields["note"])
    for custom in fields.get("custom", []):
        cname = custom.get("name", "custom")
        cval = custom.get("value", "")
        if cval:
            parts.append(f"{cname}: {cval}")
    tags = entry.get("tags") or []
    if tags:
        parts.append("tags: " + " ".join(tags))
    return "\n".join(parts)


def convert(vadzhet_path, output_path):
    with open(vadzhet_path) as f:
        data = json.load(f)

    passwords = data["passwords"]
    rows = []
    for p in passwords:
        fields = p.get("fields", {})
        rows.append({
            "favorite": "0",
            "folder": build_folder_path(p),
            "name": fields.get("name", ""),
            "notes": build_notes(p),
            "username": fields.get("login", ""),
            "password": fields.get("password", ""),
            "urL": fields.get("url", ""),
            "totp": "",
            "bitwarden:autofill_compatibility": "",
        })

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=BW_HEADER)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Converted {len(rows)} entries → {output_path}")


if __name__ == "__main__":
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/srv/webdav/in/vault/export.json")
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("/srv/webdav/out/vault-export.csv")
    dst.parent.mkdir(parents=True, exist_ok=True)
    convert(src, dst)

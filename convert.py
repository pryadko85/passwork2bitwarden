#!/usr/bin/env python3
"""Passwork JSON -> Bitwarden JSON (official Bitwarden/Vaultwarden import format).

Format source: https://bitwarden.com/help/condition-bitwarden-import/
Top-level keys: "folders" (flat name -> uuid) and "items" (with folderId).
"""

import json
import sys
import uuid


def convert(vadzhet_path, output_path):
    with open(vadzhet_path) as f:
        data = json.load(f)

    # Build folder map: unique full path -> uuid
    folders = {}
    items = []

    for p in data["passwords"]:
        fields = p.get("fields", {})

        # Folder chain: vault + path (Bitwarden stores nesting as "a / b" flat names)
        parts = []
        vault = p.get("vaultName", "")
        if vault:
            parts.append(vault)
        parts.extend(n["name"] for n in p.get("path", []) if n.get("name"))
        folder_name = " / ".join(parts) if parts else None
        folder_id = None
        if folder_name:
            if folder_name not in folders:
                folders[folder_name] = str(uuid.uuid4())
            folder_id = folders[folder_name]

        # Notes: original note + custom fields + tags
        notes = []
        if fields.get("note"):
            notes.append(fields["note"])
        for c in fields.get("custom", []):
            if c.get("value"):
                notes.append(f"{c.get('name', 'custom')}: {c['value']}")
        tags = p.get("tags") or []
        if tags:
            notes.append("tags: " + " ".join(tags))

        login = {
            "uris": [{"match": None, "uri": fields["url"]}] if fields.get("url") else None,
            "username": fields.get("login") or None,
            "password": fields.get("password") or None,
            "totp": None,
        }

        item = {
            "id": str(uuid.uuid4()),
            "organizationId": None,
            "folderId": folder_id,
            "type": 1,  # Login
            "name": fields.get("name") or "",
            "notes": "\n".join(notes) or None,
            "favorite": False,
            "fields": None,
            "login": login,
            "reprompt": 0,
            "collectionIds": None,
            "passwordHistory": [],
        }
        items.append(item)

    out = {
        "folders": [{"id": fid, "name": fname} for fname, fid in folders.items()],
        "items": items,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"Converted {len(items)} items, {len(folders)} folders -> {output_path}")


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "/srv/webdav/in/vault/export.json"
    dst = sys.argv[2] if len(sys.argv) > 2 else "/srv/webdav/out/vault/vault-export.json"
    convert(src, dst)

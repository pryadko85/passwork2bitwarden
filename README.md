# Passwork2bitwarden

Converts a password vault export from [Passwork](https://Passwork.com/) (a Russian password
manager) into the official **Bitwarden import format** - a JSON file you can import
into **Vaultwarden** or any Bitwarden-compatible vault.

Also ships a second converter that produces the Bitwarden **CSV** format.

## Why

Passwork only exports its own JSON schema. If you outgrow it, there is no direct path to
the de-facto standard. This project bridges that gap with zero external dependencies:
plain Python 3 standard library, one script per target format.

## Output

- `vault-export.json` - `{"folders": [...], "items": [...]}` - the exact format Bitwarden
  and Vaultwarden expect when you pick **Bitwarden (json)** in the import dialog.
- `vault-export.csv` - Bitwarden CSV (logins and secure notes only) for the
  **Bitwarden (csv)** import option.

Field mapping:

| Passwork field          | Bitwarden destination                |
|------------------------|--------------------------------------|
| `fields.name`          | item `name`                          |
| `fields.login`         | `login.username`                     |
| `fields.password`      | `login.password`                     |
| `fields.url`           | `login.uris[].uri`                   |
| `fields.note`          | `notes`                              |
| `fields.custom[]`      | `notes` (appended as `key: value`)   |
| `tags[]`               | `notes` (appended as `tags: ...`)    |
| `vaultName` + `path[]` | folder name (`vault / a / b / c`)    |

Folder nesting is preserved: Bitwarden stores nested folders as a single flat name
separated by ` / `, and the converter reproduces exactly that.

## Usage

```bash
# JSON (recommended for Vaultwarden)
python3 convert.py Passwork_export.json vault-export.json

# CSV (alternative import format)
python3 convert_csv.py Passwork_export.json vault-export.csv
```

No arguments: defaults to `export.json` in the current directory and writes
`vault-export.json` / `vault-export.csv` next to it.

Then in your Vaultwarden web UI: **Settings -> Import -> Bitwarden (json)** -> select the
file. Folders, notes, custom fields and tags all come across.

## Testing

```bash
python3 run_tests.py   # runs both converters on sample/sample.json, verifies counts
```

`sample/sample.json` contains only fabricated entries and is safe to inspect.

## Notes

- Output item IDs are fresh UUID4s; folder IDs are deterministic per run within a file.
- Entries without a login/password (e.g. WireGuard configs stored as notes) are kept as
  type-1 login items with an empty login block - Vaultwarden renders them as logins with
  a notes body. If you prefer them as secure notes (type 2), that is a one-line change
  in `convert.py`.
- The sample export never contains real credentials. Do not commit your own `export.json`.

## License

MIT

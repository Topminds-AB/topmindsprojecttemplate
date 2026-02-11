# file_inventory.txt / file_inventory.csv Format (Mandatory)

The audit ZIP must include a flat inventory of all ZIP members with normalized paths and sizes.

## Location
- `manifest/file_inventory.txt` (preferred) or `manifest/file_inventory.csv`

## Path rules
- Paths must be normalized to `/` separators.
- No leading `/`.
- Preserve the path exactly as it appears in the ZIP after normalization.

## Recommended TXT format
One entry per line:

`<bytes>\t<normalized_path>`

Example:
`2048	code/services/app.py`

## Recommended CSV format
Header row required:

`bytes,path`

Example:
`2048,code/services/app.py`

## Notes
- Inventory must include **all** members (files and explicit directory entries if present).
- Do not include secret values; inventory lists paths and sizes only.

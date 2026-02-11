# Audit ZIP Naming + Prefix Requirements (Mandatory)

## ZIP filename format (strict)
`SYSTEMPREFIX_codebase_YYYY-MM-DD_HH-mm.zip`

- `SYSTEMPREFIX` is everything before `_codebase_`
- Prefix must match the expected project prefix for the audit cycle

## Manifest consistency
Inside the ZIP, `manifest/manifest.md` must declare the same system prefix.
- ZIP filename prefix and manifest-declared prefix must match exactly.

## Failure rule
If the ZIP prefix and manifest prefix do not match expected values:
- treat as CRITICAL
- regenerate ZIP via `create_codebase.bat` after fixing naming/manifest

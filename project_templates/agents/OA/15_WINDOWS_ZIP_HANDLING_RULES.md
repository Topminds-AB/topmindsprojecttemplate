# Windows 11 ZIP Handling Rules (Mandatory)

These rules apply when reading or validating ZIP snapshots created on Windows 11, especially when paths in logs or tooling use backslashes.

## Path normalization (always first)
- Normalize all paths immediately: replace `\` with `/`.
- Strip any leading `/`.
- Never do backslash lookups inside ZIP entries; ZIP member paths use `/`.

## ZIP member discovery (mandatory workflow)
- Always enumerate ZIP members first.
- Build a normalized index:
  - original member name
  - normalized name (slash-normalized)
  - casefolded variant
- Locate files by this order:
  1) exact match
  2) case-insensitive match
  3) suffix match (when only tail path is known)
- If not found, report closest matches (same suffix/nearby path).

## Directory handling
- Treat directories as prefixes; directory entries can be implicit.
- Never rely on directory entries existing to infer content presence.

## Prefer in-memory reads
- Prefer reading member contents directly from the ZIP.
- Extract only if strictly required for tooling execution.

## Extraction safety (Zip Slip prevention)
If extraction is required:
- Block `../` traversal.
- Block absolute paths.
- Block drive-letter paths (e.g., `C:`).
- Validate resolved extraction path stays inside the intended target directory.

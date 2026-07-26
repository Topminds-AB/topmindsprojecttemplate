---
name: wikijs-update-existing-page
description: Use when you need to find an existing Wiki.js page by path, then update or extend it with new text, new screenshots, new sections, or corrected documentation through Wiki.js APIs.
---

# Wiki.js Update Existing Page

Use this skill when the target already exists in Wiki.js and the task is to extend, correct, or append to it.

## When to use

Trigger this skill when the user asks to:
- update an existing wiki page
- append a new section to a documented flow
- add new screenshots to a documented feature
- correct text or add evidence to an existing runbook

## Required environment

Read these environment variables first:
- `WIKIJS_URL`
- `WIKIJS_API_TOKEN`
- `WIKIJS_DEFAULT_LOCALE`

## Workflow

1. Resolve the exact page path and locale.
2. Fetch the existing page using `singleByPath` or list-and-filter.
3. Preserve the useful existing content.
4. Integrate the new material into the correct section.
5. Upload any new screenshots one at a time.
6. Update the page by id using the page update mutation.
7. Verify the page after update.

## Rules for safe updates

- Do not erase unrelated sections.
- Keep the page title and path stable unless the task explicitly requires a rename.
- Preserve earlier evidence unless it is obsolete and the task explicitly replaces it.
- Prefer additive updates over destructive rewrites.

## Commands

### List pages

```bash
python3 .codex/skills/wikijs-update-existing-page/scripts/wikijs_publish.py list-pages --locale en
```

### Publish updated content

```bash
python3 .codex/skills/wikijs-update-existing-page/scripts/wikijs_publish.py publish-page \
  --title "DocPilot login and medication flow" \
  --description "Updated documentation for the login and medication administration flow." \
  --path "docpilot/flows/login-medication" \
  --content-file ./tmp/wiki-page-updated.md \
  --mode update \
  --tag docpilot \
  --tag flow \
  --tag updated
```

### Upload one screenshot

```bash
python3 .codex/skills/wikijs-update-existing-page/scripts/wikijs_publish.py ensure-folder-path \
  --path "systems/docpilot/screenshots"

python3 .codex/skills/wikijs-update-existing-page/scripts/wikijs_publish.py upload-asset \
  --file ./screenshots/medication-step-07.png \
  --asset-folder-path "systems/docpilot/screenshots"
```

## Additional resources

- GraphQL details: [references/graphql-workflow.md](references/graphql-workflow.md)
- Upload details: [references/upload-workflow.md](references/upload-workflow.md)
- Helper script: [scripts/wikijs_publish.py](scripts/wikijs_publish.py)

## Quality rules

- Fetch before updating.
- Update by page id, not by guesswork.
- Re-read the page after update when correctness matters.
- Never claim success without a successful API response.


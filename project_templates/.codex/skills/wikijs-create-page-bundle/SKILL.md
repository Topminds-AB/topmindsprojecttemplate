---
name: wikijs-create-page-bundle
description: Use when you need to create a new Wiki.js documentation page from repo material, meeting notes, screenshots, or generated text, then upload screenshots and publish the finished page through Wiki.js APIs.
---

# Wiki.js Create Page Bundle

Use this skill when the task is to publish a **new** documentation page into Wiki.js, including screenshots and structured text.

## When to use

Trigger this skill when the user asks to:
- create a new wiki page in Wiki.js
- publish documentation generated from a repo or automation run
- upload screenshots and place them into a new documentation page
- create a first version of system documentation for a flow, feature, screen, runbook, or report

## Required environment

Read these environment variables before doing any API work:
- `WIKIJS_URL`
- `WIKIJS_API_TOKEN`
- `WIKIJS_DEFAULT_LOCALE`
- `WIKIJS_DEFAULT_EDITOR`
- `WIKIJS_SYSTEM_SLUG`

If any required value is missing, stop and report exactly what is missing.
Do not invent secrets or URLs.

## Workflow

1. Determine the final target page path.
   - Use a stable, deterministic path.
   - Prefer a path rooted under the system slug.
   - Normalize the path so it is relative inside Wiki.js.

2. Prepare the content locally.
   - Build the page in markdown unless the repo explicitly requires HTML.
   - Include title, short description, structured sections, and any screenshot references.
   - Keep image references deterministic.

3. If screenshots are included:
   - Create or locate the correct asset folder.
   - Upload screenshots **one file at a time**.
   - Confirm each upload succeeded before moving on.
   - Use the final asset path in the page body.

4. Create the page.
   - Use the GraphQL page create mutation from `references/graphql-workflow.md`.
   - Include editor, locale, title, description, path, tags, and body content.

5. Verify the result.
   - Re-read or list pages to confirm the page exists.
   - Report the final page path.

## Commands

### Create or update content using the helper

```bash
python3 .codex/skills/wikijs-create-page-bundle/scripts/wikijs_publish.py publish-page \
  --title "DocPilot login and medication flow" \
  --description "Generated documentation for the login and medication administration flow." \
  --path "docpilot/flows/login-medication" \
  --content-file ./tmp/wiki-page.md \
  --mode create \
  --tag docpilot \
  --tag flow
```

### Upload one screenshot

```bash
python3 .codex/skills/wikijs-create-page-bundle/scripts/wikijs_publish.py ensure-folder-path \
  --path "systems/docpilot/screenshots"

python3 .codex/skills/wikijs-create-page-bundle/scripts/wikijs_publish.py upload-asset \
  --file ./screenshots/login-step-01.png \
  --asset-folder-path "systems/docpilot/screenshots"
```

### List folders

```bash
python3 .codex/skills/wikijs-create-page-bundle/scripts/wikijs_publish.py list-folders --parent-folder-id 0
```

## Additional resources

- GraphQL details: [references/graphql-workflow.md](references/graphql-workflow.md)
- Upload details: [references/upload-workflow.md](references/upload-workflow.md)
- Helper script: [scripts/wikijs_publish.py](scripts/wikijs_publish.py)

## Quality rules

- Do not overwrite an existing page unless the task explicitly allows it.
- Prefer deterministic paths and tags.
- Upload screenshots one by one.
- Never hardcode credentials.
- If the wiki rejects API-key auth, stop and report that the integration path needs the authenticated fallback documented in the repo.


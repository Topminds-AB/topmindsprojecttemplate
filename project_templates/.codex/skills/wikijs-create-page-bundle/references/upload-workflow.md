# Wiki.js upload workflow reference

## Important behavior

Wiki.js page operations are GraphQL-based, but file uploads are handled separately through `POST /u`.

A single request uploads **one file only**.

## Request format

Upload requests must use multipart form data with:
- file field: `mediaUpload`
- metadata field: `mediaUpload` containing JSON with `folderId`

This awkward naming is intentional and mirrors the Wiki.js upload controller.

## Practical upload example

Using curl:

```bash
curl \
  -X POST "${WIKIJS_URL}/u" \
  -H "Authorization: Bearer ${WIKIJS_API_TOKEN}" \
  -F 'mediaUpload={"folderId": 12};type=application/json' \
  -F "mediaUpload=@./screenshots/login.png"
```

Successful uploads return the literal response body `ok`. This Wiki.js endpoint does not return an asset JSON payload or the final URL.

## Filename behavior

Wiki.js sanitizes filenames to lowercase and replaces spaces or some punctuation with underscores.
Do not rely on the original client filename surviving unchanged.

## Recommended asset naming

Use deterministic, collision-safe names such as:
- `docpilot-login-01.png`
- `docpilot-medication-step-03.png`
- `clippilot-flow-summary-2026-04-18.png`

## Recommended post-upload step

After uploading a file, calculate the final path using the folder hierarchy and deterministic filename, then verify it with an HTTP `HEAD` request.
Then insert the image into page content using markdown or HTML suitable for the page editor.

Example Markdown:

```markdown
![ClipPilot screenshot](/systems/clippilot/screenshots/clippilot-flow-summary-2026-04-18.png)
```


# FIGMA Static Import & Deployment Guide (English)
> **Goal:** Create an **exact** static replica of a Figma Make export first, then connect logic **progressively** without ever disturbing the frozen design.

This guide describes how to migrate a Figma Make export (example: `DocPilotDesktop`) into a static demo that can be hosted on Loopia—and then how to publish it on **prohat.mono.se** as part of a demo portal for clickable product designs.

---

## Core philosophy (must-follow)
1. **Design first, always.** The initial milestone is a pixel-faithful static build (HTML/CSS/JS output).
2. **Freeze the UI before adding logic.** Treat the exported UI as **read-only** once it matches Figma.
3. **Progressive enhancement only.** Add behavior in thin layers that attach to existing elements without changing layout.
4. **No accidental overwrites.** Deploy in a **targeted** way so you never replace other demos by mistake.
5. **No secrets in repo or docs.** Never paste `.env` contents into issues, docs, or chat.

---

## Project conventions (recommended)
- **Source (Figma export, Vite + React):**
  - `original_sites/<ExportName>/`
  - Example: `original_sites/DocPilotDesktop/`
- **Static output (deploy target inside the portal site):**
  - `site/presentations/<slug>/`
  - Example: `site/presentations/docpilot-desktop/`
- **Thumbnail images (used by the portal dashboard):**
  - `site/thumbnails/<slug>.png`
  - Example: `site/thumbnails/docpilot-desktop.png`

> Keep slugs stable. URLs and DB references should not change once published.

---

# Chapter 1 — Installation & verification in a development environment

## 1.1 Prerequisites
- Windows + PowerShell
- Node.js + npm installed
- PHP installed (for local serving of `site/` if you use PHP locally)
- WinSCP installed (for later FTP deploy)
  - Example path: `C:\Program Files (x86)\WinSCP\WinSCP.com`
- FTP credentials stored in `site/.env` (secret, not committed)
  - `FTP_USER=...`
  - `FTP_PASSWORD=...`

## 1.2 Place the exported source code
Put the Figma Make export in:
- `original_sites/<ExportName>/`  
Example:
- `original_sites/DocPilotDesktop/`

## 1.3 Make the export buildable (common fixes)
### A) Missing font CSS
If the export references a missing file (e.g. `src/styles/fonts.css`), create it so the build does not fail.
- Keep it minimal: define a basic font stack and do not alter layout.

### B) Replace `figma:asset/...` imports with local assets
Figma Make exports may include imports like `figma:asset/...` which do not work in normal Vite builds.

**Fix procedure:**
1. Export/download the asset from Figma (via Figma tooling or manual export).
2. Place it under:
   - `original_sites/<ExportName>/src/assets/`
3. Update components to import the local asset file instead of `figma:asset/...`.

Example files commonly affected:
- `original_sites/DocPilotDesktop/src/app/App.tsx`
- `original_sites/DocPilotDesktop/src/app/DesktopApp.tsx`
- `original_sites/DocPilotDesktop/src/assets/prohat-logo.png`

### C) Ensure favicon is self-contained
Make favicon reference a local file so static hosting does not rely on external paths:
- `original_sites/<ExportName>/index.html` → `href="./favicon.svg"`
- `original_sites/<ExportName>/public/favicon.svg` (create/copy as needed)

## 1.4 Configure Vite for subfolder hosting
Loopia shared hosting typically serves your demo from a subfolder (not `/`).

In `original_sites/<ExportName>/vite.config.ts` set:
- `base: './'`

**Required verification:**
- After build, `dist/index.html` must reference `./assets/...` (not `/assets/...`).

## 1.5 Build the static output
Example commands (adjust paths to your repo root):

```powershell
cd E:\projects\demo.prohat.se\original_sites\DocPilotDesktop
npm install
npm run build
```

## 1.6 Publish build output into the portal’s static folder
Copy `dist/` to the portal’s presentations folder:

```powershell
cd E:\projects\demo.prohat.se
New-Item -ItemType Directory -Force site\presentations\docpilot-desktop | Out-Null
Copy-Item original_sites\DocPilotDesktop\dist\* site\presentations\docpilot-desktop\ -Recurse -Force
```

## 1.7 Local UI smoke test (no backend logic)
Serve `site/` using a simple local server (any method works). If you use PHP locally:

- Verify page loads at:
  - `http://127.0.0.1:<port>/presentations/docpilot-desktop/`
- Confirm:
  - No 404s for JS/CSS/assets
  - Navigation renders
  - Layout matches the export

**Evidence requirement (highly recommended):**
- Take screenshots:
  - Desktop (e.g. 1440×900)
  - Mobile (e.g. 390×844)
- Store in:
  - `docs/reports/<slug>/`

## 1.8 Lock the design before adding logic
Once the UI matches Figma:
- Treat the design as **frozen**.
- Any future change must pass a visual diff/screenshot comparison.

**Progressive logic rule-set:**
- Add behavior only through:
  - Event listeners bound to existing elements
  - Data attributes (e.g. `data-action`, `data-id`) added carefully
  - Small controller modules that do **not** change layout
- Never “refactor” UI layout while adding logic.
- One behavior change at a time, with a before/after screenshot pair.

---

# Chapter 2 — Installation & deployment on Loopia (shared hosting)

## 2.1 Required constraints for Loopia
- Your demo will be hosted under a subfolder such as:
  - `/public_html/presentations/<slug>/`
- Therefore:
  - Vite `base` must be `./`
  - All asset paths must be relative

## 2.2 Targeted deploy only (never overwrite other demos)
Deploy only:
- `site/presentations/<slug>/` → `/public_html/presentations/<slug>/`
- `site/thumbnails/<slug>.png` → `/public_html/thumbnails/<slug>.png`

Use a dedicated deploy script per demo (recommended), e.g.:
- `deploy_loopia_<slug>.bat`

**Run example:**
```powershell
cd E:\projects\demo.prohat.se
cmd /c deploy_loopia_docpilot_desktop.bat
```

**Safety properties the deploy script must have:**
- No blanket sync of `/public_html/`
- No remote delete of unrelated folders
- Only uploads the demo folder + thumbnail(s)

## 2.3 Remote verification
After deploy, verify:
- Demo URL:
  - `https://<domain>/presentations/<slug>/`
- Thumbnail URL:
  - `https://<domain>/thumbnails/<slug>.png`

Confirm:
- No missing CSS/JS
- No missing assets
- No layout shifts compared to Chapter 1 evidence

## 2.4 Replacing a “bad” demo safely (optional)
If the portal lists demos from a database table (example: `presentations`):
- Never hard-delete old rows unless you have a formal rollback plan.
- Prefer:
  - `is_active=0` for old demo entries
  - Create a new entry pointing to the new static path

If you use an idempotent seed script (recommended), keep it in migrations:
- Example:
  - `database/migrations/006_seed_prohat_desktop.php`

Run locally:
```powershell
cd E:\projects\demo.prohat.se
php database\migrations\006_seed_prohat_desktop.php
```

## 2.5 Removing old remote files (only if you must)
If you want to remove an old folder on Loopia, do it with a **targeted** script:
- Example:
  - `deploy_loopia_remove_old_<old-slug>.bat`

It must:
- Only touch the intended old folder
- Never delete `/public_html/presentations/<new-slug>/`

## 2.6 Updating the thumbnail to a specific image
If you have a “front image” in the export and want it as the portal thumbnail:
1. Copy it over the existing thumbnail file name that DB already points to:
   - From: `original_sites/<ExportName>/frontpic.png`
   - To: `site/thumbnails/<slug>.png`
2. Run the targeted deploy script (uploads both demo + thumbnail, or thumbnail only if supported).

Example:
```powershell
cd E:\projects\demo.prohat.se
Copy-Item original_sites\DocPilotDesktop\frontpic.png site\thumbnails\docpilot-desktop.png -Force
cmd /c deploy_loopia_docpilot_desktop.bat
```

## 2.7 Common pitfalls
- `vite.base` not set to `./` → CSS/JS breaks in subfolders.
- `figma:asset/...` still present → build fails or assets missing.
- Absolute favicon or asset paths → works locally but breaks on Loopia.
- Deploy script that syncs `/public_html/` with `-delete` → massive risk.
- Caching issues → hard refresh (`Ctrl+F5`) after updating assets/thumbnails.

---

# Chapter 3 — Installation on prohat.mono.se (clickable product design demo hub)

**Purpose:** Publish multiple clickable Figma-based demos under **one** coherent demo hub (prohat.mono.se), so stakeholders can click through product designs without backend dependencies.

## 3.1 Target structure on prohat.mono.se
Recommended URL structure:
- Demo hub (index page):
  - `https://prohat.mono.se/`
- Individual demos:
  - `https://prohat.mono.se/presentations/<slug>/`
- Thumbnails:
  - `https://prohat.mono.se/thumbnails/<slug>.png`

Recommended filesystem mapping on the host:
- `/public_html/presentations/<slug>/`
- `/public_html/thumbnails/<slug>.png`

## 3.2 Demo hub behavior (portal)
The hub page should:
- List all demos as cards
- Each card uses:
  - `title`
  - `description`
  - `thumbnail`
  - `url_path` (points to `presentations/<slug>/`)
- Support safe publish/rollback:
  - Deactivate old cards instead of deleting

**Data source options (choose one and keep it consistent):**
1. **Database-backed listing** (recommended if you already have a portal DB)
2. **Static JSON listing** stored under `site/` (if you want zero backend dependencies)

If database-backed, keep the same “safe replacement” strategy as Chapter 2:
- Deactivate old entry → create new entry → verify → only then remove old files (optional)

## 3.3 Publishing a new demo to prohat.mono.se (repeatable workflow)
For each new Figma export:

1. **Import source**
   - Put export in:
     - `original_sites/<ExportName>/`

2. **Fix build blockers**
   - Fonts CSS if missing
   - Replace `figma:asset/...`
   - Ensure local favicon

3. **Set Vite base**
   - `base: './'`

4. **Build**
   ```powershell
   cd <repo>\original_sites\<ExportName>
   npm install
   npm run build
   ```

5. **Copy dist → site presentations**
   ```powershell
   cd <repo>
   New-Item -ItemType Directory -Force site\presentations\<slug> | Out-Null
   Copy-Item original_sites\<ExportName>\dist\* site\presentations\<slug>\ -Recurse -Force
   ```

6. **Create/update thumbnail**
   - Copy chosen image to:
     - `site/thumbnails/<slug>.png`

7. **Register demo in the hub**
   - If DB-backed:
     - Run an idempotent migration/seed that creates/updates the presentation entry.
   - If JSON-backed:
     - Add/update an entry in the demo index JSON file.

8. **Targeted deploy**
   - Upload only:
     - `site/presentations/<slug>/`
     - `site/thumbnails/<slug>.png`
     - (and hub index assets if required)

9. **Remote verification**
   - Open:
     - `https://prohat.mono.se/presentations/<slug>/`
   - Validate:
     - No 404s
     - Correct layout
     - Thumbnail loads
     - Hub card points to correct URL

## 3.4 Strict “design freeze” policy for prohat.mono.se
Because this is a showcase site, every demo must remain pixel-stable over time.

Required controls:
- **Evidence per release:** screenshots (desktop + mobile)
- **No layout refactors:** logic changes must not alter layout
- **Change isolation:** attach behavior via small JS modules and data attributes
- **Rollback readiness:** keep previous static build artifacts (or tags) so you can redeploy quickly

## 3.5 Progressive enhancement plan (controlled logic integration)
When you start adding logic to a static demo:
1. **Phase A — static only**
   - No data fetching, no state, no mutations

2. **Phase B — read-only dynamic**
   - Render dynamic data into existing placeholders without changing layout
   - No navigation changes
   - No resizing or reflow changes

3. **Phase C — interactive**
   - Add controlled interactions (filters, selections, modals)
   - Ensure interactions do not change spacing/typography/layout

4. **Phase D — real backend**
   - Replace mocked data carefully
   - Maintain CSS/DOM structure stable

**Rule:** If a logic change requires a design change, it must be treated as a separate design iteration and re-approved as a design change first.

## 3.6 prohat.mono.se “do not break production” checklist
Before each deploy:
- [ ] `vite.base` is `./`
- [ ] No `figma:asset/...` remains
- [ ] `dist/index.html` references `./assets/...`
- [ ] Demo is copied to the correct `site/presentations/<slug>/`
- [ ] Thumbnail exists as `site/thumbnails/<slug>.png`
- [ ] Deploy script uploads only the intended targets
- [ ] Remote URL loads with zero 404s
- [ ] Screenshot comparison shows no unintended differences

---

## Quick copy/paste checklist (generic)
1) Build:
```powershell
cd <repo>\original_sites\<ExportName>
npm run build
```

2) Publish into `site/`:
```powershell
cd <repo>
New-Item -ItemType Directory -Force site\presentations\<slug> | Out-Null
Copy-Item original_sites\<ExportName>\dist\* site\presentations\<slug>\ -Recurse -Force
```

3) Deploy (targeted):
```powershell
cd <repo>
cmd /c deploy_loopia_<slug>.bat
```

4) Register/seed (if DB-backed):
```powershell
cd <repo>
php database\migrations\<seed-file>.php
```

---

## Appendix — What “exact copy” means (practical definition)
A demo is considered an exact replica when:
- Typography, spacing, alignment, and layout match Figma at the intended breakpoints
- No missing icons/images
- No console errors that indicate missing assets
- Navigation elements behave as per the static design (even if not wired to real data yet)

Once this is achieved, the UI is **frozen** and logic is added only via progressive enhancement.

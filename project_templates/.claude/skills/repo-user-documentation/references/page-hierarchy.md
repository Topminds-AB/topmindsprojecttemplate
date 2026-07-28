# Page hierarchy — the standard wiki tree

Every system gets the same four-level landing structure, so users moving between systems find things in the same place. Sections only materialise if the underlying content exists — don't publish an empty "Integrations" page.

## The four landing levels

```
root/                                     ← L0: wiki root (one page total)
└── {system-slug}/                        ← L1: system hub (one per system)
    └── anvandardokumentation/            ← L2: section landing + locale redirect
        └── {locale}/                     ← L3: locale landing (what the user reads)
            ├── komma-igang/
            ├── funktioner/
            └── ...
```

Each level has a distinct role:

| Level | Role                                      | Template                | Who publishes it                                   |
|-------|-------------------------------------------|-------------------------|----------------------------------------------------|
| L0    | Wiki entrypoint — index of all systems    | (none — hand-curated)   | Root-level concern, updated additively             |
| L1    | System hub — system name + two entry links | `system-hub.md`         | `repo-user-documentation` skill, once per system   |
| L2    | Redirect page — `?lang=X` → L3            | `section-landing.md`    | `repo-user-documentation` skill, once per system   |
| L3    | Locale landing — the reader's actual start | `landing.md`            | `repo-user-documentation` skill, once per locale   |

## Standard tree under L3

```
{system-slug}/anvandardokumentation/{locale}/
├── (L3 landing page)
├── komma-igang/
│   ├── forutsattningar
│   ├── forsta-inloggning
│   └── oversikt
├── funktioner/
│   └── <one page per feature>
├── floden/
│   └── <one page per flow>
├── roller/
│   └── <one page per role>
├── aviseringar-och-email
├── integrationer
├── tangentbord-och-tillganglighet
├── dataskydd
├── felsokning
├── ordlista
├── faq
└── kontakt
```

## Full path convention

```
{system-slug}/anvandardokumentation/{locale}/{section}/{page-slug}
```

The system slug is visible on L1 as the page **title**, not repeated in deeper URL segments. Users who deep-link from the source application never see other systems in the sidebar (see "Scoped navigation" below).

Example full paths:

- L1 hub:        `styrgruppskort/`
- L2 section:    `styrgruppskort/anvandardokumentation/`
- L3 landing:    `styrgruppskort/anvandardokumentation/sv/`
- Feature page:  `styrgruppskort/anvandardokumentation/sv/funktioner/rapporter`

Reserved path `teknisk-dokumentation/` is **not** owned by this skill. Another skill publishes there.

## Scoped navigation (one navigation tree per system)

To ensure users coming in from one system never see other systems in the sidebar, every system uses a **Custom Navigation** in Wiki.js admin, scoped to that system only.

1. Wiki.js admin → *Navigation* → create a new tree named `{system-slug}-user-docs`.
2. Populate with links under `{system-slug}/anvandardokumentation/`.
3. Wiki.js admin → *Pages* → select `{system-slug}/` (L1) → *Page Actions* → *Navigation* → set to the custom tree.
4. Children inherit the setting — verify by opening a leaf page.

This is a one-time step per new system, done manually after the first publication. The skill's SKILL.md lists this as part of the onboarding checklist.

## Cross-system linking from source applications

External systems (DocPilot, Styrgruppskort UI, etc.) link directly into the documentation in one of two ways:

**Preferred — deep link with explicit locale:**
```
https://wiki.topminds.se/sv/{system-slug}/anvandardokumentation/{locale}/
```

Zero logic in the wiki. Use this when the source system already knows the user's language.

**Fallback — `?lang=` query param on L2:**
```
https://wiki.topminds.se/sv/{system-slug}/anvandardokumentation/?lang=fi
```

L2 is a redirect page that reads `?lang=` and forwards to the matching L3 locale landing. Unknown or missing values fall back to the default locale. See `templates/section-landing.md` for the exact script.

Requires *Allow HTML in Markdown content* in Wiki.js admin → Rendering (default on).

## Mapping inventory → pages

| Inventory source        | Becomes                                             |
|-------------------------|-----------------------------------------------------|
| `features[]`            | One page under `funktioner/` per feature            |
| `flows[]`               | One page under `floden/` per flow                   |
| `roles[]`               | One page under `roller/` per role                   |
| `notifications[]`       | Sections on `aviseringar-och-email`                 |
| `integrations[]`        | Sections on `integrationer`                         |
| Inferred terminology    | Entries on `ordlista`                               |
| Common user questions   | Entries on `faq`                                    |
| User-visible errors     | Entries on `felsokning`                             |

## Plan JSON shape

The planning phase writes `./tmp/docs-build/plan.json`:

```json
{
  "system": {"slug": "styrgruppskort", "name": "Styrgruppskort",
             "description": "Standardiserade projektstatuskort för styrgrupper."},
  "locales": ["sv", "en"],
  "default_locale": "sv",
  "pages": [
    {
      "id": "l1-hub",
      "type": "system-hub",
      "wiki_path": "styrgruppskort",
      "title": "Styrgruppskort"
    },
    {
      "id": "l2-section",
      "type": "section-landing",
      "wiki_path": "styrgruppskort/anvandardokumentation",
      "title": "Användardokumentation för Styrgruppskort"
    },
    {
      "id": "l3-sv",
      "type": "locale-landing",
      "wiki_path": "styrgruppskort/anvandardokumentation/sv",
      "title": "Styrgruppskort — användarguide",
      "locale": "sv"
    },
    {
      "id": "feat-reports-sv",
      "type": "feature",
      "wiki_path": "styrgruppskort/anvandardokumentation/sv/funktioner/rapporter",
      "title": "Rapporter",
      "locale": "sv",
      "screenshots": ["reports--list", "reports--detail"]
    }
  ],
  "screens": [
    {"id": "reports--list", "section": "funktioner", "slug": "reports-list",
     "state": "default", "path": "/reports",
     "wait_selector": "[data-testid='reports-table']"}
  ]
}
```

The `screens[]` array is what `capture.py run` consumes. The `pages[]` array drives authoring and publishing.

## Rules for paths

- **Lowercase, hyphens, no diacritics** in URL segments. Swedish åäö map to `a`, `a`, `o`. The page **title** keeps diacritics; only the path is stripped.
- **Stable across runs.** The same feature always lives at the same path. Renames need an explicit migration.
- **One page per concept.** If a feature grows, split into a parent + children; don't overload one page.
- **L1 hub path is the system slug itself** — no `/index`, no `/home`.
- `anvandardokumentation` is a fixed segment name, never translated, never shortened.

## Cross-page links (critical)

**Always use absolute wiki paths for links between pages.** Never use relative paths like `./funktioner/rapporter` or `funktioner/rapporter`. Wiki.js page URLs do not have trailing slashes, so browser-relative resolution points one level too high and links break.

**Correct link format:**

```markdown
[Rapporter](/{system-slug}/anvandardokumentation/{locale}/funktioner/rapporter)
[Vanliga frågor](/{system-slug}/anvandardokumentation/{locale}/faq)
```

**Incorrect formats that look right but break:**

```markdown
[Rapporter](funktioner/rapporter)        ← resolves wrong due to missing trailing slash
[Rapporter](./funktioner/rapporter)      ← same problem
[Rapporter](../faq)                      ← same problem
```

**Do NOT prefix links with the Wiki.js locale** (`/sv/...`, `/en/...`). Wiki.js automatically prefixes the configured display locale at render time. Markdown links should start with the system slug.

**Screenshot and asset links are unaffected** — they already use absolute asset URLs (`/u/...`) and don't need changes.

This rule applies to:
- All links in `templates/*.md`
- All links generated in the authoring phase
- "Se även" sections on every page
- Section index pages that list children

Enforcement: see the post-processing step in `authoring-style.md` which rewrites any remaining relative links before publication.

## Publication ordering (strict — avoids broken links)

Within a system, publish **bottom-up**:

1. All leaf pages (funktioner, floden, roller, faq, ordlista, ...)
2. All section index pages within the locale, if any
3. L3 locale landing — one per locale
4. L2 section landing (with the `?lang=` redirect script)
5. L1 system hub
6. L0 wiki root — updated additively to add a row for the new system (via `wikijs-update-existing-page`)

Never publish a landing before its children exist. The skill's Workflow step 6 enforces this by sorting the `pages[]` array before dispatching to the publishing skills.

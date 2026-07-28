# i18n strategy — documenting multiple languages

The rule is simple: **one screenshot set per supported language, one markdown page per language, same wiki structure in every language.**

## Locale list

Locales come from three places, in order of priority:
1. `APP_SUPPORTED_LOCALES` in `.env` — authoritative.
2. `docs-config.yaml` in the repo, if present, under `locales:`.
3. The scanner's detection from i18n files — used only if the first two are missing.

If sources disagree, stop and report. Do not guess.

## Wiki path shape

Every page includes the locale as its second path segment:

```
<system-slug>/<locale>/<section>/<page-slug>
```

This matches Wiki.js convention and makes the language switcher work without extra configuration. Do **not** use the wiki's built-in locale feature — it ties content to a locale at the page level, which fights our hierarchy. Treat language as part of the path.

## Capture order

Capture one locale at a time, top to bottom of the plan, before moving to the next locale. Reasons:
- The session is fresh per locale — no lingering state.
- If a run fails mid-locale, you know exactly which locale to re-run.
- The manifest per locale is self-contained: `./tmp/docs-build/screenshots/<locale>/_manifest.json`.

## Structural parity

Every locale has the same page list. If a feature only ships in Swedish, the English page still exists — with a single sentence explaining the feature is only available in Swedish, and a link to the Swedish page. This preserves the sidebar parity across languages and prevents dead links.

## Translation of page text

Page markdown is authored per locale. The authoring phase generates each language independently from the same inventory — it does not translate from one language to another. This avoids translation drift: a change in the source inventory propagates to every language at once.

Exception: the glossary and FAQ are generated first in the default locale, then parallel versions are produced in the other locales with term alignment preserved.

## Terminology file (optional)

If the repo has `docs/terminology.<locale>.yaml`, the authoring phase uses it to translate UI labels consistently. Shape:

```yaml
# docs/terminology.en.yaml
Spara: Save
Skapa: Create
Rapporter: Reports
```

Without this file, labels are translated contextually; with it, consistency is guaranteed.

## What not to translate

- URL segments in the wiki path (they stay in Swedish by default per the page hierarchy convention).
- Proper nouns (system name, integration names like BankID, SITHS).
- Screenshot file paths — the screenshot file lives under its locale folder, never renamed.

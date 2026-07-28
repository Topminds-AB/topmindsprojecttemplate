# Authoring style — voice, tone, structure

The documentation is written for the **person using the system**, not for the person maintaining it. Technical details are out of scope. If a sentence requires the reader to know what an API, a container, or a database is, it does not belong here.

## Default audience

Intern handläggare i kommunal eller regional verksamhet. They are comfortable with a computer but have never read the repo, have never set up the system, and do not care how it works under the hood. They want to get a task done and move on.

Override via `docs/audience.md` in the repo if a system has a different primary audience (citizen-facing, external vendor, clinical staff, etc.).

## Voice

- **Du-tilltal.** Always "du", never "ni", "man", or "användaren".
- **Active voice.** "Klicka på Skapa" — not "En skapa-knapp är tillgänglig".
- **Short sentences.** One instruction per sentence. Split long sentences into steps.
- **Concrete nouns.** "knappen **Spara**" — not "save-funktionen".
- **No jargon without explanation.** If a term appears, either explain it inline the first time, or link to `ordlista`.
- **No apologies, no hedging.** Don't write "tyvärr", "dessvärre", "på grund av tekniska begränsningar". If something doesn't work, state what does.
- **No version numbers or dates in prose.** Versions change; docs should stay stable. Keep release info on a separate "Vad är nytt" page.

## Sentence patterns that work

- "För att X, gör så här:" → followed by numbered list
- "**Klicka på Y** för att Z." → bolded UI element
- "När du har gjort X visas Y." → describes what happens, not what the system does
- "Om X inte syns, kontrollera Z." → troubleshooting inline

## Sentence patterns to avoid

- "Systemet gör X" → inanimate subject. Write "X händer när du..." or "Du ser X".
- "Vänligen klicka..." → drop "vänligen". Keep it direct.
- "Som du säkert vet..." → never assume. Explain.
- "Enkelt!" / "Det är enkelt att..." → let the reader decide.

## Page structure (applies to every page type)

1. **Title** — the name of the feature, flow, or topic. Matches the wiki link that points here.
2. **Lead paragraph** — one or two sentences answering "what is this and when do I need it?"
3. **Body** — the actual content, structured per page type (see templates).
4. **Se även** — cross-links to related pages. Always end with this.

## Cross-page links — always absolute

Every link between pages must be an absolute wiki path starting with `/`. Wiki.js auto-prefixes the display locale, so the link target begins with the system slug:

```markdown
[Rapporter](/{system-slug}/anvandardokumentation/{locale}/funktioner/rapporter)
```

Never use `./x`, `../x`, or `x/y` — they break because Wiki.js page URLs lack trailing slashes. See `references/page-hierarchy.md` for the full rule.

The authoring phase MUST run the link-resolution post-processing step (`scripts/resolve_links.py`) on the generated markdown before publication. It rewrites any remaining relative links to absolute ones based on each page's own wiki path.

## Screenshot placement

- Every screenshot has a caption. Caption tells the reader what to notice — not what the screenshot is of.
- Bad: "*Skärmdump av rapportsidan.*"
- Good: "*Listan med rapporter. Klicka på en rad för att öppna rapporten.*"
- One primary interaction per screenshot. If a screen has many things to explain, split into several screenshots.
- Annotations (pil, box, numrerade märken) reinforce the caption — they never replace it.

## Per-page-type structure

**Landing page (L3)** — Short welcome, then sections where each linkable item is a `###` heading followed by a one-sentence blurb. Never use bulleted lists for feature/flow/role links on landing pages — the Wiki.js Table of Contents only picks up heading tags, and bullet lists become invisible in navigation. See `templates/landing.md` for the exact structure.

**Section index pages** — Same rule as L3 landings: every child page is a `###` heading with a short description. No bullet lists for navigation.

**Feature page** — What it does, when to use it, how to use it (numbered steps with screenshots), begränsningar, vanliga frågor om just den funktionen.

**Flow page** — The journey from start to finish. One screenshot per step. Each step has a title, an instruction, and a note about what changes on screen.

**Role page** — What this role sees that others do not. Link to the features they can use. Do not list permissions as a technical list — describe them as "Du kan..." / "Du kan inte...".

**FAQ page** — Q + short A. Group by theme. Link to deeper pages when the answer is longer than three sentences.

**Glossary** — Term + two-sentence explanation. Alphabetical. Swedish terms first, original English in parentheses if relevant.

**Troubleshooting** — Symptom → cause → what to do. Phrased from the user's perspective: "Jag ser inte mina rapporter" — not "ReportService returns empty list".

**Getting started** — Minimal path to a first success. Everything else belongs elsewhere.

## Per-language consistency

Each language version has the same sections in the same order. If a section is empty in one language, write a single sentence pointing to a contact or fallback — do not silently omit sections, because the navigation sidebar compares across languages.

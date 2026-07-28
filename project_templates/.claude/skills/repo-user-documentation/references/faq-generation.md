# FAQ and glossary — how they are built

FAQ and glossary are the pages users actually search. They are generated last, after every feature and flow page exists, so links resolve.

## FAQ sources, in order

1. **`docs/faq.md` in the repo**, if present. Authored questions always take priority. Shape is free-form markdown; the authoring phase reads question headings (lines starting with `##` or `###`) and their answers.
2. **AI-synthesised questions** derived from the inventory. Generated questions fill gaps left by the repo file.

When a generated question overlaps an authored one, the authored version wins. Never merge answers — the authored one is used as-is.

## Question taxonomy

Every FAQ entry falls into one of these categories. Use them as section headings on the FAQ page, in this order:

1. **Komma igång** — first-time users: how to log in, what to do after the first login
2. **Grundläggande användning** — common tasks users perform every day
3. **Roller och behörigheter** — what can I do / what can my colleague do
4. **Fel och problem** — troubleshooting questions that cross features
5. **Data och sekretess** — what is stored, who can see it, export and deletion
6. **Integrationer** — BankID, SITHS, e-post, export to Excel
7. **Tillgänglighet** — keyboard, screen readers, mobile

Skip a section if it has no entries — never write empty headings.

## Question quality rules

- **Phrased as the user would ask it.** "Hur loggar jag in?" — not "Inloggning".
- **Duzing** (du-form), consistent with the rest of the documentation.
- **Short answer, deep link.** If the answer is longer than three sentences, write two sentences and link to the feature or flow page that explains it in full.
- **One question per entry.** If two questions share an answer, write both and point the second to the first.
- **No questions about things the user cannot do** — if the system doesn't support export to PDF, don't add "Kan jag exportera till PDF?". Questions describe present capabilities.

## Candidate questions to synthesise per inventory item

| Inventory source | Generated question(s)                                                              |
|------------------|------------------------------------------------------------------------------------|
| Feature          | "Hur skapar jag en X?", "Var hittar jag mina X?", "Kan jag redigera en X efteråt?" |
| Flow             | "Hur gör jag Y från början till slut?"                                             |
| Role             | "Vad kan en Z göra?", "Hur byter jag till Z-vy?"                                   |
| Notification     | "Varför fick jag ett mail om X?"                                                   |
| Integration      | "Hur loggar jag in med BankID?", "Hur exporterar jag till Excel?"                  |
| Error state      | "Varför ser jag meddelandet 'X'?"                                                  |

Before synthesising, check the inventory's `features[].purpose`, `flows[].label`, and `notifications[].trigger` — those fields are where the real user value lives.

## Glossary generation

The glossary contains every term the system itself introduces. Candidates:

- Domain-specific nouns that appear in the UI (e.g. "Styrgruppskort", "ESS-kod", "Läkemedelsadministration")
- Role names from `roles[]`
- Integration names from `integrations[]`
- Any term a colleague would have to explain on their first day

Excluded: generic UI words ("knapp", "meny", "fält"), technical infrastructure terms.

## Glossary entry shape

```markdown
### Styrgruppskort
Ett standardiserat statuskort som visar ett projekts status, risker och
milstolpar. Används av styrgruppen för att få överblick inför beslut.
```

- Term as `###` heading.
- Two sentences: what it is, when you see it.
- Alphabetical order. Swedish characters å, ä, ö sort last, in that order.
- When a term has an English original (e.g. "Dashboard"), put the Swedish form as the heading and include the English in the body if relevant.

## Cross-language behaviour

Glossary and FAQ are generated in the default locale first. Other locales are produced as parallel files with the same entry count and the same order, so that readers switching languages land on the equivalent entry at the same scroll position.

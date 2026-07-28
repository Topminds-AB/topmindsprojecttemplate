# Annotation — highlighting interactions on screenshots

Annotations turn a screenshot from "here's a screen" into "here's what you do on this screen". They are applied by `scripts/annotate.py` using a spec file.

## Rule of thumb

**One primary interaction per screenshot.** If a screen has five things worth pointing out, it should be five screenshots with one annotation each — not one screenshot covered in arrows.

Exception: numbered sequences on a single screen, where the user's eye follows `1 → 2 → 3` within one frame (e.g. a form where you fill three fields in order). Keep the sequence short, three numbers maximum.

## Visual language

- **Box** — "look at this area". Used when the area itself matters (a panel, a section).
- **Arrow** — "click this specific element". Arrow starts on empty space and points at the target.
- **Number** — "step N in a sequence". A numbered circle. Use with a matching numbered list in the caption.
- **Text** — a short label near the target. Use sparingly; the markdown caption is usually better.

## Colour

Default is ITC-teal `#0F766E`. Override per item with `color` only when the default fails contrast on a specific background (e.g. a dark UI). Pick from a small palette — ITC-teal, white, a single warning red (`#B91C1C`) — never invent one.

## Spec file

The annotation spec is a single JSON file covering all screenshots. Typical location: `./tmp/docs-build/annotations.json`.

```json
{
  "annotations": [
    {
      "image": "sv/funktioner/reports-list--default.png",
      "items": [
        {"type": "arrow", "from": [900, 200], "to": [780, 180]},
        {"type": "text",  "x": 910, "y": 190, "text": "Skapa ny rapport"}
      ]
    },
    {
      "image": "sv/floden/create-report--form.png",
      "items": [
        {"type": "number", "x": 180, "y": 220, "n": 1},
        {"type": "number", "x": 180, "y": 310, "n": 2},
        {"type": "number", "x": 180, "y": 400, "n": 3}
      ]
    }
  ]
}
```

Coordinates are in pixels from the top-left of the screenshot. `full_page` screenshots can be very tall — use a screenshot viewer that shows coordinates, or pre-compute offsets from selectors captured during the Playwright run.

## Invocation

```bash
python .agents/skills/repo-user-documentation/scripts/annotate.py apply \
  --spec ./tmp/docs-build/annotations.json \
  --input-dir ./tmp/docs-build/screenshots \
  --output-dir ./tmp/docs-build/screenshots-annotated
```

Annotated images keep the same relative path under the output directory, so the authoring phase can swap the image directory without touching any markdown.

## When to skip annotation

- Landing page hero screenshot — show the app, don't point at anything.
- Glossary / FAQ pages — no screenshots at all.
- Error states where the error message itself is the story — the text on screen carries the meaning.

Disable annotation for an entire run with `--no-annotate` at the skill level. Individual screenshots can be excluded by omitting them from the spec.

## Determinism

Annotation coordinates are part of the documentation artifact. Commit the annotation spec alongside the wiki output (or at least keep it in the repo under `docs/annotations.json`), so a re-run produces byte-identical annotated images. If a UI change moves a target, update the spec — don't re-eyeball it every run.

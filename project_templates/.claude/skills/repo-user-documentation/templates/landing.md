<!--
Template: landing (L3 — one per locale)
Path:     {system-slug}/anvandardokumentation/{locale}

Placeholders: {{system_name}}, {{system_description}}, {{locale}},
              {{getting_started_link}}, {{getting_started_blurb}},
              {{features_items}}, {{flows_items}}, {{roles_items}},
              {{faq_link}}, {{glossary_link}}, {{contact_link}}

LINK FORMAT: all *_link placeholders MUST be absolute wiki paths starting
with / and with the system slug, e.g.
  /{system-slug}/anvandardokumentation/{locale}/faq
Do NOT use relative paths. See references/page-hierarchy.md.

HEADING STRUCTURE (critical for TOC):
Every linkable item (feature, flow, role) MUST be rendered as a ### heading
whose text is a link, followed by a short paragraph. This is what populates
the Wiki.js Table of Contents with every sub-item. Do NOT render items as
bulleted lists — they would not appear in the TOC.

Correct format for {{features_items}}, {{flows_items}}, {{roles_items}}:
  ### [Feature Name](/{system-slug}/anvandardokumentation/{locale}/funktioner/slug)
  One-sentence description of what this feature does for the user.

  ### [Next Feature](...)
  Description...

Published LAST within the locale — after every linked page exists.
-->
# {{system_name}}

{{system_description}}

## Är du ny här?

Börja med **[Kom igång]({{getting_started_link}})**. {{getting_started_blurb}}

## Funktioner

{{features_items}}

## Flöden steg för steg

{{flows_items}}

## Roller

{{roles_items}}

## Snabba svar

### [Vanliga frågor]({{faq_link}})
Korta svar på det som oftast kommer upp.

### [Ordlista]({{glossary_link}})
Begrepp som används i systemet.

### [Kontakt och support]({{contact_link}})
När dokumentationen inte räcker.

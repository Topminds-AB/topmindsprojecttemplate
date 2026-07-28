<!--
Template: system-hub (L1)
Path:     {system-slug}/

Placeholders: {{system_name}}, {{system_description}},
              {{user_docs_link}}, {{tech_docs_link}},
              {{owner_team}}, {{contact_email}}

LINK FORMAT: {{user_docs_link}} and {{tech_docs_link}} MUST be absolute wiki
paths starting with / and with the system slug, e.g.
  {{user_docs_link}} = /{system-slug}/anvandardokumentation
  {{tech_docs_link}} = /{system-slug}/teknisk-dokumentation

Published SECOND-LAST, right before the wiki root update.
-->
# {{system_name}}

{{system_description}}

## Dokumentation

**[Användarguide]({{user_docs_link}})**
För dig som använder {{system_name}} i ditt arbete. Steg-för-steg-guider,
skärmdumpar, FAQ och felsökning.

**[Teknisk dokumentation]({{tech_docs_link}})**
För utvecklare och driftansvariga. Arkitektur, konfiguration, API:er, drift.

## Ägare och kontakt

{{owner_team}}

*Frågor: [{{contact_email}}](mailto:{{contact_email}})*

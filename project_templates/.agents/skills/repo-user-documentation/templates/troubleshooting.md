<!--
Template: troubleshooting
Path:     {system-slug}/anvandardokumentation/{locale}/felsokning

Placeholders: {{lead}}, {{contact_link}},
              {{entries[]}} where each entry has:
                symptom (phrased as the user sees it)
                cause_short (one sentence, plain language)
                what_to_do[] (ordered list of steps)
                screenshot (optional)

Render each entry as:
  ## {{symptom}}
  **Vad det betyder:** {{cause_short}}
  **Gör så här:**
  1. ...
  2. ...
  ![...]({{screenshot}})   <- only if set
Sort: most common problems first — not alphabetical.

LINK FORMAT: {{contact_link}} and any inline links MUST be absolute wiki
paths starting with / and with the system slug. Do NOT use relative paths.
-->
# Felsökning

{{lead}}

Det här är sidan du tittar på när något inte fungerar som du tänkt dig.
Leta reda på det du ser på skärmen i listan nedan. Löser det inte ditt
problem, [kontakta support]({{contact_link}}).

{{entries}}

<!--
Template: flow
Path:     {system-slug}/anvandardokumentation/{locale}/floden/{slug}

Placeholders: {{flow_name}}, {{flow_lead}}, {{prerequisites}},
              {{steps[]}} where each step has: title, instruction, what_changes, screenshot
              {{what_happens_next}}, {{related_links}}

Render steps as an ordered list where each step is:
  N. **{{title}}** — {{instruction}}
     ![{{title}}]({{screenshot}})
     *{{what_changes}}*

LINK FORMAT: {{related_links}} MUST be absolute wiki paths starting with /
and with the system slug. Do NOT use relative paths. See
references/page-hierarchy.md for the full rule.
-->
# {{flow_name}}

{{flow_lead}}

## Innan du börjar

{{prerequisites}}

## Steg för steg

{{steps}}

## När du är klar

{{what_happens_next}}

## Se även

{{related_links}}

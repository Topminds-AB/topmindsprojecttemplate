<!--
Template: role
Path:     {system-slug}/anvandardokumentation/{locale}/roller/{slug}

Placeholders: {{role_name}}, {{role_lead}}, {{can_do_list}}, {{cannot_do_list}},
              {{typical_workflow}}, {{role_screenshot}}, {{related_features_links}},
              {{contact_link}}

LINK FORMAT: {{contact_link}} and {{related_features_links}} MUST be absolute
wiki paths starting with / and with the system slug, e.g.
  /{system-slug}/anvandardokumentation/{locale}/kontakt
Do NOT hardcode relative paths like ../kontakt — they break.
-->
# Rollen: {{role_name}}

{{role_lead}}

## Det här kan du göra

{{can_do_list}}

## Det här kan du inte göra

{{cannot_do_list}}

*Behöver du göra något som står här? Kontakta en kollega med rätt behörighet,
eller läs [Kontakt och support]({{contact_link}}).*

## Så ser det ut för dig

![Vy för {{role_name}}]({{role_screenshot}})
*Din startsida när du loggar in som {{role_name}}.*

## Typiska arbetsuppgifter

{{typical_workflow}}

## Funktioner du använder ofta

{{related_features_links}}

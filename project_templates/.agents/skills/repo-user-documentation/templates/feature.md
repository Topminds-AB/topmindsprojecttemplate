<!--
Template: feature
Path:     {system-slug}/anvandardokumentation/{locale}/funktioner/{slug}

Placeholders: {{feature_name}}, {{feature_lead}}, {{when_to_use}},
              {{how_to_use_steps}}, {{screenshot_overview}}, {{screenshot_detail}},
              {{limitations}}, {{related_links}}

LINK FORMAT: {{related_links}} and any links inside {{how_to_use_steps}} MUST
be absolute wiki paths starting with / and with the system slug, e.g.
  - [Rapporter](/{system-slug}/anvandardokumentation/{locale}/funktioner/rapporter)
  - [Vanliga frågor](/{system-slug}/anvandardokumentation/{locale}/faq)
Screenshot/asset links ({{screenshot_*}}) are typically already absolute
(/u/... asset paths from Wiki.js) and need no rewriting.
-->
# {{feature_name}}

{{feature_lead}}

## När du behöver den här funktionen

{{when_to_use}}

## Så här gör du

{{how_to_use_steps}}

![Översikt av {{feature_name}}]({{screenshot_overview}})
*{{feature_name}} — så ser sidan ut när du öppnar den.*

## Detaljvy

![Detaljvy av {{feature_name}}]({{screenshot_detail}})
*Klicka på en rad för att öppna detaljvyn.*

## Begränsningar

{{limitations}}

## Se även

{{related_links}}

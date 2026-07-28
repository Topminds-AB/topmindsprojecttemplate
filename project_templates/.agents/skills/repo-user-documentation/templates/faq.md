<!--
Template: faq
Path:     {system-slug}/anvandardokumentation/{locale}/faq

Placeholders: {{faq_lead}}, {{contact_link}},
              {{groups[]}} where each group has:
                title (one of the seven taxonomy categories)
                entries[] where each entry has: question, answer_short, deep_link (optional)

Render each group as:
  ## {{group.title}}
  ### {{entry.question}}
  {{entry.answer_short}}
  [Läs mer]({{entry.deep_link}})   <- only if deep_link is set
Skip groups with no entries entirely.

LINK FORMAT: every deep_link and {{contact_link}} MUST be an absolute wiki
path starting with / and with the system slug. Do NOT use relative paths.
-->
# Vanliga frågor

{{faq_lead}}

{{groups}}

---

*Hittar du inte svaret på din fråga? Se [Kontakt och support]({{contact_link}}).*

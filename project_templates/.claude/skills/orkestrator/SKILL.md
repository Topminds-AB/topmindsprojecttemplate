---
name: orkestrator
description: >-
  Planera och förbered manuella parallella agentuppdrag. Använd när Mattias
  själv startar utförarsessionerna från startfiler.
license: Proprietary
metadata:
  owner: Topminds
  family: parallella-agentkorningar
  mode: manuell
---

# Orkestrator — wrapper

Läs `OBSIDIAN_VAULT_PATH` från repo-rotens `.env`. Följ sedan den kanoniska
mastern `<OBSIDIAN_VAULT_PATH>/skills/topminds/agent-orkestrator/SKILL.md`
och endast de direkt relevanta resurserna i samma katalog. Ladda bara den
klientadapter som gäller för den aktuella agenten.

För avgränsade frontendbuggar finns `agent-fix-snabb` och
`agent-orkestrator-auto-snabb`; välj dem endast när risk och uppdragsform
passar. En utförare med numrerad startfil följer `agent-utforare` och tar
aldrig över orkestratorrollen.

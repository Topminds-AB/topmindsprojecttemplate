---
name: orkestrator
description: >-
  Anta rollen som orkestrator för parallella agentkörningar i detta repo —
  äger plan, git, grindar och integration. Använd när Mattias startar en
  orkestratorsession eller beställer ett uppdrag som ska genomföras av flera
  parallella CLI-agenter. Tunn wrapper — mastern ligger i Obsidian-vaulten.
---

# Orkestrator (wrapper)

Detta är en tunn repo-wrapper. Mastern är vault-skillen och ska läsas i sin
helhet innan något annat görs:

1. Läs `OBSIDIAN_VAULT_PATH` ur repo-rotens `.env`.
2. Läs `<OBSIDIAN_VAULT_PATH>/skills/topminds/agent-orkestrator/SKILL.md`
   och följ den — inklusive dess referensfiler `planmodell.md`,
   `git-disciplin.md`, `grindprotokoll.md` samt mallarna i `mallar/`.
3. Läs därefter repots `AGENTS.md` (sektionen "Parallella agentkörningar").

Saknas `OBSIDIAN_VAULT_PATH` i `.env`: stanna och be Mattias om vaultens
sökväg — improvisera inte fram rollen utan mastern.

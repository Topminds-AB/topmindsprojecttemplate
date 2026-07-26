---
name: utforare
description: >-
  Regler för utförar-agenter i orkestrerade parallella agentkörningar i detta
  repo. Använd när en session startas med ett block ur ett uppdrags
  STARTPROMPTER-ALLA.md eller när en prompt hänvisar till utförar-reglerna.
  Tunn wrapper — mastern ligger i Obsidian-vaulten.
---

# Utförare (wrapper)

Detta är en tunn repo-wrapper. Mastern är vault-skillen och ska läsas i sin
helhet innan något annat görs:

1. Läs `OBSIDIAN_VAULT_PATH` ur repo-rotens `.env`.
2. Läs `<OBSIDIAN_VAULT_PATH>/skills/topminds/agent-utforare/SKILL.md`
   och följ den.
3. Läs därefter repots `AGENTS.md` samt uppdragets
   `prompts/00-GEMENSAMT.md` och din promptfil, enligt masterns läsordning.

Saknas `OBSIDIAN_VAULT_PATH` i `.env`: stanna och rapportera BLOCKERAD —
arbeta inte utan reglerna.

---
name: utforare
description: >-
  Regler för utförar-agenter i orkestrerade parallella agentkörningar i detta
  repo. Använd när en session startas med en separat numrerad startfil under
  `startprompter/` — av Mattias (manuellt läge) eller av en autonom
  orkestrator (skillen `orkestrator-auto`) — eller när en prompt hänvisar
  till utförar-reglerna. Tunn wrapper — mastern ligger i Obsidian-vaulten.
license: Proprietary
metadata:
  owner: Topminds
  version: "2.2.0"
  family: parallella-agentkorningar
  family_version: "3.0.0"
  mode: utforare
---

# Utförare (wrapper)

> **Variant: UTFÖRARE — master `agent-utforare` v2.2.0, familj
> `parallella-agentkorningar` v3.0.0, `mode: utforare`.** Gäller i BÅDA
> orkestreringslägena (manuellt och autonomt); startfilen kan komma från
> Mattias eller från en autonom orkestrator — reglerna är identiska. Anta
> aldrig orkestratorrollen.

Detta är en tunn repo-wrapper. Mastern är vault-skillen och ska läsas i sin
helhet innan något annat görs:

1. Läs `OBSIDIAN_VAULT_PATH` ur repo-rotens `.env`.
2. Läs `<OBSIDIAN_VAULT_PATH>/skills/topminds/agent-utforare/SKILL.md`
   och följ den.
3. Läs därefter repots `AGENTS.md` samt uppdragets
   `prompts/00-GEMENSAMT.md`, din exakta
   `startprompter/<NN>-<ID>-start.md` och angiven masterprompt, enligt masterns
   läsordning. Verifiera startfilens `master_sha256` innan arbete.

Skapa aldrig filer, kataloger eller worktrees i reposamlingens rot eller som
syskon till repot. Vid läge B måste arbetskatalogen ligga under verifierad
extern `AGENT_WORKTREE_ROOT`; annars ska körningen rapporteras BLOCKERAD innan
någon ändring.

Saknas `OBSIDIAN_VAULT_PATH` i `.env`: stanna och rapportera BLOCKERAD —
arbeta inte utan reglerna.

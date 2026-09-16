---
name: orkestrator-auto
description: >-
  Anta rollen som SJÄLVKÖRANDE orkestrator för parallella agentkörningar i
  detta repo — planerar, startar, övervakar och grindar utförar-agenterna
  själv, utan Mattias mellan vågorna. Dyraste modellen orkestrerar, planerar
  och kvalitetssäkrar ENDAST; allt utförande sker på billigare modeller
  enligt masterns modellpolicy. Använd när Mattias beställer ett uppdrag som
  ska genomföras autonomt av flera agenter (Claude eller Codex).
  Promptbaserad variant: skillen `orkestrator`. Tunn wrapper — mastern
  ligger i Obsidian-vaulten.
license: Proprietary
metadata:
  owner: Topminds
  version: "3.0.0"
  family: parallella-agentkorningar
  family_version: "3.0.0"
  mode: autonom
---

# Orkestrator-auto (wrapper, autonomt läge)

> **Variant: AUTONOM — master `agent-orkestrator-auto` v3.0.0, familj
> `parallella-agentkorningar` v3.0.0, `mode: autonom`.** Promptbaserad
> variant där Mattias är växel: skillen `orkestrator` (master
> `agent-orkestrator` v2.2.0). Är du en utförar-agent/subagent med en
> startfil: använd skillen `utforare`, inte denna.

Detta är en tunn repo-wrapper. Mastern är vault-skillen och ska läsas i sin
helhet innan något annat görs:

1. Läs `OBSIDIAN_VAULT_PATH` ur repo-rotens `.env`.
2. Läs `<OBSIDIAN_VAULT_PATH>/skills/topminds/agent-orkestrator-auto/SKILL.md`
   och följ den — inklusive dess referensfiler `modellpolicy.md`,
   `adapter-claude.md` och `adapter-codex.md`, samt den gemensamma grunden i
   systerkatalogen `agent-orkestrator/` (`SKILL.md`, `planmodell.md`,
   `git-disciplin.md`, `grindprotokoll.md`, `mallar/`).
3. Läs därefter repots `AGENTS.md` (sektionen "Parallel agent runs").

Mastern kräver: dyraste modellen orkestrerar/planerar/kvalitetssäkrar endast
och implementerar aldrig utförar-arbete; utförare startas av orkestratorn
själv (Claude-subagenter respektive dolda headless Codex-processer) på
billigare modeller enligt modellpolicyn; varje körning får en append-only
`startprompter/<NN>-<ID>-start.md`; osäkra scope serialiseras; inga filer
eller worktrees i reposamlingens rot. Läge B kräver en verifierad extern
`AGENT_WORKTREE_ROOT` från repo-rotens `.env`.

Saknas `OBSIDIAN_VAULT_PATH` i `.env`: stanna och be Mattias om vaultens
sökväg — improvisera inte fram rollen utan mastern.

---
name: orkestrator
description: >-
  Anta rollen som orkestrator för parallella agentkörningar i detta repo —
  äger plan, allt gitansvar, ren worktree, grindar och integration. MANUELLT
  läge: Mattias startar utförar-sessionerna själv från startfiler. Använd när
  Mattias startar en orkestratorsession eller beställer ett uppdrag som ska
  genomföras av flera CLI-agenter med honom som växel. Självkörande variant:
  skillen `orkestrator-auto`. Tunn wrapper — mastern ligger i
  Obsidian-vaulten.
license: Proprietary
metadata:
  owner: Topminds
  version: "2.2.0"
  family: parallella-agentkorningar
  family_version: "3.0.0"
  mode: manuell
---

# Orkestrator (wrapper, manuellt läge)

> **Variant: MANUELL — master `agent-orkestrator` v2.2.0, familj
> `parallella-agentkorningar` v3.0.0, `mode: manuell`.** Självkörande
> variant: skillen `orkestrator-auto` (master `agent-orkestrator-auto`
> v3.0.0). Är du en utförar-agent/subagent med en startfil: använd skillen
> `utforare`, inte denna.

Detta är en tunn repo-wrapper. Mastern är vault-skillen och ska läsas i sin
helhet innan något annat görs:

1. Läs `OBSIDIAN_VAULT_PATH` ur repo-rotens `.env`.
2. Läs `<OBSIDIAN_VAULT_PATH>/skills/topminds/agent-orkestrator/SKILL.md`
   och följ den — inklusive dess referensfiler `planmodell.md`,
   `git-disciplin.md`, `grindprotokoll.md` samt mallarna i `mallar/`.
3. Läs därefter repots `AGENTS.md` (sektionen "Parallel agent runs").

Mastern kräver att orkestratorn bevarar och pushar allt legitimt tidigare
arbete, håller worktree ren vid varje grind, serialiserar osäkra scope och
skapar en separat append-only `startprompter/<NN>-<ID>-start.md` för varje
faktisk körning. Inga filer eller worktrees får skapas i reposamlingens rot
eller som syskon till repot. Läge B kräver en verifierad extern
`AGENT_WORKTREE_ROOT` från repo-rotens `.env`; annars serialiseras arbetet.

Saknas `OBSIDIAN_VAULT_PATH` i `.env`: stanna och be Mattias om vaultens
sökväg — improvisera inte fram rollen utan mastern.

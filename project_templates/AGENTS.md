# AGENTS.md

<!-- NEXUS:GLOBAL-TEMPLATE:START:AGENTS -->
# Shared agent rules
The shared Topminds/DevLab agent rules are in your computer's own instruction file (`~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md` or `~/.gemini/GEMINI.md`), managed centrally through Nexus. Plan rules are in section 5 and the test model in section 6 there. This file holds only this project's own rules.
If you cannot see those shared rules (for example in a cloud session or a fresh clone on another computer), say so before you start and work by the project rules below.
<!-- NEXUS:GLOBAL-TEMPLATE:END:AGENTS -->

## Repo-specific notes

Add verified, repo-specific technical details below this line. Do not restate or contradict the shared agent rules on the computer: their plan rules (section 5) and test model (section 6) apply as written.

## Shared skills

Canonical skills live in `<OBSIDIAN_VAULT_PATH>/skills/topminds/`. Read the one that matches the assignment:
- `agent-director`: Claude directs Codex and cheap subagents (token-saving default for Claude).
- `agent-orkestrator-auto`: autonomous orchestration of a development goal.
- `agent-orkestrator`: Mattias starts each executor session manually.
- `agent-utforare`: one scoped executor task; never assumes the orchestrator role.
- `agent-fix-snabb` / `agent-orkestrator-auto-snabb`: one bounded, low-risk frontend bug.
- `dev-plan`: plan and rest list in KnowledgeHub for registered Nexus dev projects.

## Cloudflare purge
- Prefer the repo-local helpers `scripts/purge-cloudflare.ps1` or `scripts/purge-cloudflare.sh`, with explicit switches: `-Url` / `--url` for affected URLs, `-Everything` / `--everything` only when a whole-zone purge is expressly authorized.
- Credentials come from the repo's `.env` (`CLOUDFLARE_API_TOKEN`, optional `CLOUDFLARE_ZONE_ID`, preferred `SITE_DOMAIN`), then `infra/.env` if the repo uses it. Report missing keys as missing repo configuration; never guess.
- The reserve token in `<OBSIDIAN_VAULT_PATH>/_keys/Cloudflare.md` is used only through the explicit reserve-token switch. Never print or log a token value.

# AGENTS.md

<!-- NEXUS:GLOBAL-TEMPLATE:START:AGENTS -->
<!-- NEXUS:GLOBAL-TEMPLATE:END:AGENTS -->

This is the only repo-level agent entrypoint. Do not read `CLAUDE.md` or `GEMINI.md` separately unless your tool requires it; they only point back here.

## Read first
1. `docs/SoT/00_index.md`
2. `docs/SoT/20_repo_layout.md`
3. `docs/SoT/30_documentation_boundaries.md`
4. `docs/SoT/40_agent_workflow.md`
5. `docs/SoT/70_test_governance.md`
6. `docs/TESTING/TEST-STRATEGY.md`
7. `docs/PRD/PRD.md`
8. `docs/HLD/HLD.md`
9. `docs/implementation/PLAN.md`

## Repo vs Obsidian
- Repo contains repo-local truth required to build, test, deploy, audit, and understand this codebase.
- Obsidian contains cross-repo rules, shared skills, shared templates, global runbooks, and canonical worklogs.
- Resolve Obsidian from `OBSIDIAN_VAULT_PATH`. Do not hardcode personal paths.
- Repo-related Obsidian knowledge lives under `dev-projects/<repo-name>/`.

## Shared agent rules and skills
- Shared rules: `<OBSIDIAN_VAULT_PATH>/_system/agent-rules/`
- Canonical test governance: `<OBSIDIAN_VAULT_PATH>/_system/dev-standards/core/07-test-and-evidence-standard.md`
- Short agent policy: `<OBSIDIAN_VAULT_PATH>/_system/dev-standards/agent-test-governance-policy.md`
- Shared skills: `<OBSIDIAN_VAULT_PATH>/skills/`
- Shared templates: `<OBSIDIAN_VAULT_PATH>/templates/`

## Parallel agent runs

Larger assignments are executed as orchestrated parallel agent runs
(skill family `parallella-agentkorningar` v3.0.0). There are two
orchestration modes:

- **Manual mode** — skill `orkestrator` (Claude/Codex), master
  `<OBSIDIAN_VAULT_PATH>/skills/topminds/agent-orkestrator/SKILL.md`
  (v2.2.0): the orchestrator plans and gates; Mattias starts each executor
  session himself from a start file.
- **Autonomous mode** — skill `orkestrator-auto` (Claude/Codex), master
  `<OBSIDIAN_VAULT_PATH>/skills/topminds/agent-orkestrator-auto/SKILL.md`
  (v3.0.0): the orchestrator itself starts, monitors, and gates the
  executors (Claude subagents / hidden headless Codex workers) without
  Mattias between waves. The most expensive model only orchestrates, plans,
  and quality-assures; executors run on cheaper models per the skill's
  model policy.
- **Orchestrator:** exactly ONE session at a time owns the plan, git, gates
  and integration, in either mode.
- **Executor agent:** started ONLY via a numbered standalone
  `startprompter/<NN>-<ID>-start.md` — pasted by Mattias (manual mode) or
  fed by the orchestrator (autonomous mode). Rules:
  `<OBSIDIAN_VAULT_PATH>/skills/topminds/agent-utforare/SKILL.md` (v2.2.0,
  identical rules in both modes). An executor or subagent never assumes the
  orchestrator role.
- **Plans** live in `docs/plans/<assignment>-<date>/` with
  `1-genomforandeplan.md`, `2-exekveringsplan.md`, `prompts/`,
  `startprompter/` and `reports/`.
- Start files are append-only. Every rerun or corrected prompt gets a new
  sequential start file; previous start files are never overwritten.
- Executor agents commit only path-scoped within their own write scope and
  never run push/rebuild/purge/deploy — that is centralized to the
  orchestrator/integration prompt.
- The orchestrator must preserve and integrate all legitimate prior work,
  verify a clean worktree at every gate, and serialize whenever scopes or git
  ownership are uncertain.

## Test governance
- Obsidian is the canonical source of truth for test governance. Repo-local files are adapters and working copies.
- Do not implement a new behavior before the test is registered in `docs/TESTING/TEST-CATALOG.md`, created, and run red once.
- Do not use mocks, stubs, fixtures, fake integrations, or synthetic business data in automated tests unless an ADR-approved deviation says otherwise.
- Every meaningful governed test run must be appended to `docs/TESTING/TEST-LOG.md` with the latest run first.

## Cloudflare purge
- When a repo needs a Cloudflare cache purge, prefer the repo-local helpers `scripts/purge-cloudflare.ps1` or `scripts/purge-cloudflare.sh`.
- The agent must pass explicit switches:
  - PowerShell: `-Everything` or one or more `-Url`
  - Bash: `--everything` or one or more `--url`
- The default credential source is the current repo's `.env`, then `infra/.env` if that repo uses it.
- Expected repo config is:
  - `CLOUDFLARE_API_TOKEN`
  - optional `CLOUDFLARE_ZONE_ID`
  - preferred `SITE_DOMAIN`
- The reserve token in `<OBSIDIAN_VAULT_PATH>/_keys/Cloudflare.md` may only be used through the explicit reserve-token switch. Do not make the reserve token the default path.
- Never print or log the token value.
- If the repo lacks the required `.env` keys, report that as missing repo configuration instead of silently guessing.

## Phase completion
- Update the canonical worklog in Obsidian: `dev-projects/<repo-name>/worklogs/`.
- Run repo-root `create_codebase.bat` and verify that a new ZIP appears in `.codebasebackup/`.
- Run repo tests documented in `docs/SoT/00_index.md`.
- Run deploy scripts only when this repo explicitly contains and documents them.

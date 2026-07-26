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

## Parallella agentkörningar

Större uppdrag genomförs som orkestrerade parallella agentkörningar.

- **Orkestrator:** exakt EN session åt gången äger plan, git, grindar och
  integration. Rollen startas med skillen `orkestrator` (Claude/Codex) eller
  genom att läsa `<OBSIDIAN_VAULT_PATH>/skills/topminds/agent-orkestrator/SKILL.md`.
- **Utförar-agent:** startas ENDAST via ett block ur uppdragets
  `STARTPROMPTER-ALLA.md`. Regler:
  `<OBSIDIAN_VAULT_PATH>/skills/topminds/agent-utforare/SKILL.md`.
- **Planer** ligger i `docs/plans/<uppdrag>-<datum>/` med
  `1-genomforandeplan.md`, `2-exekveringsplan.md`, `STARTPROMPTER-ALLA.md`,
  `prompts/` och `reports/`.
- Utförar-agenter committar endast path-scoped inom eget skrivscope och kör
  aldrig push/rebuild/purge/deploy — det är centraliserat till orkestratorn/
  integrationsprompten.

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

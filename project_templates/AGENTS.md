# AGENTS.md

<!-- NEXUS:GLOBAL-TEMPLATE:START:AGENTS -->
# OBS: Detta block skrivs över av mallsynken — egna nycklar läggs under END-markören. 

This is the only repo-level agent entrypoint. Do not read `CLAUDE.md` or `GEMINI.md` separately unless your tool requires it; they only point back here.

## GOLDEN RULES
- You must NEVER create files or folder in any other places than in your repo if this is not explicitly allowed. 
- Worktrees and other temporary files must be removed when finished. 
- Allow at most seven failed corrective attempts for one original problem, counted across sessions and prompt names. Planned RED and successful GREEN runs do not count. For one environment root cause, allow at most two failed recovery attempts; retry only with new information or a concrete change.
- You are NOT allowed to use standard ports as 80, 3000 and other defaults. You must always check that ports are free before using them.
- No windows allowed on screen when testing since human use computer for meetings with customers. Only Headless Mode allowed for E2E - and as long as possible keep terminal windows hidden.
- All the important paths and secrets are stored in the .env-file that lives in the project root folder. This .env must be used in the whole repo. Others must not be created.
- You are not allowed to implement mock/fake-data unless this is strictly ordered. Follow the rules strictly that are defined in `<OBSIDIAN_VAULT_PATH>/_system/dev-standards/core/10-mock-registry-standard.md`
- All new processes you start with Playwright, Powershell, Chrome or other external function - must be HIDDEN. You are not allowed to smash up Windows since me - the human are trying to work and have meetings.
- Commit only your own cohesive changes. Push, rebuild, purge and deploy only when the assignment authorizes them and the repo/runtime requires them.
- Tie rebuilds to changed runtime images and purge to affected public cache. Verify the actual image or purge result before reporting it. Never claim a release step that was not performed.
- The rules for file size MUST be followed. Soft limit - 600 rows. Hard limits = 900 rows. Applies to source files such as `.py`, `.php`, `.ts`, `.js`, `.sh`, `.ps1`, `.go`, `.cs`, and similar implementation files.
- E2E/Playwright test data that writes to Obsidian MUST use paths under `dev-projects/<repo-name>/_e2e/` in the vault — NEVER the vault root — and the Playwright global-teardown MUST delete that quarantine folder after every run.
- The Agent is not allowed to add notes to frontend to explain technical details or the status of the work. This must never be done since the customers might do tests on the environment.

## Orkestrator skills
Use the matching skill for the task and its risk:
- `agent-fix-snabb` handles a bounded, low-risk frontend bug solo.
- `agent-orkestrator-auto-snabb` uses exactly one cheaper executor for a bounded, low-risk frontend bug.
- `agent-orkestrator-auto` handles ordinary autonomous orchestration and risk-based work.
- `agent-orkestrator` prepares prompts when Mattias starts executor sessions manually.
Permissions, migrations, payments, data-loss risks and broad contract changes use the normal risk-based auto workflow; reuse completed safe work when switching.

## Snabb verifiering för frontendbuggar
For either quick skill, one documented real frontend browser scenario before and after is valid evidence for a bounded, low-risk bugfix. Record user steps, visible outcome, screenshot path and limitations. A new test file, catalog entry or test-log entry is not required solely to repeat an existing UI flow. This interaction is not a governed automated test; this narrow exception takes precedence over generic catalog/log wording. Automated tests remain governed; higher-risk work and new behavior use the normal registered process. Never bypass the user's click flow through direct backend calls or page-state changes in JavaScript. Missing browser access or a remaining defect is not a pass.

## Outstanding Items
Read [RESTLISTA.md](docs/implementation/RESTLISTA.md) before starting. Log unresolved bugs, risks, and improvements with stable IDs, priority, evidence, next steps, and verifiable closure criteria. Update existing items; avoid duplicates. Do not expand scope or bypass acceptance requirements. Escalate blockers immediately. Before handoff, update the list and move resolved items to “Stängda” with a date and verification or justified decision. Preserve history.

## Test selection in every orchestration mode
Select the smallest tests proving the changed behavior and concrete regression risks; normally one affected scenario plus one relevant boundary case and a fast existing build/type check if needed. Record the selection briefly in the task/report. Reuse valid evidence across phases and reviewers; commit, push, rebuild and phase completion never independently trigger a full suite. A full test suite may run ONLY when assessed as absolutely necessary to verify the current change. Before running it, briefly document the concrete risk requiring the entire suite and why targeted tests are insufficient. Otherwise run ONLY targeted tests that confirm the change. Phase completion, final delivery, commit, push, rebuild or general caution alone are not sufficient reasons. Every full-suite rerun requires the same necessity assessment. Higher risk calls for targeted risk checks, not every unrelated test. Follow the canonical test standard for selection, evidence reuse and explicit acceptance conflicts. Do not silently waive binding repo/user requirements or claim unrun checks passed.

## AGENT TEST GOVERNANCE POLICY
Read `<OBSIDIAN_VAULT_PATH>/_system/dev-standards/core/07-test-and-evidence-standard.md` before governed test work. The two bounded frontend quick skills may use one documented real-browser scenario before and after as valid verification, without a new test file, catalog entry or test-log entry solely to repeat an existing flow. This interaction is not a governed automated test; this narrow exception takes precedence over generic catalog/log wording. Higher-risk work and new behavior follow the full registered test process. Automated tests remain fully governed.

## BEHAVIORAL GUIDELINES
Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.
**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

### 1. Think Before Coding
**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First
**Minimum code that solves the problem. Nothing speculative.**
- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### 3. Surgical Changes
**Touch only what you must. Clean up only your own mess.**
When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

### 4. Goal-Driven Execution
**Define success criteria. Loop until verified.**
Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```
Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## Read first for broad or higher-risk work
Quick skills read the repo entrypoint plus only instructions, SoT and code that are relevant to their bounded frontend scope. Load only the applicable client adapter. Broader work follows the repo-specific read sequence below.
1. `docs/SoT/00_index.md`
2. `docs/SoT/20_repo_layout.md`
3. `docs/SoT/30_documentation_boundaries.md`
4. `docs/SoT/40_agent_workflow.md`
5. `docs/SoT/70_test_governance.md`
6. `docs/TESTING/TEST-STRATEGY.md`
7. `docs/PRD/PRD.md`
8. `docs/HLD/HLD.md`
9. `docs/implementation/PLAN.md`
10. `<OBSIDIAN_VAULT_PATH>/dev-projects/<repo-name>/index.md`
11. `<OBSIDIAN_VAULT_PATH>/_system/dev-standards/00-index.md`

## Obsidian
- Resolve Obsidian from `OBSIDIAN_VAULT_PATH` in the repo-root `.env`. Do not hardcode personal paths.
- Obsidian is used for:
a. shared rules, standards, policies, runbooks, and reusable skills
b. repo-specific durable knowledge under `dev-projects/<repo-name>/`
c. canonical worklogs, open questions, plans, SoT mirrors, and cross-repo documentation
- You must use Obsidian when the task depends on shared standards, cross-repo knowledge, canonical worklogs, runbooks, reusable skills, or other durable documentation that should not live only in the repo.
- Start repo-specific Obsidian lookup at: `<OBSIDIAN_VAULT_PATH>/dev-projects/<repo-name>/index.md`
- Start shared standards lookup at: `<OBSIDIAN_VAULT_PATH>/_system/dev-standards/00-index.md`
- Read the short agent test policy when the task involves implementation, testing, or verification: `<OBSIDIAN_VAULT_PATH>/_system/dev-standards/agent-test-governance-policy.md`
- Read the full test and evidence standard when the task involves governed tests, evidence, or completion claims: `<OBSIDIAN_VAULT_PATH>/_system/dev-standards/core/07-test-and-evidence-standard.md`

## Important skills
- Skills are available in the shared Obsidian directory "<OBSIDIAN_VAULT_PATH>/skills/topminds"
- If you are asked to do a system check you must use the skill `<OBSIDIAN_VAULT_PATH>/skills/topminds/project-status-check/SKILL.md`
- When working with TypeSafe AI or Jev, read <OBSIDIAN_VAULT_PATH>/skills/external/typesafe-ai/SKILL.md directly; resolve OBSIDIAN_VAULT_PATH from the repository-root .env.
  Use the shared skill and follow its current documentation. Do not install or copy TypeSafe skills into individual repositories.

## Important direct links

- Cloudflare FAQ: `<OBSIDIAN_VAULT_PATH>/_system/runbooks/cloudflare/faq.md`
- Mock data rules: `<OBSIDIAN_VAULT_PATH>/_system/dev-standards/core/10-mock-registry-standard.md`
- Test and evidence standard: `<OBSIDIAN_VAULT_PATH>/_system/dev-standards/core/07-test-and-evidence-standard.md`

## Graphify

- Repo graph entrypoint for searching this repo: `<OBSIDIAN_VAULT_PATH>/dev-projects/<repo-name>/docs/repo-graph/index.md`
- Wiki graph entrypoint for searching Obsidian wiki content: `<OBSIDIAN_VAULT_PATH>/_system/wiki-graph/index.md`
- Treat Graphify as a generated navigation layer, not as canonical truth.
- Use Graphify first for structure, dependency, blast-radius, and relationship questions, then verify against real repo files or canonical Obsidian pages before making claims or changes.

### Phase completion
- Update the canonical worklog when this repo's completion rules or the assignment require one.
- Create a codebase snapshot when the repo's documented completion process requires it; verify the resulting archive.
- Run relevant repo checks. Rebuild only affected runtime images and purge only an affected public cache; verify each claimed operation.
- Deploy only when the assignment requires it and this repo documents the deploy process.
- Commit and push only when authorized by the current ownership and delivery instructions.

# OBS: Detta block skrivs över av mallsynken — egna nycklar läggs under END-markören.
<!-- NEXUS:GLOBAL-TEMPLATE:END:AGENTS -->

This is the only repo-level agent entrypoint. Do not read `CLAUDE.md` or `GEMINI.md` separately unless your tool requires it; they only point back here.

## Read first for broad or higher-risk work
Quick skills read only the repo entrypoint, applicable quick-skill contract, and repo instructions, SoT and code relevant to the bounded frontend bug. Load only the applicable client adapter.
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

Larger assignments use the full orchestration workflow (skill family
`parallella-agentkorningar` v4.0.0). Match the mode to the scope:

- **Manual mode** — skill `orkestrator` (Claude/Codex), master
  `<OBSIDIAN_VAULT_PATH>/skills/topminds/agent-orkestrator/SKILL.md`
  (v4.0.0): the orchestrator plans and gates; Mattias starts each executor
  session himself from a start file.
- **Autonomous mode** — skill `orkestrator-auto` (Claude/Codex), master
  `<OBSIDIAN_VAULT_PATH>/skills/topminds/agent-orkestrator-auto/SKILL.md`
  (v4.0.0): the orchestrator itself starts, monitors, and gates the
  executors (Claude subagents / hidden headless Codex workers) without
  Mattias between waves. The most expensive model only orchestrates, plans,
  and quality-assures; executors run on cheaper models per the skill's
  model policy.
- **Solo quick fix** — `agent-fix-snabb` investigates, fixes and verifies one
  bounded low-risk frontend bug without subagents.
- **Autonomous quick fix** — `agent-orkestrator-auto-snabb` delegates to
  exactly one cheaper executor and reviews the diff and evidence.
- Quick modes use one documented real-browser scenario before and after as
  valid evidence; they do not require the full plan/wave/report ceremony or a
  new test file solely to repeat an existing flow. See the repo's
  `docs/skills/50_orchestration-quick-v4.md` when available.
- **Orchestrator:** exactly ONE session at a time owns the plan, git, gates
  and integration, in either mode.
- **Full-workflow executor:** starts from a numbered standalone
  `startprompter/<NN>-<ID>-start.md` — pasted by Mattias (manual mode) or
  fed by the orchestrator (autonomous mode). Rules:
  `<OBSIDIAN_VAULT_PATH>/skills/topminds/agent-utforare/SKILL.md` (v4.0.0,
  shared rules for full orchestration). An executor or subagent never assumes the
  orchestrator role.
- **Quick executor:** receives a short scoped task from
  `agent-orkestrator-auto-snabb`; it does not use the full start-file/report
  ceremony and never assumes the orchestrator role.
- **Plans** live in `docs/plans/<assignment>-<date>/` with
  `1-genomforandeplan.md`, `2-exekveringsplan.md`, `prompts/`,
  `startprompter/` and `reports/`.
- Full-workflow start files are append-only. Every rerun or corrected prompt
  gets a new sequential start file; previous start files are never overwritten.
  Quick executor briefs are scoped separately and do not use this numbered
  full-workflow start-file rule.
- In the full workflow, executors do not push/rebuild/purge/deploy unless the
  prompt explicitly assigns it. Quick executors give a concise handoff; the
  orchestrator owns external delivery actions.
- Preserve unrelated and pre-existing work. Never reset, stash, clean or
  overwrite foreign changes. Record actual state; block only dependent work
  or serialize when ownership is uncertain. Do not claim a clean worktree
  unless it is verified.
- Track failed corrective attempts across sessions and prompt names: at most
  seven per original problem. An environment root cause allows at most two
  failed recovery attempts; each retry needs new information or a concrete
  change. Planned RED and successful GREEN runs are not failures.

## Test governance
- Obsidian is the canonical source of truth for test governance. Repo-local files are adapters and working copies.
- Do not implement a new behavior before the test is registered in `docs/TESTING/TEST-CATALOG.md`, created, and run red once.
- For the two bounded frontend quick skills only, a documented real-browser scenario before and after may verify a low-risk fix to existing behavior without a new test file or catalog row solely to repeat that flow. New behavior and higher-risk work use the full registered process. Any automated tests remain fully governed.
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
- Update the canonical worklog when the repo's completion rules or the assignment require one.
- Create a codebase snapshot when the repo's documented completion process requires it; verify the resulting archive.
- Run relevant repo checks. Rebuild only affected runtime images and purge only an affected public cache; verify each claimed operation.
- Deploy only when the assignment requires it and this repo documents the deploy process.

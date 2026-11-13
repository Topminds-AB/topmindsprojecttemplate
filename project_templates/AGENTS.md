# AGENTS.md

<!-- NEXUS:GLOBAL-TEMPLATE:START:AGENTS -->
# Topminds/DevLab — Global Agent Rules
DevLab / Topminds — Shared Agent Rules
This is the single repository entrypoint for Codex, Claude and other development agents. If CLAUDE.md or GEMINI.md exists, it must point to this file instead of duplicating the rules. Repository-specific instructions may add verified technical details, but may not override the user, security boundaries or the shared test standard.
1. Mission, authority and recovery
- Act as a technical executor in the assigned repository, environment and scope. Inspect, implement, configure, verify and finish the requested work; make ordinary technical decisions independently. Do not invent runtime targets, configuration values, accounts, approvals or additional requirements.
- Never expand the assignment into unrelated architecture, organizational, legal, procurement or policy assessments unless explicitly requested. Preserve user work, other agents' changes, unrelated services and existing permissions.
- Ask the user only for a necessary missing decision, a genuine policy/permission blocker or a proposed expansion of scope. An access denial blocks the denied operation, not all unrelated work.
- Diagnose denied operations using authorized read-only evidence and ordinary fixes within assigned rights. Never bypass a denial with another identity, tool, transport or indirect route. Permission increases and protected security changes need explicit authorization.
- After two failed corrections for the same cause, obtain new diagnostics before attempting another correction. Stop that fault's correction loop after seven failed attempts, record the blocker and continue independent work.
2. Frontend-first work and mock boundaries
- For web products, establish the intended navigation, page layout and actual user journeys frontend first, before the backing implementation. Maintain a concise USER-FLOWS.md for the flows that exist in this project.
- Mocks and fake functionality are forbidden by default. Explicit approval or an explicitly requested frontend-first design phase permits temporary UI-only mocks in the approved scope; a mock never proves the real feature works.
- Every affected mock-backed view has a persistent visible MOCK DATA / DEMO banner. Every link into mock-backed content is visibly labeled MOCK before click.
- Register every mocked function, endpoint and data source in the existing repo register, normally docs/SoT/mock-registry.jsonl, with a stable ID, actual code location, affected UI, simulated behavior and removal condition. Follow docs/SoT/mock.md and the shared mock standard. Never create a competing second register.
- Keep mock entries as retired when removed; remove the matching UI labels only after real functionality has been implemented and verified. Report prototypes as prototypes, not completed integrations.
3. Safe runtime and invisible automation
- Before binding a new host port, check existing listeners and container mappings. Do not allocate a common/default host port (including 80, 443, 3000 or 8080) to a new service; use a verified free non-default host port and document it in the existing project configuration.
- Do not stop, remove or reconfigure unrelated listeners, containers, proxies or services to free resources. Preserve the actual reverse proxy already configured in this repository.
- All automated browser tests run headless. Shells, scripts, scheduled tasks and other background processes must not steal focus or open visible windows on the user's desktop. If invisible execution is unavailable, report the limitation.
4. Secrets, identity and approved integration paths
- Use the existing approved secrets source for this repo. If the project is configured for Psono, use its established authorized client. Never print, log, commit, copy into documentation or hardcode secrets.
- Do not create extra .env files to store secrets or copy credentials between files. Use existing configuration and authorized process injection. Do not invent missing credentials or test identities.
- For authentication changes, use the identity provider actually configured in this repo (Keycloak when configured). Verify real positive and denied access paths. Never add or alter identities, rights or security controls solely to make tests pass.
5. One plan, real progress and concise handover
- Maintain one canonical project plan: PLAN.md by default, or the repo's already established plan location, as identified in docs/SoT/00_index.md. Use phases and Markdown checkboxes. Do not create a duplicate plan. In a registered Nexus dev project the KnowledgeHub plan is canonical: work through the `dev-plan` skill (devplan MCP or CLI), tick items off as they are finished, and never hand-edit PLAN.md or RESTLISTA.md there, because they are generated exports.
- Mark a deliverable complete only when its observed feature works and its applicable checks pass. A test file, administrative receipt, percentage update or mock-only demo does not complete a real feature.
- Add unresolved faults to the repo's established rest list if it exists, avoiding duplicates. Systems such as Nexus may read canonical progress; do not require extra per-test or per-item writebacks or receipts as a routine prerequisite.
- At session end, report only the working result and target, affected plan items, relevant actual checks, code version/commit status and blockers. Do not repeat full transcripts or old test history.
6. Implementation and mandatory test model
- Change only the files and behavior within the assignment. Prefer clear maintainable code. Document functions, classes and parameters in English, with Google-style docstrings where the language supports them. Do not silently delete or rewrite unrelated code.
- Canonical cross-repo test process: <OBSIDIAN_VAULT_PATH>/_system/dev-standards/core/07-test-and-evidence-standard.md. The repo-local docs/SoT/70_test_governance.md is only a pointer; docs/TESTING/TEST-STRATEGY.md maps that standard to this project's real commands, tests and execution target.
- Director owns test selection, strictly through the central standard's fixed change table; do not ask the user to grade ordinary technical risk or manually choose test suites.
- Before coding: record observable acceptance criteria and required test packages in the canonical plan. Divide work into coherent packages of at most five deliverables. Do not create executable tests or demand a RED baseline before implementation.
- While coding: run only existing static checks (syntax, formatter, lint, type and build). Do not repeatedly run full functional suites, browser E2E or real AI-provider sessions between small edits.
- After the completed package: create or reuse executable tests for its acceptance criteria, then run the union of its mandatory real test packages once. A change to documentation or comments only needs no functional test run.
- After a failure: fix it, then rerun only the failed tests and the tests that touch the components you changed. A test that passed, and whose code, configuration and runtime are unchanged, is never rerun. The package is green when the first run's passes plus the targeted reruns cover every mandatory test; no extra complete run is needed to confirm that.
- Rerun budget. Test reruns are the largest avoidable cost here, so this rule is binding for every agent, subagent, reviewer and skill, and it wins over briefs, handovers, LEARNINGS files and older repo text: a complete suite or package runs at most once per version (same commit, configuration and image). Never run it a second time on an unchanged version. If you think another complete run is needed after changes, stop, report why, and wait for the Director's decision; an executor never decides that alone.
- A reported green result is evidence. Directors, orchestrators, reviewers, Sentinel and stewards verify by reading the command, version and result. They do not re-execute tests to confirm them; re-execute one single case only for a concrete, stated doubt.
- If docs/TESTING/TEST-STRATEGY.md lacks a targeted command, use the test runner's own filter (file, test name or tag) and write the working command into TEST-STRATEGY.md. A missing mapping is never a reason to run everything.
- At the phase gate: run one relevant full phase/regression verification on the final running version, including real user flow and applicable denied-access checks. Reuse a valid unchanged green final run. No routine RED-first, triple green runs or manual per-test catalog/log registration.
- Never weaken, skip, delete or manipulate a failing test simply to obtain GREEN. Document real changes to approved requirements before updating expectations; distinguish product, test, environment and requirement defects. Mocked behavior cannot count as real functional verification.
- This section wins over any text below the managed block in this file, and over repo-local documents, that asks for RED-first, test registration before implementation, TEST-CATALOG or TEST-LOG entries, or repeated green runs. Such text is outdated; do not follow it.
- Record one concise result per consolidated test run in the canonical plan. Do not create TEST-CATALOG.md, TEST-LOG.md, separate RED receipts or duplicate Nexus status logs as routine test-administration requirements. Preserve existing project histories if they already exist.
7. Real running outcome
- Source code alone is not a delivered feature. Verify the changed behavior at the assigned actual target and on the current installed version.
- Where the assigned application uses container images, rebuild/recreate only affected images and containers as authorized by the assignment, preserving unrelated workloads and proxies.
- If a configured cache/front door (for example Cloudflare) serves the affected site, invalidate only affected assets using the repo's existing authorized helper. Do not treat missing unrelated Cloudflare configuration as a project-wide blocker.
- When using Cloudflare helpers, pass explicit affected-URL switches; a whole-zone purge requires express authorization. Use an existing reserve credential only through an explicit authorized reserve-token path, never as the default, and never log its value.
- Do not initiate releases, deployments, external changes or security-sensitive mutations beyond the user-assigned target and approved existing workflow.
8. Git ownership and session completion
- Inspect git status first. Preserve pre-existing changes and the work of other agents. Commit and push only changes belonging to this assignment on the established branch, through the repo's authorized workflow. Report a blocked push or conflicts accurately; never stage foreign work to make the tree clean.
- Create and verify a codebase snapshot only if the repository's established completion procedure requires one. Do not generate heavy archives or reports automatically for each small fix.
- Report technical blockers with what was observed, what was corrected and what evidence is still missing. Do not present unperformed checks or unresolved approvals as completed work.
9. Read only relevant project knowledge
- Read this entrypoint, the current assignment, the relevant part of the canonical plan, affected user flows and directly relevant code. Use docs/SoT/00_index.md as a small verified map; do not preload whole PRD/HLD/ADR trees, historical test logs or unrelated skills.
- Shared Obsidian standards are resolved through the repo's already configured OBSIDIAN_VAULT_PATH. Use the required test standard for test decisions and the mock standard only for approved mock work. Do not invent a vault location if missing.
- Use existing specialist skills and configured indexes (such as Graphify) only when relevant to the assignment. Read only the applicable tool/client adapter. The chosen Director/orchestrator owns integration across parallel executors.
- Repo-specific SoT, runtime and test paths must reflect the actual repo. If a generated template still contains EJ_KARTLAGT, the first Director resolves it from real code/configuration once; do not repeatedly ask the user for information already available locally.
<!-- NEXUS:GLOBAL-TEMPLATE:END:AGENTS -->

## Repo-specific notes

Add verified, repo-specific technical details below this line. Do not restate or contradict the managed block above: its plan rules (section 5) and test model (section 6) apply as written.

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

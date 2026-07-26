# Handoff Contract

## Shared truth
The source of truth is `./.orch/state.json`.

## Allowed orchestration files
- `./.orch/state.json`
- `./.orch/oa_to_ia.md`
- `./.orch/ia_to_oa.md`
- `./.orch/oa_to_ta.md`
- `./.orch/ta_to_oa.md`

## Turn-taking
Only one agent may be active at a time.
Only one agent may own the current turn.
Every active agent must update the shared state before and after its turn.

## Agent responsibilities
### OA responsibilities
OA must review repository truth and route the process to one of these outcomes:
- approve,
- send a precise next IA prompt,
- send a precise TA verification prompt,
- or halt for user input.

### IA responsibilities
IA must implement within scope, activate the changed system in the real environment when the task reaches a testable state, and return a factual handoff to OA.

### TA responsibilities
TA must verify repository test quality, test coverage relevance, runtime truth, real execution evidence, and Playwright MCP browser evidence, then return a factual handoff to OA.

## Prompt composition rule
The active agent must always read prompts in this order:
1. `docs/orchestration/PROMPT_BASE.md`
2. role prompt (`OA_SYSTEM_PROMPT.md`, `IA_SYSTEM_PROMPT.md`, or `TA_SYSTEM_PROMPT.md`)
3. `docs/orchestration/HANDOFF_CONTRACT.md`
4. current handoff file referenced by `state.json`

## Required handoff intent
### OA to IA
Use when OA wants implementation work.
Must contain:
1. Objective
2. Scope
3. Constraints
4. Required implementation actions
5. Runtime or deployment actions required
6. Test and Playwright MCP readiness requirements
7. Verification required
8. Exit rule

### IA to OA
Use when IA has completed a scoped implementation turn.
Must contain:
1. Phase summary
2. Files changed
3. Why each change was needed
4. Runtime and deployment actions performed
5. Test and Playwright MCP readiness status
6. Tests run
7. Remaining risks
8. Recommended next OA action

### OA to TA
Use when OA wants formal verification.
Must contain:
1. Verification objective
2. Scope under test
3. Expected runtime platform
4. Required test suites
5. Playwright MCP requirements
6. Required evidence artifacts
7. Exit rule

### TA to OA
Use when TA has completed verification.
Must contain:
1. Verification summary
2. Test structure findings
3. Tests executed
4. Runtime platform used
5. Playwright MCP evidence
6. Failures or gaps
7. Recommended next OA action

# TEST-STRATEGY – Executable Verification for This Repository

<!-- NEXUS:GLOBAL-TEMPLATE:START:TEST-STRATEGY -->
> **Managed block.** The text between the markers is updated centrally through Nexus and must not be edited in this repo. Record this repository's verified values in the project part **below** the block.

> **Type:** reusable project template. **Owner:** Director. **Scope:** the actual code, environment, and test tools of this repository only. Never copy commands or environment values from another project.

## 1. Authority and working sequence

**Binding common standard:** `<OBSIDIAN_VAULT_PATH>/_system/dev-standards/core/07-test-and-evidence-standard.md`. `docs/SoT/70_test_governance.md` is a pointer, not a second policy. The central standard controls test selection, execution limits, failure handling, E2E evidence, and independent Test Guru reviews. This document records only the repository-specific implementation of those requirements.

1. **Before coding:** Director divides the phase into packages of at most five deliverables and records observable acceptance cases and mandatory test packages in the repository's existing `PLAN.md`.
2. **During coding:** run only existing syntax, formatter, lint, type, and build checks. No mandatory RED-first step, executable test code in advance, or repeated real AI/browser functional runs between small edits.
3. **After a completed package:** create the necessary executable tests, reuse existing ones, and run the union of packages matched by the central standard's **fixed change table** once against the correct version.
4. **After a failure:** classify and correct the problem; rerun only failed tests and tests affected by actually changed components. Initial passing results plus valid targeted reruns may establish green coverage. **Do not run another full package or suite solely to confirm green.** A new complete run after changes requires the Director's decision under the central standard.
5. **At the phase gate:** verify required package coverage, applicable `@smoke` and changed browser flows, affected shared-component regression, and required denied-access checks on the final applicable version. Reuse still-valid results; after fixes apply the same targeted-rerun rule. Repeat affected smoke checks only when their previous results were invalidated, subject to the central run budget. Record human acceptance separately. Never do routine duplicate or triple full-suite runs.

## 2. Discover the actual test environment once per repository

During repository initialization, Director checks actual source files (for example manifests, build scripts, test configurations, and existing CI) and enters **verified values only**. If a value cannot be verified, use `MISSING` or `NOT_MAPPED` as appropriate, never a borrowed command. The placeholders in project part A are not execution instructions.

For repositories with a web interface, the E2E mapping in project part B must also be established through existing test tooling when E2E becomes applicable. **Do not construct a new reporting service or require developers to write additional evidence summaries.**

## 3. Binding mapping to this repository's actual tests

Assign **every matching package** from the central standard's change table. In project part C, populate the third column with the actual test file/function, verified executable command, or real user flow. `NOT_MAPPED` is **not** a test result. If a package is mandatory for a completed change but cannot be executed, the affected deliverable is **BLOCKED**, never green. For a package that cannot apply to this repository, record `NOT_APPLICABLE` with a verified reason; do not invent components or tests.

One test can prove multiple packages and must run only once in a consolidated execution. Executable tests are **not** required before implementation. This mapping does not require implementing unused technologies or testing non-existent functionality. Missing mapping never authorizes an unfiltered full-suite run. Use the test runner's verified file/test/tag filter and record it in project part C when needed.

## 4. Real environment, security, and evidence

- Verify the actual running version, target environment, user flow, and approved test identity. Creating a database or API session directly does **not** prove the real identity-provider login chain works.
- Use the project's **already approved** secret and identity mechanisms. Do not create new secret files, accounts, privilege grants, or alternative transports to bypass denied access.
- Run browser tests **headless**. Run lifecycle and other potentially disruptive flows in isolation and serially.
- Hidden mocks, fabricated integrations, or synthetic model outcomes never count as real functional verification. Expressly approved frontend-first mocks follow `docs/SoT/mock.md` and the central mock standard; mocked UI is not a completed real integration.
- When E2E applies, existing tooling must generate a browsable HTML report with **at least one screenshot per test**, including passing tests, associated with that execution. Where feasible, the screenshot shows the verified outcome after the final assertion. Existing diagnostics/traces are retained as required by the central standard and confidentiality rules. Developers do not manually inspect every image as a routine step.
- `devlab-test-guru` independently reads existing Git changes, test definitions/configuration, execution evidence, and relevant E2E artifacts. It flags omitted mandatory tests, altered expectations, weakened assertions, skipped/filtered cases, hidden mocks, and unverifiable results. **The Guru performs the extra investigation, does not change code or tests, and does not create extra routine test runs or developer paperwork.** Confirmed violations are `BLOCKED`; missing mandatory evidence is `UNVERIFIED`; advisory suggestions do not block.

## 5. Results – a single run-status source

After each **consolidated** execution or phase gate, Director writes one concise status line in the existing project `PLAN.md`:

`Package | verified commit/version | execution target | test packages | pass/fail counts | blockers | done/not done`

For applicable E2E runs, the same line also references the **existing HTML report path**. Preserve automatically produced failure output only as needed for diagnosis or the phase gate. There is **no requirement** to create or manually maintain `TEST-CATALOG.md`, `TEST-LOG.md`, separate RED receipts, duplicate Nexus status logs, or additional test-integrity statements. Existing historical evidence may remain without being copied into new project records.

**Independent corrective follow-up:** If Test Guru confirms an actionable defect, it—not the developer—records the concise finding in `docs/TESTING/TEST-GURU-FINDINGS.md`, or an already existing equivalent finding register. This is an **exception register**, not a new test-run log; create it only upon the first confirmed finding. Link a blocker from the existing plan rather than duplicating execution history. Guru gives Director a precise, minimal proposed correction; the assigned development agent implements it, and Guru validates existing evidence afterward. Guru updates its own `LEARNINGS.md` after each assignment. For a confirmed and corrected developer mistake, the developer stores only a brief reusable lesson in its existing learning mechanism. Repeated **verified** mistakes are escalated to Director for a targeted preventive change, not additional routine administration.
<!-- NEXUS:GLOBAL-TEMPLATE:END:TEST-STRATEGY -->

# Project part – verified values for this repository

## A. Test environment

| Required before applicable test execution | Verified value | Source |
|---|---|---|
| Actual application execution target | `NOT_DISCOVERED` | `NOT_DISCOVERED` |
| Static-check command | `NOT_DISCOVERED` | `NOT_DISCOVERED` |
| Approved test identities and authorization method | `NOT_DISCOVERED` | `NOT_DISCOVERED` |
| How to deploy and identify the exact application version | `NOT_DISCOVERED` | `NOT_DISCOVERED` |
| How to select individual tests without running everything | `NOT_DISCOVERED` | `NOT_DISCOVERED` |

## B. E2E mapping

| E2E mapping | Verified value | Source |
|---|---|---|
| Exact filtered `@smoke` command | `NOT_MAPPED` | `NOT_DISCOVERED` |
| Exact command/filter for changed-flow specs | `NOT_MAPPED` | `NOT_DISCOVERED` |
| Existing HTML report and per-test screenshot location | `NOT_DISCOVERED` | `NOT_DISCOVERED` |

## C. Test package mapping

| Test package | Required verification under the central change table | Actual test function/command or real flow |
|---|---|---|
| `UI` | Page rendering, interaction, saving, and reload where applicable | `NOT_MAPPED` |
| `API` | Successful and rejected/invalid endpoint or backend behavior | `NOT_MAPPED` |
| `AUTH` | Real sign-in/authorization and an actual denied attempt through the configured identity solution | `NOT_MAPPED` |
| `DATA` | Persistent write/read and migration where schema changes apply | `NOT_MAPPED` |
| `WS` | Two clients, ordering, and reconnection/reload | `NOT_MAPPED` |
| `RUNNER` | Real affected AI-provider, agent, or protocol turn where applicable | `NOT_MAPPED` |
| `LIFECYCLE` | Start, stop, timeout, and correct process cleanup | `NOT_MAPPED` |
| `EXTERNAL` | Actual authorized email/file integration and denied unauthorized access to protected resources | `NOT_MAPPED` |
| `DOCS` | Documentation/comments only: links and formatting; **no functional tests** | Check the affected documents |

# TEST-STRATEGY – Executable Verification for This Repository

<!-- NEXUS:GLOBAL-TEMPLATE:START:TEST-STRATEGY -->
> **Managed block.** Updated centrally through Nexus; do not edit between the markers. The shared test rules, including how to fill in this file, are in the shared agent rules on your computer (section 6 and "Test strategy file"). Record this repository's verified values in the project part **below** the block.
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

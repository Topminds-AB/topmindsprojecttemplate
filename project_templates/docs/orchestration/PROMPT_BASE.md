You must always follow these global project rules.

Global execution rules:
- Work directly from repository truth, runtime truth, deployment truth, and verification truth.
- Do not invent system behavior, files, settings, test results, runtime results, deployment results, or configuration values.
- Do not silently broaden scope.
- Do not modify unrelated code or documents.
- Prefer small, direct, justified changes within scope.
- If something must be removed, disabled, or bypassed, explain clearly why and preserve traceability where appropriate.
- Use repository evidence, runtime evidence, deployment evidence, and explicit task instructions as the source of truth.
- Be strict, concrete, explicit, and factual.
- Do not claim work is complete unless code, runtime, deployment, state handoff, and verification are actually complete.
- Mock data, fake integrations, stubbed business behavior, placeholder flows, and simulated completion are forbidden unless the task explicitly permits them.
- If mocks, fixtures, or stubs are explicitly permitted, they must be clearly documented in code and in the relevant handoff.

Programming and implementation rules:
- Treat existing functionality as protected unless the current task explicitly changes it.
- Do not refactor unrelated areas.
- Do not introduce new variables, files, or structures unless they are required by the task.
- Before introducing a new setting or variable, inspect the repository and reuse existing configuration patterns where applicable.
- Keep naming, architecture, and file structure aligned with repository conventions.
- In code tasks, prefer full-file rewrites for changed files rather than partial fragments when the delivery format permits it.
- Never change unrelated code just because it seems cleaner.
- If a change requires touching adjacent code, explain exactly why that adjacent code is part of the true scope.

Documentation and code quality rules:
- All code documentation, comments, and docstrings must be written in English.
- Use clear Google-style docstring conventions when writing Python code.
- Explain why changes are necessary, especially when touching existing code.
- If code is commented out or remmed instead of removed, explain why in code and in the handoff.

Runtime, deployment, and environment rules:
- If a real web server is already installed in the target environment, use it.
- If Nginx is installed, prefer the real Nginx-served application path over a temporary development server.
- Do not treat a local dev server as final verification when a real installed web server exists.
- Verification should be performed on the intended runtime platform whenever reasonably possible.
- Before handing off for testing or approval, ensure the system is actually rebuilt, compiled, restarted, published, deployed, or otherwise made runnable in the real environment.
- It is not acceptable to leave the environment stale and expect the next agent to discover that the latest code was never made active.

Testing and verification rules:
- Tests must verify real behavior, not just satisfy the current implementation.
- A previously approved test is authoritative until proven incorrect by repository truth or explicit user instruction.
- It is forbidden to weaken, dilute, or cosmetically alter a failing approved test merely to make it pass while the code remains incorrect.
- If a test is wrong, the reason must be evidenced and documented explicitly.
- Test coverage is part of implementation quality. Missing tests for relevant behavior must be treated as a real gap.
- End-to-end tests should be run on the platform the system is intended to run on.
- Playwright MCP must be the default browser automation path for E2E verification when browser testing is relevant.
- If Playwright MCP is missing in the repository, local toolchain, or IDE environment, install and configure it before claiming browser E2E coverage is complete.
- When Playwright exists or is expected for the project, Playwright E2E must be run with screenshots or equivalent durable evidence.
- Test output must be reported clearly, including what was run, where it was run, what passed, what failed, and what evidence was captured.

Prompt discipline rules:
- Always read this base prompt first.
- Then read the role-specific prompt.
- Then read the handoff contract.
- Then read the current handoff and repository context.
- The role-specific prompt may add responsibilities, but it must not weaken these global rules.

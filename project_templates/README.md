# Project README

## Short description
- **What is the system?**  
  (1–3 sentences)

- **Who is it for?**  
  (1 sentence)

- **What does it deliver?**  
  (1 sentence)

## Architecture (short)
- **Main components:** (e.g. frontend, API, DB, workers)
- **Data stores:** (e.g. MySQL/Postgres, vector store)
- **External services:** (e.g. SMTP, AI provider, storage)
- **Runtime:** (e.g. Docker Compose / native)

> For details, see SoT and HLD.

## Documentation (sources of truth)
- **SoT (quick map):** `docs/SoT/00_index.md`
- **Repo rails / anti-monolith:** `docs/SoT/20_repo_layout.md`
- **HLD:** `docs/HLD/HLD.md`
- **PRD:** `docs/PRD/PRD.md`
- **Implementation Plan:** `docs/implementation/PLAN.md`

## Quickstart
See `docs/SoT/00_index.md` for the exact commands to run locally and run tests.

## Agent workflow
- The only repo-level agent entry point is `AGENTS.md`.
- File classes (which files agents may edit) are listed in `.nexus/file-classes.json` when present.

## After each phase
- Follow the repository's applicable verification and delivery instructions.
- If Loopia is used: `deploy_loopia.bat`.

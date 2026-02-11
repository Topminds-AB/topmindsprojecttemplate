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
- This repo uses `/agents`:
  - `agents/IA/` (Implementation Agent rules)
  - `agents/OA/` (Orchestration Agent rules)
- Repo-level entry points are in: `AGENTS.md`

## After each phase (mandatory)
- Run: `create_codebase.bat`
- If Loopia is used: `deploy_loopia.bat`

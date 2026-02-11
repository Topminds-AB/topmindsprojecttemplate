# SoT — 00 Index
> **Purpose:** A 2–5 minute map of this repo. Keep it short and practical.  
> **Owner:** PO (content), OA (structure updates), IA (keeps it current when implementing changes)

---

## 1) What this system is
- **Product:**  
- **Primary users:**  
- **Core outcome:**  
- **Non-goals (explicitly not included):**  

---

## 2) Delivery profile
- **Current profile:** `MVP_FAST | STANDARD | AUDIT_STRICT`
- **Notes:** (when/why profile changes)

---

## 3) Quickstart (copy/paste)
### Local run
- **Prereqs:** (docker, node, python, etc.)
- **Command(s):**
  - 
- **Local URL(s):**
  - 
- **Default dev credentials (non-secret):**
  - 

### Tests (minimum)
- **Command(s):**
  - 
- **Expected result:**
  - 

---

## 4) Repo map (where things live)
> Keep this aligned with actual folders.

- `docs/HLD/` → High level design
- `docs/PRD/` → Product requirements
- `docs/SoT/` → Source of truth (this folder)
- `docs/implementation/` → Phase plan(s)
- `docs/worklogs/` → Worklogs (per phase)
- `agents/` → Agent library (OA/IA docs and templates)
- `scripts/` → Automation, helpers, snapshot tooling
- `services/` → (if used) main application services
- `apps/` → (if used) frontend(s)
- `packages/` → (if used) shared libraries
- `infra/` → (if used) infrastructure/deploy definitions
- `tests/` → (if used) test suites
- `storage/` → (if used) local storage (usually gitignored)

---

## 5) Architecture (high level)
> 5–15 bullets. Link to HLD for details.

- **Components:**
  - 
- **Data flow (short):**
  - 
- **External dependencies:**
  - 
- **Hosting/runtime:**
  - 

---

## 6) Data stores
- **Primary DB engine:**  
- **Migrations / schema source:**  
- **Dumps:** (where, how, and when included in snapshots)  
- **Vector store (if any):**  

---

## 7) Configuration
> The canonical list of variables for this repo lives in `docs/SoT/10_runtime_and_config.md`.

- **Config entrypoints:** (e.g. `.env`, `docker-compose.yml`, `config/*.json`)
- **Secrets policy:** `.env` is gitignored, `.env.example` is committed.

---

## 8) Key flows (top 3)
1)  
2)  
3)  

---

## 9) Known risks / tech debt (short)
-  
-  

---

## 10) Canonical links
- **HLD:** `docs/HLD/HLD.md`
- **PRD:** `docs/PRD/PRD.md`
- **Implementation Plan:** `docs/implementation/PLAN.md`
- **Repo layout rules:** `docs/SoT/20_repo_layout.md`
- **Worklogs:** `docs/worklogs/`

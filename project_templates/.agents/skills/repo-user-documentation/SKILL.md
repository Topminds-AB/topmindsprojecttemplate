---
name: repo-user-documentation
description: Scan a repository, capture its user-facing surfaces, and generate structured user documentation using the scripts, references, and templates in this bundle.
---

# Repo User Documentation

Use this skill when repository-specific user documentation must be generated or
updated from the real repository and runtime.

**Always run** `config_check.py` **first** to know which prompts will be needed:

```bash
python .agents/skills/repo-user-documentation/scripts/config_check.py \
  --repo-root . --output ./tmp/docs-build/config-status.json
```

The output tells the agent exactly what to ask interactively (if anything) and what to proceed with silently. Pre-filling `docs-config.yaml` reduces interactive questions to zero — see `config/docs-config.schema.yaml` for the complete schema.

## Workflow

1. **Pre-flight check** — Validate config and env before doing anything destructive. Run `config_check.py`. If it returns blocking issues, stop and report. If only warnings, proceed but plan to ask the listed questions.

   ```bash
   python .agents/skills/repo-user-documentation/scripts/config_check.py \
     --repo-root . --output ./tmp/docs-build/config-status.json
   ```

2. **Discovery** — Read `.env`, `README.md`, `CHANGELOG.md`, manifests, `docs/`. Run the scanner to produce an inventory. Fill gaps from `docs-config.yaml` first; ask interactively only for items still missing. See `references/discovery.md`.

   ```bash
   python .agents/skills/repo-user-documentation/scripts/scan_repo.py full-inventory \
     --repo-root . --output ./tmp/docs-build/inventory.json
   ```

3. **Planning** — Build the page hierarchy from the inventory per `references/page-hierarchy.md`. Write `./tmp/docs-build/plan.json` and a human-readable `plan.md`. Stop here on `--plan-only`.

4. **Capture** — For each locale in `APP_SUPPORTED_LOCALES`, log in, switch locale, navigate and screenshot every planned screen. See `references/capture-playwright.md` and `references/i18n-strategy.md`.

5. **Annotate** — Apply arrow/box highlights per screen. Off with `--no-annotate`. See `references/annotation.md`.

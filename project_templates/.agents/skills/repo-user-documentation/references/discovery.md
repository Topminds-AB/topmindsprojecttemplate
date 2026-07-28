# Discovery — scanning a repo for its user surface

Discovery is the phase before anything else. The goal is a complete inventory of what the user can see and do in the system. `scripts/scan_repo.py` gives you a baseline; the agent must review the output and fill gaps by reading code directly.

## What to collect

- **System metadata**: slug, human name, one-line description.
- **Stack**: framework (Next.js, React Router, Vue, Django, Express, Laravel), language, package manager. Influences which scanner pass to trust.
- **Locales**: list of supported languages, read from i18n folders or message files.
- **Routes**: every path a user can land on. Include whether authentication is required.
- **Features**: logical groups of routes (e.g. "Reports" covers `/reports`, `/reports/new`, `/reports/:id`).
- **Flows**: multi-step user journeys (login, create-case, approve-request). Not auto-detected — read the code.
- **Roles**: user types that see different UI (admin, handläggare, läsare). Read auth/permission code.
- **Notifications**: in-app toasts, emails, SMS. Check notification/mail modules and template files.
- **Integrations**: external services the user sees (BankID, SITHS, export to Excel, Skolfederation). Check `.env.example`, third-party SDK imports.
- **Error states**: user-facing error pages and messages. Check 404/500/error-boundary files.

## How to run the scanner

```bash
python .agents/skills/repo-user-documentation/scripts/scan_repo.py full-inventory \
  --repo-root . --output ./tmp/docs-build/inventory.json
```

Output JSON has a `gaps` array listing what the scanner could not find. **Every item in `gaps` is a task for the agent to resolve before planning.**

## Framework-specific notes

**Next.js App Router** — Routes live at `app/**/page.{tsx,jsx,ts,js}`. Folder names starting with `(group)` do not appear in the URL. Dynamic segments `[id]` map to `:id`. `layout.tsx` and `route.ts` are not user-facing pages.

**Next.js Pages Router** — Routes at `pages/**/*.{tsx,jsx}`. Files starting with `_` are not routes. `index.tsx` means `/`.

**React Router / Vue Router** — Look for `path:` or `path=` in route config files under `src/`. Often centralised in `routes.ts`, `router.ts`, or `App.tsx`.

**Django** — Every `urls.py` contributes. Follow `include(...)` chains to assemble full paths.

**Express** — `app.get/post/use` calls; check `routes/` directory if present. Route modules are often composed via a central `index.ts` or `server.ts`.

**Server-rendered templates (Laravel Blade, Django templates, Rails ERB)** — The route list comes from routing files, but the screens also need a visual pass — server-rendered UIs frequently have forms and modals not reflected in URLs.

## Authentication gates

Identify protected routes so capture can decide whether to log in first. Typical markers:
- Next.js middleware: `middleware.ts` with `matcher`
- HOC wrappers: `withAuth`, `RequireAuth`, `ProtectedRoute`
- Django: `@login_required` decorators
- Server middleware: `app.use(authenticate)` on route prefixes

If uncertain, assume a route is protected and capture with login.

## Inventory JSON shape

```json
{
  "system": {"slug": "styrgruppskort", "name": "Styrgruppskort", "description": "..."},
  "stack": {"framework": "express", "language": "javascript", "package_manager": "npm"},
  "locales": ["sv", "en"],
  "routes": [
    {"path": "/dashboard", "auth": true, "source_file": "src/routes/dashboard.ts"}
  ],
  "features": [
    {"id": "reports", "label": "Rapporter", "routes": ["/reports", "/reports/:id"],
     "purpose": "Skapa och exportera projektstatusrapporter."}
  ],
  "flows": [
    {"id": "login", "label": "Logga in", "steps": [
      {"title": "Öppna inloggningen", "path": "/login", "state": "empty"},
      {"title": "Fyll i uppgifter", "path": "/login", "state": "filled"},
      {"title": "Landningssida", "path": "/dashboard", "state": "default"}
    ]}
  ],
  "roles": [
    {"id": "admin", "label": "Administratör", "sees": ["alla funktioner", "användarhantering"]}
  ],
  "notifications": [
    {"id": "report-ready", "channel": "email", "trigger": "När en rapport är klar"}
  ],
  "integrations": [
    {"id": "bankid", "label": "BankID", "user_facing": "Används vid inloggning."}
  ],
  "gaps": []
}
```

Keep field names stable — the authoring phase depends on them.

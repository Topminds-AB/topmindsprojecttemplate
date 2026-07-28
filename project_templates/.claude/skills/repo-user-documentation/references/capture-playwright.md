# Capture — Playwright workflow

`scripts/capture.py` drives Playwright against the deployed environment. It is read-only by default: no form submissions, no record creation, no deletions.

## One-time setup (per machine)

```bash
pip install playwright python-dotenv pillow
playwright install chromium
```

## Verifying login before a full run

```bash
python .claude/skills/repo-user-documentation/scripts/capture.py login-check --locale sv
```

Prints the landing URL after login. If this fails, the full run will also fail — fix env vars and selectors first.

## Selectors for the login form

Defaults cover most cases:

- username: `input[name="username"], input[type="email"], input[name="email"]`
- password: `input[name="password"], input[type="password"]`
- submit:   `button[type="submit"], input[type="submit"]`

Override via `APP_USERNAME_SELECTOR`, `APP_PASSWORD_SELECTOR`, `APP_SUBMIT_SELECTOR` if the app uses custom markup. For apps behind SSO/BankID, log-in automation is not supported — use a session cookie exported to a Playwright storage state file and point `APP_STORAGE_STATE` at it (future extension; not currently implemented).

## Required environment

```env
APP_URL=https://staging.example.se
APP_USERNAME=doc-user@example.se
APP_PASSWORD=...
APP_LOGIN_PATH=/login
APP_POST_LOGIN_URL_CONTAINS=/dashboard
APP_SUPPORTED_LOCALES=sv,en
APP_LOCALE_SWITCH_STRATEGY=path-prefix
APP_LOCALE_SWITCH_PARAM=lang
```

`APP_POST_LOGIN_URL_CONTAINS` is strongly recommended — without it, a failed login can silently pass through and result in screenshots of the login screen. Setting it makes the script exit loudly.

## Locale switching strategies

| Strategy      | How URL is built                     | When to use                               |
|---------------|--------------------------------------|-------------------------------------------|
| `path-prefix` | `/sv/dashboard`, `/en/dashboard`     | Next.js i18n, Vue i18n with routing       |
| `url-param`   | `/dashboard?lang=sv`                 | Apps that read a query param              |
| `cookie`      | URL unchanged; cookie set on context | Server-rendered apps storing locale in a cookie |
| `user-setting`| URL unchanged; switch must be scripted | Locale stored on the user account. Requires a manual preparation step before the run — set the user's preferred locale in the app, once per locale, before capture. |

For `user-setting`, run capture for one locale, change the user's profile language in the app, run capture for the next locale, and so on. The script does not attempt to automate the profile change.

## Screen naming convention

```
<output-dir>/<section>/<slug>--<state>.png
```

- `section` matches the page hierarchy (`funktioner`, `floden`, ...).
- `slug` is the per-screen identifier from the plan.
- `state` is one of `default`, `empty`, `filled`, `error`, or a custom label. Default if omitted.

This convention is what the authoring phase expects when injecting images into markdown. **Never rename screenshots manually** — edit the plan and re-run.

## Waiting for the page to settle

The plan can set `wait_selector` (CSS selector that must appear) and `wait_ms` (extra milliseconds) per screen. Prefer a selector; `wait_ms` is a last resort. Fullscreen modals and toasts are common sources of flaky screenshots — wait for the element you actually want to capture.

## Troubleshooting

- **Screenshot shows login form** — login failed silently. Set `APP_POST_LOGIN_URL_CONTAINS`.
- **Empty-looking page** — content loads after the initial render; add a `wait_selector`.
- **Cookie banner in every screenshot** — add a pre-navigation step to accept or dismiss it. The simplest fix is to set a cookie on the context before any navigation.
- **Screenshots differ run-to-run at the pixel level** — disable animations globally by setting `prefers-reduced-motion` via `context.add_init_script`. Not yet wired; add if flakiness hurts annotation accuracy.
- **Very long pages produce huge files** — set `full_page: false` on that screen in the plan.

# PR: Security hardening, website builder, tests/docs/CI overhaul (curated sync)

Base: `main`
Head: `integration/curated-sync-2025-08-12`

## Summary
This PR consolidates our recent work into a clean, stable branch to continue development on one working version. It focuses on:

- Security hardening across OS and Website apps (IDOR, injection, XSS, safe redirects).
- A comprehensive test suite expansion with higher coverage and CI integration.
- Website content builder improvements (ContentPage), templates hardened and new views/tests.
- Repo hygiene: remove accidental virtualenv artifacts, stop tracking logs, add robust `.gitignore`.

## Scope (high-level)
- Tests: add extensive `app/**/tests/**` suites and targeted security tests.
- Docs: update `docs/security-hardening.md`, add `docs/security-hardening-report.md`.
- CI: add `.github/workflows/tests.yml` and `coverage.yml`.
- Security & views/services:
  - `app/nadooit_os/views.py`: enforce per-customer object-level auth on role-giving and contract endpoints; return 403/404 consistently.
  - `app/nadooit_os/services.py`: sanitize CSV export, ID-based lookup guards, safe API key hashing.
  - Templates hardened (escape, guard variables) e.g. `nadooit_os/base.html`, website video embed.
  - `app/nadooit_website` ContentPage builder additions: templates, migrations, forms, views, services.
- Hygiene: `.gitignore` updated (venv/logs/pycache), remove `.venv.bak.*/` and logs from VCS.

## Key changes (selected)
- `app/nadooit_os/views.py`: per-customer checks in `give_*_role` and HR contract activate/deactivate; anonymous guarded by `login_required` in URLs.
- `app/nadooit_os/services.py`: CSV sanitization (formula-injection safe), UUID/ValidationError guards for ID lookups, API key hashing.
- `app/nadooit_website/...`:
  - ContentPage: migrations `0046`, `0047`, templates (`content_page*.html`), forms/views/urls; JS-embedded values escaped in `video_embed.html`.
- Tests added (non-exhaustive):
  - `app/nadooit_os/tests/test_contract_permissions.py`
  - `app/nadooit_os/tests/test_hr_contract_activation.py`
  - `app/nadooit_os/tests/test_role_giving_permissions.py`
  - `app/nadooit_os/tests/test_export_transactions.py`
  - `app/nadooit_os/tests/test_api_key_views*.py`
  - `app/nadooit_website/tests/test_content_pages*.py`, `test_views_*`, `test_templates_security.py`, `test_services_*`
- CI: `.github/workflows/tests.yml`, `coverage.yml`.
- Repo hygiene: removed tracked `.venv.bak.1754741511/**`, stopped tracking `app/logs/*.log`.

## Security hardening (highlights)
- Enforce object-level authorization for role-giving endpoints to prevent cross-customer escalation (IDOR).
- Harden HR contract endpoints: 403 for unauthorized, 404 for unknown/invalid IDs; no auto-creation of acting manager contracts.
- CSV export neutralizes spreadsheet formula injection, including whitespace-prefixed cases.
- API key hashing fixed (store hashed, never raw), request hashing aligned.
- Template XSS hardening: escape error messages and JS-embedded values.
- UUID/ID coercion guards return safe fallbacks instead of exceptions.

See `docs/security-hardening.md` for detailed entries.

## Tests & coverage
- Local runs show all current tests passing post-hardening in prior sessions; CI (GitHub Actions) added to validate in PR.
- Root-level `conftest.py` ensures pytest-django discovers settings (adds `app/` to `sys.path`).

## Backwards compatibility and risks
- Behavior changes: unauthorized now returns 403 (not 302) on protected OS endpoints; login redirect behaviors standardized.
- CSV export may prefix risky cells with apostrophes by design.
- Minimal surface-area change in models/data migrations beyond ContentPage additions.

## Deployment/ops
- No DB migrations outside ContentPage additions.
- No secrets committed; logs and virtualenv are now ignored.

## Checklist
- [x] Remove large/tracked logs from VCS; add ignores for logs/pycache/venv.
- [x] Remove accidental `.venv.bak.*` from VCS.
- [x] Add/verify CI workflows.
- [x] Security docs updated.
- [x] Tests green locally prior to push; CI to validate.

## How to review
- Focus on `app/nadooit_os/views.py`, `app/nadooit_os/services.py`, and new Website ContentPage files.
- Verify test intent by reading new tests in `app/**/tests/**`.
- Confirm CI passes.

## Links
- Branch: `integration/curated-sync-2025-08-12`
- Compare & create PR:
  - https://github.com/NADOOIT/NADOO-IT/compare/main...integration/curated-sync-2025-08-12?expand=1

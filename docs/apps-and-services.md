# Apps and Services Catalog

This catalog summarizes the major components that make up NADOO-IT. It’s a living document and will be refined as features evolve.

Services (runtime)
- Web app (Django)
  - Dev: runserver_plus HTTPS
  - Prod: uWSGI behind Nginx proxy
- Proxy (Nginx)
  - TLS termination, serves static/media
  - Works with Certbot to obtain/renew certificates
- Redis
  - Message broker for Celery
- Celery worker
  - Background job execution using the same Django settings

Project apps (Django)
Note: Code for each app is under `app/<app_name>/` unless otherwise noted. Third‑party apps are installed from `requirements.txt`.

Core/third‑party
- django.contrib.* – Built‑in Django apps (admin, auth, sessions, staticfiles, etc.)
- rest_framework – Django REST Framework
- pwa – Progressive Web App support
- django_extensions – Dev utilities (shell_plus, etc.)
- mfa – Multi‑factor authentication
- crispy_forms, crispy_bootstrap5 – Form rendering
- debug_toolbar – Django Debug Toolbar (dev)
- django_htmx – HTMX integration
- grappelli – Enhanced Django admin UI
- ordered_model – Ordered models helper
- django_is_url_active_templatetag – Template tag to mark active URLs

Custom (NADOO‑IT)
- nadooit_auth – Custom user model and authentication (AUTH_USER_MODEL)
- nadooit_api_key – API key management and verification
- nadooit_crm – CRM features (contacts, organizations, etc.)
- nadooit_hr – Human Resources (employees, roles, policies)
  - See: `docs/contracts-and-access-control.md` for contracts, permissions, and manager roles.
  - Security: Contract activation/deactivation is enforced with object-level authorization scoped to customer and manager abilities; see `docs/security-hardening.md`.
- nadooit_time_account – Time balance and billing for digital workers: manages purchased (prepaid) time remaining and consumed time owed (postpaid)
- nadooit_workflow – Generic workflow engine / state handling
- nadooit_network – Networking / relationships across entities
- nadooit_program – Program and project management
- nadooit_program_ownership_system – Ownership and permissions around programs
- nadooit_api_executions_system – Managing and tracking API executions
- nadooit_website – Public website CMS (sections, video/file embeds)
- nadooit_os – OS‑level utilities and integrations
  - Hosts HR contract endpoints (activate/deactivate). Security-critical: object-level checks ensure only authorized employee managers for the same customer and with delete ability can toggle contracts. See `docs/security-hardening.md`.
  - Role-giving endpoints (Time Account, Program Execution, Program, Employee Manager) enforce per-customer object-level authorization and use explicit get-only/create-only/ability-setter helpers to avoid implicit contract creation. See `docs/security-hardening.md` for details and tests.
  - Idempotency: manager contract creation helpers return existing contracts when present; duplicate POSTs to role‑giving views do not create duplicate manager contracts.
  - Authentication: all `nadooit_os` routes require authentication via `login_required`. Global `LOGIN_URL` is set to `/auth/login-user` so anonymous access is consistently redirected. Tests: `app/nadooit_os/tests/test_views_os_permissions.py` (GET/POST smoke tests).
  - Deprecated (service helpers): legacy auto-creating getters (e.g., `get__employee_contract__for__employee__and__customer`, `get__employee_manager_contract__for__user_code__and__customer`) remain for backward compatibility and tests. Do not use these in views or authorization paths. Prefer the explicit pattern: `get_only__...` to check, `create__...` to create, and `set__list_of_abilities__...` to assign abilities.
    - Tests: `app/nadooit_os/tests/test_manager_contract_helpers.py`, `app/nadooit_os/tests/test_role_giving_permissions.py::TestRoleGivingIdempotency`, `app/nadooit_os/tests/test_hr_permissions.py::test_give_employee_manager_role_idempotent`.
- nadooit_key – Key / credential management utilities
- nadooit_questions_and_answers – Q&A knowledge features
- nadoo_complaint_management – Complaint / ticket management
- bot_management – Managing automation/bots
  Note on experimental integrations
  - WhatsApp (under `bot_management/plattforms/whatsapp`) is experimental and disabled by default.
    - Feature flag: set environment variable `WHATSAPP_ENABLED=1` to enable routes and tests.
    - When disabled, the WhatsApp webhook URL is not registered and WhatsApp tests are skipped.
    - If you plan to work on WhatsApp, enable the flag first and write/enable tests accordingly.
- nadoo_erp – ERP features (finance, inventory, etc.)
- djmoney – Money fields and currency handling (third‑party, used by ERP/finance modules)

Notes
- Some modules above are grouped by domain and share models across apps. Check each app’s `apps.py`, `models.py`, and `admin.py` for exact scope.
- If an app is not yet in use, it is still listed for completeness and may be expanded later.
- Background jobs for each app should live under `tasks.py` and run in the Celery worker.

See also
 - Architecture overview: `docs/architecture.md`
 - Running the system: `docs/running.md`
 - Website system details: `docs/website-system.md`

---

## App deep dives

### Time Accounting (nadooit_time_account)
Purpose
- Manage time balances for digital workers per customer: how much time was purchased (prepaid) vs how much was consumed and owed (postpaid).
- Support recharges/top-ups and consumption recording to keep an accurate running balance.

Key concepts and models
- TimeAccount: the core ledger of time (in seconds or hours) for a scope (e.g., customer/program).
- CustomerTimeAccount, EmployeeTimeAccount: specialized links for the account holder or assignee.
- WorkTimeAccountEntry: consumption entries that deduct from available time (or accumulate owed time in postpaid flows).

Typical flows
- Prepaid: customer purchases N hours → balance increases; as digital workers execute tasks, entries reduce balance → when low, trigger alerts/top-up.
- Postpaid: workers execute tasks → consumption entries accumulate owed time; billing/invoicing clears balance on payment.

Integrations
- Used by operational services (e.g., `nadooit_os.services`) to compute and format balances and to display remaining/owed time.
- Surfaces in admin for manual adjustments and reviews.

Operational notes
- Ensure tasks that record consumption are idempotent to avoid double-charging.
- Consider Celery tasks for nightly balance checks and notifications.

### API Executions System (nadooit_api_executions_system)
Purpose
- Track, audit, and optionally orchestrate programmatic API executions.
- Provide visibility into status, duration, payloads (where appropriate), and outcomes.

Typical capabilities
- Create execution records when API calls are received/triggered.
- Store status transitions (queued → running → succeeded/failed) with timestamps and error context.
- Expose admin views and, when applicable, API endpoints for querying execution history.

### Program Ownership (nadooit_program_ownership_system)
Purpose
- Define and enforce ownership/permission relationships around programs/projects.
- Link customers/users to programs with specific roles and scopes.
- See: `docs/contracts-and-access-control.md` for how customer ownership ties into access checks.

Cross-app links
- References `nadooit_time_account` in templates and models where time budgeting or display is required.
- Used by CRM/HR to constrain who can act on which program artifacts.

### Website CMS (nadooit_website)
Purpose
- Section-based CMS used to render the public website.
- Supports rich content including embedded videos/files.

How it works
- Sections are persisted in the DB and can be exported/imported via management commands.
- Static/media are served by Nginx in production for performance.
- See details in `docs/website-system.md`.

### Auth and API Keys (nadooit_auth, nadooit_api_key)
Purpose
- Custom user model and authentication flows, plus API key issuance/verification for programmatic access.

Notes
- MFA support is available via installed third-party apps.
- API keys gate sensitive endpoints; rotate keys and use least privilege.
 - Security:
   - API keys are stored using Argon2 (per-key salt). Raw keys are never persisted; clients send RAW keys and verification uses Argon2 `PasswordHasher.verify` against the stored hash.
   - Create: restricted to Api Key Managers (decorated view); anonymous/non-managers are redirected to login.
   - Revoke: login required and only affects the caller’s own active keys.

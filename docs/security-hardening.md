# Security Hardening Report (Living Document)

This document tracks changes, tests, and findings related to security hardening across the NADOO-IT project. It is updated incrementally as protections and tests are added.

## Cumulative Summary (as of 2025-08-10)

Scope: Restore missing contract views, close IDOR gaps, strengthen input handling and file safety, harden redirects and templates, and add targeted tests.

Highlights
- Contract system hardening (nadooit_os)
  - Restored accidentally truncated views in `nadooit_os/views.py`.
  - Added strict object-level authorization to `activate_contract` and `deactivate_contract`:
    - 404 on unknown contract ID; 403 unless manager is authorized for the same customer and has `can_delete_employee=True`.
    - Removed `user_passes_test` to avoid 302 redirects for unauthorized access; rely on explicit 403 checks.
    - State changes performed only through service functions.
  - Tests: `app/nadooit_os/tests/test_contract_permissions.py` (cross-customer denial, missing ability denial, happy path, 404s).

- CSV injection defenses
  - Hardened CSV sanitizer to neutralize formula injection, including leading whitespace cases.
  - View-level tests for `export_transactions` (login required, 404 customer, unknown filter → empty CSV, sanitizer coverage).

- Redirect safety
  - `safe_redirect` prevents open redirects; consistent fallback to reversed URL.
  - Security tests ensure malicious `next` params are blocked.

- Template XSS defenses
  - Escaped reflected error messages and JS-embedded variables (`escapejs`) in video embeds.
  - Tests ensure HTML/JS contexts are safe.

- File/Path safety
  - ZIP extraction hardened against path traversal; added tests including Windows-style backslashes (xfail where applicable).
  - HLS playlist path handling validated.

- ID-based lookups and session validation
  - ID helpers return None on invalid/injection-like input; no exceptions propagate.
  - `check__session_id__is_valid` coerces to UUID and returns False on invalid input to prevent unnecessary DB lookups.

- WhatsApp webhook
  - Entire integration guarded behind `WHATSAPP_ENABLED` flag (default off); tests aligned.

- Compatibility and CI quality
  - Python 3.9 compatibility fixes (Optional/Union annotations).
  - Root pytest config fixed; full suite runs with coverage.

Status
- Tests: 197 passed, 3 skipped, 1 xfailed.
- Coverage: 71.79% (>= 50% target).

Next wave (prioritized)
- Contract flows beyond activation/deactivation
  - Add/extend tests for: employee creation (`hr/add-employee`), manager role assignment (`hr/give-employee-manager-role`).
  - Verify object-level checks ensure only authorized managers scoped to the same customer can act.
- Broaden input-hardening tests
  - Unicode/edge cases for `nadooit_website/services.py` and related templates.
  - Additional CSV edge cases (extreme lengths, mixed whitespace, locale variations).
- Audit read/list endpoints for IDOR risks
  - Ensure listings and detail views filter by authorized scopes; add explicit tests.
- Continue documenting findings here with dates and test paths.

## Latest additions

Date: current

- Authentication enforcement (nadooit_os)
  - Set a global `LOGIN_URL = "/auth/login-user"` so all `login_required` redirects are consistent and safe.
  - Wrapped all `nadooit_os` routes with `login_required` in `app/nadooit_os/urls.py` to enforce authentication across the board.
  - Added smoke tests to ensure anonymous access is always redirected to the login page:
    - GET routes: `app/nadooit_os/tests/test_views_os_permissions.py::test_all_os_routes_require_login_redirect` iterates through major routes and asserts redirect contains `login-user`.
    - POST routes: `app/nadooit_os/tests/test_views_os_permissions.py::test_all_os_post_routes_require_login_redirect` covers sensitive POST endpoints (role-giving, add-employee, API key create/revoke, complaint send) and asserts redirect to login.
  - Updated website test to align with the global `LOGIN_URL` change: `test_upload_zip_requires_login` now expects `/auth/login-user`.

- Contract activation/deactivation (nadooit_os)
  - Added strict object-level authorization to `activate_contract` and `deactivate_contract` views:
    - Safely fetch target contract; return 404 when not found.
    - Require an `EmployeeManagerContract` for the current user's employee on the SAME customer as the target contract, with `contract__is_active=True` and `can_delete_employee=True`.
    - Deny with 403 when authorization fails (prevents IDOR).
    - Mutations are performed via existing service functions only after authorization.
  - Added tests in `app/nadooit_os/tests/test_contract_permissions.py`:
    - Manager from other customer cannot deactivate (403) and target remains unchanged.
    - Manager without `can_delete_employee` cannot activate (403).
    - Authorized manager can deactivate and then activate for the same customer (200, state toggles).
    - Unknown contract ID returns 404 for both endpoints.

- CSV export (nadooit_os)
  - Added tests for `export_transactions` view:
    - Requires login (redirects anonymous users to `login-user`).
    - Returns 404 when customer is not found.
    - Unknown `filter_type` returns an empty CSV (header only).
    - Neutralizes spreadsheet formula injection in CSV cells for program names:
      - Direct risky start (`=`, `+`, `-`, `@`) → prefixed with two apostrophes `''`.
      - Space-prefixed risky (e.g., `' =SUM'`) → prefixed with a single apostrophe `'`.
      - Non-space whitespace-prefixed risky (e.g., `"\t@IMP"`) → prefixed with two apostrophes `''`.
  - Covered in: `app/nadooit_os/tests/test_export_transactions.py`.

- WhatsApp webhook (bot_management) [guarded]
  - Routes and tests are disabled by default behind `WHATSAPP_ENABLED=1`.
  - GET challenge handling avoids DB lookups; POST returns 400 when bot not registered.

- Auth redirects (nadooit_auth)
  - `safe_redirect` prevents open redirects; fallback uses exact reversed URL (with trailing slash) in tests.

- Template XSS
  - Error messages are escaped in templates, and tests assert no HTML injection.

- ZIP extraction and path handling (nadooit_website)
  - Hardened `_safe_extract` and path joins to prevent traversal.

- Website templates and services (nadooit_website)
  - Hardened `video_embed.html` to use `escapejs` for all JS-embedded variables (`player_uuid`, playlist URLs) to prevent breaking out of string literals and XSS.
  - Hardened `check__session_id__is_valid` to safely coerce strings to `UUID` and return `False` on invalid/injection-like inputs; prevents exceptions from propagating and DB lookups with malformed IDs.
  - Added tests:
    - `app/nadooit_website/tests/test_templates_security.py` verifies HTML escaping in `file_download_button.html` and safe JS context escaping in `video_embed.html`.
    - `app/nadooit_website/tests/test_services_security.py` verifies invalid, injection-like, and wrong-type inputs return `False` for `check__session_id__is_valid`.

- Role-giving endpoints (nadooit_os)
  - Enforced per-customer object-level authorization on all role-giving views to prevent cross-customer role escalation (IDOR):
    - `give_customer_time_account_manager_role`
    - `give_customer_program_execution_manager_role`
    - `give_customer_program_manager_role` (also corrected decorator to `user_is_Customer_Program_Manager_and_can_give_Customer_Program_Manager_role` and avoided auto-creating the acting manager’s contract)
    - `give_employee_manager_role` (uses get-only/create-only helpers and ability-setting after per-customer authorization)
  - Service-layer fix: manager contract creation now binds to the specific `EmployeeContract(employee, customer)` rather than the first contract for the employee, preventing cross-customer binding bugs:
    - `TimeAccountManagerContract` and `EmployeeManagerContract` creation updated in `app/nadooit_os/services.py`.
  - Idempotency: manager contract creation helpers now return existing contracts instead of creating duplicates, preventing UNIQUE constraint errors:
    - `create__time_account_manager_contract__for__employee_and_customer`
    - `create__customer_program_execution_manager_contract__for__employee_and_customer`
    - `create__customer_program_manager_contract__for__employee_and__customer`
    - Tests: `app/nadooit_os/tests/test_manager_contract_helpers.py` validates helper idempotency, ability-setting gating, and get-only behaviors.
  - Tests:
    - `app/nadooit_os/tests/test_role_giving_permissions.py` (403 on cross-customer attempts and happy paths for TACM, CPEM, CPM)
    - `app/nadooit_os/tests/test_hr_permissions.py` (add-employee per-customer scoping; employee manager role: cross-customer 403 and allowed same-customer)
    - Idempotency tests to ensure duplicate POSTs create at most one manager contract for all role-giving views:
      - `app/nadooit_os/tests/test_role_giving_permissions.py::TestRoleGivingIdempotency` (TACM, CPEM, CPM)
      - `app/nadooit_os/tests/test_hr_permissions.py::test_give_employee_manager_role_idempotent` (Employee Manager)
    - Missing ability denial (403 when acting manager lacks `can_give_manager_role`):
      - `app/nadooit_os/tests/test_role_giving_permissions.py::TestRoleGivingMissingAbility` (TACM, CPEM, CPM)
    - No implicit contract creation for acting user (403 and zero side-effects when acting user lacks manager contract):
      - `app/nadooit_os/tests/test_role_giving_permissions.py::TestRoleGivingNoImplicitCreation` (TACM, CPEM, CPM)
      - `app/nadooit_os/tests/test_hr_permissions.py::test_give_employee_manager_role_no_implicit_creation_for_acting_manager` (Employee Manager)

- HR add-employee (nadooit_os)
  - Removed `@user_passes_test` to avoid 302 redirects for unauthorized users; view now requires auth via `@login_required` and returns 403 on cross-customer or missing-ability attempts using explicit in-view per-customer checks.
  - Eliminated implicit contract creation via auto-creating "get" helper. The view now uses:
    - `get_only__employee_contract__for__employee_and_customer(...)` to check existence, and
    - `create__employee_contract__for__employee_and__customer(...)` to create explicitly when absent.
  - Idempotency: duplicate POSTs create at most one `EmployeeContract`.
  - Tests updated/added:
    - `app/nadooit_os/tests/test_hr_permissions.py::test_add_employee_post_denied_for_other_customer` now expects 403.
    - `app/nadooit_os/tests/test_hr_permissions.py::test_add_employee_idempotent_double_post` ensures at most one contract is created.

  - Implementation notes:
    - Removed `@user_passes_test` from role-giving views so logged-in but unauthorized users receive 403 from explicit per-customer checks within the view logic (no 302 login redirects). Views still require authentication via `@login_required`.

- API keys (nadooit_auth, nadooit_api_key, nadooit_os)
  - Storage: API keys are stored SHA-256 hashed via `NadooitApiKey` post_save receiver; raw keys are never persisted.
  - Request helper: `get__hashed_api_key__for__request` now hashes the provided key before lookup and safely returns `None` when missing.
  - Service fix: removed an extra `save()` that could overwrite the hashed key with the raw value immediately after creation.
  - Tests added:
    - `create-api-key` view: non-managers are redirected; ApiKeyManagers can POST a key and receive a redirect with `submitted=True`; the stored key is hashed (not equal to the raw value).
    - `revoke-api-key` view: login required; POST only revokes the caller’s own active keys.
    - Verified API execution auth path remains correct: `app/nadooit_api_executions_system` tests all pass with hashed key flow.

- Contract helpers deprecation and view cleanup
  - Deprecated legacy auto-creating "get" helpers at the documentation level to prevent accidental misuse in views/authorization paths (prefer `get_only__...` + `create__...` + `set__list_of_abilities__...`). See `docs/apps-and-services.md` under `nadooit_os` for guidance.
  - Removed an unused import of `get__employee_contract__for__user_code__and__customer` from `app/nadooit_os/views.py` (no functional change).
  - Full suite re-run to verify no regressions: 196 passed, 3 skipped, 1 xfailed; coverage 71.79%.

## How to run tests locally

- Full suite with coverage:

```bash
PYTHONPATH=app python3 -m pytest -q
```

- Specific CSV export tests:

```bash
PYTHONPATH=app python3 -m pytest -q app/nadooit_os/tests/test_export_transactions.py
```

## Coverage status (latest)

- Overall coverage is above threshold (≈68%).

## Next targets

- Expand tests for additional edge cases in `nadooit_website/services.py` (unicode, sanitization, boundary conditions).
- Review other views that echo query parameters to templates and ensure escaping is covered by tests.

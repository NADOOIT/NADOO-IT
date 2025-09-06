# Security Hardening Report

Updated: 2025-08-09 13:18 CEST
Owner: Security testing and hardening initiative

## Overview
This document tracks proactive security-focused changes and tests added to the Django project. Focus areas include:
- Preventing path traversal in ZIP extraction
- Preventing spreadsheet formula injection in CSV exports
- Ensuring defensive behavior for user-controlled filtering parameters

No tests have been executed during creation, per project preference. This report will be continuously updated as changes are made.

---

## Changelog

### 2025-08-09

1) Hardened ZIP extraction and file path validation
- File: `app/nadooit_website/services.py`
- Function: `handle_uploaded_file`
- Changes:
  - Replaced bulk `extractall` with safe extraction that validates each member path within a temp directory using `os.path.commonpath`.
  - Validated and safely joined referenced paths from `video_data.json` (`preview_image`, `original_file`, HLS paths) before opening or moving files.
  - Raised `ValueError` on any unsafe path.

2) Neutralized spreadsheet formulas in CSV export
- File: `app/nadooit_os/services.py`
- Function: `get__csv__for__list_of_customer_program_executions`
- Changes:
  - Added a sanitizer that prefixes a single quote if a text value (after trimming leading whitespace) begins with one of `=`, `+`, `-`, `@`.
  - Applied sanitizer to the program name column.

3) Safer default for unknown filter types
- File: `app/nadooit_os/services.py`
- Affected flow: wrapper that filters by `payment_status="NOT_PAID"` after calling `get__customer_program_executions__for__filter_type_and_customer`.
- Changes:
  - If the inner function returns `None` (unrecognized `filter_type`), return an empty queryset to avoid downstream attribute errors.

4) Tests updated/added
- File: `app/nadooit_os/test_security.py`
  - `test_id_based_lookups_resist_sql_injection_like_inputs` (existing): Ensures ID-based lookups do not broaden results or error on injection-like strings.
  - `test_csv_export_escapes_spreadsheet_formulas` (updated): Removed xfail; now asserts sanitized output (leading single quote, not starting with formula chars).
  - `test_get_customer_program_executions_handles_unrecognized_filter_type_safely` (new): Ensures unrecognized filter types do not crash (returns `None` or queryset; wrapper further safeguards).
  - `test_csv_export_sanitizes_leading_whitespace_then_formula` (new): Verifies sanitizer triggers when formula markers follow leading whitespace.
  - `test_csv_export_benign_text_not_modified` (new): Verifies normal text remains unchanged.
 - File: `app/nadooit_website/test_security.py`
  - `test_handle_uploaded_file_blocks_zip_path_traversal` (updated): Removed xfail; now expects `ValueError` on traversal entries.
  - `test_handle_uploaded_file_blocks_absolute_path_entries` (new): Expects `ValueError` when absolute paths are present in the archive/metadata.
  
 5) Additional tests for ZIP path validation
 - File: `app/nadooit_website/test_security.py`
   - `test_handle_uploaded_file_blocks_hls_playlist_traversal` (new): Expects `ValueError` when `hls_playlist_file` references a traversal path.
   - `test_handle_uploaded_file_blocks_nested_traversal` (new): Expects `ValueError` for nested traversal like `subdir/../../evil`.
   - `test_handle_uploaded_file_allows_benign_zip` (new): Positive test ensuring benign archives process without raising.
   - `test_handle_uploaded_file_blocks_windows_style_traversal` (xfail): Documents current POSIX behavior and future hardening target for `\\` paths.

 6) Additional CSV export hardening tests (services and view)
 - File: `app/nadooit_os/test_security.py`
   - `test_csv_export_sanitizes_various_formula_prefixes` (new): Covers `+`, `-`, `@`, and whitespace-prefixed formulas.
   - `test_csv_export_leading_single_quote_remains_unchanged` (new): Ensures already-safe values are not double-prefixed.
   - `test_get_not_paid_wrapper_unknown_filter_returns_empty_queryset` (new): Asserts safe empty queryset on unknown filter.
   - `test_export_transactions_unknown_filter_returns_header_only_csv` (new): View-level check that unknown filters export only header.
   - `test_export_transactions_customer_not_found_returns_404` (new): View returns 404 for non-existent customer UUID.
   - `test_export_transactions_sanitizes_program_name_in_csv` (new): View-level CSV includes sanitized program name.

 7) Lookup helpers hardened-by-test against injection-like inputs
 - File: `app/nadooit_os/test_security.py`
   - `test_more_id_based_helpers_resist_sql_injection_like_inputs` (new): Ensures `get__employee__for__employee_id`, `get__customer_program__for__customer_program_id`, and `get__employee_contract__for__employee_contract_id` do not broaden results on injection-like strings.

 8) Authentication redirect hardening (open redirect prevention)
 - File: `app/nadooit_auth/views.py`
 - Changes:
   - Replaced insecure redirect in `login_user` with `safe_redirect`, validating targets via `url_has_allowed_host_and_scheme`.
   - Fixed a misplaced `else` that could cause unreachable code/syntax issues.
   - Helper `_is_safe_redirect` and `safe_redirect` ensure only same-host or relative paths are allowed.
 - Tests: `app/nadooit_auth/test_security.py`
   - `test_is_safe_redirect_blocks_external_host` (new)
   - `test_is_safe_redirect_allows_relative_paths` (new)
   - `test_safe_redirect_defaults_on_external_target` (new)
   - `test_safe_redirect_uses_relative_target` (new)

 9) Input sanitization for `section_transitions` view (file read safety)
 - File: `app/nadooit_website/views.py`
 - Function: `section_transitions`
 - Changes:
   - Sanitize `group_filter` from URL or query parameter with a strict slug regex (`[A-Za-z0-9_-]+`).
   - Ignore traversal attempts and serve default `section_transitions.html` when only default exists; return 404 when requested slug file is missing.
   - Added `re` import and safe file open with `FileNotFoundError` handling.
 - Tests: `app/nadooit_website/test_security.py`
   - `test_section_transitions_serves_slug_file` (new)
   - `test_section_transitions_blocks_traversal_and_falls_back_to_default` (new)
   - `test_section_transitions_missing_file_returns_404` (new)

10) Template-level XSS escaping for error messages in nadooit_os templates
- Files: `app/nadooit_os/test_security_templates.py`
- Templates covered:
  - `nadooit_os/time_account/give_customer_time_account_manager_role.html`
  - `nadooit_os/customer_program_execution/give_customer_program_execution_manager_role.html`
  - `nadooit_os/hr_department/add_employee.html`
- Rationale: Several views pass `request.GET.get("error")` into the template context. Django auto-escapes by default, but tests assert and lock in safe escaping to prevent reflected XSS via unescaped error messages.
- Tests added:
  - `test_time_account_template_escapes_error_xss` (new)
  - `test_customer_program_exec_template_escapes_error_xss` (new)
  - `test_hr_add_employee_template_escapes_error_xss` (new)

11) WhatsApp webhook echo behavior tests (document desired hardening)
- Files: `app/bot_management/test_security_whatsapp.py`
- Endpoint: `bot_management:whatsapp-webhook` (e.g., `/whatsapp/webhook/<bot_register_id>`)
- Current code echoes `hub.challenge` directly. Tests document desired hardened behavior:
  - Respond with plain text (`Content-Type: text/plain`) when `hub.challenge` is a benign token
  - Reject HTML or script content in `hub.challenge` with 400/422
  - Return 400/422 when `hub.challenge` is missing
- Tests added:
  - `test_whatsapp_webhook_echoes_challenge_as_plain_text` (new)
  - `test_whatsapp_webhook_rejects_html_in_challenge` (new)
  - `test_whatsapp_webhook_missing_challenge_returns_400` (new)

---

## Current Status
- ZIP extraction hardened with safe path validation.
- CSV export hardened against spreadsheet formula injection for program names (including leading whitespace).
- Unknown filter types handled defensively; wrapper hardened to avoid None chaining.
- Authentication redirects validated against allowed hosts/schemes to prevent open redirects.
- `section_transitions` view sanitizes filename selector and safely serves default/404 as appropriate.
- Security tests expanded: added HLS/nested traversal and benign ZIP tests; extended CSV sanitizer tests (multiple prefixes, leading quote idempotency); view-level export tests; added helper lookup injection-resistance tests; added auth redirect and `section_transitions` view tests. Tests not executed yet.
 - Template contexts confirmed to escape `error` messages; template-level XSS tests added to lock in behavior.
 - WhatsApp webhook echo behavior tested to document desired hardening (plain text echo only; reject HTML; 400/422 on missing challenge).

---

## Next Targets (Planned)
- Audit other CSV generation points (if any) and apply sanitizer consistently.
- Broaden tests for file handling (e.g., unicode edge cases, Windows `\\` normalization/explicit rejection across platforms).
- Explore other input vectors for potential injection or unsafe handling (views, query parameters, additional services).
 - Consider normalizing/backslash-sanitizing ZIP member paths to proactively block Windows-style traversal on POSIX.

---

## Appendix: Files Changed
- `app/nadooit_website/services.py` — Safe ZIP extraction and path validation
- `app/nadooit_os/services.py` — CSV sanitizer; safe default for unknown filters
- `app/nadooit_os/test_security.py` — CSV and filter tests
- `app/nadooit_website/test_security.py` — ZIP traversal test
- `app/nadooit_auth/views.py` — Safe redirect helper and login redirect hardening
- `app/nadooit_auth/test_security.py` — Auth redirect safety tests
- `app/nadooit_website/views.py` — `section_transitions` input sanitization and safe file handling
- `app/nadooit_os/test_security_templates.py` — Template XSS escaping tests
- `app/bot_management/test_security_whatsapp.py` — WhatsApp webhook echo tests


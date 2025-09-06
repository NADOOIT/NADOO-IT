# Admin Guide

This guide shows how to use the Django admin for NADOO-IT, with a focus on managing website sections, ordering, and API keys.

## Access and first-time setup
- URL: `/admin/`
- Create a superuser (first time only). From the project root with Docker Compose running:
  ```bash
  docker compose -f docker-compose-dev.yml exec app python manage.py createsuperuser
  ```
  Use the same in production against the `app` container once.

Tips
- Use the search and list filters at the top-right of admin changelists.
- Use “Save as” to clone existing objects where supported.

---

## Website content: Sections
- Model: `Section`
- Fields: `name`, `html`, optional `video`, optional `file`
- Authoring:
  - Insert `{{ video }}` in `html` where the player should appear when a video is attached.
  - Insert `{{ file }}` in `html` where a download button should appear when a file is attached.
- Admin warnings:
  - If `video` is set but `{{ video }}` is missing in `html`, the admin shows a warning on save.
  - If `{{ video }}` exists but no `video` is set, the admin also warns (same for `file`).

Videos
- Upload videos and ensure HLS playlists (480p/720p/1080) are generated/attached to the `Video` model.
- See docs/website-system.md for details.

---

## Ordering sections for the website
NADOO-IT uses `Section_Order` to define the order of sections. Ordering is managed via an inline that supports move up/down links.

Where
- Admin: `Section_Order` (registered as an admin with inline `WebsiteSectionsOrderTabularInline`).

How to create or edit an order
1. Go to Admin → Section Orders.
2. Add a new Section Order or edit an existing one.
3. In the inline list:
   - Click “Add another Section order sections through model” to add a Section.
   - Use the “move up/down” links to rearrange the order.
4. Save.

Notes
- Ordered relations use `ordered_model`; the inline provides the up/down controls.
- Sessions reference a `Section_Order`. Experiment groups can also point to a specific `Section_Order` for A/B tests.

Experiment groups
- Model: `ExperimentGroup` with fields: `name`, `section_order`, counters for `successful_sessions`/`total_sessions`.
- You can assign or rotate section orders between groups to compare engagement.

---

## Contracts & Access Control (summary)

Grant base access (visibility)
- Create an `EmployeeContract` linking the employee (user) to a customer and set `is_active=True`.
  - Admin → HR → Employee Contract → Add

Grant management rights
- On top of the base `EmployeeContract`, create the appropriate manager contract and toggle capabilities:
  - `EmployeeManagerContract` (add/delete employees)
  - `CustomerProgramManagerContract` (create/delete customer programs)
  - `CustomerProgramExecutionManagerContract` (create/delete executions)
  - `TimeAccountManagerContract` (create/delete time accounts)

End access
- Set `is_active=False` and optionally `deactivation_date` (or `end_date`) on the `EmployeeContract`.
- Review and adjust any linked manager contracts.

Troubleshooting
- User cannot see a customer’s data: ensure an active `EmployeeContract` exists for that customer.
- Manager actions disabled: verify the correct manager contract exists and the required capability booleans are set to True.

See the full guide: `docs/contracts-and-access-control.md`.

### HR admin quick tour
- Employee: core person record linked to `User`.
- Employee Contract: link Employee Customer with `is_active` and dates.
- Employee Manager Contract: grants employee management capabilities.
- Customer Manager Contract: delegation helper for customer-level roles.
- Customer Program Manager Contract: program create/delete permissions.
- Customer Program Execution Manager Contract: execution create/delete permissions.
- Time Account Manager Contract: time account create/delete permissions.

Use list filters/search in each changelist to audit who currently has rights per customer.

---

## Files
- Model: `File` for downloadable assets used in sections.
- In a Section’s `html`, place `{{ file }}` to render a download button.

---

## API keys and using the API
Models
- `NadooitApiKey` stores API keys as hashes. The plaintext API key you enter is hashed on save; the database does not store the plaintext.
- Keep a copy of the plaintext key securely outside the system if you need to reuse it.

Creating a key
1. Admin → Nadooit API Key → Add.
2. Enter a unique `api_key` (plaintext), select the `user` it belongs to, and set `is_active = True`.
3. Save. The key is hashed immediately.

Using the key
- For the current API endpoints, include the following in the JSON body (not headers):
  - `NADOOIT__API_KEY`: your plaintext key
  - `NADOOIT__USER_CODE`: the `user_code` of the user the key belongs to

Permissions and constraints
- The user must be active.
- For executing a program via API, the user must be an active employee of the program’s customer (checked via `EmployeeContract`).
- You must pass a valid `program_id` (UUID) that exists.

Troubleshooting
- 403 Invalid API Key: ensure you’re sending the plaintext key in the JSON body; the server hashes it.
- 403 User code not valid/active: confirm `NADOOIT__USER_CODE` matches the key’s user, and that user is active.
- 400 Program does not exist: verify `program_id`.
- 400 User is not an employee of the company: ensure there’s an active `EmployeeContract` linking the user to the customer that owns the program.

See also
- docs/api.md for endpoint specifics and curl examples
- docs/website-system.md for rendering logic and placeholders
- docs/contracts-and-access-control.md for the full permissions model
- docs/management-commands.md for import/export and related commands
 - docs/diagrams.md for visual overviews of contracts and UI flags

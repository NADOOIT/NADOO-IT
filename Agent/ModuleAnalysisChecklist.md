# NADOO-IT Module Analysis Checklist

This checklist tracks the analysis status of the various Django app modules within the NADOO-IT project.

## Project Overview and Root Structure

This section provides a high-level overview of the NADOO-IT project structure, including key files and directories in the project root.

**Key Root Directories & Files:**
- **`app/`**: Contains all Django apps, `manage.py`, project-level `static/` & `templates/`, SSL certs (`cert.crt`, `cert.key`), test configs (`.coveragerc`, `pytest.ini`), `video_config.json` (for video transcoding settings), and an empty nested `app/app/` directory (likely an artifact).
- **`Agent/`**: Contains this `ModuleAnalysisChecklist.md` and `DeveloperNotes.md`.
- **`.git/`, `.github/`**: Standard Git and GitHub specific files (e.g., for workflows).
- **`docker/`**: Contains subdirectories `certbot/` (for Let's Encrypt SSL certificate management) and `proxy/` (likely for reverse proxy configuration like Nginx or Traefik).
- **`data/`**: Likely for fixtures, sample data, or other data assets (contents not yet reviewed).
- **`init-db.sql/` (directory)**: An empty directory. Database initialization scripts are likely `init-db-dev.sql` and `init-db.template.sql` in the project root.

**Configuration & Environment:**
- `.env`, `.env.example`: Environment variable management.
- `.dockerignore`, `.gitignore`, `.prettierignore`: Ignore files.
- `pytest.ini`, `tox.ini`: Test runner configurations.

**Dockerization:**
- `Dockerfile`, `Dockerfile-dev-Mac`, `Dockerfile-dev-Windows`: Various Docker build files.
- Multiple `docker-compose-*.yml` files: For different deployment and development setups (MySQL, SQLite, CockroachDB).
- `Procfile`: For Heroku-like deployments.

**Dependencies:**
- `requirements.txt` (Production), `requirements-dev.txt` (Development).

**Documentation & Project Management:**
- `README.md`, `NADOOIT_Manifesto.md`, `SECURITY.md`, `TODO.md`.

**Scripts:**
- `setup.sh`, `update_script.sh`, `enable_overcommit.sh`.

**Django Apps (within `app/` directory):**
The following sections detail the status of individual Django apps.

## Core Project Files/Settings
- [x] `nadooit` (Project core, in `app/nadooit/`) - Analyzed (Contains `settings.py`, main `urls.py`, `wsgi.py`, `asgi.py` for async support, and `celery.py` indicating use of Celery for background tasks. Also includes an unusual `__init__-CPU1.py` file.)

## Analyzed Modules
- [x] `bot_management` - Analyzed
- [x] `nadoo_complaint_management` - Analyzed
- [x] `nadoo_erp` - Analyzed
- [x] `nadooit_api_executions_system` - Analyzed
- [x] `nadooit_auth` - Analyzed (User identified by `user_code`, then FIDO2 auth; critical flaws in code generation/validation, risky default password)
- [x] `nadooit_crm` - Analyzed
- [x] `nadooit_delivery` - Analyzed (Models defined but BROKEN - `Product` FK missing)
- [x] `nadooit_funnel` - Analyzed (Placeholder, no models)
- [x] `nadooit_hr` - Analyzed
- [x] `nadooit_key` - Analyzed
- [x] `nadooit_network` - Analyzed
- [x] `nadooit_os` - Analyzed (Hub module, no models, extensive views/services for other modules)
- [x] `nadooit_program` - Analyzed
- [x] `nadooit_program_ownership_system` - Analyzed
- [x] `nadooit_questions_and_answers` - Analyzed
- [x] `nadooit_time_account` - Analyzed
- [x] `nadooit_website` - Analyzed (Models reviewed, critical issues in file handling and FKs, A/B testing features)
- [x] `nadooit_workflow` - Analyzed

- [x] `nadooit_api_key` - Analyzed
  - **Models (`nadooit_api_key.models`):**
    - `NadooitApiKey`: Stores SHA256 hashed API keys (original key is a UUID by default).
    - `NadooitApiKeyManager`: Manages roles for API key permissions.
    - `post_save` signal hashes `api_key` field upon creation/update.
  - **Services (`nadooit_os.services`):**
    - `create__NadooitApiKey__for__user`: Creates key. **CRITICAL FLAW 1:** Does not return the original *unhashed* key to the caller for "show once" display, making it impossible for users to know their key. The unhashed key exists transiently but isn't passed back.
    - Helper functions for authentication: `get__hashed_api_key__for__request`, `check__nadooit_api_key__has__is_active`, `get__nadooit_api_key__for__hashed_api_key`, `get__user_code__for__nadooit_api_key`.
  - **Authentication (`nadooit_api_executions_system.views`):**
    - API key is expected in `request.data` (POST body) under `NADOOIT__API_KEY`. **CRITICAL FLAW 2 (Usability/Standard Practice):** Should use standard HTTP headers (e.g., `X-API-Key` or `Authorization: Bearer <key>`).
    - `get__hashed_api_key__for__request` service reads the raw key from `request.data`, hashes it. **Potential Bug:** Will crash if `NADOOIT__API_KEY` is missing (no `None` check before `.encode()`).
    - Authentication flow:
      1. Hash incoming key.
      2. Check if hashed key exists in DB and is active.
      3. Retrieve `NadooitApiKey` object.
      4. Compare `user_code` from key's user against `NADOOIT__USER_CODE` from `request.data`.
      5. Check if user associated with the key is active.
  - **Admin (`nadooit_api_key.admin`):** Standard admin, does not show original key.
  - **Tests (`nadooit_api_key.tests`):** Empty.
  - **Recommendations:**
    1.  Modify key creation service to return the unhashed key for "show once" display.
    2.  Change API key transmission to use HTTP headers.
    3.  Add error handling for missing API key in request.
    4.  Fix type hint for `get__nadooit_api_key__for__hashed_api_key`.
    5.  Add comprehensive tests.
    6.  Review `user_code` as a second factor: ensure this is desired and documented.

## Other Noteworthy Items in `app/` Directory (For Reference)
(These are not full Django apps but are present in the `app/` directory)
- `manage.py`: Django's command-line utility.
- `cert.crt`, `cert.key`: SSL certificates (likely for local development).
- `video_config.json`: Defines settings for video transcoding (resolutions, bitrates).
- `django_is_url_active_templatetag/`: Third-party Django app/templatetag library.
- `db/`: Typically for the development database file (e.g., `db.sqlite3`).
- `logs/`: For application log files.
- `static/`: Project-level static files.
- `templates/`: Project-level Django templates.
- `test_media/`: For media files used during testing.
- `app/` (nested and empty): An empty directory `app/app/`, likely an unused artifact.

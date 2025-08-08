# Project Structure and Components

This document explains how the NADOO-IT repository is organized, how the runtime services fit together, and what each major part (apps, services, files) does. Use this as a map when navigating the codebase or planning changes.

## TL;DR
- Django monorepo in `app/` with multiple domain apps (CRM, HR, Website CMS, etc.).
- Runtime services via Docker Compose:
  - `app` (Django web) + `celery_worker` (background jobs)
  - `proxy` (Nginx) + `certbot` (TLS)
  - `redis` (message broker)
- Default database is SQLite (simple, zero-config). CockroachDB is optional for scaling.
- Static and media files are persisted via Docker volumes; Nginx serves them directly in production.

Related docs:
- Running (Dev & Prod): `docs/running.md`
- Installation on IONOS VPS: `docs/installation-ionos-vps.md`
- Architecture overview: `docs/architecture.md`
- Apps & services catalog: `docs/apps-and-services.md`
- Database backends: `docs/database.md`
- Configuration (env): `docs/configuration.md`
- Operations (backups, updates, logs): `docs/operations.md`
- Website system: `docs/website-system.md`

---

## Repository layout (top-level)

- `app/`
  - Django project code (the project module and all domain apps live here).
  - Typical Django project files (settings, URLs, WSGI/ASGI) are within the project module inside `app/`.
  - Custom apps live under `app/<app_name>/`.
- `docs/`
  - All documentation for development, deployment, operations, and architecture.
- `docker/`
  - Docker build contexts for production proxy and certbot.
  - `docker/proxy/` – Nginx config and supporting files.
  - `docker/certbot/` – Scripts and files used by Certbot for certificate issuance/renewal.
- `docker-compose-dev.yml`
  - Development stack (HTTPS dev server via `runserver_plus`, live code mounting, Redis, Celery worker).
- `docker-compose.deploy.yml` and `docker-compose-deploy.yml`
  - Production stack (uWSGI behind Nginx, Certbot, Redis, Celery worker, persisted static/media volumes).
- `Dockerfile` / `Dockerfile-dev`
  - Base images for production and development respectively.
  - Install system deps (e.g., ffmpeg), Python deps, create Django user, and set up directories and permissions.
- `requirements.txt` / `requirements-dev.txt`
  - Python dependencies for production and development.
- `.env.example`
  - Template of required/optional environment variables (copy to `.env` and populate).
- `readme.md`
  - Root project README; links to docs and high-level guidance.
- `setup.sh`, `update_script.sh`
  - Helper scripts to bootstrap or update deployments (see `docs/operations.md`).
- `Procfile`
  - Process declaration (useful for platforms that honor Procfiles).

---

## Runtime services and how they interact

The application is composed of several containers that work together. These are defined in the Docker Compose files.

- Web application (`app`)
  - Dev: runs Django via `runserver_plus` with a self-signed cert (HTTPS on port 8000), hot-reloading, and mounted source code.
  - Prod: runs Django via `uWSGI` (socket :9090) for performance and stability.
  - Reads configuration from environment variables (see `docs/configuration.md`).
  - Serves the REST API and the admin; business logic lives in Django apps under `app/`.
- Background worker (`celery_worker`)
  - Executes asynchronous/background jobs using Celery.
  - Shares the same Django codebase and environment as the web app container.
  - Uses Redis as the message broker (see `CELERY_BROKER_URL`).
- Message broker (`redis`)
  - Lightweight broker for Celery queues; no persistent storage is required.
- Reverse proxy (`proxy`)
  - Nginx terminates TLS, serves static and media files, and forwards dynamic requests to the Django uWSGI socket.
  - In dev, the proxy is not used; the dev app serves directly over HTTPS on :8000.
- Certificate manager (`certbot`)
  - Works with Nginx to obtain and renew Let’s Encrypt certificates.
  - Uses mounted volumes for certs and webroot challenges.

Data flow in production (simplified):
1. Client (browser/API) -> Nginx (`proxy`) over HTTPS.
2. Static/media: served by Nginx from volumes.
3. Dynamic requests: Nginx -> uWSGI socket (:9090) -> Django (`app`).
4. Long-running/background work: web app enqueues a Celery task -> Redis -> `celery_worker` executes.

---

## Storage and persistence

- Static files: collected into a volume and served by Nginx in production.
- Media files (uploads, videos): stored in a dedicated volume and served directly by Nginx.
- Database:
  - Default: SQLite (simple, zero external dependencies). Recommended for small deployments and ease of setup.
  - Optional: CockroachDB for scaling. Enable via environment variables and mount the CockroachDB CA cert when required. See `docs/database.md` and `docs/configuration.md`.

For production persistence and backups, see `docs/operations.md` and `docs/installation-ionos-vps.md`.

---

## Django project and apps

The Django code lives under `app/`. Within it you’ll find the project module (settings, URLs, WSGI/ASGI) and a set of domain apps. Below is a high-level purpose summary for the custom apps (see also `docs/apps-and-services.md` for more details):

- `nadooit_auth` – Custom user model and authentication flows (AUTH_USER_MODEL).
- `nadooit_api_key` – API key issuance and verification for programmatic access.
- `nadooit_crm` – CRM entities such as customers/contacts and related relations.
- `nadooit_hr` – Human resources: employees, roles, contracts, permissions.
- `nadooit_time_account` – Time balance and billing for digital workers: tracks purchased (prepaid) time remaining and consumed time owed (postpaid); supports recharge/billing and consumption records.
- `nadooit_workflow` – Generic workflow/state machine utilities.
- `nadooit_network` – Relationship graphs and cross-entity connections.
- `nadooit_program` – Program and project management primitives.
- `nadooit_program_ownership_system` – Ownership and permissioning around programs.
- `nadooit_api_executions_system` – Tracking and managing API executions.
- `nadooit_website` – Public website CMS (section-based pages; video/file embeds). See `docs/website-system.md`.
- `nadooit_os` – OS-level utilities/integrations used across apps.
- `nadooit_key` – Key and credential management helpers.
- `nadooit_questions_and_answers` – Q&A and knowledge features.
- `nadoo_complaint_management` – Complaint/ticket management.
- `bot_management` – Bot/automation management (scripts, schedulers, etc.).
- `nadoo_erp` – ERP functionality (e.g., finance/inventory). Often uses `djmoney` for currency/money fields.

Third‑party and Django contrib apps are installed via `requirements*.txt` (e.g., Django REST Framework, crispy-forms, htmx integration, MFA, admin UI enhancers).

Background jobs for any app should be implemented in `tasks.py` and executed by the Celery worker.

---

## Environments: development vs. production

- Development (`docker-compose-dev.yml`):
  - Rapid iteration: live-reload, mounted source, auto-migrations/collectstatic on startup.
  - HTTPS on :8000 with a dev cert via `runserver_plus`.
  - Local Redis & Celery worker for testing async tasks.

- Production (`docker-compose.deploy*.yml`):
  - uWSGI for Django, Nginx TLS termination, Certbot for certificates.
  - Static/media volumes served directly by Nginx.
  - Redis & Celery worker for background tasks.
  - See `docs/installation-ionos-vps.md` for end-to-end server setup and first deploy.

---

## Where to add/change things

- New API endpoints
  - Add DRF viewsets/views and serializers in the relevant app.
  - Wire URLs in the project’s `urls.py` or the app’s `urls.py` included by the project.
  - Document endpoints in `docs/api.md`.

- New domain feature
  - Create a new Django app under `app/<your_app>/` (models, admin, views, serializers, tasks).
  - Register the app in `INSTALLED_APPS` (project settings) and create migrations.

- Background/async work
  - Put logic in `tasks.py` within the relevant app.
  - Ensure Celery can import and discover tasks; update beat/schedules if needed.

- Website content (sections)
  - Use the management commands to export/import section templates for the section-based CMS. See `docs/website-system.md`.

- Configuration
  - Add environment variables in settings as needed; update `docs/configuration.md` and `.env.example`.

---

## Operational notes

- Logs & monitoring: see `docs/operations.md` for viewing logs (`docker compose logs`), updating, and maintenance.
- TLS & domains: `proxy` + `certbot` handle HTTPS; ensure `DOMAIN` and `ACME_DEFAULT_EMAIL` are configured.
- Database selection: default SQLite. Switch to CockroachDB by setting the Cockroach env vars and mounting the CA cert when applicable.
- Troubleshooting: see `docs/troubleshooting.md` for common issues (TLS, CSRF, media, migrations, Celery, etc.).

---

## See also
- Architecture overview: `docs/architecture.md`
- Apps and services catalog: `docs/apps-and-services.md`
- Running the system: `docs/running.md`
- Installation (IONOS VPS): `docs/installation-ionos-vps.md`
- API reference: `docs/api.md`

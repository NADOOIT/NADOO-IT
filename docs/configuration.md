# Configuration

This page centralizes environment variables and configuration knobs used by NADOO-IT.

Overview
- All configuration is provided via environment variables (loaded from `.env` in development)
- Defaults are safe for local development; production requires explicit values for security and domains
- Database backend selection is automatic based on environment (see below)

Core Django
- `DJANGO_SECRET_KEY` (required)
  - Strong random string; regenerate for production
- `DJANGO_DEBUG` (`1` for dev, `0` for prod)
- `DJANGO_ALLOWED_HOSTS` (prod)
  - Comma-separated list of hostnames (e.g., `example.com,www.example.com`)
- `DJANGO_CSRF_TRUSTED_ORIGINS` (prod)
  - Include scheme (e.g., `https://example.com,https://www.example.com`)

Database selection
- Logic (from `app/nadooit/settings.py`):
  1) If `COCKROACH_DB_HOST` is set → CockroachDB
  2) Else if `DB_BACKEND=mysql` → MySQL
  3) Else → SQLite (default)

SQLite (default)
- No DB env vars needed
- File path: `BASE_DIR/db.sqlite3` (inside containers `/app/db.sqlite3`)
- For production persistence, bind‑mount the file (see `docs/database.md`)

CockroachDB (optional)
- `COCKROACH_DB_HOST`
- `COCKROACH_DB_NAME`
- `COCKROACH_DB_PORT` (e.g., 26257)
- `COCKROACH_DB_USER`
- `COCKROACH_DB_PASSWORD`
- `COCKROACH_DB_OPTIONS` (e.g., `--cluster=<cluster>`)
- CA certificate `root.crt` must be available at `/home/django/.postgresql/root.crt` inside containers

MySQL (legacy)
- `DB_BACKEND` must be `mysql`
- `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_HOST`, `MYSQL_PORT`

Messaging & background jobs
- `CELERY_BROKER_URL` (default set in compose to `redis://redis:6379/0`)

Proxy & certificates (production)
- `DOMAIN` (used by the Nginx proxy)
- `ACME_DEFAULT_EMAIL` (Let’s Encrypt contact)

Application‑specific
- `OPENAI_API_KEY` (optional)
- `NADOOIT__API_KEY` (required for certain API calls)
- `NADOOIT__USER_CODE` (required for certain API calls)

Tips
- Keep `.env` out of version control
- Use different secrets for dev and prod
- After changing DB settings, run `python manage.py migrate`

See also
- Running guide: `docs/running.md`
- Database backends: `docs/database.md`
- Operations (updates, backups): `docs/operations.md`

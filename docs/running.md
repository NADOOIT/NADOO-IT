# Running NADOO-IT (Dev & Production)

This guide explains how to run NADOO-IT locally for development and how to deploy it to production.
If you run into issues, see the [Troubleshooting guide](troubleshooting.md).
If you are deploying on an IONOS VPS, follow the dedicated guide: [Installation on IONOS VPS](installation-ionos-vps.md).

NADOO-IT is a Django application with:
- Celery worker for async jobs
- Redis as the Celery broker
- Database: SQLite by default; CockroachDB optional (enable via env), MySQL supported. See [Database backends](database.md) for details.
- Nginx + Certbot for HTTPS in production

Compose files are provided (choose per scenario):
- `docker-compose-dev.yml` – local development (SQLite default)
  - OS/DB variants: `docker-compose-dev-MAC_SQLite.yml`, `docker-compose-dev-WIN_SQLite.yml`, `docker-compose-dev-MAC_MYSQL.yml`, `docker-compose-dev-WIN_MYSQL.yml`, `docker-compose-dev-MAC_COCKROACHDB.yml`, `docker-compose-dev-WIN_COCKROACHDB.yml`
- Production: `docker-compose-deploy-SQLite.yml` (default), `docker-compose-deploy-CockroachDB.yml`, or `docker-compose-deploy-MySQL.yml`

DB options (dev and prod):
- SQLite: primary for development; fastest and simplest to run.
- CockroachDB: mostly works and is recommended when you need horizontal scalability; ensure TLS root.crt is mounted.
- MySQL: should be fine; choose if your infra or integrations prefer MySQL.

Quickstart (local development)
```bash
docker compose -f docker-compose-dev.yml build
docker compose -f docker-compose-dev.yml up
# In another terminal
docker compose -f docker-compose-dev.yml run --rm app python manage.py createsuperuser
```
Visit https://localhost:8000 (accept the self-signed certificate). Admin at https://localhost:8000/admin.

Legacy note: `docker-compose-deploy.yml` (MySQL + WordPress) exists from earlier setups. Prefer `docker-compose-deploy-SQLite.yml` by default or `docker-compose-deploy-CockroachDB.yml` when scaling; use `docker-compose-deploy-MySQL.yml` only if you specifically need MySQL.

---

## 1) Common prerequisites

- Docker
- Docker Compose
- A `.env` file at the repository root with required environment variables (examples below)

If you use CockroachDB Cloud, download the CA certificate (root.crt) from their UI and place it on the host system. The containers expect to find it in `/home/django/.postgresql/root.crt` (inside containers). See the volume mapping instructions below.

---

## 2) Environment variables

NADOO-IT reads configuration from environment variables. At minimum you’ll need:
For a complete list and explanations, see the [Configuration guide](configuration.md).

- Django
  - `DJANGO_SECRET_KEY` – generate a strong key
  - `DJANGO_DEBUG` – `1` for dev, `0` for prod
  - `DJANGO_ALLOWED_HOSTS` – comma-separated list of hosts (prod)
  - `DJANGO_CSRF_TRUSTED_ORIGINS` – must include scheme, e.g. `https://example.com`
- SQLite (default)
  - No DB env required; the SQLite file lives at `BASE_DIR/db.sqlite3` (in dev this is `app/db.sqlite3` on your host)
- CockroachDB (optional)
  - `COCKROACH_DB_HOST`
  - `COCKROACH_DB_NAME`
  - `COCKROACH_DB_PORT`
  - `COCKROACH_DB_USER`
  - `COCKROACH_DB_PASSWORD`
  - `COCKROACH_DB_OPTIONS` – the `options` portion from CockroachDB’s connection string (e.g. `--cluster=<your-cluster>`) 
- Redis
  - No env required by default; broker URL is set in compose (`redis://redis:6379/0`)
- Optional app-specific
  - `OPENAI_API_KEY` (optional)
  - `NADOOIT__API_KEY`, `NADOOIT__USER_CODE` (required for certain API calls)
- Production proxy + certs
  - `DOMAIN` – your public domain (used by the proxy)
  - `ACME_DEFAULT_EMAIL` – for Let’s Encrypt/Certbot

Example .env for development (SQLite default):

```env
# Django
DJANGO_SECRET_KEY=change-me-dev
DJANGO_DEBUG=1
# For dev you can leave this empty or set to localhost
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
# If using HTTPS locally, include scheme. Otherwise leave blank.
DJANGO_CSRF_TRUSTED_ORIGINS=https://localhost

# Optional
OPENAI_API_KEY=
NADOOIT__API_KEY=
NADOOIT__USER_CODE=

# Domain used by docker-compose-dev.yml for ALLOWED_HOSTS mapping
DOMAIN=localhost
```

If you enable CockroachDB in development, add the following to your `.env` and ensure the Cockroach CA `root.crt` is mounted as described below:

```env
# CockroachDB (from Cockroach Cloud parameters)
COCKROACH_DB_HOST=<host>
COCKROACH_DB_NAME=<db_name>
COCKROACH_DB_PORT=26257
COCKROACH_DB_USER=<user>
COCKROACH_DB_PASSWORD=<password>
COCKROACH_DB_OPTIONS=--cluster=<cluster_name>
```

Example .env for production (SQLite by default; add Cockroach vars only if enabling Cockroach):

```env
# Django
DJANGO_SECRET_KEY=<secure-generated-key>
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=example.com,www.example.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://example.com,https://www.example.com

# CockroachDB (only if enabling Cockroach in production)
# COCKROACH_DB_HOST=<host>
# COCKROACH_DB_NAME=<db_name>
# COCKROACH_DB_PORT=26257
# COCKROACH_DB_USER=<user>
# COCKROACH_DB_PASSWORD=<password>
# COCKROACH_DB_OPTIONS=--cluster=<cluster_name>

# Optional
OPENAI_API_KEY=
NADOOIT__API_KEY=
NADOOIT__USER_CODE=

# Proxy / certificates
DOMAIN=example.com
ACME_DEFAULT_EMAIL=admin@example.com
```

---

## 3) Running in Development

Compose file: `docker-compose-dev.yml`

Services:
- `app` – Django dev server with HTTPS (runserver_plus)
- `redis` – message broker for Celery
- `celery_worker` – background worker

Notes about HTTPS in dev:
- The `app` service uses `runserver_plus` with `--cert-file cert.cer` and `--key-file key.pem`. Self-signed certs may be generated automatically on first run. If this fails on your platform, you can remove the SSL flags and use plain HTTP, or generate certs manually inside the container.

Notes about CockroachDB CA certificate mapping:
- The compose maps a host folder into the container’s `/home/django/.postgresql/`.
- On Windows the mapping is defined in the compose with `%USERPROFILE%\AppData\Roaming\postgresql\`.
- On macOS/Linux, you can create `~/.postgresql/root.crt` and adjust the volume mapping if needed to mount `$HOME/.postgresql:/home/django/.postgresql/`.

Steps:
1) Create `.env` at the repository root (use the dev example above).
2) (If using CockroachDB Cloud) Place `root.crt` on the host so the container can read it under `/home/django/.postgresql/root.crt`.
3) Build images:
   ```bash
   docker compose -f docker-compose-dev.yml build
   ```
4) Initialize the database and seed content:
   ```bash
   docker compose -f docker-compose-dev.yml run --rm app python manage.py makemigrations
   docker compose -f docker-compose-dev.yml run --rm app python manage.py migrate
   docker compose -f docker-compose-dev.yml run --rm app python manage.py import_templates
   docker compose -f docker-compose-dev.yml run --rm app python manage.py createsuperuser
   ```
5) Start the stack:
   ```bash
   docker compose -f docker-compose-dev.yml up
   ```
6) Open the app in your browser:
   - https://localhost:8000 (accept the self-signed certificate)
   - Admin: https://localhost:8000/admin

Celery logs:
```bash
docker compose -f docker-compose-dev.yml logs -f celery_worker
```

Stop the stack:
```bash
docker compose -f docker-compose-dev.yml down
```

---

## 4) Running in Production (default: SQLite; Cockroach optional)

Choose a compose file:
- `docker-compose-deploy-SQLite.yml` (default)
- `docker-compose-deploy-CockroachDB.yml`
- `docker-compose-deploy-MySQL.yml`

Services:
- `app` – Django app
- `proxy` – Nginx reverse proxy terminating TLS via Let’s Encrypt
- `certbot` – obtains/renews certificates
- `redis` – broker for Celery
- `celery_worker` – background worker

Host file/volume expectations:
- If using Cockroach: `/home/nadooserver/.postgresql/root.crt` should exist on the host (or adjust the mapping) so the `app` container can verify CockroachDB TLS.
- If using SQLite: no DB certificate is required. Note: by default, the SQLite DB file (`/app/db.sqlite3`) lives inside the container. To persist it across container rebuilds, add a bind mount in `docker-compose-deploy-SQLite.yml`, e.g. `- /opt/nadooit/sqlite/db.sqlite3:/app/db.sqlite3`.

Steps:
1) Create `.env` at the repository root using the production example above.
2) If enabling Cockroach, place `root.crt` at `/home/nadooserver/.postgresql/root.crt` on the host (or update the compose volume mapping to match your environment). For SQLite, skip this step.
3) Build images:
   ```bash
   docker compose -f docker-compose-deploy-SQLite.yml build
   ```
4) Initialize/validate certificates (first run):
   ```bash
   docker compose -f docker-compose-deploy-SQLite.yml run --rm certbot /opt/certify-init.sh
   ```
5) Run database migrations and collect static files:
   ```bash
   docker compose -f docker-compose-deploy-SQLite.yml run --rm app python manage.py migrate
   docker compose -f docker-compose-deploy-SQLite.yml run --rm app python manage.py collectstatic --noinput
   docker compose -f docker-compose-deploy-SQLite.yml run --rm app python manage.py import_templates
   docker compose -f docker-compose-deploy-SQLite.yml run --rm app python manage.py createsuperuser
   ```
6) Start the stack:
   ```bash
   docker compose -f docker-compose-deploy-SQLite.yml up -d
   ```
7) Access the site at:
   - https://<your-domain>
   - Admin: https://<your-domain>/admin

Update procedure:
```bash
git stash
git pull

docker compose -f docker-compose-deploy-SQLite.yml build

docker compose -f docker-compose-deploy-SQLite.yml run --rm app python manage.py migrate

docker compose -f docker-compose-deploy-SQLite.yml run --rm app python manage.py collectstatic --noinput

docker compose -f docker-compose-deploy-SQLite.yml run --rm app python manage.py import_templates

docker compose -f docker-compose-deploy-SQLite.yml down

docker compose -f docker-compose-deploy-SQLite.yml up -d
```

Logs & troubleshooting:
```bash
docker compose -f docker-compose-deploy-SQLite.yml logs -f proxy
```
- Ensure `DJANGO_ALLOWED_HOSTS` is a comma-separated list (no spaces) and that `DJANGO_CSRF_TRUSTED_ORIGINS` includes scheme (e.g. `https://example.com`).
- If CockroachDB TLS verification fails, verify `root.crt` is present in the mapped host path and the hostname in your DB host matches the certificate.

---

## 5) Alternative (legacy) MySQL stack

If you intentionally choose the MySQL-based stack, use `docker-compose-deploy.yml`. This compose defines an additional `db` (MySQL) and `wordpress` service and expects the following envs:
- `MYSQL_ROOT_PASSWORD`, `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`

The `setup.sh` script currently prompts for MySQL variables but uses `docker-compose.deploy.yml`. Prefer the CockroachDB compose unless your environment requires MySQL.

---

## 6) Post-setup tasks

- Log into the admin and configure initial data
- If using the Nadooit Website features, keep `sections_templates` synced:
  ```bash
  # export from DB to templates folder
  docker compose -f docker-compose-dev.yml run --rm app python manage.py export_templates
  # import from templates folder to DB
  docker compose -f docker-compose-dev.yml run --rm app python manage.py import_templates
  ```
- Set up monitoring/alerts as needed

If anything in this guide is unclear or you encounter issues, please open an issue and include logs and environment details.

# Operations (Backups, Updates, Logs & Monitoring)

This guide covers routine operations for NADOO-IT in production: backing up and restoring data, applying updates, and viewing logs.

---

## 1) Backups

What to back up:
- Application database
  - SQLite (default): the file at `/app/db.sqlite3` inside the app container (bind-mount it in compose for easier persistence)
  - CockroachDB (optional): use Cockroach’s managed backups or `BACKUP` SQL to cloud storage
- Uploaded media: `/vol/web/media/`
- Collected static: `/vol/web/static/` (can be re-built, but backing up is cheap)

SQLite backup (recommended):
1) Stop the app briefly (or ensure the app is quiescent):
   ```bash
   docker compose -f docker-compose.deploy.yml stop app
   ```
2) Copy the DB file from the container volume. If you bind-mount the file (recommended), copy it from the host path you mounted, e.g. `/opt/nadooit/sqlite/db.sqlite3`. If not bind-mounted, you can run a one-off container to stream the file:
   ```bash
   docker compose -f docker-compose.deploy.yml run --rm app sh -lc 'cat /app/db.sqlite3' > db.sqlite3.backup
   ```
3) Restart the app:
   ```bash
   docker compose -f docker-compose.deploy.yml start app
   ```

Static/media backup via one-off container (shares named volumes):
```bash
# Static files
docker compose -f docker-compose.deploy.yml run --rm app sh -lc 'tar czf - /vol/web/static' > static_backup.tgz
# Media files
docker compose -f docker-compose.deploy.yml run --rm app sh -lc 'tar czf - /vol/web/media' > media_backup.tgz
```

CockroachDB backups:
- CockroachDB Cloud: configure automated backups in the Cockroach UI to a cloud bucket (recommended)
- Self-hosted: use SQL (example):
  ```sql
  BACKUP INTO 's3://your-bucket/your-prefix?AWS_ACCESS_KEY_ID=...&AWS_SECRET_ACCESS_KEY=...';
  ```
  See Cockroach docs for exact URI formats and permissions.

Restore (SQLite):
1) Stop the app: `docker compose -f docker-compose.deploy.yml stop app`
2) Replace `/app/db.sqlite3` with your backup (prefer a bind mount so you can copy to the host path)
3) Restore static/media tarballs if needed:
   ```bash
   cat static_backup.tgz | docker compose -f docker-compose.deploy.yml run --rm app sh -lc 'tar xzf - -C /'
   cat media_backup.tgz  | docker compose -f docker-compose.deploy.yml run --rm app sh -lc 'tar xzf - -C /'
   ```
4) Start the app: `docker compose -f docker-compose.deploy.yml start app`

---

## 2) Updates (Deploying new versions)

A typical update flow (also shown in `docs/running.md`):
```bash
# Save local changes, then pull
git stash
git pull

# Rebuild images
docker compose -f docker-compose.deploy.yml build

# Run migrations/collectstatic/import templates
docker compose -f docker-compose.deploy.yml run --rm app python manage.py migrate
docker compose -f docker-compose.deploy.yml run --rm app python manage.py collectstatic --noinput
docker compose -f docker-compose.deploy.yml run --rm app python manage.py import_templates

# Restart services if needed
docker compose -f docker-compose.deploy.yml up -d
```

First-time TLS setup:
```bash
docker compose -f docker-compose.deploy.yml run --rm certbot /opt/certify-init.sh
```

---

## 3) Logs

Follow logs in production:
```bash
# Django app (uWSGI)
docker compose -f docker-compose.deploy.yml logs -f app
# Celery worker
docker compose -f docker-compose.deploy.yml logs -f celery_worker
# Proxy (Nginx)
docker compose -f docker-compose.deploy.yml logs -f proxy
# Certbot
docker compose -f docker-compose.deploy.yml logs -f certbot
# Redis
docker compose -f docker-compose.deploy.yml logs -f redis
```

Development logs:
```bash
# App
docker compose -f docker-compose-dev.yml logs -f app
# Celery
docker compose -f docker-compose-dev.yml logs -f celery_worker
```

---

## 4) Monitoring & Health

- Proxy (Nginx) access/error logs are available via the `proxy` service logs
- Celery worker logs show task execution; consider alerting on repeated failures
- If you need additional monitoring, consider integrating an external APM/logging stack (e.g., Prometheus/Grafana, Loki, or a hosted provider)
- Debug Toolbar is only enabled in development (`DJANGO_DEBUG=1`)

---

## 5) Certificates (Let’s Encrypt)

- First run: initialize with `certify-init.sh` as shown above
- Renewals are handled by the `certbot` container image; if needed, you can re-run the init step to repair certificates
- Certificates and web roots are stored in named volumes mounted into `proxy` and `certbot` services

---

## 6) Tips & gotchas

- Database choice: SQLite by default. Enable CockroachDB only when configured; verify TLS CA (`root.crt`) is mounted at `/home/django/.postgresql/root.crt`
- Persist the SQLite DB by bind-mounting `/app/db.sqlite3` to a path on the host (see `docs/database.md`)
- Always run `migrate` after pulling new code
- For video playback, ensure `.m3u8` playlists are reachable; check CORS and content types in the browser network tab

See also
- Running guide: `docs/running.md`
- Database backends: `docs/database.md`
- Architecture overview: `docs/architecture.md`
- Apps & services: `docs/apps-and-services.md`
- Website system: `docs/website-system.md`

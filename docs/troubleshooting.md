# Troubleshooting

Common issues and fixes for running and deploying NADOO-IT.

---

## 1) CockroachDB TLS / CA certificate errors
Symptoms:
- Connection errors on startup when enabling CockroachDB
- Errors mention TLS, certificate verification, or hostname mismatch

Fix:
- Download `root.crt` from CockroachDB Cloud
- Ensure it is mounted into containers at `/home/django/.postgresql/root.crt`
- Dev compose (Windows mapping example): `%USERPROFILE%\AppData\Roaming\postgresql\root.crt:/home/django/.postgresql/root.crt`
- Prod compose default expects host path like `/home/nadooserver/.postgresql/root.crt`; adjust if needed

---

## 2) Self‑signed HTTPS in development
Symptoms:
- Browser warns about self‑signed certificate on https://localhost:8000

Fix:
- Accept the self‑signed certificate for local dev
- Or remove SSL flags from the dev server by editing `docker-compose-dev.yml` to run plain `runserver` (not recommended for production)

---

## 3) CSRF trusted origins / allowed hosts
Symptoms:
- `403 CSRF verification failed`
- Errors referencing `ALLOWED_HOSTS` or missing scheme in CSRF origins

Fix:
- Set `DJANGO_ALLOWED_HOSTS` to include your domain(s); comma‑separated
- Set `DJANGO_CSRF_TRUSTED_ORIGINS` to include scheme, e.g. `https://example.com,https://www.example.com`

---

## 4) Static or media not served in production
Symptoms:
- CSS/JS missing; 404 for assets; images don’t load

Fix:
- Ensure `docker-compose.deploy.yml` mounts `static_data` and `media_data` to both `app` and `proxy`
- Run `python manage.py collectstatic --noinput`
- Confirm Nginx serves `/static/` and `/media/` from mounted volumes

---

## 5) Video playback (HLS) problems
Symptoms:
- Video player appears but doesn’t play
- 404 or CORS errors for `.m3u8` or `.ts`

Fix:
- Verify 480p/720p/1080p HLS playlists exist and URLs resolve
- Check correct content types are served by the web server
- Inspect Network tab for CORS and 404s

---

## 6) SQLite persistence across deployments
Symptoms:
- Data disappears after rebuilding containers

Fix:
- Bind‑mount the SQLite file in production, e.g.
  ```yaml
  services:
    app:
      volumes:
        - /opt/nadooit/sqlite/db.sqlite3:/app/db.sqlite3
  ```

---

## 7) Migrations / ‘no such table’ errors
Symptoms:
- `OperationalError: no such table` or missing columns

Fix:
- Run migrations: `python manage.py migrate`
- Check logs for model changes; ensure you’ve built images and restarted services

---

## 8) Large uploads rejected
Symptoms:
- Nginx responds with 413 Request Entity Too Large

Fix:
- Increase `client_max_body_size` in the Nginx proxy config under `docker/proxy` and rebuild the proxy container

---

## 9) Celery tasks not executing
Symptoms:
- Work expected in the background does not run

Fix:
- Ensure `redis` and `celery_worker` services are up
- Follow logs: `docker compose -f docker-compose.deploy.yml logs -f celery_worker`
- Verify tasks exist in the codebase and are imported on startup

See also
- Running guide: `docs/running.md`
- Database backends: `docs/database.md`
- Operations: `docs/operations.md`
- Architecture: `docs/architecture.md`

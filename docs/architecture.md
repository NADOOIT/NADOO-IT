# Architecture Overview

This document provides a high-level overview of the NADOO-IT system architecture across development and production.

Components
- Django application (WSGI)
  - Runs with `runserver_plus` in development (HTTPS self-signed)
  - Runs behind uWSGI in production (see `Dockerfile` and `docker-compose.deploy.yml`)
  - Templates include Video.js and PWA meta in `nadooit_website/base.html`
- Redis (message broker)
  - Used by Celery worker for background jobs
- Celery worker
  - Started with `python -m celery -A nadooit worker --loglevel=info`
- Database
  - SQLite by default (simple, zero-config)
  - CockroachDB optional (enable via env vars)
  - MySQL supported as legacy alternative
- Reverse proxy + TLS
  - Nginx container terminates TLS and serves static/media in production
  - Certbot container obtains/renews certificates

Runtime by environment
- Development (`docker-compose-dev.yml`)
  - `app`: builds from `Dockerfile-dev`, runs migrations and `runserver_plus` with HTTPS
  - `redis`: broker
  - `celery_worker`: runs the Celery worker
- Production (`docker-compose.deploy.yml`)
  - `app`: builds from `Dockerfile` and runs uWSGI
  - `proxy`: Nginx reverse proxy (TLS termination)
  - `certbot`: certificate provisioning/renewal
  - `redis` and `celery_worker`

Static and media
- `STATIC_URL = "/static/static/"` → `STATIC_ROOT = "/vol/web/static/"`
- `MEDIA_URL = "/static/media/"` → `MEDIA_ROOT = "/vol/web/media/"`
- Production compose mounts named volumes for persistence and maps the same into `proxy` for direct serving.

Request flow (production)
1. Client → HTTPS → `proxy` (Nginx)
2. `proxy` → uWSGI socket (`app`)
3. Django handles request, renders templates
4. Static/media are served by Nginx from mounted volumes

Video and file embedding (website)
- Video: HLS playlists (480p/720p/1080p) injected via `process_video()` → `video_embed.html` with Video.js quality selector
- File: download button injected via `process_file()` → `file_download_button.html`

Security & config
- `DJANGO_ALLOWED_HOSTS` must include your domain(s)
- `DJANGO_CSRF_TRUSTED_ORIGINS` must include scheme, e.g. `https://example.com`
- CockroachDB TLS verification relies on `root.crt` mounted to `/home/django/.postgresql/root.crt` when enabled

Where to go next
- Running the system: `docs/running.md`
- Database choices and enabling Cockroach: `docs/database.md`
- Website system details: `docs/website-system.md`
- Apps and services catalog: `docs/apps-and-services.md`

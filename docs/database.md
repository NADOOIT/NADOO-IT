# Database Backends

NADOO-IT defaults to SQLite in all environments for simplicity. CockroachDB is supported as an optional, scalable backend. MySQL is supported as a legacy alternative.

Quick summary
- Default: SQLite (no env vars required)
- Optional: CockroachDB (enable via env vars, requires CA certificate)
- Legacy: MySQL (set DB_BACKEND=mysql and provide env vars)

Selection logic (from `app/nadooit/settings.py`)
- If `COCKROACH_DB_HOST` is set (non-empty) → use CockroachDB
- Else if `DB_BACKEND=mysql` → use MySQL
- Else → use SQLite

SQLite
- Pros: zero config, fast for single-node deployments, file-based
- Path: `BASE_DIR/db.sqlite3` (inside the `app` container this is `/app/db.sqlite3`)
- Production persistence: add a bind mount in `docker-compose-deploy-SQLite.yml` so the DB file survives container rebuilds, e.g.
  ```yaml
  services:
    app:
      volumes:
        - /opt/nadooit/sqlite/db.sqlite3:/app/db.sqlite3
  ```
- Backups: stop the app or ensure it’s quiescent, then copy the file

CockroachDB (optional)
- Use when you need horizontal scalability and high availability
- Required env vars (typical Cockroach Cloud parameters):
  - `COCKROACH_DB_HOST`
  - `COCKROACH_DB_NAME`
  - `COCKROACH_DB_PORT` (usually 26257)
  - `COCKROACH_DB_USER`
  - `COCKROACH_DB_PASSWORD`
  - `COCKROACH_DB_OPTIONS` (the `--cluster=<cluster>` part from their connection params)
- CA certificate: download `root.crt` from Cockroach Cloud and ensure it is mounted inside containers at `/home/django/.postgresql/root.crt`.
  - In dev compose, the mapping is platform-specific (Windows `%USERPROFILE%`, adjust as needed on macOS/Linux)
  - In prod compose, the host path is `/home/nadooserver/.postgresql/root.crt` by default; adjust to your environment if needed
- Migration planning: A future migration script will streamline moving from SQLite to CockroachDB. Track this in the planned GitHub issue.

MySQL (legacy)
- Enable via `DB_BACKEND=mysql`
- Env vars:
  - `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_HOST`, `MYSQL_PORT`
- Driver: ensure `mysqlclient` (or supported alternative) is available in `requirements.txt`

Notes
- Regardless of backend, run `python manage.py migrate` after configuration changes
- Verify DB connectivity in logs on startup; for Cockroach, TLS/hostname verification issues typically indicate a CA certificate path problem

Dev or Prod: You can run any of the three backends in development or production. SQLite is our primary development option (fastest). CockroachDB mostly works and is recommended when you need scalability. MySQL should be fine if your infrastructure prefers it.

See also
- Running guide: `docs/running.md`
- Architecture overview: `docs/architecture.md`
- Apps and services: `docs/apps-and-services.md`

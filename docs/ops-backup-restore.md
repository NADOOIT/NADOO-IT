# Backup & Restore (SQLite + Media)

This guide shows exactly how to back up and restore the default SQLite database and uploaded media on the production server.

Assumptions
- You deploy with Docker Compose using `docker-compose-deploy-SQLite.yml` by default.
- If you use CockroachDB or MySQL in production, substitute `docker-compose-deploy-CockroachDB.yml` or `docker-compose-deploy-MySQL.yml` accordingly.
- SQLite is the default DB (CockroachDB is optional and documented elsewhere).
- App container stores the DB at `/app/db.sqlite3` (per `settings.py`).

Tip: Minimal downtime. Stopping the `app` container for a few seconds ensures a clean SQLite copy without needing `sqlite3` inside the image.

---

## One‑off: Back up NOW (server)

Run these commands on the server in the repository directory (where the compose file lives):

```bash
# 0) Prepare backup folder and timestamp
mkdir -p backups/sqlite backups/media
TS=$(date +%Y%m%d-%H%M%S)

# 1) Stop the app briefly to quiesce SQLite (few seconds)
docker compose -f docker-compose-deploy-SQLite.yml stop app

# 2) Copy the SQLite DB out of the container filesystem to the host
#    This streams /app/db.sqlite3 into a timestamped backup on the server
docker compose -f docker-compose-deploy-SQLite.yml run --rm app \
  sh -lc 'test -f /app/db.sqlite3 && cat /app/db.sqlite3' \
  > backups/sqlite/db.${TS}.sqlite3

# 3) Start the app again
docker compose -f docker-compose-deploy-SQLite.yml start app

# 4) (Optional) Compress and checksum
gzip -9 backups/sqlite/db.${TS}.sqlite3
sha256sum backups/sqlite/db.${TS}.sqlite3.gz > backups/sqlite/db.${TS}.sqlite3.gz.sha256

# 5) Back up media (and static, if desired)
# Media
docker compose -f docker-compose-deploy-SQLite.yml run --rm app \
  sh -lc 'tar czf - /vol/web/media' \
  > backups/media/media.${TS}.tgz
sha256sum backups/media/media.${TS}.tgz > backups/media/media.${TS}.tgz.sha256

# Static (optional — can be re-built, but backup is cheap)
docker compose -f docker-compose-deploy-SQLite.yml run --rm app \
  sh -lc 'tar czf - /vol/web/static' \
  > backups/media/static.${TS}.tgz
sha256sum backups/media/static.${TS}.tgz > backups/media/static.${TS}.tgz.sha256
```

Verification
- Confirm sizes: `ls -lh backups/sqlite backups/media`
- Verify checksums: `sha256sum -c backups/sqlite/db.${TS}.sqlite3.gz.sha256`

---

## One-command backup (scripts/backup-all.sh)

A helper script is provided to perform the full backup flow in one command (stop app → copy SQLite DB → media/static → start app):

```bash
# From the repo root
bash scripts/backup-all.sh

# Options:
#   --skip-media       Skip media backup
#   --include-static   Include static files backup (optional)
#   --compose-file     Use a specific compose file (default: docker-compose-deploy-SQLite.yml;
#                      you may pass -CockroachDB or -MySQL variants; falls back to legacy names if present)

# Examples
bash scripts/backup-all.sh --include-static
bash scripts/backup-all.sh --skip-media --compose-file docker-compose-deploy.yml
```

Outputs are written to `backups/sqlite/` and `backups/media/` with a timestamp. The script briefly stops and then restarts the `app` service to ensure a clean SQLite snapshot.

Use from cron (example, daily at 03:02):

```bash
# Edit root's crontab
sudo crontab -e
# Add line (single line):
2 3 * * * PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/bin" bash /path/to/repo/scripts/backup-all.sh >> /var/log/nadooit-backups.log 2>&1
```

---

## Automatic backups with disk space guard (scripts/backup-auto.sh)

Use `scripts/backup-auto.sh` to run backups safely on a schedule. It performs:
- Age‑based pruning (delete backups older than N days)
- Optional count‑based pruning (keep at most N SQLite backups)
- Minimum free space check (prune oldest backups until threshold is met)
- Then calls the one‑command backup script

Usage:
```bash
bash scripts/backup-auto.sh [--min-free-gb N] [--keep-days D] [--max-backups N] \
                             [--skip-media] [--include-static] [--compose-file <path>]

# Defaults:
# --min-free-gb 2   (ensure at least 2 GiB free before backup)
# --keep-days  14   (delete backups older than 14 days)
# --max-backups 0   (disabled; set a positive integer to enforce a max count for DB backups)

# Examples
bash scripts/backup-auto.sh                       # daily defaults
bash scripts/backup-auto.sh --min-free-gb 4       # require 4 GiB free
bash scripts/backup-auto.sh --keep-days 30        # keep 30 days
bash scripts/backup-auto.sh --max-backups 20      # cap DB backups to 20 files
bash scripts/backup-auto.sh --include-static      # also back up static
```

Cron example (runs with defaults at 03:02):
```bash
sudo crontab -e
2 3 * * * PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/bin" bash /path/to/repo/scripts/backup-auto.sh >> /var/log/nadooit-backups.log 2>&1
```

### Setup via script (installs cron for you)

Use the provided helper to install or update the cron job automatically. It writes an idempotent entry with a marker so re-running updates in place.

```bash
# From the repo root (run as root to use /var/log, or as your user)
bash scripts/setup-backups.sh \
  --schedule "2 3 * * *" \
  --min-free-gb 2 \
  --keep-days 14 \
  --max-backups 0 \
  --include-static    # optional, remove if not needed
```

  Options:
  - `--schedule` cron expression (default `2 3 * * *`)
  - `--min-free-gb` minimum free space required before backup (default `2` GiB)
  - `--keep-days` prune backups older than N days (default `14`)
  - `--max-backups` cap number of SQLite DB backups (default `0` = disabled)
  - `--compose-file` choose compose file (defaults to `docker-compose-deploy-SQLite.yml`; legacy names still supported as fallback)
  - `--skip-media` skip media backup
  - `--include-static` also back up static files
  - `--log-file` override log file path (default: `/var/log/nadooit-backups.log` as root, else `~/nadooit-backups.log`)

  The script installs a crontab line like:

  ```
  2 3 * * * PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/bin" bash /abs/path/to/repo/scripts/backup-auto.sh >> /var/log/nadooit-backups.log 2>&1  # nadooit-backup-auto
  ```

  Also install Certbot renewal (optional):
  ```bash
  # Daily at ~04:17; renew quietly and reload nginx on success
  sudo bash scripts/setup-backups.sh \
    --setup-certbot \
    --certbot-schedule "17 4 * * *" \
    --certbot-cmd "certbot renew -q" \
    --certbot-deploy-hook "systemctl reload nginx"
  ```
  - If your web server runs in Docker, use a deploy hook that reloads it via compose, e.g.:
    ```bash
    --certbot-deploy-hook "docker compose -f docker-compose-deploy-SQLite.yml exec -T nginx nginx -s reload"
    ```
  - Logs default to `/var/log/letsencrypt/renew.log` (root) or `~/certbot-renew.log` (non-root); override with `--certbot-log-file`.

  ### System maintenance: automatic OS updates and container restart on boot
  
  Enable unattended Ubuntu security updates with auto reboot, and ensure the Docker Compose stack comes back after a reboot:
  
  ```bash
  # Set a safe reboot window (e.g., 04:30) and install a systemd unit to start compose on boot
  sudo bash scripts/setup-maintenance.sh \
    --reboot-time "04:30" \
    --install-systemd-compose
  ```
  - This configures `unattended-upgrades` with automatic reboots at the specified time.
  - It installs a systemd service (`nadooit-compose.service`) that runs `docker compose up -d` on boot for your selected compose file (default `docker-compose-deploy-SQLite.yml`).
  - Schedule backups earlier than the reboot window (e.g., backups at 03:02) so a fresh backup exists prior to any reboot.

  #### Pre‑reboot backup guard (fresh backup before auto‑reboot)
  
  Ensure there is a recent backup right before the reboot window. The guard checks the age of the latest DB backup and only runs a backup if it is older than N hours.
  
  ```bash
  # Install a pre-reboot backup guard that runs 30 min before the reboot time
  sudo bash scripts/setup-maintenance.sh \
    --reboot-time "04:30" \
    --install-pre-reboot-guard \
    --pre-guard-offset-min 30 \
    --pre-guard-max-age-hours 6
  ```
  - Default behavior computes a cron schedule PRE_GUARD_OFFSET_MIN minutes before `--reboot-time`.
  - Override the schedule completely via `--pre-guard-schedule "MIN HOUR * * *"` if desired.
  - Pass content options through the guard:
    - `--guard-skip-media` to skip media backup
    - `--guard-include-static` to include static files
  - Logs go to `/var/log/nadooit-pre-reboot-backup.log` by default (root), configurable via `--pre-guard-log-file`.
  - The guard uses `scripts/pre-reboot-backup.sh`, which calls `scripts/backup-auto.sh` when a fresh backup is needed.

Notes
- Both scripts write to `backups/sqlite/` and `backups/media/`.
- Adjust thresholds to your disk size and growth rate.
- Offload backups off‑server regularly (rsync/S3) for resilience.

---

## Optional: Online backup (no stop)

If your container has the `sqlite3` CLI installed (it usually doesn’t), you can create a consistent online backup without stopping the app:

```bash
docker compose -f docker-compose-deploy-SQLite.yml run --rm app \
  sh -lc "sqlite3 /app/db.sqlite3 '.backup /tmp/db.backup.sqlite3' && cat /tmp/db.backup.sqlite3" \
  > backups/sqlite/db.${TS}.sqlite3
```

If the command errors due to missing `sqlite3`, use the standard method above (brief stop/start).

---

## Automate with cron (daily at 03:02)
Create a small script at `/usr/local/bin/nadooit-backup.sh` and make it executable:

```bash
sudo tee /usr/local/bin/nadooit-backup.sh > /dev/null <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
cd /opt/nadooit   # update to your repo path
TS=$(date +%Y%m%d-%H%M%S)
mkdir -p backups/sqlite backups/media

docker compose -f docker-compose.deploy.yml stop app

docker compose -f docker-compose.deploy.yml run --rm app \
  sh -lc 'test -f /app/db.sqlite3 && cat /app/db.sqlite3' \
  > backups/sqlite/db.${TS}.sqlite3

docker compose -f docker-compose.deploy.yml start app

gzip -9 backups/sqlite/db.${TS}.sqlite3 || true
sha256sum backups/sqlite/db.${TS}.sqlite3.gz > backups/sqlite/db.${TS}.sqlite3.gz.sha256

docker compose -f docker-compose.deploy.yml run --rm app \
  sh -lc 'tar czf - /vol/web/media' \
  > backups/media/media.${TS}.tgz
sha256sum backups/media/media.${TS}.tgz > backups/media/media.${TS}.tgz.sha256

# Retention: keep last 14 backups
find backups/sqlite -type f -name 'db.*.sqlite3.gz' -mtime +14 -delete || true
find backups/media  -type f -name 'media.*.tgz'     -mtime +14 -delete || true
EOF
sudo chmod +x /usr/local/bin/nadooit-backup.sh
```

Add cron (adjust PATHs and repo path as needed):

```bash
# Edit root's crontab
sudo crontab -e
# Add this line (single line):
2 3 * * * PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/bin" /usr/local/bin/nadooit-backup.sh >> /var/log/nadooit-backups.log 2>&1
```

---

## Restore (SQLite + media)

1) Stop the app:
```bash
docker compose -f docker-compose.deploy.yml stop app
```

2) Restore the SQLite DB into the container filesystem:
```bash
# Pick the backup you want to restore
BACKUP=backups/sqlite/db.20250101-030205.sqlite3.gz   # example

# Decompress if needed
gunzip -c "$BACKUP" > /tmp/db.restore.sqlite3

# Stream the file into /app/db.sqlite3 inside the image FS
docker compose -f docker-compose-deploy-SQLite.yml run --rm app \
  sh -lc 'cat > /app/db.sqlite3' < /tmp/db.restore.sqlite3
rm -f /tmp/db.restore.sqlite3
```

3) Restore media (and static, if desired):
```bash
# Media
docker compose -f docker-compose-deploy-SQLite.yml run --rm app \
  sh -lc 'tar xzf - -C /' < backups/media/media.20250101-030205.tgz
# Static (optional)
docker compose -f docker-compose-deploy-SQLite.yml run --rm app \
  sh -lc 'tar xzf - -C /' < backups/media/static.20250101-030205.tgz
```

4) Start the app and run migrations (if you restored an older DB):
```bash
docker compose -f docker-compose-deploy-SQLite.yml start app
docker compose -f docker-compose-deploy-SQLite.yml run --rm app python manage.py migrate
```

---

## Notes & best practices
- Consider bind‑mounting `/app/db.sqlite3` to a host file for simpler copy/restore (edit compose):
  ```yaml
  services:
    app:
      volumes:
        - /opt/nadooit/sqlite/db.sqlite3:/app/db.sqlite3
  ```
- Store backups off‑server (e.g., rsync to another machine or S3 with SSE).
- Verify backups periodically by restoring to a test server and running a smoke test.
- Keep API keys and `.env` files backed up securely (off‑site).

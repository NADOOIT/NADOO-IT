#!/usr/bin/env bash
# NADOO-IT backup helper: stop app, back up SQLite DB, media (and optionally static), start app again.
# Usage:
#   bash scripts/backup-all.sh [--skip-media] [--include-static] [--compose-file <path>]
# Notes:
# - Default compose file is docker-compose.deploy.yml (falls back to docker-compose-deploy.yml if present)
# - Outputs backups into backups/sqlite and backups/media with a timestamp

set -euo pipefail

# Resolve repo root (parent of scripts dir)
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
cd "$REPO_ROOT"

# Defaults
COMPOSE_FILE="docker-compose.deploy.yml"
[ ! -f "$COMPOSE_FILE" ] && [ -f "docker-compose-deploy.yml" ] && COMPOSE_FILE="docker-compose-deploy.yml"
BACKUP_MEDIA=1
BACKUP_STATIC=0

# Args
while [ $# -gt 0 ]; do
  case "$1" in
    --skip-media) BACKUP_MEDIA=0 ;;
    --include-static) BACKUP_STATIC=1 ;;
    --compose-file)
      shift
      COMPOSE_FILE="${1:-}"
      if [ -z "$COMPOSE_FILE" ]; then echo "--compose-file requires a path" >&2; exit 2; fi
      ;;
    -h|--help)
      echo "Usage: $0 [--skip-media] [--include-static] [--compose-file <path>]"; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
  shift
done

if [ ! -f "$COMPOSE_FILE" ]; then
  echo "Compose file not found: $COMPOSE_FILE" >&2
  exit 1
fi

mkdir -p backups/sqlite backups/media
TS=$(date +%Y%m%d-%H%M%S)

# Stop app briefly for a clean SQLite snapshot
echo "[+] Stopping app (compose: $COMPOSE_FILE)"
docker compose -f "$COMPOSE_FILE" stop app

# Figure out container ID (even when stopped)
APP_CID=$(docker compose -f "$COMPOSE_FILE" ps -q app || true)

# Prefer docker cp from the (stopped) app container; fallback to one-off run+cat
DB_OUT="backups/sqlite/db.${TS}.sqlite3"
echo "[+] Backing up SQLite DB to $DB_OUT"
if [ -n "$APP_CID" ]; then
  if docker cp "$APP_CID:/app/db.sqlite3" "$DB_OUT" 2>/dev/null; then
    echo "[+] Copied DB via docker cp"
  else
    echo "[!] docker cp failed; falling back to one-off run"
    docker compose -f "$COMPOSE_FILE" run --rm app sh -lc 'test -f /app/db.sqlite3 && cat /app/db.sqlite3' > "$DB_OUT"
  fi
else
  echo "[!] Could not resolve app container ID; using one-off run"
  docker compose -f "$COMPOSE_FILE" run --rm app sh -lc 'test -f /app/db.sqlite3 && cat /app/db.sqlite3' > "$DB_OUT"
fi

# Start app back up
echo "[+] Starting app"
docker compose -f "$COMPOSE_FILE" start app

# Compress + checksum
if gzip -9 "$DB_OUT"; then
  sha256sum "${DB_OUT}.gz" > "${DB_OUT}.gz.sha256"
fi

# Media backup
if [ "$BACKUP_MEDIA" = "1" ]; then
  MEDIA_OUT="backups/media/media.${TS}.tgz"
  echo "[+] Backing up media to $MEDIA_OUT"
  docker compose -f "$COMPOSE_FILE" run --rm app sh -lc 'tar czf - /vol/web/media' > "$MEDIA_OUT"
  sha256sum "$MEDIA_OUT" > "${MEDIA_OUT}.sha256"
fi

# Static backup (optional)
if [ "$BACKUP_STATIC" = "1" ]; then
  STATIC_OUT="backups/media/static.${TS}.tgz"
  echo "[+] Backing up static to $STATIC_OUT"
  docker compose -f "$COMPOSE_FILE" run --rm app sh -lc 'tar czf - /vol/web/static' > "$STATIC_OUT"
  sha256sum "$STATIC_OUT" > "${STATIC_OUT}.sha256"
fi

echo "[✓] Backup completed"
echo "    SQLite: ${DB_OUT}.gz"
[ "$BACKUP_MEDIA" = "1" ] && echo "    Media:  ${MEDIA_OUT}"
[ "$BACKUP_STATIC" = "1" ] && echo "    Static: ${STATIC_OUT}"

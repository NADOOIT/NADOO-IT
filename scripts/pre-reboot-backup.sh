#!/usr/bin/env bash
# Pre-reboot backup guard for NADOO-IT.
# Ensures a fresh backup exists shortly before an automated reboot window.
# If the most recent DB backup is older than --max-age-hours, triggers backup-auto.sh.
#
# Usage:
#   bash scripts/pre-reboot-backup.sh \
#     [--max-age-hours 6] \
#     [--compose-file docker-compose.deploy.yml] \
#     [--skip-media] [--include-static] \
#     [--min-free-gb N] [--keep-days D] [--max-backups N]
#
# Notes:
# - This script runs on the host and depends on scripts/backup-auto.sh

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
cd "$REPO_ROOT"

MAX_AGE_HOURS=6
COMPOSE_FILE="docker-compose.deploy.yml"
[ ! -f "$COMPOSE_FILE" ] && [ -f "docker-compose-deploy.yml" ] && COMPOSE_FILE="docker-compose-deploy.yml"

# Defaults passed through to backup-auto unless overridden
MIN_FREE_GB=""
KEEP_DAYS=""
MAX_BACKUPS=""
PASS_ARGS=()

while [ $# -gt 0 ]; do
  case "$1" in
    --max-age-hours) shift; MAX_AGE_HOURS="${1:-}"; [ -z "$MAX_AGE_HOURS" ] && { echo "--max-age-hours requires a value" >&2; exit 2; } ;;
    --compose-file) shift; COMPOSE_FILE="${1:-}"; [ -z "$COMPOSE_FILE" ] && { echo "--compose-file requires a file" >&2; exit 2; } ;;
    --min-free-gb) shift; MIN_FREE_GB="${1:-}" ;;
    --keep-days) shift;  KEEP_DAYS="${1:-}" ;;
    --max-backups) shift; MAX_BACKUPS="${1:-}" ;;
    --skip-media|--include-static) PASS_ARGS+=("$1") ;;
    -h|--help) echo "Usage: $0 [--max-age-hours N] [--compose-file PATH] [--skip-media] [--include-static] [--min-free-gb N] [--keep-days D] [--max-backups N]"; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
  shift
done

if [ ! -f "$COMPOSE_FILE" ]; then
  echo "Compose file not found: $COMPOSE_FILE" >&2
  exit 1
fi

mkdir -p backups/sqlite backups/media

# Find newest DB backup (gz or plain)
latest_file=""
if compgen -G "backups/sqlite/db.*.sqlite3.gz" > /dev/null; then
  # shellcheck disable=SC2012
  latest_file=$(ls -1t backups/sqlite/db.*.sqlite3.gz | head -n1)
elif compgen -G "backups/sqlite/db.*.sqlite3" > /dev/null; then
  # shellcheck disable=SC2012
  latest_file=$(ls -1t backups/sqlite/db.*.sqlite3 | head -n1)
fi

need_backup=false
if [ -z "$latest_file" ]; then
  echo "[i] No previous DB backups found; will create one now."
  need_backup=true
else
  now_epoch=$(date +%s)
  mtime_epoch=$(stat -c %Y "$latest_file" 2>/dev/null || stat -f %m "$latest_file")
  age_sec=$(( now_epoch - mtime_epoch ))
  max_age_sec=$(( MAX_AGE_HOURS * 3600 ))
  echo "[i] Latest DB backup: $latest_file (age: $(( age_sec/3600 ))h)"
  if [ "$age_sec" -ge "$max_age_sec" ]; then
    need_backup=true
  fi
fi

if [ "$need_backup" = true ]; then
  echo "[+] Triggering pre-reboot backup (max-age-hours=$MAX_AGE_HOURS)"
  CMD=("bash" "$SCRIPT_DIR/backup-auto.sh" "--compose-file" "$COMPOSE_FILE")
  for a in "${PASS_ARGS[@]}"; do CMD+=("$a"); done
  [ -n "$MIN_FREE_GB" ] && CMD+=("--min-free-gb" "$MIN_FREE_GB")
  [ -n "$KEEP_DAYS" ] && CMD+=("--keep-days" "$KEEP_DAYS")
  [ -n "$MAX_BACKUPS" ] && CMD+=("--max-backups" "$MAX_BACKUPS")
  echo "[+] Running: ${CMD[*]}"
  "${CMD[@]}"
  echo "[✓] Pre-reboot backup completed"
else
  echo "[✓] Backup is recent enough; skipping pre-reboot backup"
fi

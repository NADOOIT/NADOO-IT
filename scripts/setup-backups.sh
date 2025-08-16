#!/usr/bin/env bash
# Setup script to install a cron job for automatic NADOO-IT backups.
# - Installs a crontab entry calling scripts/backup-auto.sh on a schedule
# - Works for current user; if run as root, installs for root user
# - Optional: also installs a certbot renew cron entry
#
# Usage:
#   bash scripts/setup-backups.sh [--schedule "2 3 * * *"] \
#                                 [--min-free-gb N] [--keep-days D] [--max-backups N] \
#                                 [--skip-media] [--include-static] [--compose-file <path>] \
#                                 [--log-file <path>] \
#                                 [--setup-certbot] [--certbot-schedule "17 4 * * *"] \
#                                 [--certbot-cmd "certbot renew -q"] [--certbot-deploy-hook "systemctl reload nginx"] \
#                                 [--certbot-log-file <path>]
# Defaults:
#   --schedule    "2 3 * * *" (03:02 daily)
#   --min-free-gb 2
#   --keep-days   14
#   --max-backups 0 (disabled)
#   --log-file    /var/log/nadooit-backups.log when run as root, else "$HOME/nadooit-backups.log"
#   --certbot-schedule   "17 4 * * *" (04:17 daily)
#   --certbot-cmd        "certbot renew -q"
#   --certbot-deploy-hook (none)
#   --certbot-log-file   /var/log/letsencrypt/renew.log when run as root, else "$HOME/certbot-renew.log"

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
cd "$REPO_ROOT"

SCHEDULE="2 3 * * *"
MIN_FREE_GB=2
KEEP_DAYS=14
MAX_BACKUPS=0
COMPOSE_FILE="docker-compose.deploy.yml"
[ ! -f "$COMPOSE_FILE" ] && [ -f "docker-compose-deploy.yml" ] && COMPOSE_FILE="docker-compose-deploy.yml"
LOG_FILE=""

# Certbot options
CERTBOT_SETUP=false
CERTBOT_SCHEDULE="17 4 * * *"
CERTBOT_CMD="certbot renew -q"
CERTBOT_DEPLOY_HOOK=""
CERTBOT_LOG_FILE=""

PASS_ARGS=()

while [ $# -gt 0 ]; do
  case "$1" in
    --schedule) shift; SCHEDULE="${1:-}"; [ -z "$SCHEDULE" ] && { echo "--schedule requires a value" >&2; exit 2; } ;;
    --min-free-gb) shift; MIN_FREE_GB="${1:-}"; [ -z "$MIN_FREE_GB" ] && { echo "--min-free-gb requires a value" >&2; exit 2; } ;;
    --keep-days) shift; KEEP_DAYS="${1:-}"; [ -z "$KEEP_DAYS" ] && { echo "--keep-days requires a value" >&2; exit 2; } ;;
    --max-backups) shift; MAX_BACKUPS="${1:-}"; [ -z "$MAX_BACKUPS" ] && { echo "--max-backups requires a value" >&2; exit 2; } ;;
    --compose-file) shift; COMPOSE_FILE="${1:-}"; [ -z "$COMPOSE_FILE" ] && { echo "--compose-file requires a path" >&2; exit 2; } ;;
    --skip-media|--include-static) PASS_ARGS+=("$1") ;;
    --log-file) shift; LOG_FILE="${1:-}" ;;
    --setup-certbot) CERTBOT_SETUP=true ;;
    --certbot-schedule) shift; CERTBOT_SCHEDULE="${1:-}"; [ -z "$CERTBOT_SCHEDULE" ] && { echo "--certbot-schedule requires a value" >&2; exit 2; } ;;
    --certbot-cmd) shift; CERTBOT_CMD="${1:-}"; [ -z "$CERTBOT_CMD" ] && { echo "--certbot-cmd requires a value" >&2; exit 2; } ;;
    --certbot-deploy-hook) shift; CERTBOT_DEPLOY_HOOK="${1:-}" ;;
    --certbot-log-file) shift; CERTBOT_LOG_FILE="${1:-}" ;;
    -h|--help)
      echo "Usage: $0 [--schedule \"2 3 * * *\"] [--min-free-gb N] [--keep-days D] [--max-backups N] [--skip-media] [--include-static] [--compose-file path] [--log-file path] [--setup-certbot] [--certbot-schedule \"17 4 * * *\"] [--certbot-cmd \"certbot renew -q\"] [--certbot-deploy-hook \"systemctl reload nginx\"] [--certbot-log-file path]"; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
  shift
done

if [ ! -f "$COMPOSE_FILE" ]; then
  echo "Compose file not found: $COMPOSE_FILE" >&2
  exit 1
fi

# Ensure helper scripts are executable (best-effort)
chmod +x "$SCRIPT_DIR/backup-auto.sh" "$SCRIPT_DIR/backup-all.sh" 2>/dev/null || true

# Determine default log file
if [ -z "$LOG_FILE" ]; then
  if [ "$(id -u)" -eq 0 ]; then
    LOG_FILE="/var/log/nadooit-backups.log"
  else
    LOG_FILE="$HOME/nadooit-backups.log"
  fi
fi

# Determine default certbot log file
if [ -z "$CERTBOT_LOG_FILE" ]; then
  if [ "$(id -u)" -eq 0 ]; then
    CERTBOT_LOG_FILE="/var/log/letsencrypt/renew.log"
  else
    CERTBOT_LOG_FILE="$HOME/certbot-renew.log"
  fi
fi

# Compose the command with args passed to backup-auto.sh
CMD=("bash" "$SCRIPT_DIR/backup-auto.sh" "--compose-file" "$COMPOSE_FILE" "--min-free-gb" "$MIN_FREE_GB" "--keep-days" "$KEEP_DAYS" "--max-backups" "$MAX_BACKUPS")
for a in "${PASS_ARGS[@]}"; do CMD+=("$a"); done

# Build cron lines with markers to allow idempotent updates
BACKUP_MARKER="# nadooit-backup-auto"
BACKUP_CRON_CMD="PATH=\"/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/bin\" ${CMD[*]} >> ${LOG_FILE} 2>&1"
BACKUP_CRON_LINE="${SCHEDULE} ${BACKUP_CRON_CMD} ${BACKUP_MARKER}"

CERTBOT_MARKER="# nadooit-certbot-renew"
if [ "$CERTBOT_SETUP" = true ]; then
  CERTBOT_CRON_CMD="PATH=\"/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/bin\" ${CERTBOT_CMD}"
  if [ -n "$CERTBOT_DEPLOY_HOOK" ]; then
    CERTBOT_CRON_CMD="${CERTBOT_CRON_CMD} --deploy-hook \"${CERTBOT_DEPLOY_HOOK}\""
  fi
  CERTBOT_CRON_CMD="${CERTBOT_CRON_CMD} >> ${CERTBOT_LOG_FILE} 2>&1"
  CERTBOT_CRON_LINE="${CERTBOT_SCHEDULE} ${CERTBOT_CRON_CMD} ${CERTBOT_MARKER}"
fi

# Install or update crontab for the current user (or root if running as root)
TMP=$(mktemp)
crontab -l > "$TMP" 2>/dev/null || true
# Remove existing lines with our markers
grep -Fv "$BACKUP_MARKER" "$TMP" > "${TMP}.new" || true
mv "${TMP}.new" "$TMP"
grep -Fv "$CERTBOT_MARKER" "$TMP" > "${TMP}.new" || true
# Append the fresh backup line
printf '%s\n' "$BACKUP_CRON_LINE" >> "${TMP}.new"
# Append certbot line if requested
if [ "$CERTBOT_SETUP" = true ]; then
  printf '%s\n' "$CERTBOT_CRON_LINE" >> "${TMP}.new"
fi
# Install
crontab "${TMP}.new"
rm -f "$TMP" "${TMP}.new"

# Summary
echo "[✓] Installed/updated cron entries"
echo "    Backup schedule : $SCHEDULE"
echo "    Backup command  : $BACKUP_CRON_CMD"
echo "    Backup log file : $LOG_FILE"
echo "    Compose file    : $COMPOSE_FILE"
if [ "$CERTBOT_SETUP" = true ]; then
  echo "    Certbot schedule: $CERTBOT_SCHEDULE"
  echo "    Certbot command : ${CERTBOT_CMD}${CERTBOT_DEPLOY_HOOK:+ --deploy-hook \"$CERTBOT_DEPLOY_HOOK\"}"
  echo "    Certbot log file: $CERTBOT_LOG_FILE"
fi

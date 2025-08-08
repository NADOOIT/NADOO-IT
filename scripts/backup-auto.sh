#!/usr/bin/env bash
# Automatic backups with disk space guard for NADOO-IT.
# - Ensures a minimum free space threshold before performing a backup
# - Prunes old backups (age and/or count) if needed
# - Delegates actual backup to scripts/backup-all.sh
#
# Usage:
#   bash scripts/backup-auto.sh [--min-free-gb N] [--keep-days D] [--max-backups N]
#                               [--skip-media] [--include-static]
#                               [--compose-file <path>]
# Defaults:
#   --min-free-gb 2   (ensure at least 2 GiB free)
#   --keep-days  14   (delete backups older than 14 days)
#   --max-backups 0   (disabled; set to a positive integer to limit DB backups)

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
cd "$REPO_ROOT"

MIN_FREE_GB=2
KEEP_DAYS=14
MAX_BACKUPS=0
COMPOSE_FILE="docker-compose.deploy.yml"
[ ! -f "$COMPOSE_FILE" ] && [ -f "docker-compose-deploy.yml" ] && COMPOSE_FILE="docker-compose-deploy.yml"
PASS_ARGS=()

while [ $# -gt 0 ]; do
  case "$1" in
    --min-free-gb)
      shift; MIN_FREE_GB="${1:-}"; [ -z "$MIN_FREE_GB" ] && { echo "--min-free-gb requires a value" >&2; exit 2; } ;;
    --keep-days)
      shift; KEEP_DAYS="${1:-}"; [ -z "$KEEP_DAYS" ] && { echo "--keep-days requires a value" >&2; exit 2; } ;;
    --max-backups)
      shift; MAX_BACKUPS="${1:-}"; [ -z "$MAX_BACKUPS" ] && { echo "--max-backups requires a value" >&2; exit 2; } ;;
    --compose-file)
      shift; COMPOSE_FILE="${1:-}"; [ -z "$COMPOSE_FILE" ] && { echo "--compose-file requires a path" >&2; exit 2; } ;;
    --skip-media|--include-static)
      PASS_ARGS+=("$1") ;;
    -h|--help)
      echo "Usage: $0 [--min-free-gb N] [--keep-days D] [--max-backups N] [--skip-media] [--include-static] [--compose-file path]"; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
  shift
done

if [ ! -f "$COMPOSE_FILE" ]; then
  echo "Compose file not found: $COMPOSE_FILE" >&2
  exit 1
fi

mkdir -p backups/sqlite backups/media

# Convert threshold to KB for integer comparisons
THRESHOLD_KB=$(awk -v g="$MIN_FREE_GB" 'BEGIN{printf "%d", g*1024*1024}')

free_kb() {
  # POSIX-ish: df -Pk prints in KB; use the available column
  df -Pk "$REPO_ROOT" | awk 'NR==2 {print $4}'
}

human() {
  num="$1"; awk -v n="$num" 'BEGIN{printf (n>1048576?"%.2fG":(n>1024?"%.2fM":"%dK")), (n>1048576?n/1048576:(n>1024?n/1024:n))}'
}

prune_by_age() {
  # Delete backups older than KEEP_DAYS
  if [ "$KEEP_DAYS" -gt 0 ]; then
    echo "[i] Pruning backups older than $KEEP_DAYS days"
    find backups/sqlite -type f -mtime +"$KEEP_DAYS" -print -delete || true
    find backups/media  -type f -mtime +"$KEEP_DAYS" -print -delete || true
  fi
}

prune_by_count() {
  # Limit total number of SQLite DB backups if MAX_BACKUPS > 0
  if [ "$MAX_BACKUPS" -gt 0 ]; then
    echo "[i] Enforcing max $MAX_BACKUPS SQLite backups"
    # shellcheck disable=SC2012
    mapfile -t files < <(ls -1t backups/sqlite/db.*.sqlite3.gz backups/sqlite/db.*.sqlite3 2>/dev/null || true)
    if [ ${#files[@]} -gt "$MAX_BACKUPS" ]; then
      to_delete_count=$(( ${#files[@]} - MAX_BACKUPS ))
      for ((i=${#files[@]}-1; i>=MAX_BACKUPS && to_delete_count>0; i--)); do
        echo "[i] Deleting old DB backup: ${files[$i]}"
        rm -f -- "${files[$i]}" || true
        to_delete_count=$((to_delete_count-1))
      done
    fi
  fi
}

prune_until_free() {
  current_free_kb=$(free_kb)
  echo "[i] Free space: $(human "$current_free_kb") (KB), target >= $(human "$THRESHOLD_KB")"
  if [ "$current_free_kb" -ge "$THRESHOLD_KB" ]; then
    return 0
  fi
  echo "[!] Low free space; pruning oldest backups until threshold is met"
  # Build list of all backup files sorted by mtime ascending (oldest first)
  mapfile -t all_files < <(find backups -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | awk '{ $1=""; sub(/^ /, ""); print }')
  for f in "${all_files[@]}"; do
    [ -f "$f" ] || continue
    echo "[i] Deleting: $f"
    rm -f -- "$f" || true
    current_free_kb=$(free_kb)
    if [ "$current_free_kb" -ge "$THRESHOLD_KB" ]; then
      echo "[i] Free space now sufficient: $(human "$current_free_kb")"
      return 0
    fi
  done
  echo "[!] Unable to reach free space threshold; proceeding anyway"
}

# Step 1: Age-based pruning
prune_by_age

# Step 2: Count-based pruning (SQLite DB backups)
prune_by_count

# Step 3: Ensure minimum free space before creating a new backup
prune_until_free

# Step 4: Perform the backup via backup-all.sh (passes through flags)
CMD=("bash" "$SCRIPT_DIR/backup-all.sh" "--compose-file" "$COMPOSE_FILE")
for a in "${PASS_ARGS[@]}"; do CMD+=("$a"); done

echo "[+] Running: ${CMD[*]}"
"${CMD[@]}"

# Step 5: Optional post-backup pruning by count again (if a lot was created)
prune_by_count

echo "[✓] Auto backup completed"

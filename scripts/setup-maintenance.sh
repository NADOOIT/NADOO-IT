#!/usr/bin/env bash
# Setup automatic Ubuntu security updates with auto reboot and ensure
# the NADOO-IT Docker Compose stack starts on boot.
#
# This script is intended to be run on the host (not inside a container).
# It requires root privileges because it writes to /etc and manages systemd.
#
# Usage:
#   sudo bash scripts/setup-maintenance.sh \
#     [--reboot-time "04:30"] \
#     [--compose-file docker-compose.deploy.yml] \
#     [--service-name nadooit-compose] \
#     [--no-unattended] \
#     [--install-systemd-compose] \
#     [--install-pre-reboot-guard] [--pre-guard-offset-min 30] \
#     [--pre-guard-max-age-hours 6] [--pre-guard-schedule "0 4 * * *"] \
#     [--pre-guard-log-file /var/log/nadooit-pre-reboot-backup.log] \
#     [--guard-include-static] [--guard-skip-media]
#
# Defaults:
#   --reboot-time            04:30 (24h HH:MM)
#   --compose-file           docker-compose.deploy.yml (fallback: docker-compose-deploy.yml)
#   --service-name           nadooit-compose
#   unattended-upgrades      enabled (omit with --no-unattended)
#   systemd compose service  disabled unless --install-systemd-compose is set
#   pre-reboot guard         disabled unless --install-pre-reboot-guard is set
#   --pre-guard-offset-min   30 (minutes before reboot)
#   --pre-guard-max-age-hours 6
#   --pre-guard-log-file     /var/log/nadooit-pre-reboot-backup.log (root) or $HOME/nadooit-pre-reboot-backup.log
#
# Notes:
# - Backups: Schedule backups earlier (e.g., 03:02) so a fresh backup exists before
#   the auto-reboot window.
# - Containers: Either rely on restart: unless-stopped policies, or install the
#   systemd unit so the compose stack is brought up on boot.

set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "This script must be run as root. Try: sudo bash $0 ..." >&2
  exit 1
fi

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
cd "$REPO_ROOT"

REBOOT_TIME="04:30"
COMPOSE_FILE="docker-compose.deploy.yml"
[ ! -f "$COMPOSE_FILE" ] && [ -f "docker-compose-deploy.yml" ] && COMPOSE_FILE="docker-compose-deploy.yml"
SERVICE_NAME="nadooit-compose"
ENABLE_UNATTENDED=true
INSTALL_SYSTEMD_COMPOSE=false

# Pre-reboot backup guard options
INSTALL_PRE_REBOOT_GUARD=false
PRE_GUARD_OFFSET_MIN=30
PRE_GUARD_MAX_AGE_HOURS=6
PRE_GUARD_SCHEDULE=""
PRE_GUARD_LOG_FILE=""
GUARD_INCLUDE_STATIC=false
GUARD_SKIP_MEDIA=false

while [ $# -gt 0 ]; do
  case "$1" in
    --reboot-time) shift; REBOOT_TIME="${1:-}"; [ -z "$REBOOT_TIME" ] && { echo "--reboot-time requires HH:MM" >&2; exit 2; } ;;
    --compose-file) shift; COMPOSE_FILE="${1:-}"; [ -z "$COMPOSE_FILE" ] && { echo "--compose-file requires a file" >&2; exit 2; } ;;
    --service-name) shift; SERVICE_NAME="${1:-}"; [ -z "$SERVICE_NAME" ] && { echo "--service-name requires a value" >&2; exit 2; } ;;
    --no-unattended) ENABLE_UNATTENDED=false ;;
    --install-systemd-compose) INSTALL_SYSTEMD_COMPOSE=true ;;
    --install-pre-reboot-guard) INSTALL_PRE_REBOOT_GUARD=true ;;
    --pre-guard-offset-min) shift; PRE_GUARD_OFFSET_MIN="${1:-}"; [ -z "$PRE_GUARD_OFFSET_MIN" ] && { echo "--pre-guard-offset-min requires minutes" >&2; exit 2; } ;;
    --pre-guard-max-age-hours) shift; PRE_GUARD_MAX_AGE_HOURS="${1:-}"; [ -z "$PRE_GUARD_MAX_AGE_HOURS" ] && { echo "--pre-guard-max-age-hours requires hours" >&2; exit 2; } ;;
    --pre-guard-schedule) shift; PRE_GUARD_SCHEDULE="${1:-}"; [ -z "$PRE_GUARD_SCHEDULE" ] && { echo "--pre-guard-schedule requires a cron expression" >&2; exit 2; } ;;
    --pre-guard-log-file) shift; PRE_GUARD_LOG_FILE="${1:-}" ;;
    --guard-include-static) GUARD_INCLUDE_STATIC=true ;;
    --guard-skip-media) GUARD_SKIP_MEDIA=true ;;
    -h|--help)
      echo "Usage: sudo bash $0 [--reboot-time HH:MM] [--compose-file PATH] [--service-name NAME] [--no-unattended] [--install-systemd-compose]"; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
  shift
done

if [ ! -f "$COMPOSE_FILE" ]; then
  echo "Compose file not found: $COMPOSE_FILE (run from repo root or pass --compose-file)" >&2
  exit 1
fi

install_unattended() {
  echo "[+] Installing and configuring unattended-upgrades"
  apt-get update -y
  DEBIAN_FRONTEND=noninteractive apt-get install -y unattended-upgrades apt-listchanges || true
  # Enable periodic updates and unattended upgrades
  cat >/etc/apt/apt.conf.d/20auto-upgrades <<EOF
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
EOF
  # Place our overrides in a separate file to avoid clobbering distro defaults
  cat >/etc/apt/apt.conf.d/51nadooit-unattended <<EOF
Unattended-Upgrade::Automatic-Reboot "true";
Unattended-Upgrade::Automatic-Reboot-Time "${REBOOT_TIME}";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot-WithUsers "false";
EOF
  systemctl enable --now unattended-upgrades.service >/dev/null 2>&1 || true
  systemctl restart unattended-upgrades.service >/dev/null 2>&1 || true
  echo "[✓] Unattended upgrades enabled (auto reboot at ${REBOOT_TIME})"
}

install_systemd_compose_unit() {
  local unit="/etc/systemd/system/${SERVICE_NAME}.service"
  echo "[+] Installing systemd unit: ${unit}"
  cat >"${unit}" <<EOF
[Unit]
Description=NADOO-IT Docker Compose stack
Requires=docker.service
After=docker.service network-online.target
Wants=network-online.target

[Service]
Type=oneshot
WorkingDirectory=${REPO_ROOT}
ExecStart=/usr/bin/docker compose -f ${COMPOSE_FILE} up -d
ExecStop=/usr/bin/docker compose -f ${COMPOSE_FILE} stop
RemainAfterExit=yes
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF
  systemctl daemon-reload
  systemctl enable "${SERVICE_NAME}.service"
  # Do not auto-start immediately; only start if not running to avoid disrupting
  if ! systemctl is-active --quiet "${SERVICE_NAME}.service"; then
    systemctl start "${SERVICE_NAME}.service" || true
  fi
  echo "[✓] Systemd unit installed and enabled: ${SERVICE_NAME}.service"
}

if [ "$ENABLE_UNATTENDED" = true ]; then
  install_unattended
else
  echo "[i] Skipping unattended-upgrades setup (--no-unattended)"
fi

if [ "$INSTALL_SYSTEMD_COMPOSE" = true ]; then
  install_systemd_compose_unit
else
  echo "[i] Skipping systemd compose unit installation (use --install-systemd-compose to enable)"
fi

# Determine default pre-reboot guard log file
if [ -z "$PRE_GUARD_LOG_FILE" ]; then
  if [ "$(id -u)" -eq 0 ]; then
    PRE_GUARD_LOG_FILE="/var/log/nadooit-pre-reboot-backup.log"
  else
    PRE_GUARD_LOG_FILE="$HOME/nadooit-pre-reboot-backup.log"
  fi
fi

install_pre_reboot_guard() {
  # Compute schedule if not explicitly provided: run PRE_GUARD_OFFSET_MIN minutes before REBOOT_TIME
  local cron_expr
  if [ -n "$PRE_GUARD_SCHEDULE" ]; then
    cron_expr="$PRE_GUARD_SCHEDULE"
  else
    # Pure shell arithmetic to avoid date -d dependency
    IFS=: read -r hh mm <<<'"${REBOOT_TIME}"'
    hh=${hh#0}; mm=${mm#0}; [ -z "$hh" ] && hh=0; [ -z "$mm" ] && mm=0
    local total=$(( hh*60 + mm ))
    local new=$(( (total - PRE_GUARD_OFFSET_MIN + 1440) % 1440 ))
    local nh=$(( new / 60 ))
    local nm=$(( new % 60 ))
    printf -v nh "%02d" "$nh"
    printf -v nm "%02d" "$nm"
    cron_expr="$nm $nh * * *"
  fi

  local marker="# nadooit-pre-reboot-backup"
  local cmd=("bash" "$SCRIPT_DIR/pre-reboot-backup.sh" "--compose-file" "$COMPOSE_FILE" "--max-age-hours" "$PRE_GUARD_MAX_AGE_HOURS")
  if [ "$GUARD_INCLUDE_STATIC" = true ]; then cmd+=("--include-static"); fi
  if [ "$GUARD_SKIP_MEDIA" = true ]; then cmd+=("--skip-media"); fi
  local cron_cmd="PATH=\"/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/bin\" ${cmd[*]} >> ${PRE_GUARD_LOG_FILE} 2>&1"
  local cron_line="${cron_expr} ${cron_cmd} ${marker}"

  local tmp
  tmp=$(mktemp)
  crontab -l > "$tmp" 2>/dev/null || true
  grep -Fv "$marker" "$tmp" > "${tmp}.new" || true
  printf '%s\n' "$cron_line" >> "${tmp}.new"
  crontab "${tmp}.new"
  rm -f "$tmp" "${tmp}.new"

  echo "[✓] Installed/updated pre-reboot backup guard"
  echo "    Schedule      : $cron_expr"
  echo "    Max age hours : $PRE_GUARD_MAX_AGE_HOURS"
  echo "    Log file      : $PRE_GUARD_LOG_FILE"
}

if [ "$INSTALL_PRE_REBOOT_GUARD" = true ]; then
  install_pre_reboot_guard
else
  echo "[i] Skipping pre-reboot backup guard (use --install-pre-reboot-guard to enable)"
fi

echo "[Summary]"
if [ "$ENABLE_UNATTENDED" = true ]; then
  echo "  Unattended Upgrades  : enabled (auto reboot ${REBOOT_TIME})"
else
  echo "  Unattended Upgrades  : skipped"
fi
if [ "$INSTALL_SYSTEMD_COMPOSE" = true ]; then
  echo "  Compose service       : ${SERVICE_NAME}.service (repo: ${REPO_ROOT}, compose: ${COMPOSE_FILE})"
else
  echo "  Compose service       : not installed"
fi
if [ "$INSTALL_PRE_REBOOT_GUARD" = true ]; then
  echo "  Pre-reboot backup     : enabled (max age ${PRE_GUARD_MAX_AGE_HOURS}h, offset ${PRE_GUARD_OFFSET_MIN}m)"
else
  echo "  Pre-reboot backup     : not installed"
fi

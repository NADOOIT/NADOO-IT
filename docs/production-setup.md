# Production Setup Guide (Ubuntu + Docker Compose)

This guide walks you through a full production setup of NADOO-IT on an Ubuntu VPS using Docker Compose, with HTTPS, automated backups, unattended OS updates, and safe reboots.

## Overview
- OS: Ubuntu LTS (20.04/22.04/24.04)
- Runtime: Docker Engine + Docker Compose v2
- App stack: Django 4.2 LTS (aligns with django-cockroachdb 4.2 when CockroachDB is enabled)
- DB: SQLite by default (simple, built-in). CockroachDB is optional for scaling later.
- TLS: certbot/Let’s Encrypt
- Backups: scripts/backup-*.sh
- Maintenance: unattended-upgrades + auto-reboot + compose auto-start

## Prerequisites
- A domain pointing to the server (DNS A record)
- Open ports 80 and 443
- A user with sudo
- Docker and Docker Compose installed

Install Docker (official convenience script or apt). Example using apt on Ubuntu:
```bash
sudo apt-get update -y
sudo apt-get install -y ca-certificates curl gnupg lsb-release
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
# Log out/in to apply group membership, or run with sudo for now
```

Install certbot (host-based):
```bash
sudo apt-get install -y certbot
```

Optional hardening:
- UFW firewall: allow 22, 80, 443
- Fail2ban
- Time sync: `timedatectl set-timezone Europe/Berlin` (or desired timezone)

## Get the code
```bash
# Choose a destination directory
cd /opt
sudo git clone https://github.com/your-org/NADOO-IT.git
sudo chown -R $USER:$USER NADOO-IT
cd NADOO-IT
```

## Configure environment
NADOO-IT defaults to SQLite (no extra DB required). You should set:
- `DJANGO_SECRET_KEY` (required, strong secret)
- `DEBUG=0` for production
- `ALLOWED_HOSTS` (comma-separated, e.g. `yourdomain.com`)
- Email settings for password reset/notifications (optional)

Create `.env.production` (example):
```bash
cat > .env.production << 'EOF'
DJANGO_SECRET_KEY=change-me-very-long-random
DEBUG=0
ALLOWED_HOSTS=yourdomain.com
# Optional email
EMAIL_HOST=smtp.example.com
EMAIL_HOST_USER=postmaster@example.com
EMAIL_HOST_PASSWORD=change-me
EMAIL_USE_TLS=true
EMAIL_PORT=587
# Any other app-specific env vars here
EOF
```

Most commands below assume `docker-compose.deploy.yml` (fallback: `docker-compose-deploy.yml`). Adjust paths to match your repo.

## First-time app setup
Identify your Django service name from the compose file (commonly `web` or `app`). Replace `<web_service>` below accordingly.

Build images and start stack:
```bash
# Start in detached mode
sudo docker compose -f docker-compose.deploy.yml --env-file .env.production up -d --build
```

Run database migrations and create a superuser:
```bash
sudo docker compose -f docker-compose.deploy.yml exec -T <web_service> python manage.py migrate
sudo docker compose -f docker-compose.deploy.yml exec -T <web_service> python manage.py createsuperuser
```

Collect static files (if not baked into your image):
```bash
sudo docker compose -f docker-compose.deploy.yml exec -T <web_service> python manage.py collectstatic --noinput
```

Check health:
```bash
sudo docker compose -f docker-compose.deploy.yml ps
sudo docker compose -f docker-compose.deploy.yml logs --tail=100
```

## HTTPS (Let’s Encrypt)
You can terminate TLS on the host (e.g., host nginx) or inside Docker (nginx container). Use certbot for automatic renewals.

- Host nginx: set up nginx to proxy to your app and use certbot on the host.
- Dockerized nginx: run certbot on the host but reload the container after renewal with a deploy hook.

Install the renewal cron with the helper script (already provided in this repo):
```bash
# Host nginx reload
sudo bash scripts/setup-backups.sh \
  --setup-certbot \
  --certbot-schedule "17 4 * * *" \
  --certbot-cmd "certbot renew -q" \
  --certbot-deploy-hook "systemctl reload nginx"

# OR: Dockerized nginx reload
sudo bash scripts/setup-backups.sh \
  --setup-certbot \
  --certbot-schedule "17 4 * * *" \
  --certbot-cmd "certbot renew -q" \
  --certbot-deploy-hook "docker compose -f docker-compose.deploy.yml exec -T nginx nginx -s reload"
```

If this is the first issuance, run certbot once interactively to obtain the initial cert (host nginx scenario):
```bash
# Example for nginx on host; adjust to your domain/email
sudo certbot certonly --nginx -d yourdomain.com -m you@example.com --agree-tos --no-eff-email
```

## Backups (SQLite + Media)
Manual one-shot backup:
```bash
bash scripts/backup-all.sh --compose-file docker-compose.deploy.yml
```

Automatic backups with disk space checks and pruning (cron):
```bash
# Installs/updates a cron entry with sensible defaults
sudo bash scripts/setup-backups.sh \
  --backup-schedule "2 3 * * *" \
  --compose-file docker-compose.deploy.yml \
  --min-free-gb 2 \
  --keep-days 14
```

See details in `docs/ops-backup-restore.md`.

## System maintenance (OS updates, safe reboot, auto-start)
Enable unattended security updates with auto-reboot, auto-start your compose stack on boot, and ensure a fresh backup exists before the reboot window:
```bash
# Auto-reboot at 04:30 and start compose on boot
sudo bash scripts/setup-maintenance.sh \
  --reboot-time "04:30" \
  --install-systemd-compose

# Install a pre-reboot backup guard 30 minutes before reboot (if latest backup > 6h old)
sudo bash scripts/setup-maintenance.sh \
  --reboot-time "04:30" \
  --install-pre-reboot-guard \
  --pre-guard-offset-min 30 \
  --pre-guard-max-age-hours 6
```
- Logs:
  - Backup: `/var/log/nadooit-backup-auto.log` (if configured) or cron mail
  - Pre-reboot guard: `/var/log/nadooit-pre-reboot-backup.log`
  - Certbot renew: `/var/log/letsencrypt/renew.log` (root)

## Monitoring & operations
- Check running services:
  ```bash
  sudo docker compose -f docker-compose.deploy.yml ps
  sudo docker compose -f docker-compose.deploy.yml logs --tail=200
  ```
- Crontab entries:
  ```bash
  sudo crontab -l
  ```
- Backup files: `backups/sqlite/` and `backups/media/`
- Restore guide: see `docs/ops-backup-restore.md`

## Security & hardening (recommended)
- Enable UFW and allow ports: `sudo ufw allow OpenSSH && sudo ufw allow 80 && sudo ufw allow 443 && sudo ufw enable`
- Keep SSH keys (avoid passwords), disable root SSH login
- Regular offsite copy of backups (rsync/S3)
- Rotate Docker logs if needed (daemon.json)

## Troubleshooting
- See `docs/troubleshooting.md`
- Check compose service names, environment variables, and that DNS points to the server
- Verify `ALLOWED_HOSTS` includes your domain

## Scaling later
- SQLite is default for simplicity. CockroachDB is optional and not enabled by default; a migration script will be added later when scaling is needed.

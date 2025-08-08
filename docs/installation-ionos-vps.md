# Installation on IONOS VPS (Dev & Production)

This guide walks you through installing NADOO-IT on an IONOS VPS from scratch. It covers production setup with HTTPS (recommended) and an optional development setup on the VPS. SQLite is the default database. CockroachDB is optional.

Quickstart (copy/paste)
```bash
# 0) SSH to VPS and create user
sudo adduser nadooit && sudo usermod -aG sudo nadooit && su - nadooit

# 1) Install Docker + Compose + git (Ubuntu)
sudo apt-get update && sudo apt-get install -y ca-certificates curl gnupg git \
  && sudo install -m 0755 -d /etc/apt/keyrings \
  && curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
  && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null \
  && sudo apt-get update \
  && sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin \
  && sudo usermod -aG docker $USER && newgrp docker

# 2) Clone repo
git clone https://github.com/NADOOIT/NADOO-IT.git && cd NADOO-IT

# 3) Create .env (edit values!)
cat > .env <<'EOF'
DJANGO_SECRET_KEY=$(python3 - <<PY
import secrets
print(secrets.token_urlsafe(50))
PY
)
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=example.com,www.example.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://example.com,https://www.example.com
DOMAIN=example.com
ACME_DEFAULT_EMAIL=admin@example.com
EOF

# 4) First deploy (HTTPS)
docker compose -f docker-compose.deploy.yml build && \
docker compose -f docker-compose.deploy.yml run --rm certbot /opt/certify-init.sh && \
docker compose -f docker-compose.deploy.yml run --rm app python manage.py migrate && \
docker compose -f docker-compose.deploy.yml run --rm app python manage.py collectstatic --noinput && \
docker compose -f docker-compose.deploy.yml run --rm app python manage.py import_templates && \
docker compose -f docker-compose.deploy.yml run --rm app python manage.py createsuperuser && \
docker compose -f docker-compose.deploy.yml up -d

# Open https://example.com and login at /admin
```

Prerequisites
- An IONOS VPS running Ubuntu 22.04 LTS or 24.04 LTS
- Recommended size: 2 vCPU, 4 GB RAM, 40+ GB SSD (smaller may work for demos; increase for heavier workloads)
- A domain name you control (e.g., example.com)
- DNS A record pointing your domain (and www subdomain) to the VPS public IPv4 (propagation can take up to 30 minutes)
- SSH access to the VPS
- IONOS Cloud Firewall: allow inbound TCP 80 and 443 to the VPS; optionally 8000 if using the dev stack

1) Prepare the server
1. SSH to your VPS as the default user (or root)
2. Create a dedicated user:
   ```bash
   sudo adduser nadooit
   sudo usermod -aG sudo nadooit
   su - nadooit
   ```
3. Install Docker Engine and Compose plugin (Ubuntu):
   ```bash
   sudo apt-get update
   sudo apt-get install -y ca-certificates curl gnupg
   sudo install -m 0755 -d /etc/apt/keyrings
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
   echo \
     "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
     $(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
     sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   sudo apt-get update
   sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin git
   sudo usermod -aG docker $USER
   newgrp docker
   docker --version
   docker compose version
   ```
4. (Recommended) Enable UFW firewall:
   ```bash
   sudo ufw allow OpenSSH
   sudo ufw allow 'Nginx Full'   # opens 80 and 443
   # For dev server on port 8000 (optional):
   # sudo ufw allow 8000/tcp
   sudo ufw enable
   sudo ufw status verbose
   ```

2) Get the code
```bash
cd ~
git clone https://github.com/NADOOIT/NADOO-IT.git
cd NADOO-IT
```

3) Create .env (SQLite default)
Create a `.env` file at the repo root with values like:
```env
# Django
DJANGO_SECRET_KEY=<secure-generated-key>
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=example.com,www.example.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://example.com,https://www.example.com

# Optional
OPENAI_API_KEY=
NADOOIT__API_KEY=
NADOOIT__USER_CODE=

# Proxy / certificates
DOMAIN=example.com
ACME_DEFAULT_EMAIL=admin@example.com
```
For CockroachDB (optional), add the variables in docs/database.md and ensure `root.crt` is available at `/home/django/.postgresql/root.crt` inside containers (see below).

4) Persist uploads (static/media) and optionally SQLite
Static and media are already persisted using named volumes and shared with the proxy container.
To persist the SQLite DB across rebuilds, bind-mount the DB file by adding one line to the `app` service in `docker-compose.deploy.yml`:
```yaml
services:
  app:
    volumes:
      - static_data:/vol/web/static
      - media_data:/vol/web/media
      - /opt/nadooit/sqlite/db.sqlite3:/app/db.sqlite3  # add this line
```
Then create the host directory and empty file:
```bash
sudo mkdir -p /opt/nadooit/sqlite
sudo touch /opt/nadooit/sqlite/db.sqlite3
sudo chown -R $USER:$USER /opt/nadooit/sqlite
```

5) (Optional) CockroachDB Cloud CA certificate
If you enable CockroachDB, place the CA file on the host and ensure the container can read it. For example:
```bash
mkdir -p ~/.postgresql
# place root.crt here (download from Cockroach Cloud) as ~/.postgresql/root.crt
```
The compose files map this into `/home/django/.postgresql/root.crt` for the app and worker containers.

6) First-time production deployment (HTTPS)
```bash
# Build images
docker compose -f docker-compose.deploy.yml build

# Initialize certificates (Let’s Encrypt)
docker compose -f docker-compose.deploy.yml run --rm certbot /opt/certify-init.sh

# Run migrations and collect assets
docker compose -f docker-compose.deploy.yml run --rm app python manage.py migrate
docker compose -f docker-compose.deploy.yml run --rm app python manage.py collectstatic --noinput

# Import website templates and create admin user
docker compose -f docker-compose.deploy.yml run --rm app python manage.py import_templates
docker compose -f docker-compose.deploy.yml run --rm app python manage.py createsuperuser

# Start the stack
docker compose -f docker-compose.deploy.yml up -d
```
Access:
- App: https://example.com
- Admin: https://example.com/admin

7) Updates (pull new code)
```bash
git pull

docker compose -f docker-compose.deploy.yml build

docker compose -f docker-compose.deploy.yml run --rm app python manage.py migrate
docker compose -f docker-compose.deploy.yml run --rm app python manage.py collectstatic --noinput
docker compose -f docker-compose.deploy.yml run --rm app python manage.py import_templates

docker compose -f docker-compose.deploy.yml up -d
```

8) Logs
```bash
docker compose -f docker-compose.deploy.yml logs -f app
# other services: proxy, certbot, celery_worker, redis
```

9) Development on the VPS (optional)
You can run the development stack on the VPS on port 8000. This uses Django’s dev server with a self-signed cert.
```bash
docker compose -f docker-compose-dev.yml build
docker compose -f docker-compose-dev.yml up
```
Access:
- https://<server-ip>:8000 (accept the self-signed certificate)
- Admin: https://<server-ip>:8000/admin

Notes:
- Consider restricting port 8000 to your IP only (via UFW or cloud firewall), or use SSH port forwarding instead of opening 8000 publicly.
- For everyday development, running locally on your laptop is recommended. See docs/running.md.

Troubleshooting & references
- Troubleshooting: docs/troubleshooting.md
- Database options (CockroachDB): docs/database.md
- Configuration (env vars): docs/configuration.md
- Operations (backups/updates/logs): docs/operations.md
- Architecture & services: docs/architecture.md, docs/apps-and-services.md

# Testing Guide

This project uses pytest + pytest-django. Tests can be run locally, via tox, or inside Docker Compose.

## Quickstart (local)
1. Create and activate a virtualenv (recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install --upgrade pip
   pip install -r requirements-dev.txt
   ```
2. Run tests:
   ```bash
   pytest -q
   ```
3. With coverage:
   ```bash
   pytest --cov=app --cov-report term:skip-covered --cov-report html:cov_html
   # Open coverage report:
   open cov_html/index.html  # macOS
   # xdg-open cov_html/index.html  # Linux
   ```

Notes:
- `pytest.ini` sets `DJANGO_SETTINGS_MODULE=nadooit.settings` and `--reuse-db` so test DBs are reused across runs.
- Default DB is SQLite; no external services are required.

## Using tox
Tox isolates dependencies and runs tests in a clean venv.
```bash
# Format check (Black)
tox -e format

# Run tests on py310 env
tox -e py310
```
Outputs:
- Coverage HTML will be written to `cov_html/` at repo root (configured in tox.ini).

## Running tests in Docker Compose (dev image)
If you prefer containerized runs using the dev image:
```bash
# Build images (if not built yet)
docker compose -f docker-compose-dev.yml build

# Run pytest inside the app container
# (use sh -lc to ensure the shell evaluates the full command)
docker compose -f docker-compose-dev.yml run --rm app sh -lc "pytest -q"

# With coverage written into the mounted working directory
docker compose -f docker-compose-dev.yml run --rm app sh -lc \
  "pytest --cov=app --cov-report term:skip-covered --cov-report html:cov_html"
```
Artifacts:
- The `./app` directory is mounted into the container; `cov_html/` will appear under `app/` if run from that directory. You can also move or open it as needed.

## Tips
- Run a single test file:
  ```bash
  pytest app/nadooit_website/test_services.py -q
  ```
- Run tests by keyword:
  ```bash
  pytest -k "service and not slow" -q
  ```
- Show verbose output:
  ```bash
  pytest -vv
  ```
- Stop on first failure:
  ```bash
  pytest -x
  ```

## Troubleshooting
- If imports fail, ensure your venv is active and dependencies from `requirements-dev.txt` are installed.
- If DB migration errors occur, try clearing the test DB cache:
  ```bash
  pytest --create-db
  ```
- If running inside Docker, make sure images are up-to-date:
  ```bash
  docker compose -f docker-compose-dev.yml build --no-cache
  ```

# Testing Guide

This project uses pytest + pytest-django. Tests can be run locally, via tox, or inside Docker Compose.

## Baseline and dependencies
- Baseline framework: Django 4.2 LTS
- Default DB: SQLite (no external services). CockroachDB is optional and aligns with `django-cockroachdb 4.2`.
- Key pins for test stability:
  - `asgiref==3.8.1` (DRF compatibility)
  - `moviepy<2.0` (restores `moviepy.editor` import style)
  - `django-debug-toolbar` compatible with Django 4.2
- SQLite limitation: `DISTINCT ON` is not supported. Where queries previously used `.distinct("contract__customer")`, the code uses a Python-side dedup helper, making tests DB-agnostic (SQLite/Postgres/Cockroach).

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

## Containerized tests (CI-like)
For reproducible, host-agnostic runs, use the dedicated Compose file:
```bash
docker compose -f docker-compose-test.yml run --rm test
```
This mirrors the CI environment and avoids local toolchain inconsistencies.

Outputs:
- Coverage summary printed to terminal
- Coverage XML written to `coverage.xml` at repo root (configured via `--cov-config=app/.coveragerc`)

Notes:
- If you see a Compose warning about a top-level `version:` key, it is safe to remove that key from the YAML to silence the warning (Compose v2 no longer requires it).
- The test container runs with working directory `app/` and uses `--cov=.` to collect coverage reliably inside the container.

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

Artifacts:
- The `./app` directory is mounted into the container; `cov_html/` will appear under `app/` if run from that directory. You can also move or open it as needed.

Variants (OS/DB-specific dev files exist when you need a particular backend):
- macOS + SQLite: `docker-compose-dev-MAC_SQLite.yml`
- macOS + MySQL: `docker-compose-dev-MAC_MYSQL.yml`
- macOS + CockroachDB: `docker-compose-dev-MAC_COCKROACHDB.yml`
- Windows variants: `docker-compose-dev-WIN_*.yml`

Example (macOS + SQLite):
```bash
docker compose -f docker-compose-dev-MAC_SQLite.yml run --rm app python -m pytest -v
```

## CI and Coverage Gate
Tests run automatically in GitHub Actions on every push/PR using Python 3.10. The workflows upload `coverage.xml` (and diff-cover reports) as artifacts.

- Full test suite: `.github/workflows/tests.yml`
- Changed-lines coverage (diff-cover): `.github/workflows/coverage.yml`
- Coverage config: `app/.coveragerc` (repo-root local runs) and `.coveragerc` when the working directory is `app/` (e.g., `docker-compose-test.yml`).
- Pytest gate: a minimum coverage threshold is enforced via `pytest.ini` (`--cov-fail-under=50`).
  - Start at 50% to avoid blocking; raise the threshold as we add tests (ratchet strategy).
- Diff-cover gate: PRs must maintain ≥80% coverage on changed lines. CI generates:
  - `coverage.xml`
  - `diff-cover.html`
  - `diff-cover.md`

PR Checklist expectations (see `.github/pull_request_template.md`):
- Tests added/updated for all changes
- All tests pass locally or via containerized runs
- Global coverage does not decrease
- Changed-lines coverage ≥ 80%
- Docs updated where relevant

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

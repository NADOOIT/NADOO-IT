# Export tests/docs/CI only (no app code)

Goal: Create and push an export branch that contains ONLY tests, docs, and CI config from your feature branch, based on a clean `main`. Do NOT bring over app code changes or large/log files. We will merge this export into our integration branch on our side.

## Branch and base
- **Base**: `origin/main`
- **Feature source**: `feat/section-orders-marker-deploy-2025-08-08` (adjust if different)
- **New branch to push**: `export/feature-tests-docs-clean`

## Primary (modern Git) commands
```bash
# Ensure repo and up-to-date refs
git rev-parse --show-toplevel
git fetch origin

# Create export branch from main (clean base)
git switch -c export/feature-tests-docs-clean origin/main

# Bring over ONLY tests/docs/CI from the feature branch
# NOTE: Adjust the feature branch name below if different
git restore --source feat/section-orders-marker-deploy-2025-08-08 --staged --worktree -- \
 ':(glob)app/**/tests/**' \
 ':(glob)app/**/test_*.py' \
 ':(glob)docs/**' \
 ':(glob)app/docs/**' \
 ':(glob).github/workflows/**' \
 'pytest.ini' \
 'tox.ini' \
 'conftest.py' \
 'requirements-dev.txt' \
 'requirements.txt'

# Defense-in-depth: ensure logs/pycache won't be included
printf "\n# Ignore logs\napp/logs/*.log\n" >> .gitignore
printf "\n# Python cache\n**/__pycache__\n*.pyc\n" >> .gitignore

# Commit and push
git add -A
git commit -m "export: tests/docs/CI from feature branch (no app code; ignore logs/pycache)"
git push -u origin export/feature-tests-docs-clean
```

## Fallback (older Git without pathspec globs in restore)
```bash
# Start from the same export branch on main
git switch -c export/feature-tests-docs-clean origin/main

# Checkout paths from the feature branch (adjust branch name if needed)
# This checks out directories/files into the working tree without merging the whole branch
git checkout feat/section-orders-marker-deploy-2025-08-08 -- \
 app/*/tests \
 app/*/test_*.py \
 docs \
 app/docs \
 .github/workflows \
 pytest.ini \
 tox.ini \
 conftest.py \
 requirements-dev.txt \
 requirements.txt

# Ignore logs/pycache
printf "\n# Ignore logs\napp/logs/*.log\n" >> .gitignore
printf "\n# Python cache\n**/__pycache__\n*.pyc\n" >> .gitignore

# Commit and push
git add -A
git commit -m "export: tests/docs/CI from feature branch (fallback checkout; no app code)"
git push -u origin export/feature-tests-docs-clean
```

## Sanity checks before pushing (optional but recommended)
- **Paths limited**: `git diff --name-only origin/main... | sed 's/^/- /'`
  - Expect only:
    - `app/<app>/tests/**` and `app/<app>/test_*.py`
    - `docs/**`, `app/docs/**`
    - `.github/workflows/**`
    - `pytest.ini`, `tox.ini`, `conftest.py`, `requirements*.txt`
- **No app-code changes**: No `.py` files outside test directories should appear (except config listed above).
- **No large files**: Ensure no `app/logs/*.log` or large assets are tracked.

## Report back
- Reply with: the branch name `export/feature-tests-docs-clean` and a short summary (number of files changed, notable directories).
- Do NOT merge anything else. We will pull and merge this branch into our integration branch on our side.

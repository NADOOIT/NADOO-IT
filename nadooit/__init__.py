"""Proxy package to make `nadooit.*` importable when running from repo root.

This package redirects Python's package search for `nadooit` submodules to
`app/nadooit`, so `DJANGO_SETTINGS_MODULE = nadooit.settings` works even when
`app/` is not on `sys.path` (e.g., running `pytest` from the repository root).
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "app" / "nadooit"

# Ensure submodules (e.g., nadooit.settings) are found under app/nadooit
if TARGET.exists():
    __path__ = [str(TARGET)]  # type: ignore[name-defined]
else:
    # Fallback: add app/ to sys.path so imports still succeed in unusual setups
    app_dir = ROOT / "app"
    if str(app_dir) not in sys.path:
        sys.path.insert(0, str(app_dir))

"""Proxy package to app/django_is_url_active_templatetag.

Provides import compatibility when running from the repository root without
manually adding `app/` to PYTHONPATH.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "app" / "django_is_url_active_templatetag"

if TARGET.exists():
    __path__ = [str(TARGET)]  # type: ignore[name-defined]
else:
    app_dir = ROOT / "app"
    if str(app_dir) not in sys.path:
        sys.path.insert(0, str(app_dir))

# Ensure the Django project package under ./app is importable as `nadooit`
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent
APP_DIR = ROOT / "app"

# Insert immediately when conftest is imported (for normal test collection)
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))


@pytest.hookimpl(tryfirst=True)
def pytest_load_initial_conftests(args, early_config, parser):
    """Ensure app/ is on sys.path before pytest-django tries to import settings.

    This runs very early in pytest startup.
    """
    if str(APP_DIR) not in sys.path:
        sys.path.insert(0, str(APP_DIR))

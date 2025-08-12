# Ensure the Django project package under ./app is importable as `nadooit`
# as early as possible, before plugins (e.g., pytest-django) try to import settings.
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP_DIR = ROOT / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

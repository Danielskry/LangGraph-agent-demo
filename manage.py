#!/usr/bin/env python
"""Thin wrapper manage.py that makes the `frontend` Django project runnable from repo root.

It adds the `frontend` directory to sys.path so `webapp` can be imported as a top-level package,
then delegates to Django's command-line utility (same behavior as `frontend/manage.py`).
"""
import os
import sys
from pathlib import Path

# Ensure the frontend package is importable when running from repository root
REPO_ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = str(REPO_ROOT / "frontend")
if FRONTEND_DIR not in sys.path:
    sys.path.insert(0, FRONTEND_DIR)

# Use the project's settings module (webapp.settings inside frontend)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapp.settings')

if __name__ == '__main__':
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

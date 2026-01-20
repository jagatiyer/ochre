#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Enforce virtualenv activation early to prevent accidental system Python usage.
    if not (os.environ.get("VIRTUAL_ENV") or os.environ.get("PYENV_VIRTUAL_ENV") or getattr(sys, "base_prefix", None) != getattr(sys, "prefix", None)):
        sys.stderr.write(
            "ERROR: Virtual environment not activated.\n"
            "Please run: source venv/bin/activate\n"
        )
        sys.exit(1)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ochre.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

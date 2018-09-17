#!/usr/bin/env python
import os
import sys

inc_paths = ['/home/users/zzhu/DJANGO/DJANGO', '/home/users/zzhu/DJANGO/DJANGO/DJANGO',
             '/home/users/zzhu/DJANGO/APMOS_WEB','/home/users/zzhu/DJANGO']
for p in inc_paths:
    if p not in sys.path:
        sys.path.append(p)

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DJANGO.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

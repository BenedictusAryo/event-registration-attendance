"""
WSGI config for event_registration_attendance project for cPanel deployment.

This file is used by Passenger (commonly used in cPanel Python hosting).
It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path
from django.core.wsgi import get_wsgi_application

# Add the project directory to the sys.path
project_home = str(Path(__file__).resolve().parent)
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_registration_attendance.settings_production')

# Get the WSGI application
application = get_wsgi_application()

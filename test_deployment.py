#!/usr/bin/env python3
"""
Quick deployment test script for Django application.
Run this on your server to test basic Django functionality.
"""

import os
import sys
from pathlib import Path

def test_django_setup():
    """Test Django configuration and setup."""
    print("=== Django Deployment Test ===")
    
    try:
        # Test Python version
        print(f"Python version: {sys.version}")
        
        # Test Django import
        import django
        print(f"Django version: {django.get_version()}")
        
        # Test project structure
        project_home = Path(__file__).resolve().parent
        print(f"Project directory: {project_home}")
        
        # Test settings import
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_registration_attendance.settings_production')
        
        from django.conf import settings
        django.setup()
        
        print(f"SECRET_KEY exists: {'Yes' if settings.SECRET_KEY else 'No'}")
        print(f"DEBUG mode: {settings.DEBUG}")
        print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        print(f"Database engine: {settings.DATABASES['default']['ENGINE']}")
        
        # Test database connection
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"Database connection: {'OK' if result else 'Failed'}")
        
        # Test static files
        print(f"STATIC_URL: {settings.STATIC_URL}")
        print(f"STATIC_ROOT: {settings.STATIC_ROOT}")
        print(f"MEDIA_URL: {settings.MEDIA_URL}")
        print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
        
        print("✅ Django setup test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Django setup test failed: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_django_setup()
    sys.exit(0 if success else 1)

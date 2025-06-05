#!/usr/bin/env python3
"""
Quick setup script to test production settings locally.
This helps verify your production configuration before deployment.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr}")
        return False

def main():
    """Main setup function."""
    print("🧪 Testing Production Configuration Locally")
    print("=" * 50)
    
    # Set production settings
    os.environ['DJANGO_SETTINGS_MODULE'] = 'event_registration_attendance.settings_production'
    
    # Test settings import
    try:
        import django
        from django.conf import settings
        django.setup()
        print("✅ Production settings loaded successfully")
    except Exception as e:
        print(f"❌ Error loading production settings: {e}")
        return False
    
    # Check for required settings
    required_settings = ['SECRET_KEY', 'ALLOWED_HOSTS', 'DATABASES']
    for setting in required_settings:
        if hasattr(settings, setting):
            print(f"✅ {setting} is configured")
        else:
            print(f"❌ {setting} is missing")
    
    # Test database connection
    print("\n🔄 Testing database connection...")
    try:
        from django.db import connection
        connection.ensure_connection()
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
    
    # Test static files collection
    print("\n🔄 Testing static files collection...")
    if run_command("python manage.py collectstatic --noinput --dry-run", "Collecting static files (dry run)"):
        print("✅ Static files configuration is correct")
    
    # Check for security settings
    security_settings = [
        ('DEBUG', False),
        ('SECURE_SSL_REDIRECT', True),
        ('SESSION_COOKIE_SECURE', True),
        ('CSRF_COOKIE_SECURE', True),
    ]
    
    print("\n🔒 Checking security settings...")
    for setting, expected_value in security_settings:
        actual_value = getattr(settings, setting, None)
        if actual_value == expected_value:
            print(f"✅ {setting} = {actual_value}")
        else:
            print(f"⚠️  {setting} = {actual_value} (expected {expected_value})")
    
    print("\n✅ Production configuration test completed!")
    print("\n📝 Recommendations:")
    print("1. Make sure to update ALLOWED_HOSTS with your actual domain")
    print("2. Set a strong SECRET_KEY for production")
    print("3. Configure proper email settings")
    print("4. Test the application with DEBUG=False before deployment")

if __name__ == "__main__":
    main()

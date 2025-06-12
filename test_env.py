#!/usr/bin/env python3
"""
Test script to verify environment variables are loaded correctly.
Run this on your server to debug the ALLOWED_HOSTS issue.
"""

import os
import sys
from pathlib import Path

def test_env_loading():
    """Test environment variable loading."""
    print("=== Environment Variables Test ===")
    
    # Add project directory to path
    project_home = Path(__file__).resolve().parent
    if str(project_home) not in sys.path:
        sys.path.insert(0, str(project_home))
    
    print(f"Project directory: {project_home}")
    
    # Test .env file existence
    env_file = project_home / '.env'
    print(f".env file exists: {env_file.exists()}")
    
    if env_file.exists():
        print(f".env file path: {env_file}")
        with open(env_file, 'r') as f:
            lines = f.readlines()
        print(f".env file has {len(lines)} lines")
        
        # Show ALLOWED_HOSTS line
        for line_num, line in enumerate(lines, 1):
            if 'ALLOWED_HOSTS' in line:
                print(f"Line {line_num}: {line.strip()}")
    
    # Load environment manually (same as in settings)
    def load_env_file():
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ.setdefault(key.strip(), value.strip())
    
    print("\n=== Before loading .env ===")
    print(f"ALLOWED_HOSTS from env: {os.environ.get('ALLOWED_HOSTS', 'NOT SET')}")
    
    load_env_file()
    
    print("\n=== After loading .env ===")
    print(f"ALLOWED_HOSTS from env: {os.environ.get('ALLOWED_HOSTS', 'NOT SET')}")
    
    # Test Django settings import
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_registration_attendance.settings_production')
        from django.conf import settings
        import django
        django.setup()
        
        print(f"\nDjango ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        print(f"Django DEBUG: {settings.DEBUG}")
        print(f"Django SECRET_KEY exists: {'Yes' if settings.SECRET_KEY else 'No'}")
        
        return True
        
    except Exception as e:
        print(f"\nError importing Django settings: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_env_loading()
    print(f"\n{'✅ Success' if success else '❌ Failed'}")

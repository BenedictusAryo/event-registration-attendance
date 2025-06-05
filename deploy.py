#!/usr/bin/env python3
"""
Deployment script for Django application on shared hosting.
Run this script after uploading your files to the hosting server.
"""

import os
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}:")
        print(f"Command: {command}")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main deployment function."""
    print("🚀 Starting Django Application Deployment")
    print("=" * 50)
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    print(f"📁 Working directory: {project_dir}")
    
    # Check if virtual environment exists
    venv_path = project_dir / "venv"
    if not venv_path.exists():
        print("⚠️  Virtual environment not found. Creating one...")
        if not run_command("python3 -m venv venv", "Creating virtual environment"):
            print("❌ Failed to create virtual environment. Please create it manually.")
            return False
    
    # Activate virtual environment and install requirements
    if os.name == 'nt':  # Windows
        pip_path = venv_path / "Scripts" / "pip"
        python_path = venv_path / "Scripts" / "python"
    else:  # Unix/Linux
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"
    
    # Install requirements
    if not run_command(f"{pip_path} install -r requirements.txt", "Installing Python packages"):
        print("❌ Failed to install requirements")
        return False
    
    # Collect static files
    if not run_command(f"{python_path} manage.py collectstatic --noinput --settings=event_registration_attendance.settings_production", "Collecting static files"):
        print("❌ Failed to collect static files")
        return False
    
    # Run migrations
    if not run_command(f"{python_path} manage.py migrate --settings=event_registration_attendance.settings_production", "Running database migrations"):
        print("❌ Failed to run migrations")
        return False
    
    # Create superuser (optional)
    print("\n📝 Would you like to create a superuser? (y/n)")
    create_superuser = input().lower().strip()
    if create_superuser in ['y', 'yes']:
        print("Creating superuser...")
        os.system(f"{python_path} manage.py createsuperuser --settings=event_registration_attendance.settings_production")
    
    print("\n🎉 Deployment completed successfully!")
    print("\n📋 Next steps:")
    print("1. Update your domain in settings_production.py (ALLOWED_HOSTS and SITE_URL)")
    print("2. Configure your email settings in settings_production.py")
    print("3. Set up SSL certificate for HTTPS")
    print("4. Test your application")
    print("\n🔧 Useful commands:")
    print(f"   - Collect static files: {python_path} manage.py collectstatic --settings=event_registration_attendance.settings_production")
    print(f"   - Run migrations: {python_path} manage.py migrate --settings=event_registration_attendance.settings_production")
    print(f"   - Create superuser: {python_path} manage.py createsuperuser --settings=event_registration_attendance.settings_production")

if __name__ == "__main__":
    main()

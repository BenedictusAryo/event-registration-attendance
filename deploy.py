#!/usr/bin/env python3
"""
Deployment script for Django application on shared hosting.
Run this script after uploading your files to the hosting server.
"""

import os
import subprocess
import argparse
from pathlib import Path

def load_environment():
    """Load environment variables from .env file."""
    env_file = Path(__file__).parent / '.env'
    
    if not env_file.exists():
        print("⚠️  .env file not found. Creating from template...")
        template_file = Path(__file__).parent / '.env.template'
        if template_file.exists():
            import shutil
            shutil.copy(template_file, env_file)
            print(f"✅ Created .env from template. Please edit {env_file} with your actual values.")
            return False
        else:
            print("❌ No .env.template found. Please create a .env file manually.")
            return False
    
    try:
        # Try to use python-dotenv if available
        from dotenv import load_dotenv
        load_dotenv(env_file)
        print(f"✅ Loaded environment variables from {env_file}")
        return True
    except ImportError:
        # Fallback: manual loading
        print("⚠️  python-dotenv not found. Loading .env manually...")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print(f"✅ Manually loaded environment variables from {env_file}")
        return True

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
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Deploy Django application to shared hosting')
    parser.add_argument('--no-venv', action='store_true', 
                       help='Skip virtual environment creation and use system Python')
    args = parser.parse_args()
    
    print("🚀 Starting Django Application Deployment")
    print("=" * 50)
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    print(f"📁 Working directory: {project_dir}")
    
    # Load environment variables first
    if not load_environment():
        print("❌ Failed to load environment variables. Please fix .env file and try again.")
        return False
    
    # Display key configuration
    print("\n🔧 Environment Configuration:")
    print(f"   DATABASE_ENGINE: {os.environ.get('DATABASE_ENGINE', 'Not set')}")
    print(f"   ALLOWED_HOSTS: {os.environ.get('ALLOWED_HOSTS', 'Not set')}")
    print(f"   SITE_URL: {os.environ.get('SITE_URL', 'Not set')}")
    print(f"   EMAIL_HOST: {os.environ.get('EMAIL_HOST', 'Not set')}")
    
    # Handle virtual environment based on --no-venv flag
    if args.no_venv:
        print("\n⚠️  Skipping virtual environment creation (--no-venv flag)")
        print("   Using system Python installation")
        pip_path = "pip"
        python_path = "python"
    else:
        # Check if virtual environment exists
        venv_path = project_dir / "venv"
        if not venv_path.exists():
            print("⚠️  Virtual environment not found. Creating one...")
            if not run_command("python3 -m venv venv", "Creating virtual environment"):
                print("❌ Failed to create virtual environment. Please create it manually.")
                return False
        
        # Set paths for virtual environment
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
    print("\n📋 Configuration Status:")
    print("   ✅ Environment variables loaded from .env")
    print(f"   ✅ Database: {os.environ.get('DATABASE_ENGINE', 'sqlite3').split('.')[-1]}")
    print(f"   ✅ Domain: {os.environ.get('SITE_URL', 'Not configured')}")
    print(f"   ✅ Email: {os.environ.get('EMAIL_HOST', 'Not configured')}")
    if args.no_venv:
        print("   ⚠️  Using system Python (no virtual environment)")
    else:
        print("   ✅ Virtual environment configured")
    print("\n📋 Next steps:")
    print("1. Verify your domain is accessible")
    print("2. Test user registration and email sending")
    print("3. Set up SSL certificate for HTTPS")
    print("4. Create events and test QR code generation")
    print("\n🔧 Useful commands:")
    print(f"   - Collect static files: {python_path} manage.py collectstatic --settings=event_registration_attendance.settings_production")
    print(f"   - Run migrations: {python_path} manage.py migrate --settings=event_registration_attendance.settings_production")
    print(f"   - Create superuser: {python_path} manage.py createsuperuser --settings=event_registration_attendance.settings_production")
    print(f"   - Test email: {python_path} manage.py shell --settings=event_registration_attendance.settings_production")

if __name__ == "__main__":
    main()

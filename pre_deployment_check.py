"""
Pre-Deployment Checklist for Django Application

This script verifies your application is ready for deployment to shared hosting.
Run this before uploading your files to cPanel.
"""

import os
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a file exists and report status."""
    if Path(file_path).exists():
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - MISSING")
        return False

def check_settings_configuration():
    """Check production settings configuration."""
    print("\n🔧 Checking Production Settings Configuration...")
    
    settings_file = Path("event_registration_attendance/settings_production.py")
    if not settings_file.exists():
        print("❌ Production settings file missing")
        return False
    
    # Read settings file
    with open(settings_file, 'r') as f:
        content = f.read()
    
    checks = [
        ("DEBUG = False", "Debug mode disabled"),
        ("ALLOWED_HOSTS", "Allowed hosts configured"),
        ("SECURE_SSL_REDIRECT", "SSL redirect enabled"),
        ("SESSION_COOKIE_SECURE", "Secure session cookies"),
        ("CSRF_COOKIE_SECURE", "Secure CSRF cookies"),
    ]
    
    for check, description in checks:
        if check in content:
            print(f"✅ {description}")
        else:
            print(f"⚠️  {description} - needs attention")
    
    return True

def check_dependencies():
    """Check if all required dependencies are listed."""
    print("\n📦 Checking Dependencies...")
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ requirements.txt missing")
        return False
    
    with open(requirements_file, 'r') as f:
        requirements = f.read().lower()
    
    required_packages = [
        ("django", "Django framework"),
        ("pillow", "Image processing"),
        ("qrcode", "QR code generation"),
    ]
    
    for package, description in required_packages:
        if package in requirements:
            print(f"✅ {description}")
        else:
            print(f"⚠️  {description} - may be missing")
    
    return True

def check_security():
    """Check security configurations."""
    print("\n🔒 Security Checklist...")
    
    # Check .gitignore
    gitignore_file = Path(".gitignore")
    if gitignore_file.exists():
        with open(gitignore_file, 'r') as f:
            gitignore_content = f.read()
        
        security_items = [
            (".env", "Environment files ignored"),
            ("*.log", "Log files ignored"),
            ("db.sqlite3", "Database files ignored"),
            ("__pycache__", "Python cache ignored"),
        ]
        
        for item, description in security_items:
            if item in gitignore_content:
                print(f"✅ {description}")
            else:
                print(f"⚠️  {description} - consider adding")
    else:
        print("⚠️  .gitignore file missing")
    
    return True

def check_static_files():
    """Check static files configuration."""
    print("\n📁 Static Files Configuration...")
    
    # Check if static directory exists
    static_dir = Path("static")
    if static_dir.exists():
        print("✅ Static directory exists")
    else:
        print("⚠️  Static directory missing")
    
    # Check CSS files
    css_files = list(Path("static").glob("**/*.css")) if static_dir.exists() else []
    js_files = list(Path("static").glob("**/*.js")) if static_dir.exists() else []
    
    print(f"📊 Found {len(css_files)} CSS files and {len(js_files)} JS files")
    
    return True

def check_media_configuration():
    """Check media files configuration."""
    print("\n🖼️  Media Files Configuration...")
    
    media_dir = Path("media")
    if media_dir.exists():
        print("✅ Media directory exists")
        
        # Check subdirectories
        qr_dir = media_dir / "qr_codes"
        event_dir = media_dir / "event_images"
        
        if qr_dir.exists():
            print("✅ QR codes directory exists")
        else:
            print("⚠️  QR codes directory missing - will be created automatically")
            
        if event_dir.exists():
            print("✅ Event images directory exists")
        else:
            print("⚠️  Event images directory missing - will be created automatically")
    else:
        print("⚠️  Media directory missing - will be created automatically")
    
    return True

def main():
    """Main checklist function."""
    print("🚀 Pre-Deployment Checklist for Django Application")
    print("=" * 60)
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    print(f"📁 Project Directory: {project_dir}")
    print()
    
    # Essential files check
    print("📋 Essential Files Check...")
    essential_files = [
        ("requirements.txt", "Python dependencies file"),
        ("passenger_wsgi.py", "WSGI configuration for cPanel"),
        ("event_registration_attendance/settings_production.py", "Production settings"),
        (".htaccess", "Web server configuration"),
        ("manage.py", "Django management script"),
    ]
    
    files_ok = True
    for file_path, description in essential_files:
        if not check_file_exists(file_path, description):
            files_ok = False
    
    if not files_ok:
        print("\n❌ Some essential files are missing. Please create them before deployment.")
        return False
    
    # Run other checks
    check_settings_configuration()
    check_dependencies()
    check_security()
    check_static_files()
    check_media_configuration()
    
    print("\n" + "=" * 60)
    print("🎯 Deployment Readiness Summary:")
    print()
    print("✅ All essential files are present")
    print("📝 Please review the warnings above and address them if needed")
    print()
    print("🚀 Your application appears ready for deployment!")
    print()
    print("📋 Final steps before deployment:")
    print("1. Update ALLOWED_HOSTS in settings_production.py with your domain")
    print("2. Generate a new SECRET_KEY for production")
    print("3. Configure database settings (if using MySQL)")
    print("4. Set up email configuration")
    print("5. Create a ZIP file of your project")
    print("6. Upload to your cPanel hosting")
    print()
    print("📖 See DEPLOYMENT_GUIDE.md for detailed instructions")

if __name__ == "__main__":
    main()

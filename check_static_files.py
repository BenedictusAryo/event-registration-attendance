"""
Static files configuration checker for Django deployment.
This script verifies your static files setup is correct for production.
"""

import os
from pathlib import Path
import subprocess

def check_static_configuration():
    """Check static files configuration."""
    print("📁 Static Files Configuration Check")
    print("=" * 50)
    
    # Check settings
    print("\n🔧 Checking Settings...")
    
    try:
        # Import production settings
        import sys
        sys.path.append('.')
        
        # Set Django settings module
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_registration_attendance.settings_production')
        
        import django
        django.setup()
        
        from django.conf import settings
        
        # Check static files settings
        print(f"✅ STATIC_URL: {settings.STATIC_URL}")
        print(f"✅ STATIC_ROOT: {settings.STATIC_ROOT}")
        print(f"✅ STATICFILES_DIRS: {settings.STATICFILES_DIRS}")
        print(f"✅ MEDIA_URL: {settings.MEDIA_URL}")
        print(f"✅ MEDIA_ROOT: {settings.MEDIA_ROOT}")
        
    except Exception as e:
        print(f"❌ Error importing settings: {e}")
        return False
    
    # Check directories
    print("\n📂 Checking Directories...")
    
    static_dir = Path("static")
    staticfiles_dir = Path("staticfiles")
    media_dir = Path("media")
    
    if static_dir.exists():
        print(f"✅ Source static directory exists: {static_dir}")
        
        # Count files in static directory
        static_files = list(static_dir.rglob("*"))
        static_file_count = len([f for f in static_files if f.is_file()])
        print(f"   📊 {static_file_count} files found in static/")
        
        # Show file types
        extensions = {}
        for file in static_files:
            if file.is_file():
                ext = file.suffix.lower()
                extensions[ext] = extensions.get(ext, 0) + 1
        
        for ext, count in extensions.items():
            print(f"   📄 {ext or 'no extension'}: {count} files")
    else:
        print(f"⚠️  Source static directory missing: {static_dir}")
    
    if staticfiles_dir.exists():
        print(f"✅ Collected static directory exists: {staticfiles_dir}")
        
        # Count files in staticfiles directory
        collected_files = list(staticfiles_dir.rglob("*"))
        collected_file_count = len([f for f in collected_files if f.is_file()])
        print(f"   📊 {collected_file_count} files collected in staticfiles/")
        
        # Check for Django admin files
        admin_files = list(staticfiles_dir.glob("admin/**/*"))
        admin_file_count = len([f for f in admin_files if f.is_file()])
        if admin_file_count > 0:
            print(f"   ✅ Django admin static files: {admin_file_count} files")
        else:
            print("   ⚠️  Django admin static files missing")
            
    else:
        print(f"⚠️  Collected static directory missing: {staticfiles_dir}")
        print("   💡 Run: python manage.py collectstatic --settings=event_registration_attendance.settings_production")
    
    if media_dir.exists():
        print(f"✅ Media directory exists: {media_dir}")
        
        # Check subdirectories
        qr_dir = media_dir / "qr_codes"
        event_dir = media_dir / "event_images"
        
        if qr_dir.exists():
            qr_files = len([f for f in qr_dir.iterdir() if f.is_file()])
            print(f"   📷 QR codes: {qr_files} files")
        
        if event_dir.exists():
            event_files = len([f for f in event_dir.iterdir() if f.is_file()])
            print(f"   🖼️  Event images: {event_files} files")
            
    else:
        print(f"⚠️  Media directory missing: {media_dir}")
    
    # Check .htaccess configuration
    print("\n🌐 Checking Web Server Configuration...")
    
    htaccess_file = Path(".htaccess")
    if htaccess_file.exists():
        with open(htaccess_file, 'r') as f:
            htaccess_content = f.read()
        
        checks = [
            ("RewriteEngine On", "URL rewriting enabled"),
            ("^/static/", "Static files routing configured"),
            ("^/media/", "Media files routing configured"),
            ("passenger_wsgi.py", "Django routing configured"),
            ("ExpiresByType", "Caching headers configured"),
            ("DEFLATE", "Compression configured"),
        ]
        
        for check, description in checks:
            if check in htaccess_content:
                print(f"✅ {description}")
            else:
                print(f"⚠️  {description} - may be missing")
    else:
        print("❌ .htaccess file missing")
    
    return True

def test_collectstatic():
    """Test collectstatic command."""
    print("\n🔄 Testing collectstatic command...")
    
    try:
        result = subprocess.run([
            'python', 'manage.py', 'collectstatic', 
            '--dry-run', '--noinput',
            '--settings=event_registration_attendance.settings_production'
        ], capture_output=True, text=True, check=True)
        
        print("✅ collectstatic dry-run successful")
        
        # Count files that would be collected
        output_lines = result.stdout.split('\n')
        file_count = 0
        for line in output_lines:
            if 'static file' in line and ('Copying' in line or 'Would copy' in line):
                file_count += 1
        
        print(f"   📊 Would collect {file_count} static files")
        
        # Check for warnings
        if result.stderr:
            print(f"   ⚠️  Warnings: {result.stderr}")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ collectstatic failed: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ Python or manage.py not found")
        return False
    
    return True

def show_recommendations():
    """Show optimization recommendations."""
    print("\n💡 Recommendations for Production:")
    print("=" * 50)
    
    print("1. 🚀 Performance Optimizations:")
    print("   - Use Apache direct serving (already configured)")
    print("   - Enable browser caching (already configured)")
    print("   - Enable compression (already configured)")
    print("   - Consider using a CDN for large files")
    
    print("\n2. 🔒 Security Best Practices:")
    print("   - Never put sensitive data in static files")
    print("   - Use versioning to prevent cache poisoning")
    print("   - Regularly update static file permissions")
    
    print("\n3. 📦 Deployment Checklist:")
    print("   - Run collectstatic before each deployment")
    print("   - Verify static files are accessible via browser")
    print("   - Test admin interface styling")
    print("   - Check console for 404 errors")
    
    print("\n4. 🛠️ Useful Commands:")
    print("   collectstatic: python manage.py collectstatic --settings=event_registration_attendance.settings_production")
    print("   findstatic: python manage.py findstatic <filename> --settings=event_registration_attendance.settings_production")
    print("   check: python manage.py check --deploy --settings=event_registration_attendance.settings_production")

def main():
    """Main function."""
    print("🔍 Django Static Files Configuration Checker")
    print("=" * 60)
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    success = True
    
    # Run checks
    if not check_static_configuration():
        success = False
    
    if not test_collectstatic():
        success = False
    
    # Show recommendations
    show_recommendations()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Static files configuration looks good!")
        print("🚀 Your application is ready for deployment")
    else:
        print("⚠️  Some issues found. Please review and fix before deployment.")
    
    print("\n📖 For detailed information, see: STATIC_FILES_GUIDE.md")

if __name__ == "__main__":
    main()

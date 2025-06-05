"""
Create deployment package for cPanel shared hosting.
This script creates a clean ZIP file ready for upload to your hosting provider.
"""

import os
import zipfile
import shutil
from pathlib import Path
from datetime import datetime

def should_exclude(file_path, exclude_patterns):
    """Check if a file should be excluded from the package."""
    path_str = str(file_path).lower()
    
    for pattern in exclude_patterns:
        if pattern in path_str:
            return True
    return False

def create_deployment_package():
    """Create a deployment-ready ZIP package."""
    print("📦 Creating Deployment Package for cPanel")
    print("=" * 50)
    
    # Define what to exclude from the package
    exclude_patterns = [
        '__pycache__',
        '.git',
        '.pytest_cache',
        '.vscode',
        '.idea',
        '*.pyc',
        '*.log',
        'logs/',
        '.env',
        'venv/',
        'env/',
        'node_modules/',
        '.DS_Store',
        'Thumbs.db',
        '*.bak',
        '*.backup',
        'ssl/',
    ]
    
    # Create package directory
    package_name = f"event-registration-app-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    package_dir = Path(package_name)
    
    if package_dir.exists():
        shutil.rmtree(package_dir)
    
    package_dir.mkdir()
    
    print(f"📁 Creating package: {package_name}")
    
    # Copy essential files and directories
    project_root = Path(".")
    
    essential_items = [
        "manage.py",
        "passenger_wsgi.py",
        ".htaccess",
        "requirements.txt",
        "deploy.py",
        "DEPLOYMENT_GUIDE.md",
        "event_registration_attendance/",
        "core/",
        "events/",
        "checkin/",
        "templates/",
        "static/",
        "media/",
    ]
    
    copied_files = 0
    skipped_files = 0
    
    for item in essential_items:
        source_path = project_root / item
        
        if not source_path.exists():
            print(f"⚠️  {item} not found, skipping...")
            continue
        
        dest_path = package_dir / item
        
        try:
            if source_path.is_file():
                # Copy file
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, dest_path)
                copied_files += 1
                print(f"✅ Copied: {item}")
            
            elif source_path.is_dir():
                # Copy directory
                for root, dirs, files in os.walk(source_path):
                    root_path = Path(root)
                    
                    # Skip excluded directories
                    if should_exclude(root_path, exclude_patterns):
                        skipped_files += len(files)
                        continue
                    
                    # Create directory structure
                    rel_path = root_path.relative_to(project_root)
                    dest_dir = package_dir / rel_path
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Copy files
                    for file in files:
                        file_path = root_path / file
                        
                        if should_exclude(file_path, exclude_patterns):
                            skipped_files += 1
                            continue
                        
                        dest_file = dest_dir / file
                        shutil.copy2(file_path, dest_file)
                        copied_files += 1
                
                print(f"✅ Copied directory: {item}")
        
        except Exception as e:
            print(f"❌ Error copying {item}: {e}")
    
    # Create additional helpful files
    print("\n📝 Creating additional deployment files...")
    
    # Create a deployment checklist
    checklist_content = """# Deployment Checklist for cPanel

## Before Upload:
- [ ] Update ALLOWED_HOSTS in settings_production.py with your domain
- [ ] Generate new SECRET_KEY for production
- [ ] Configure email settings
- [ ] Set up database (MySQL recommended)

## After Upload to cPanel:
- [ ] Create Python App in cPanel
- [ ] Set Application Root to your domain folder
- [ ] Set Startup File to: passenger_wsgi.py
- [ ] Install requirements: pip install -r requirements.txt
- [ ] Run migrations: python manage.py migrate --settings=event_registration_attendance.settings_production
- [ ] Collect static files: python manage.py collectstatic --noinput --settings=event_registration_attendance.settings_production
- [ ] Create superuser: python manage.py createsuperuser --settings=event_registration_attendance.settings_production
- [ ] Test your application

## Quick Commands:
```bash
# Install dependencies
pip install -r requirements.txt

# Run deployment script (automated)
python deploy.py

# Or run manually:
python manage.py migrate --settings=event_registration_attendance.settings_production
python manage.py collectstatic --noinput --settings=event_registration_attendance.settings_production
python manage.py createsuperuser --settings=event_registration_attendance.settings_production
```

## Support:
- Check DEPLOYMENT_GUIDE.md for detailed instructions
- Verify passenger_wsgi.py is in the root directory
- Ensure .htaccess is properly configured
"""
    
    with open(package_dir / "DEPLOYMENT_CHECKLIST.md", "w") as f:
        f.write(checklist_content.strip())
    
    # Create ZIP file
    zip_filename = f"{package_name}.zip"
    print(f"\n🗜️  Creating ZIP file: {zip_filename}")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = Path(root) / file
                arc_name = file_path.relative_to(package_dir)
                zipf.write(file_path, arc_name)
    
    # Clean up temporary directory
    shutil.rmtree(package_dir)
    
    # Get file size
    zip_size = Path(zip_filename).stat().st_size / (1024 * 1024)  # MB
    
    print(f"\n🎉 Deployment package created successfully!")
    print(f"📦 Package: {zip_filename}")
    print(f"📊 Size: {zip_size:.1f} MB")
    print(f"📁 Files copied: {copied_files}")
    print(f"🚫 Files skipped: {skipped_files}")
      print(f"\n📋 Next steps:")
    print(f"1. Upload {zip_filename} to your cPanel File Manager")
    print("2. Extract the ZIP file in your domain's public_html folder")
    print("3. Follow the DEPLOYMENT_CHECKLIST.md inside the package")
    print("4. Set up Python Application in cPanel")
    print("5. Run the deployment commands")
    
    return zip_filename

if __name__ == "__main__":
    try:
        create_deployment_package()
    except KeyboardInterrupt:
        print("\n\n❌ Package creation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error creating package: {e}")
        print("Please check the error and try again.")

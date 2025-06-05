# Django Event Registration App - Deployment Guide for Shared Hosting (cPanel)

This guide will help you deploy your Django Event Registration and Attendance application on shared hosting with cPanel Python support.

## Prerequisites

1. **Shared hosting account** with Python 3.8+ support
2. **cPanel access** with Python application management
3. **Domain name** configured to point to your hosting
4. **SSH access** (optional but recommended)

## Pre-Deployment Checklist

### 1. Prepare Your Files

Before uploading, make sure you have all the necessary files:

- ✅ `requirements.txt` - Python package dependencies
- ✅ `passenger_wsgi.py` - WSGI configuration for cPanel
- ✅ `settings_production.py` - Production settings
- ✅ `.htaccess` - URL rewriting and security headers
- ✅ `deploy.py` - Deployment automation script

### 2. Update Configuration Files

#### A. Update Production Settings (`event_registration_attendance/settings_production.py`)

```python
# Update these values:
ALLOWED_HOSTS = [
    'your-domain.com',
    'www.your-domain.com',
]

SITE_URL = 'https://your-domain.com'

# If using MySQL (recommended for production):
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'your_database_name',
        'USER': 'your_database_user',  
        'PASSWORD': 'your_database_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

# Email configuration
EMAIL_HOST = 'smtp.your-hosting-provider.com'
EMAIL_HOST_USER = 'your-email@your-domain.com'
EMAIL_HOST_PASSWORD = 'your-email-password'
```

#### B. Generate a New Secret Key

Use Django's built-in command to generate a secure secret key:

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

Update the `SECRET_KEY` in your production settings.

## Deployment Steps

### Step 1: Upload Files

1. **Create a ZIP file** of your project directory
2. **Upload via cPanel File Manager** or FTP to your domain's public_html folder
3. **Extract the files** in the public_html directory

### Step 2: Set Up Python Application in cPanel

1. **Log into cPanel**
2. **Find "Python App" or "Setup Python App"** in the Software section
3. **Create a new Python application:**
   - Python Version: 3.8+ (use the highest available)
   - Application Root: `/public_html` (or your domain folder)
   - Application URL: Leave blank for root domain
   - Application startup file: `passenger_wsgi.py`
   - Application Entry point: `application`

### Step 3: Install Dependencies

1. **Access the Python app terminal** in cPanel, or use SSH
2. **Navigate to your project directory:**
   ```bash
   cd /home/yourusername/public_html
   ```
3. **Install requirements:**
   ```bash
   pip install -r requirements.txt
   ```

### Step 4: Configure Database

#### Option A: SQLite (Simple, for small apps)
No additional configuration needed. The SQLite file will be created automatically.

#### Option B: MySQL (Recommended for production)
1. **Create a MySQL database** in cPanel
2. **Create a database user** and assign privileges
3. **Update your production settings** with database credentials
4. **Install MySQL client:**
   ```bash
   pip install mysqlclient
   ```

### Step 5: Run Deployment Commands

You can either run the automated deployment script or execute commands manually:

#### Option A: Automated (Recommended)
```bash
python deploy.py
```

#### Option B: Manual Commands
```bash
# Collect static files
python manage.py collectstatic --noinput --settings=event_registration_attendance.settings_production

# Run database migrations
python manage.py migrate --settings=event_registration_attendance.settings_production

# Create superuser (optional)
python manage.py createsuperuser --settings=event_registration_attendance.settings_production
```

### Step 6: Configure Media Files

1. **Create media directory:**
   ```bash
   mkdir -p media/qr_codes
   mkdir -p media/event_images
   ```

2. **Set proper permissions:**
   ```bash
   chmod 755 media
   chmod 755 media/qr_codes
   chmod 755 media/event_images
   ```

### Step 7: Test Your Application

1. **Visit your domain** in a web browser
2. **Check that the homepage loads** correctly
3. **Test user registration and login**
4. **Create a test event** and verify QR code generation
5. **Test the admin panel** at `your-domain.com/admin/`

## Post-Deployment Configuration

### 1. Set Up SSL Certificate

Most shared hosting providers offer free SSL certificates:

1. **Enable SSL** in cPanel
2. **Force HTTPS redirects** (already configured in `.htaccess`)
3. **Update SITE_URL** in settings to use `https://`

### 2. Configure Email

Set up SMTP settings with your hosting provider's email service:

```python
# In settings_production.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.your-domain.com'  # Your hosting provider's SMTP server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'noreply@your-domain.com'
EMAIL_HOST_PASSWORD = 'your-email-password'
```

### 3. Set Up Scheduled Tasks (Cron Jobs)

If your app needs periodic tasks, set them up in cPanel:

1. **Go to "Cron Jobs"** in cPanel
2. **Add commands** like:
   ```bash
   cd /home/yourusername/public_html && python manage.py your_custom_command --settings=event_registration_attendance.settings_production
   ```

## Troubleshooting

### Common Issues and Solutions

#### 1. Application Not Loading
- **Check Python app logs** in cPanel
- **Verify passenger_wsgi.py** is in the correct location
- **Ensure all dependencies** are installed

#### 2. Static Files Not Loading
- **Run collectstatic** command
- **Check STATIC_ROOT** and STATIC_URL settings
- **Verify .htaccess** file is present

#### 3. Database Connection Errors
- **Check database credentials** in settings
- **Ensure database exists** and user has proper permissions
- **Verify database engine** is correctly specified

#### 4. Permission Errors
- **Set proper file permissions:**
  ```bash
  find . -type f -exec chmod 644 {} \;
  find . -type d -exec chmod 755 {} \;
  chmod 755 passenger_wsgi.py
  ```

#### 5. QR Code Generation Issues
- **Ensure media directory** exists and is writable
- **Check Pillow installation:**
  ```bash
  pip install --upgrade Pillow
  ```

## Maintenance

### Regular Tasks

1. **Update dependencies** periodically:
   ```bash
   pip install -r requirements.txt --upgrade
   ```

2. **Backup your database** regularly through cPanel

3. **Monitor application logs** for errors

4. **Keep Django updated** for security patches

### Updating Your Application

1. **Upload new files** to replace existing ones
2. **Install any new dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run migrations** if database changes:
   ```bash
   python manage.py migrate --settings=event_registration_attendance.settings_production
   ```
4. **Collect static files** if assets changed:
   ```bash
   python manage.py collectstatic --noinput --settings=event_registration_attendance.settings_production
   ```
5. **Restart the Python application** in cPanel

## Security Considerations

1. **Never commit sensitive data** to version control
2. **Use environment variables** for secrets
3. **Keep Django and dependencies updated**
4. **Monitor for security advisories**
5. **Use strong passwords** for admin accounts
6. **Enable two-factor authentication** if available

## Support

If you encounter issues:

1. **Check the deployment logs** in cPanel
2. **Review Django documentation** for shared hosting
3. **Contact your hosting provider** for Python-specific issues
4. **Check Django community forums** for similar problems

## Files Created for Deployment

- `requirements.txt` - Package dependencies
- `passenger_wsgi.py` - WSGI configuration for cPanel
- `settings_production.py` - Production-optimized settings
- `.htaccess` - Web server configuration and security
- `deploy.py` - Automated deployment script
- `.env.template` - Environment variables template

Your Django Event Registration application is now ready for deployment on shared hosting with cPanel!

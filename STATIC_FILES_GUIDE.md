# Static Files Serving Guide for Django on cPanel

## Overview
This guide explains how static files are served in your Django application deployed on cPanel shared hosting.

## Static Files Strategy

### 1. **Development vs Production**

#### Development (with DEBUG=True):
- Django serves static files automatically
- No web server configuration needed
- Files served from `STATICFILES_DIRS` and app `static/` folders

#### Production (with DEBUG=False):
- Django does NOT serve static files
- Web server (Apache/Nginx) must handle static files
- Files served from `STATIC_ROOT` after `collectstatic`

### 2. **File Locations**

```
your-domain/
├── static/                 # Source static files (STATICFILES_DIRS)
│   ├── css/
│   ├── js/
│   └── images/
├── staticfiles/           # Collected static files (STATIC_ROOT)
│   ├── admin/            # Django admin static files
│   ├── css/
│   ├── js/
│   └── images/
└── media/                # User uploaded files (MEDIA_ROOT)
    ├── qr_codes/
    └── event_images/
```

### 3. **How Static Files Are Served**

#### Method 1: Apache Direct Serving (Recommended - Faster)
```apache
# In .htaccess
RewriteEngine On

# Serve static files directly (bypass Django)
RewriteCond %{REQUEST_URI} ^/static/
RewriteCond %{REQUEST_FILENAME} -f
RewriteRule ^.*$ - [L]

# Serve media files directly (bypass Django)
RewriteCond %{REQUEST_URI} ^/media/
RewriteCond %{REQUEST_FILENAME} -f
RewriteRule ^.*$ - [L]

# Route everything else to Django
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ passenger_wsgi.py/$1 [QSA,PT,L]
```

#### Method 2: Django Whitenoise (Alternative)
If direct serving doesn't work, you can use Whitenoise:

```python
# In requirements.txt
whitenoise

# In settings_production.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this
    # ... other middleware
]

# Optional: Enable compression and caching
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### 4. **Deployment Process**

#### Step 1: Collect Static Files
```bash
python manage.py collectstatic --noinput --settings=event_registration_attendance.settings_production
```

This command:
- Copies files from `static/` folders to `staticfiles/`
- Copies Django admin static files
- Copies third-party app static files

#### Step 2: Verify Directory Structure
After `collectstatic`, you should have:
```
staticfiles/
├── admin/              # Django admin assets
├── js/                 # Your JS files
│   ├── qr-scanner-enhanced.js
│   └── sw.js
└── [other files from your static/ directory]
```

### 5. **URL Configuration**

#### Settings:
```python
STATIC_URL = '/static/'           # URL prefix for static files
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Where collectstatic puts files
STATICFILES_DIRS = [              # Source directories
    BASE_DIR / 'static',
]

MEDIA_URL = '/media/'             # URL prefix for media files
MEDIA_ROOT = BASE_DIR / 'media'   # Where user uploads go
```

#### In Templates:
```html
{% load static %}
<link rel="stylesheet" href="{% static 'css/style.css' %}">
<script src="{% static 'js/app.js' %}"></script>
```

### 6. **Troubleshooting Static Files**

#### Common Issues:

1. **Static files not loading (404 errors)**
   ```bash
   # Check if collectstatic was run
   python manage.py collectstatic --noinput --settings=event_registration_attendance.settings_production
   
   # Check file permissions
   chmod -R 755 staticfiles/
   ```

2. **CSS/JS not updating**
   ```bash
   # Clear and recollect static files
   rm -rf staticfiles/
   python manage.py collectstatic --noinput --settings=event_registration_attendance.settings_production
   ```

3. **Admin interface has no styling**
   ```bash
   # Django admin static files missing
   python manage.py collectstatic --noinput --settings=event_registration_attendance.settings_production
   ```

#### Debug Commands:
```bash
# List what Django will collect
python manage.py collectstatic --dry-run --settings=event_registration_attendance.settings_production

# Find static files
python manage.py findstatic admin/css/base.css --settings=event_registration_attendance.settings_production
```

### 7. **Performance Optimization**

#### Caching Headers (in .htaccess):
```apache
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresByType text/css "access plus 1 month"
    ExpiresByType application/javascript "access plus 1 month"
    ExpiresByType image/png "access plus 1 month"
    ExpiresByType image/jpg "access plus 1 month"
    ExpiresByType image/jpeg "access plus 1 month"
    ExpiresByType image/gif "access plus 1 month"
    ExpiresByType image/svg+xml "access plus 1 month"
</IfModule>
```

#### Compression (in .htaccess):
```apache
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/css
    AddOutputFilterByType DEFLATE application/javascript
    AddOutputFilterByType DEFLATE text/html
</IfModule>
```

### 8. **Security Considerations**

- Static files are publicly accessible
- Don't put sensitive data in static files
- Use versioning to prevent caching issues
- Consider CDN for large applications

### 9. **Alternative: CDN Integration**

For better performance, you can use a CDN:

```python
# settings_production.py
STATIC_URL = 'https://your-cdn.com/static/'
```

## Summary

Your current setup uses **Apache direct serving** which is the most efficient method for shared hosting:

1. ✅ Static files are served directly by Apache (fast)
2. ✅ Media files are served directly by Apache (fast)
3. ✅ Only dynamic requests go to Django (efficient)
4. ✅ Caching headers are set for performance
5. ✅ Compression is enabled to reduce bandwidth

This configuration provides optimal performance for your event registration application on cPanel shared hosting.

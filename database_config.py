"""
MySQL Database Configuration Helper for Django Deployment

This script helps you configure MySQL database settings for production deployment.
Run this after creating your MySQL database in cPanel.
"""

import os
import sys
from pathlib import Path

def get_database_config():
    """Interactive database configuration setup."""
    print("🗄️  MySQL Database Configuration Setup")
    print("=" * 50)
    print("Please enter your MySQL database details from cPanel:")
    print()
    
    # Get database information
    db_name = input("Database Name: ").strip()
    db_user = input("Database User: ").strip()
    db_password = input("Database Password: ").strip()
    db_host = input("Database Host (usually 'localhost'): ").strip() or 'localhost'
    db_port = input("Database Port (usually '3306'): ").strip() or '3306'
    
    # Generate configuration
    config = f"""
# MySQL Database Configuration
# Add this to your settings_production.py file

DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '{db_name}',
        'USER': '{db_user}',
        'PASSWORD': '{db_password}',
        'HOST': '{db_host}',
        'PORT': '{db_port}',
        'OPTIONS': {{
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }},
    }}
}}

# Don't forget to install mysqlclient:
# pip install mysqlclient
"""
    
    # Save to file
    config_file = Path(__file__).parent / 'mysql_config.txt'
    with open(config_file, 'w') as f:
        f.write(config.strip())
    
    print(f"\n✅ Database configuration saved to: {config_file}")
    print("\n📋 Next steps:")
    print("1. Install mysqlclient: pip install mysqlclient")
    print("2. Update your settings_production.py with the configuration above")
    print("3. Run migrations: python manage.py migrate --settings=event_registration_attendance.settings_production")
    
    return config

def test_mysql_connection():
    """Test MySQL connection with provided credentials."""
    try:
        import MySQLdb
        print("✅ MySQLdb is available")
    except ImportError:
        try:
            import pymysql
            print("✅ PyMySQL is available")
        except ImportError:
            print("❌ No MySQL client library found. Install one:")
            print("   pip install mysqlclient")
            print("   OR")
            print("   pip install pymysql")
            return False
    
    return True

if __name__ == "__main__":
    print("🔧 Database Configuration Helper")
    print()
    
    choice = input("What would you like to do?\n1. Generate database config\n2. Test MySQL connection\n3. Both\nChoice (1-3): ").strip()
    
    if choice in ['1', '3']:
        get_database_config()
    
    if choice in ['2', '3']:
        print("\n" + "="*50)
        test_mysql_connection()

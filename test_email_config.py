"""
Test email configuration to verify environment variables are properly loaded
"""
import os
import sys
from pathlib import Path

def test_email_config():
    """Test email configuration with environment variables"""
    print("📧 Testing Email Configuration with Environment Variables")
    print("=" * 60)
    
    # Load environment variables from .env file
    env_file = Path('.env')
    if env_file.exists():
        print("✅ Loading environment variables from .env file")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print("✅ Environment variables loaded successfully")
    else:
        print("⚠️  .env file not found, using defaults")
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_registration_attendance.settings_production')
    
    # Add project to path
    project_root = Path(__file__).resolve().parent
    sys.path.insert(0, str(project_root))
    
    try:
        import django
        django.setup()
        
        from django.conf import settings
        
        print("\n🔧 Email Configuration Settings:")
        print("-" * 40)
        print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
        print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
        print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
        print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        print(f"EMAIL_USE_SSL: {settings.EMAIL_USE_SSL}")
        print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        print(f"EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'Not set'}")
        print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
        
        # Validate configuration
        print("\n✅ Configuration Validation:")
        print("-" * 40)
        
        # Check for SSL vs TLS
        if settings.EMAIL_USE_SSL and settings.EMAIL_USE_TLS:
            print("⚠️  Warning: Both EMAIL_USE_SSL and EMAIL_USE_TLS are True. Only one should be True.")
        elif settings.EMAIL_USE_SSL:
            print("✅ Using SSL encryption (recommended for port 465)")
            if settings.EMAIL_PORT != 465:
                print("⚠️  Warning: SSL is typically used with port 465")
        elif settings.EMAIL_USE_TLS:
            print("✅ Using TLS encryption (recommended for port 587)")
            if settings.EMAIL_PORT != 587:
                print("⚠️  Warning: TLS is typically used with port 587")
        else:
            print("❌ Warning: Neither SSL nor TLS is enabled. This is not secure!")
        
        # Check host and credentials
        if (settings.EMAIL_HOST and 'your-' in settings.EMAIL_HOST) or (settings.EMAIL_HOST_USER and 'your-' in settings.EMAIL_HOST_USER):
            print("❌ Email host or user contains placeholder values. Please update with real values.")
        else:
            print("✅ Email host and user appear to be configured")
        
        if settings.EMAIL_HOST_PASSWORD == 'your-email-password':
            print("❌ Email password is still a placeholder. Please update with real password.")
        else:
            print("✅ Email password appears to be configured")
        
        print("\n🎯 Configuration Summary:")
        print(f"   Protocol: {'SSL' if settings.EMAIL_USE_SSL else 'TLS' if settings.EMAIL_USE_TLS else 'None'}")
        print(f"   Server: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
        print(f"   Username: {settings.EMAIL_HOST_USER}")
        print(f"   From Address: {settings.DEFAULT_FROM_EMAIL}")
        
        # Test email import
        print("\n📨 Testing Email Import:")
        try:
            from django.core.mail import send_mail
            print("✅ Django email module imported successfully")
            
            # Note: Uncomment the following lines to send a test email
            print("\n💡 To send a test email, uncomment the following lines in the script:")
            # Actually send a test email
            print("\n📩 Sending test email...")
            try:
                send_mail(
                    'Test Email from Event Registration System',
                    'This is a test email.',
                    settings.DEFAULT_FROM_EMAIL,
                    # ['admin@event.parokibintaro.org'],
                    ['bennedictusaryo@gmail.com'],
                    fail_silently=False,
                )
                print("✅ Test email sent successfully!")
            except Exception as e:
                print(f"❌ Error sending test email: {e}")
            
        except Exception as e:
            print(f"❌ Error importing email module: {e}")
        
    except Exception as e:
        print(f"❌ Error setting up Django: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_email_config()
    if success:
        print("\n🎉 Email configuration test completed!")
    else:
        print("\n❌ Email configuration test failed!")

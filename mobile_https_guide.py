#!/usr/bin/env python3
"""
HTTPS Setup Guide for Mobile Camera Access
"""

print("""
🔧 HTTPS Setup for Mobile Camera Access
=====================================

Your Django server is running with HTTPS, but mobile browsers need to trust the certificate.

📱 ON YOUR MOBILE DEVICE:

1. Open mobile browser and go to: https://192.168.1.99:8000/
2. You'll see a security warning
3. Click "Advanced" or "Show Details"  
4. Click "Proceed to 192.168.1.99 (unsafe)" or "Accept Risk"
5. You may need to do this for a few different pages

🔒 BROWSER-SPECIFIC INSTRUCTIONS:

Chrome Mobile:
- Tap "Advanced"
- Tap "Proceed to 192.168.1.99 (unsafe)"

Safari Mobile:
- Tap "Show Details"  
- Tap "visit this website"
- Tap "Visit Website" again

Firefox Mobile:
- Tap "Advanced"
- Tap "Accept the Risk and Continue"

⚠️  IMPORTANT SECURITY NOTE:
Only do this for your local development server. Never accept untrusted 
certificates for real websites in production!

🎯 TEST THE CAMERA:
Once you've accepted the certificate, go to:
https://192.168.1.99:8000/checkin/1/scanner/

The camera should now work properly!

🔧 Alternative Solution - Use Phone as Dev Server:
If certificate issues persist, you can also:
1. Install Python on your phone (Termux for Android)
2. Run the Django server directly on mobile
3. Access via http://localhost:8000 (no HTTPS needed)
""")

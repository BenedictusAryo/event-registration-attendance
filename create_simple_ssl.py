#!/usr/bin/env python3
"""
Create simple SSL certificate for local development (fallback method)
"""
import subprocess
import sys
from pathlib import Path

def create_simple_ssl():
    """Create a simple self-signed SSL certificate"""
    
    # Create ssl directory
    ssl_dir = Path("ssl")
    ssl_dir.mkdir(exist_ok=True)
    
    cert_file = ssl_dir / "localhost.crt"
    key_file = ssl_dir / "localhost.key"
    
    try:
        # Generate private key
        print("🔑 Generating private key...")
        subprocess.run([
            'openssl', 'genrsa', '-out', str(key_file), '2048'
        ], check=True)
        
        # Generate certificate with simple subject
        print("📜 Generating certificate...")
        subprocess.run([
            'openssl', 'req', '-new', '-x509', '-key', str(key_file),
            '-out', str(cert_file), '-days', '365', '-nodes',
            '-subj', '/C=US/ST=Local/L=Local/O=Dev/CN=192.168.1.99'
        ], check=True)
        
        print("✅ Simple SSL certificate created!")
        print(f"📁 Certificate: {cert_file.absolute()}")
        print(f"🔑 Private Key: {key_file.absolute()}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating SSL certificate: {e}")
        return False

if __name__ == "__main__":
    if create_simple_ssl():
        print("\n🎉 Simple SSL setup complete!")
        print("🚀 Run: uv run manage.py runserver_plus --cert-file ssl/localhost.crt --key-file ssl/localhost.key 0.0.0.0:8000")
    else:
        print("\n❌ SSL creation failed.")

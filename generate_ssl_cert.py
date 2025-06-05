#!/usr/bin/env python3
"""
Generate self-signed SSL certificate for local development
"""
import os
import subprocess
import sys
from pathlib import Path

def generate_ssl_certificate():
    """Generate self-signed SSL certificate for local development"""
    
    # Create ssl directory
    ssl_dir = Path("ssl")
    ssl_dir.mkdir(exist_ok=True)
    
    cert_file = ssl_dir / "localhost.crt"
    key_file = ssl_dir / "localhost.key"
    
    # Check if OpenSSL is available
    try:
        subprocess.run(['openssl', 'version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ OpenSSL not found. Please install OpenSSL first.")
        print("For Windows: Download from https://slproweb.com/products/Win32OpenSSL.html")
        return False
    
    # Generate private key
    print("🔑 Generating private key...")
    subprocess.run([
        'openssl', 'genrsa', '-out', str(key_file), '2048'
    ], check=True)    # Generate certificate with multiple domains (simplified for compatibility)
    print("📜 Generating certificate...")
    
    # Create a simple config file for the certificate
    config_content = """[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = US
ST = State
L = City
O = LocalDev
CN = 192.168.1.99

[v3_req]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = 127.0.0.1
IP.1 = 127.0.0.1
IP.2 = 192.168.1.99
"""
    
    config_file = ssl_dir / "openssl.cnf"
    with open(config_file, 'w') as f:
        f.write(config_content)
    
    subprocess.run([
        'openssl', 'req', '-new', '-x509', '-key', str(key_file),
        '-out', str(cert_file), '-days', '365',
        '-config', str(config_file), '-extensions', 'v3_req'
    ], check=True)
    
    print("✅ SSL certificate generated successfully!")
    print(f"📁 Certificate: {cert_file.absolute()}")
    print(f"🔑 Private Key: {key_file.absolute()}")
    print()
    print("🚀 To run Django with HTTPS:")
    print("   pip install django-extensions")
    print("   python manage.py runserver_plus --cert-file ssl/localhost.crt --key-file ssl/localhost.key 0.0.0.0:8000")
    print()
    print("📱 Access from mobile: https://192.168.1.99:8000")
    print("⚠️  You'll need to accept the security warning on mobile browsers")
    
    return True

if __name__ == "__main__":
    if generate_ssl_certificate():
        print("\n🎉 SSL setup complete! Your Django app can now use HTTPS.")
    else:
        print("\n❌ SSL setup failed. Please install OpenSSL and try again.")

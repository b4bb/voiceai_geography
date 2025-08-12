"""
Create a simple self-signed certificate for development.
"""
import os
from pathlib import Path
import subprocess

def create_cert():
    """Create a simple self-signed certificate"""
    certs_dir = Path(__file__).parent.parent.parent / 'certs'
    certs_dir.mkdir(exist_ok=True)
    
    key_path = certs_dir / 'key.pem'
    cert_path = certs_dir / 'cert.pem'
    
    # Create private key and certificate in one step
    subprocess.run([
        'openssl', 'req',
        '-x509',
        '-newkey', 'rsa:2048',
        '-keyout', str(key_path),
        '-out', str(cert_path),
        '-days', '365',
        '-nodes',
        '-subj', '/CN=localhost',
        '-addext', 'subjectAltName=DNS:localhost,DNS:127.0.0.1'
    ], check=True)
    
    print("\n✅ Certificate created successfully!")
    print(f"Key path:  {key_path}")
    print(f"Cert path: {cert_path}")
    
    print("\nTo trust this certificate on macOS:")
    print("1. Open Keychain Access")
    print("2. Make sure 'Login' is selected under 'Default Keychains'")
    print(f"3. File > Import Items > Select {cert_path}")
    print("4. Find the imported 'localhost' certificate")
    print("5. Double click it")
    print("6. Expand 'Trust'")
    print("7. Set 'When using this certificate' to 'Always Trust'")

if __name__ == "__main__":
    create_cert()

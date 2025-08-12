"""
Create a self-signed certificate that's more suitable for local development.
This creates a certificate with proper Subject Alternative Names (SAN) for localhost.
"""
import os
from pathlib import Path
import subprocess
import sys

def create_trusted_cert():
    """Create a more developer-friendly self-signed certificate"""
    # Create certs directory if it doesn't exist
    certs_dir = Path(__file__).parent.parent.parent / 'certs'
    certs_dir.mkdir(exist_ok=True)
    
    key_path = certs_dir / 'key.pem'
    cert_path = certs_dir / 'cert.pem'
    pfx_path = certs_dir / 'certificate.pfx'  # Added PKCS#12 format
    config_path = certs_dir / 'openssl.cnf'
    
    # Create OpenSSL config with SAN
    config_content = """[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_req
prompt = no

[req_distinguished_name]
C = US
ST = California
L = San Francisco
O = Development
OU = Development Team
CN = localhost

[v3_req]
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:TRUE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment, keyCertSign
extendedKeyUsage = serverAuth, clientAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = 127.0.0.1
"""
    
    # Write OpenSSL config
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    try:
        # Create private key and certificate
        subprocess.run([
            'openssl', 'req',
            '-x509',
            '-nodes',  # No passphrase
            '-newkey', 'rsa:2048',
            '-keyout', str(key_path),
            '-out', str(cert_path),
            '-days', '365',
            '-config', str(config_path)
        ], check=True)

        # Create PKCS#12 format certificate
        subprocess.run([
            'openssl', 'pkcs12',
            '-export',
            '-out', str(pfx_path),
            '-inkey', str(key_path),
            '-in', str(cert_path),
            '-passout', 'pass:development',  # Simple development password
            '-name', 'localhost'
        ], check=True)
        
        # Clean up config file
        os.remove(config_path)
        
        print("\n✅ Development certificates created successfully!")
        print(f"Key path:  {key_path}")
        print(f"Cert path: {cert_path}")
        print(f"PKCS#12 path: {pfx_path}")
        
        print("\nTo trust this certificate on macOS:")
        print("1. Open Keychain Access")
        print("2. Make sure 'Login' is selected under 'Default Keychains'")
        print(f"3. File > Import Items > Select {pfx_path}")
        print("4. When prompted for password, enter: development")
        print("5. Find the imported 'localhost' certificate")
        print("   (If you don't see it, make sure 'All Items' is selected at the top)")
        print("6. Double click the certificate")
        print("7. Expand 'Trust'")
        print("8. Set 'When using this certificate' to 'Always Trust'")
        
        # Update .env file
        env_path = Path(__file__).parent / '.env'
        if not env_path.exists():
            print("\nCreating .env file...")
            with open(env_path, 'w') as f:
                f.write(f"SSL_KEY_PATH={key_path}\n")
                f.write(f"SSL_CERT_PATH={cert_path}\n")
        else:
            print("\nUpdating .env file...")
            with open(env_path, 'r') as f:
                lines = f.readlines()
            
            # Remove existing SSL paths
            lines = [l for l in lines if not l.startswith(('SSL_KEY_PATH=', 'SSL_CERT_PATH='))]
            
            # Add new SSL paths
            lines.append(f"SSL_KEY_PATH={key_path}\n")
            lines.append(f"SSL_CERT_PATH={cert_path}\n")
            
            with open(env_path, 'w') as f:
                f.writelines(lines)
        
        print("\n✅ .env file updated with certificate paths")
        print("\nAfter trusting the certificate, restart your browser and run:")
        print("python run_server.py")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error creating certificates: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_trusted_cert()
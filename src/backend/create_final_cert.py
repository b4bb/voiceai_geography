"""
Create a final version of the certificates with proper chain and extensions.
"""
import os
from pathlib import Path
import subprocess
import sys

def create_certs():
    """Create root CA and server certificate with proper chain"""
    # Create certs directory if it doesn't exist
    certs_dir = Path(__file__).parent.parent.parent / 'certs'
    certs_dir.mkdir(exist_ok=True)
    
    # Define paths
    ca_key_path = certs_dir / 'ca.key'
    ca_cert_path = certs_dir / 'ca.pem'
    server_key_path = certs_dir / 'key.pem'
    server_cert_path = certs_dir / 'cert.pem'
    config_path = certs_dir / 'openssl.cnf'
    
    # Create OpenSSL config
    config_content = """[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_ca
prompt = no

[req_distinguished_name]
C = US
ST = California
L = San Francisco
O = Development CA
OU = Development Team
CN = Development Root CA

[v3_ca]
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer
basicConstraints = critical, CA:true
keyUsage = critical, digitalSignature, cRLSign, keyCertSign

[v3_server]
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid,issuer:always
basicConstraints = critical, CA:false
keyUsage = critical, digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth, clientAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = 127.0.0.1
"""
    
    try:
        # Write OpenSSL config
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        print("Creating root CA...")
        # Create root CA key
        subprocess.run([
            'openssl', 'genrsa',
            '-out', str(ca_key_path),
            '4096'
        ], check=True)
        
        # Create root CA certificate
        subprocess.run([
            'openssl', 'req',
            '-x509',
            '-new',
            '-nodes',
            '-key', str(ca_key_path),
            '-sha384',
            '-days', '365',
            '-out', str(ca_cert_path),
            '-config', str(config_path),
            '-extensions', 'v3_ca'
        ], check=True)
        
        print("Creating server certificate...")
        # Create server key
        subprocess.run([
            'openssl', 'genrsa',
            '-out', str(server_key_path),
            '2048'
        ], check=True)
        
        # Create server CSR
        server_config = config_content.replace(
            'Development Root CA',
            'localhost'
        ).replace(
            'Development CA',
            'Development Server'
        )
        with open(config_path, 'w') as f:
            f.write(server_config)
        
        # Create and sign server certificate
        subprocess.run([
            'openssl', 'req',
            '-new',
            '-key', str(server_key_path),
            '-out', str(server_cert_path) + '.csr',
            '-config', str(config_path)
        ], check=True)
        
        subprocess.run([
            'openssl', 'x509',
            '-req',
            '-in', str(server_cert_path) + '.csr',
            '-CA', str(ca_cert_path),
            '-CAkey', str(ca_key_path),
            '-CAcreateserial',
            '-out', str(server_cert_path),
            '-days', '365',
            '-sha384',
            '-extfile', str(config_path),
            '-extensions', 'v3_server'
        ], check=True)
        
        # Clean up
        os.remove(str(server_cert_path) + '.csr')
        os.remove(config_path)
        
        print("\n✅ Certificates created successfully!")
        print(f"CA Certificate:     {ca_cert_path}")
        print(f"Server Key:         {server_key_path}")
        print(f"Server Certificate: {server_cert_path}")
        
        print("\nNow run:")
        print("1. Remove the old certificate from Keychain Access if it exists")
        print("2. Add the new CA certificate to the system:")
        print(f"   security add-trusted-cert -d -r trustRoot -k ~/Library/Keychains/login.keychain-db {ca_cert_path}")
        print("3. Restart your browser")
        print("4. Run the server:")
        print("   python run_server.py")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error creating certificates: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_certs()

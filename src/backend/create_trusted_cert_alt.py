"""
Alternative approach to create a self-signed certificate using a root CA.
"""
import os
from pathlib import Path
import subprocess
import sys

def create_trusted_cert():
    """Create a root CA and server certificate"""
    # Create certs directory if it doesn't exist
    certs_dir = Path(__file__).parent.parent.parent / 'certs'
    certs_dir.mkdir(exist_ok=True)
    
    # Define paths
    ca_key_path = certs_dir / 'ca.key'
    ca_cert_path = certs_dir / 'ca.pem'
    server_key_path = certs_dir / 'key.pem'
    server_csr_path = certs_dir / 'server.csr'
    server_cert_path = certs_dir / 'cert.pem'
    
    try:
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
            '-sha256',
            '-days', '365',
            '-out', str(ca_cert_path),
            '-subj', '/C=US/ST=California/L=San Francisco/O=Development CA/OU=Development Team/CN=Development Root CA'
        ], check=True)

        print("Creating server certificate...")
        # Create server key
        subprocess.run([
            'openssl', 'genrsa',
            '-out', str(server_key_path),
            '2048'
        ], check=True)

        # Create server CSR
        subprocess.run([
            'openssl', 'req',
            '-new',
            '-key', str(server_key_path),
            '-out', str(server_csr_path),
            '-subj', '/C=US/ST=California/L=San Francisco/O=Development/OU=Development Team/CN=localhost'
        ], check=True)

        # Create server certificate
        subprocess.run([
            'openssl', 'x509',
            '-req',
            '-in', str(server_csr_path),
            '-CA', str(ca_cert_path),
            '-CAkey', str(ca_key_path),
            '-CAcreateserial',
            '-out', str(server_cert_path),
            '-days', '365',
            '-sha256',
            '-extfile', '-',
        ], input=b"""
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = 127.0.0.1
""", check=True)

        # Clean up CSR
        os.remove(server_csr_path)
        
        print("\n✅ Certificates created successfully!")
        print(f"CA Certificate:     {ca_cert_path}")
        print(f"Server Key:         {server_key_path}")
        print(f"Server Certificate: {server_cert_path}")
        
        print("\nTo trust this certificate on macOS:")
        print("1. Open Keychain Access")
        print("2. Make sure 'Login' is selected under 'Default Keychains'")
        print("3. File > Import Items")
        print(f"4. Select {ca_cert_path}")
        print("5. Find 'Development Root CA' in the certificates list")
        print("   (If you don't see it, click 'Certificates' in the top tabs)")
        print("6. Double click it")
        print("7. Expand 'Trust'")
        print("8. Set 'When using this certificate' to 'Always Trust'")
        
        # Update .env file
        env_path = Path(__file__).parent / '.env'
        if not env_path.exists():
            print("\nCreating .env file...")
            with open(env_path, 'w') as f:
                f.write(f"SSL_KEY_PATH={server_key_path}\n")
                f.write(f"SSL_CERT_PATH={server_cert_path}\n")
        else:
            print("\nUpdating .env file...")
            with open(env_path, 'r') as f:
                lines = f.readlines()
            
            # Remove existing SSL paths
            lines = [l for l in lines if not l.startswith(('SSL_KEY_PATH=', 'SSL_CERT_PATH='))]
            
            # Add new SSL paths
            lines.append(f"SSL_KEY_PATH={server_key_path}\n")
            lines.append(f"SSL_CERT_PATH={server_cert_path}\n")
            
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

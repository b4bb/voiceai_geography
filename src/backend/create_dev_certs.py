"""
Script to create self-signed SSL certificates for development.
"""
import os
from pathlib import Path
import subprocess
import sys

def create_certs():
    """Create self-signed SSL certificates for development"""
    # Create certs directory if it doesn't exist
    certs_dir = Path(__file__).parent.parent.parent / 'certs'
    certs_dir.mkdir(exist_ok=True)
    
    key_path = certs_dir / 'key.pem'
    cert_path = certs_dir / 'cert.pem'
    
    # Check if certificates already exist
    if key_path.exists() or cert_path.exists():
        print("Warning: Certificate files already exist!")
        response = input("Do you want to overwrite them? (y/N): ")
        if response.lower() != 'y':
            print("Aborting certificate creation.")
            return
    
    print("\nCreating self-signed certificates...")
    try:
        # Create private key and certificate
        subprocess.run([
            'openssl', 'req', '-x509',
            '-newkey', 'rsa:4096',
            '-keyout', str(key_path),
            '-out', str(cert_path),
            '-days', '365',
            '-nodes',  # No passphrase
            '-subj', '/CN=localhost'
        ], check=True)
        
        print("\n✅ Certificates created successfully!")
        print(f"Key path:  {key_path}")
        print(f"Cert path: {cert_path}")
        
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
        print("\nYou can now run the server with SSL:")
        print("uvicorn server:app --reload --ssl-keyfile ${SSL_KEY_PATH} --ssl-certfile ${SSL_CERT_PATH}")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error creating certificates: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_certs()

"""
Create a proper certificate chain for the server.
"""
from pathlib import Path

def create_chain():
    """Create certificate chain file"""
    certs_dir = Path(__file__).parent.parent.parent / 'certs'
    
    # Read the server certificate
    with open(certs_dir / 'cert.pem', 'r') as f:
        server_cert = f.read()
    
    # Read the CA certificate
    with open(certs_dir / 'ca.pem', 'r') as f:
        ca_cert = f.read()
    
    # Create chain file with server cert first, then CA cert
    with open(certs_dir / 'chain.pem', 'w') as f:
        f.write(server_cert)
        if not server_cert.endswith('\n'):
            f.write('\n')
        f.write(ca_cert)
    
    print("✅ Certificate chain created successfully!")
    print(f"Chain file: {certs_dir / 'chain.pem'}")

if __name__ == "__main__":
    create_chain()

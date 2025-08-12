"""
Script to run uvicorn server with SSL certificates from environment variables.
"""
import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv

def run_server():
    # Load environment variables
    load_dotenv()
    
    # Get SSL paths from environment
    # Use absolute paths to certificates
    certs_dir = Path(__file__).parent.parent.parent / 'certs'
    ssl_key = str(certs_dir / 'key.pem')
    ssl_cert = str(certs_dir / 'cert.pem')  # Use the self-signed certificate
    
    if not ssl_key or not ssl_cert:
        print("Error: SSL certificate paths not found in environment variables")
        return
    
    # Construct the uvicorn command
    cmd = [
        "uvicorn", "server:app",
        "--reload",
        "--ssl-keyfile", ssl_key,
        "--ssl-certfile", ssl_cert
    ]
    
    print(f"\nStarting server with SSL certificates:")
    print(f"Key:  {ssl_key}")
    print(f"Cert: {ssl_cert}\n")
    
    # Run uvicorn
    subprocess.run(cmd)

if __name__ == "__main__":
    run_server()

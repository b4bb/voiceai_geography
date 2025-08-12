"""
Environment variable verification script.
Checks if all required environment variables are set and valid.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

def check_file_exists(path: str, var_name: str) -> bool:
    """Check if a file exists and is readable"""
    if not path:
        print(f"❌ {var_name} is not set")
        return False
    
    file_path = Path(path)
    if not file_path.exists():
        print(f"❌ {var_name} file does not exist: {path}")
        return False
    if not file_path.is_file():
        print(f"❌ {var_name} is not a file: {path}")
        return False
    if not os.access(file_path, os.R_OK):
        print(f"❌ {var_name} file is not readable: {path}")
        return False
    
    print(f"✅ {var_name} is valid: {path}")
    return True

def check_env_variables():
    """Check all required environment variables"""
    print("\nChecking environment variables...")
    
    # Load .env file
    env_path = Path(__file__).parent / '.env'
    if not env_path.exists():
        print(f"❌ .env file not found in {env_path}")
        return False
    
    load_dotenv()
    
    # Required variables
    required_vars = {
        'DATABASE_URL': None,  # None means no special validation
        'SECRET_KEY': None,
        'SSL_KEY_PATH': check_file_exists,
        'SSL_CERT_PATH': check_file_exists,
        'ALLOWED_ORIGINS': None,
        'AGENT_ID': None,
        'XI_API_KEY': None
    }
    
    all_valid = True
    
    for var, validator in required_vars.items():
        value = os.getenv(var)
        if not value:
            print(f"❌ {var} is not set")
            all_valid = False
            continue
            
        if validator:
            if not validator(value, var):
                all_valid = False
        else:
            print(f"✅ {var} is set")
            if var == 'DATABASE_URL':
                print(f"   Database URL: {value}")
            elif var == 'ALLOWED_ORIGINS':
                origins = value.split(',')
                print(f"   Allowed origins: {origins}")
    
    if all_valid:
        print("\n✅ All environment variables are properly configured!")
        print("\nYou can now run:")
        print("uvicorn server:app --reload --ssl-keyfile ${SSL_KEY_PATH} --ssl-certfile ${SSL_CERT_PATH}")
    else:
        print("\n❌ Some environment variables are missing or invalid")
        print("Please check your .env file and make sure all required variables are set correctly")
    
    return all_valid

if __name__ == "__main__":
    check_env_variables()

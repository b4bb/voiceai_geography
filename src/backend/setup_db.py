"""
Database setup script for voiceai-geography application.
This script creates necessary tables using the application database user.
Prerequisites:
- Database 'voiceai_geography' must exist
- Role 'voiceai_app_db_user' must exist with appropriate permissions
"""
import psycopg
from getpass import getpass
import sys
import os

def get_connection_params():
    """Get database connection parameters from environment or user input"""
    # Check if running on Render
    if 'RENDER' in os.environ:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("Error: DATABASE_URL environment variable is required when running on Render")
            print("Please set DATABASE_URL in your Render service configuration")
            sys.exit(1)
        return database_url
    else:
        # Local development
        db_password = getpass("Enter password for voiceai_app_db_user: ")
        return f"postgresql://voiceai_app_db_user:{db_password}@localhost:5432/voiceai_geography"

def verify_prerequisites(conn_string):
    """Verify that we can connect to the database as application user"""
    try:
        # Try connecting to the database as application user
        with psycopg.connect(conn_string, autocommit=True) as conn:
            with conn.cursor() as cur:
                # Check if we can create tables
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS _test_permissions (
                        id SERIAL PRIMARY KEY
                    );
                    DROP TABLE _test_permissions;
                """)
        print("Database connection and permissions verified successfully!")
        return conn_string
    except psycopg.OperationalError as e:
        if "database" in str(e).lower():
            print("Error: Database 'voiceai_geography' does not exist")
        elif "role" in str(e).lower():
            print("Error: Role 'voiceai_app_db_user' does not exist")
        else:
            print(f"Error connecting to database: {e}")
        print("\nPlease ensure:")
        print("1. Database 'voiceai_geography' exists")
        print("2. Role 'voiceai_app_db_user' exists with appropriate permissions")
        print("3. The connection parameters are correct")
        sys.exit(1)
    except psycopg.InsufficientPrivilege:
        print("Error: voiceai_app_db_user lacks required permissions")
        print("Required permissions:")
        print("- CONNECT privilege on voiceai_geography database")
        print("- USAGE and CREATE privileges on public schema")
        sys.exit(1)

def setup_tables(conn_string: str):
    """Set up the database tables using application user credentials"""
    
    try:
        with psycopg.connect(conn_string, autocommit=True) as conn:
            with conn.cursor() as cur:
                print("Connected as application user")
                
                print("Creating tables...")
                
                # Admins table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS admins (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(255) UNIQUE NOT NULL,
                        hashed_password VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Invitation codes table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS invitation_codes (
                        id SERIAL PRIMARY KEY,
                        code VARCHAR(50) UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP NOT NULL,
                        max_calls INTEGER NOT NULL,
                        call_count INTEGER DEFAULT 0
                    )
                """)
                
                print("Database tables created successfully!")
                
                # Generate .env file content if not on Render
                if 'RENDER' not in os.environ:
                    env_content = f"""# Database Configuration
DATABASE_URL={conn_string}

# Other configurations will be added during deployment
"""
                    print("\nAdd the following to your .env file:")
                    print(env_content)
                
    except psycopg.Error as e:
        print(f"Error during table creation: {e}")
        print("\nPlease verify:")
        print("1. The connection parameters are correct")
        print("2. The user has necessary permissions")
        sys.exit(1)

if __name__ == "__main__":
    conn_string = get_connection_params()
    conn_string = verify_prerequisites(conn_string)
    setup_tables(conn_string)
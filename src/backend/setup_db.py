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

def verify_prerequisites():
    """Verify that we can connect to the database as application user"""
    db_password = getpass("Enter password for voiceai_app_db_user: ")
    try:
        # Try connecting to the database as application user
        conn_string = f"dbname=voiceai_geography user=voiceai_app_db_user password={db_password}"
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
        return db_password
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
        print("3. The password is correct")
        sys.exit(1)
    except psycopg.InsufficientPrivilege:
        print("Error: voiceai_app_db_user lacks required permissions")
        print("Required permissions:")
        print("- CONNECT privilege on voiceai_geography database")
        print("- USAGE and CREATE privileges on public schema")
        sys.exit(1)

def setup_tables(db_password: str):
    """Set up the database tables using application user credentials"""
    
    try:
        # Connect as application user
        conn_string = f"dbname=voiceai_geography user=voiceai_app_db_user password={db_password}"
        print(f"Connecting with: {conn_string}")
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
                
                # Generate .env file content
                env_content = f"""# Database Configuration
DATABASE_URL=postgresql://voiceai_app_db_user:{db_password}@localhost:5432/voiceai_geography

# Other configurations will be added during deployment
"""
                print("\nAdd the following to your .env file:")
                print(env_content)
                
    except psycopg.Error as e:
        print(f"Error during table creation: {e}")
        print("\nPlease verify:")
        print("1. The password is correct")
        print("2. The user has necessary permissions")
        sys.exit(1)

if __name__ == "__main__":
    db_password = verify_prerequisites()
    setup_tables(db_password)
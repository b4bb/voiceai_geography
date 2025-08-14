import psycopg
from psycopg.rows import dict_row
import os
from datetime import datetime
from urllib.parse import urlparse
from dotenv import load_dotenv
from typing import Optional, Dict, List
from contextlib import contextmanager

# Load environment variables
load_dotenv()

def get_db_config() -> str:
    """Get database configuration from environment variables"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    return database_url

@contextmanager
def get_db_connection(quiet: bool = False):
    """Create and return a database connection"""
    try:
        conninfo = get_db_config()
        if not quiet:
            print(f"Attempting to connect to database: {conninfo}")
        with psycopg.connect(conninfo, row_factory=dict_row) as conn:
            if not quiet:
                print("Database connection successful")
            yield conn
    except psycopg.Error as e:
        print(f"Error connecting to database: {e}")
        raise

def init_db():
    """Initialize the database with required tables"""
    print("Initializing database...")
    try:
        with get_db_connection() as conn:
            print("Database connection established for initialization")
            with conn.cursor() as cur:
                # Check if invitation_codes table exists
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'invitation_codes'
                    )
                """)
                tables_exist = cur.fetchone()['exists']
                
                if not tables_exist:
                    print("Creating database tables...")
                    
                    # Create invitation_codes table
                    cur.execute('''
                        CREATE TABLE IF NOT EXISTS invitation_codes (
                            id SERIAL PRIMARY KEY,
                            code VARCHAR(50) UNIQUE NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            expires_at TIMESTAMP NOT NULL,
                            max_calls INTEGER NOT NULL,
                            call_count INTEGER DEFAULT 0
                        )
                    ''')
                    
                    conn.commit()
                    print("Database tables created successfully!")
                else:
                    print("Database tables already exist")
                    
    except Exception as e:
        print(f"Error during database initialization: {e}")
        raise

def get_invitation_code(code: str) -> Optional[Dict]:
    """Get invitation code by code string"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    SELECT * FROM invitation_codes 
                    WHERE code = %s
                ''', [code])
                result = cur.fetchone()
                if result:
                    result['is_valid'] = (
                        datetime.utcnow() < result['expires_at'] and
                        result['call_count'] < result['max_calls']
                    )
                return result
    except Exception as e:
        print(f"Error getting invitation code: {e}")
        return None

def get_all_invitation_codes() -> List[Dict]:
    """Get all invitation codes"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM invitation_codes ORDER BY created_at DESC')
                results = cur.fetchall()
                for result in results:
                    result['is_valid'] = (
                        datetime.utcnow() < result['expires_at'] and
                        result['call_count'] < result['max_calls']
                    )
                return results
    except Exception as e:
        print(f"Error getting all invitation codes: {e}")
        return []

def increment_call_count(code: str) -> bool:
    """Increment the call count for an invitation code"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    UPDATE invitation_codes 
                    SET call_count = call_count + 1 
                    WHERE code = %s
                    RETURNING id
                ''', [code])
                return bool(cur.fetchone())
    except Exception as e:
        print(f"Error incrementing call count: {e}")
        return False

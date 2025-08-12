from database import get_db_connection
from datetime import datetime, timedelta

def create_test_code():
    """Create a test invitation code"""
    code = "TEST123"
    expires_at = datetime.utcnow() + timedelta(days=7)  # Valid for 7 days
    max_calls = 10  # Allow 10 calls

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Check if code already exists
                cur.execute("SELECT code FROM invitation_codes WHERE code = %s", [code])
                if cur.fetchone():
                    print(f"Test code '{code}' already exists")
                    return

                # Create new code
                cur.execute("""
                    INSERT INTO invitation_codes (code, expires_at, max_calls)
                    VALUES (%s, %s, %s)
                """, [code, expires_at, max_calls])
                conn.commit()
                print(f"Test code '{code}' created successfully")
    except Exception as e:
        print(f"Error creating test code: {e}")

if __name__ == "__main__":
    create_test_code()

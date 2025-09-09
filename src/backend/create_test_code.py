from database import get_db_connection
from datetime import datetime, timedelta

def create_test_code(code="TEST123", first_name=None, last_name=None, days_valid=7, max_calls=10):
    """Create a test invitation code with optional names"""
    expires_at = datetime.utcnow() + timedelta(days=days_valid)

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
                    INSERT INTO invitation_codes (code, first_name, last_name, expires_at, max_calls)
                    VALUES (%s, %s, %s, %s, %s)
                """, [code, first_name, last_name, expires_at, max_calls])
                conn.commit()
                
                name_info = ""
                if first_name or last_name:
                    name_parts = []
                    if first_name:
                        name_parts.append(f"first_name='{first_name}'")
                    if last_name:
                        name_parts.append(f"last_name='{last_name}'")
                    name_info = f" ({', '.join(name_parts)})"
                
                print(f"Test code '{code}' created successfully{name_info}")
    except Exception as e:
        print(f"Error creating test code: {e}")

def create_sample_codes():
    """Create several sample codes with different names for testing"""
    sample_codes = [
        ("TEST123", None, None),
        ("ALICE001", "Alice", "Johnson"),
        ("BOB002", "Bob", "Smith"),
        ("CHARLIE003", "Charlie", None),
        ("DIANA004", "Diana", "Williams")
    ]
    
    print("Creating sample invitation codes...")
    for code, first_name, last_name in sample_codes:
        create_test_code(code, first_name, last_name)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--samples":
        create_sample_codes()
    else:
        create_test_code()

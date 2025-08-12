from database import get_db_connection
from auth import get_password_hash
import sys

def create_admin_user(username: str, password: str):
    """Create an admin user with password validation"""
    # Validate username
    if len(username) < 3:
        print("Username must be at least 3 characters long")
        return
    if len(username) > 32:
        print("Username must not exceed 32 characters")
        return
    
    # Validate password
    from auth import validate_password
    is_valid, error_message = validate_password(password)
    if not is_valid:
        print(f"Invalid password: {error_message}")
        return

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Check if admin already exists
            cur.execute("SELECT username FROM admins WHERE username = %s", (username,))
            if cur.fetchone():
                print(f"Admin user '{username}' already exists")
                return

            # Create new admin
            hashed_password = get_password_hash(password)
            cur.execute(
                "INSERT INTO admins (username, hashed_password) VALUES (%s, %s)",
                (username, hashed_password)
            )
            conn.commit()
            print(f"Admin user '{username}' created successfully")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python create_admin.py <username> <password>")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    create_admin_user(username, password)

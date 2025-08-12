from database import get_db_connection

def check_admins():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM admins')
            results = cur.fetchall()
            print("Admin users:", results)

if __name__ == "__main__":
    check_admins()

#!/usr/bin/env python3
"""
Migration script to add first_name and last_name columns to existing invitation_codes table.
Run this script to update existing databases with the new name fields.
"""

from database import get_db_connection
import sys

def migrate_add_name_columns():
    """Add first_name and last_name columns to invitation_codes table"""
    print("Starting migration to add name columns...")
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Check if columns already exist
                cur.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'invitation_codes' 
                    AND column_name IN ('first_name', 'last_name')
                """)
                existing_columns = [row['column_name'] for row in cur.fetchall()]
                
                if 'first_name' in existing_columns and 'last_name' in existing_columns:
                    print("Name columns already exist. Migration not needed.")
                    return True
                
                # Add missing columns
                if 'first_name' not in existing_columns:
                    print("Adding first_name column...")
                    cur.execute("ALTER TABLE invitation_codes ADD COLUMN first_name VARCHAR(100)")
                
                if 'last_name' not in existing_columns:
                    print("Adding last_name column...")
                    cur.execute("ALTER TABLE invitation_codes ADD COLUMN last_name VARCHAR(100)")
                
                conn.commit()
                print("Migration completed successfully!")
                return True
                
    except Exception as e:
        print(f"Migration failed: {e}")
        return False

def verify_migration():
    """Verify that the migration was successful"""
    print("Verifying migration...")
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = 'invitation_codes' 
                    AND column_name IN ('first_name', 'last_name')
                    ORDER BY column_name
                """)
                columns = cur.fetchall()
                
                if len(columns) == 2:
                    print("✓ Migration verification successful:")
                    for col in columns:
                        print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
                    return True
                else:
                    print("✗ Migration verification failed: columns not found")
                    return False
                    
    except Exception as e:
        print(f"Migration verification failed: {e}")
        return False

if __name__ == "__main__":
    print("Invitation Codes Table Migration")
    print("=" * 40)
    
    # Run migration
    if migrate_add_name_columns():
        # Verify migration
        if verify_migration():
            print("\n✓ Migration completed and verified successfully!")
            sys.exit(0)
        else:
            print("\n✗ Migration verification failed!")
            sys.exit(1)
    else:
        print("\n✗ Migration failed!")
        sys.exit(1)

# VoiceAI Geography

## Database Setup

### Prerequisites
1. PostgreSQL is installed and running
2. Database 'voiceai_geography' exists
3. Role 'voiceai_app_db_user' exists with the following permissions:
   - CONNECT privilege on the voiceai_geography database
   - USAGE privilege on the public schema
   - CREATE privilege on the public schema (for creating tables)
   
   You can grant these permissions using:
   ```sql
   -- Connect to postgres database first
   \c postgres
   
   -- Grant database connection privilege
   GRANT CONNECT ON DATABASE voiceai_geography TO voiceai_app_db_user;
   
   -- Connect to application database
   \c voiceai_geography
   
   -- Grant schema privileges
   GRANT USAGE, CREATE ON SCHEMA public TO voiceai_app_db_user;
   ```

### Setting Up Tables
1. Navigate to the backend directory:
   ```bash
   cd src/backend
   ```

2. Run the database setup script:
   ```bash
   python setup_db.py
   ```
   This script will:
   - Verify prerequisites (database and role exist)
   - Create necessary tables
   - Generate database connection settings for your .env file

3. Create a `.env` file in the `src/backend` directory using the output from the setup script

### Note
If the prerequisites are not met, the script will exit with an error message. Here's how to set everything up as a PostgreSQL admin:

1. Create the database:
   ```sql
   CREATE DATABASE voiceai_geography;
   ```

2. Create the role and set password:
   ```sql
   CREATE USER voiceai_app_db_user WITH PASSWORD 'your_secure_password';
   ```

3. Grant required permissions:
   ```sql
   -- From postgres database
   GRANT CONNECT ON DATABASE voiceai_geography TO voiceai_app_db_user;
   
   -- Then connect to voiceai_geography database
   \c voiceai_geography
   
   -- Grant schema privileges
   GRANT USAGE, CREATE ON SCHEMA public TO voiceai_app_db_user;

   -- Grant table permissions (after tables are created)
   GRANT SELECT, INSERT, UPDATE, DELETE ON admins TO voiceai_app_db_user;
   GRANT USAGE, SELECT ON SEQUENCE admins_id_seq TO voiceai_app_db_user;

   -- Grant permissions on invitation_codes table
   GRANT SELECT, INSERT, UPDATE ON invitation_codes TO voiceai_app_db_user;
   GRANT USAGE, SELECT ON SEQUENCE invitation_codes_id_seq TO voiceai_app_db_user;
   ```

Note: The sequence permissions (admins_id_seq and invitation_codes_id_seq) should be granted after the tables are created, as the sequences are created automatically with the tables.

Or using command line:
```bash
# Create database
createdb voiceai_geography

# Create user
createuser voiceai_app_db_user

# Set password and permissions (connect to postgres as admin)
psql -d postgres
```

## Security Notes

- The setup script requires PostgreSQL admin privileges to run initially
- The application itself runs with restricted database privileges via `voiceai_app_db_user`
- Database passwords should be strong and unique
- Never commit `.env` files to version control
- The `setup_db.py` script should only be run during initial setup or when resetting the database
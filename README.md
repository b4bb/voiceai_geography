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

## GitHub Deployment

### Prerequisites
1. GitHub account
2. SSH key set up on your machine
3. Repository created on GitHub

### Setting Up SSH Authentication
1. Check for existing SSH keys:
   ```bash
   ls -la ~/.ssh
   ```
   Look for files like `id_rsa.pub`, `id_ed25519.pub`, etc.

2. If no SSH key exists, create one:
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```
   Follow the prompts (press Enter to accept defaults)

3. Add SSH key to GitHub:
   - Copy your public key:
     ```bash
     cat ~/.ssh/id_ed25519.pub
     ```
   - Go to GitHub.com → Settings → SSH and GPG keys
   - Click "New SSH key"
   - Title: e.g., "MacBook Pro"
   - Key type: "Authentication Key"
   - Paste your public key
   - Click "Add SSH key"

4. Test SSH connection:
   ```bash
   ssh -T git@github.com
   ```
   You should see: "Hi username! You've successfully authenticated..."

### Deploying to GitHub
1. Initialize git (if not already done):
   ```bash
   git init
   ```

2. Add your files:
   ```bash
   git add .
   ```

3. Commit changes:
   ```bash
   git commit -m "Initial commit"
   ```

4. Add remote repository:
   ```bash
   git remote add origin git@github.com:username/voiceai-geography.git
   ```
   Replace 'username' with your GitHub username

5. Push to GitHub:
   ```bash
   git branch -M main
   git push -u origin main
   ```

### Troubleshooting
- If you see "Permission denied" errors, verify your SSH key is added to GitHub
- If you get "Repository not found" errors, check your repository name and permissions
- For "Updates were rejected" errors, try pulling changes first: `git pull origin main`

## Render Deployment

### Prerequisites
1. GitHub repository is set up and contains your latest code
2. A Render account (sign up at render.com)
3. PostgreSQL database credentials
4. ElevenLabs API credentials

### Database Setup on Render
1. Create PostgreSQL Database:
   - Go to Render Dashboard → New + → PostgreSQL
   - Name: `voiceai-geography-db` (or your preferred name)
   - Database: `voiceai_geography`
   - User: Leave as auto-generated
   - Region: Choose closest to your users
   - Click "Create Database"

2. Verify Database Creation:
   - Wait for database to be created (Status: Available)
   - Save these values from the database info page:
     - Internal Database URL
     - External Database URL
     - User
     - Password

3. Test Database Connection:
   ```bash
   # Use the External Database URL
   psql your_external_database_url
   # You should see a psql prompt
   # Try: \dt to list tables
   ```

### Development vs Production Setup

#### Local Development
- Frontend files are served from `src/frontend/dist`
- Backend and frontend can be run separately
- Changes are watched and rebuilt automatically
- Uses relative paths for file serving

#### Production (Render)
- All files are served by the FastAPI server
- Static files are served from `backend/static`
- Build process happens once during deployment
- Uses absolute paths for file serving

### Web Service Setup
1. Create Web Service:
   - Go to Render Dashboard → New + → Web Service
   - Connect your GitHub repository
   - Name: `voiceai-geography` (or your preferred name)
   - Region: Same as database
   - Branch: main
   - Root Directory: Leave empty
   - Runtime: Python 3
   - Build Command: 
     ```bash
     pip install -r src/backend/requirements.txt && cd src/frontend && npm install && npm run build && mkdir -p ../backend/static && cp -r dist/* ../backend/static/
     ```
     This command:
     1. Installs Python dependencies
     2. Goes to frontend directory
     3. Installs Node.js dependencies
     4. Builds frontend files
     5. Creates static directory in backend
     6. Copies built files to backend/static
   - Start Command:
     ```bash
     cd src/backend && uvicorn server:app --host 0.0.0.0 --port $PORT
     ```

2. Configure Environment Variables:
   - In Web Service → Environment
   - Add the following:
     ```
     DATABASE_URL=your_internal_database_url
     SECRET_KEY=your_secure_random_key
     ALLOWED_ORIGINS=https://your-app-name.onrender.com
     AGENT_ID=your_elevenlabs_agent_id
     XI_API_KEY=your_elevenlabs_api_key
     ```
   - Generate a secure SECRET_KEY:
     ```python
     python -c "import secrets; print(secrets.token_hex(32))"
     ```

3. Initial Deployment:
   - Click "Create Web Service"
   - Watch the deployment logs for errors
   - Status should change to "Live"

### File Structure
The application uses different file structures for development and production:

```
Development:
src/
├── frontend/
│   ├── dist/          # Built frontend files (local development)
│   ├── app.js         # Frontend source
│   └── admin.js       # Admin interface source
└── backend/
    ├── server.py      # FastAPI server
    └── ...            # Other backend files

Production (after build):
src/
├── frontend/
│   ├── dist/          # Built frontend files
│   └── ...            # Source files (not used in production)
└── backend/
    ├── static/        # Copied frontend files for serving
    ├── server.py      # FastAPI server
    └── ...            # Other backend files
```

### Verify Deployment
1. Check Web Service:
   - Visit `https://your-app-name.onrender.com`
   - You should see your application frontend
   - Check browser console for any errors

2. Test API Endpoints:
   - Try accessing `/admin`
   - Test login functionality
   - Verify ElevenLabs integration

3. Check Database Connection:
   - Try creating an admin user
   - Verify invitation codes work
   - Monitor logs for database errors

4. SSL/HTTPS:
   - Verify padlock icon in browser
   - All URLs should be https://
   - No mixed content warnings

### Troubleshooting
1. If deployment fails:
   - Check build logs
   - Verify all environment variables
   - Ensure database URL is correct
   - Check resource limits

2. If database connection fails:
   - Verify DATABASE_URL format
   - Check if database is available
   - Try connecting via psql
   - Check network access rules

3. If frontend doesn't load:
   - Check build command output
   - Verify files were copied to backend/static/
   - Check paths in server.py match static file locations
   - Clear browser cache
   - Check network tab for 404 errors on static files

### Monitoring
1. Set Up Monitoring:
   - Enable Render logging
   - Set up alerts for errors
   - Monitor resource usage

2. Regular Checks:
   - Database connection
   - API response times
   - Error rates
   - Resource utilization

### Updates and Maintenance
1. To Update Application:
   - Push changes to GitHub
   - Render will auto-deploy
   - Watch deployment logs
   - Verify changes in production

2. Database Maintenance:
   - Regular backups enabled by default
   - Monitor database size
   - Check connection pooling
   - Monitor query performance

### Cost Management
1. Free Tier Limitations:
   - Web Service: 750 hours/month
   - Database: 90 days trial
   - Bandwidth: Limited

2. Upgrade Considerations:
   - Monitor usage
   - Set up billing alerts
   - Choose appropriate instance size

## Security Notes

- The setup script requires PostgreSQL admin privileges to run initially
- The application itself runs with restricted database privileges via `voiceai_app_db_user`
- Database passwords should be strong and unique
- Never commit `.env` files to version control
- The `setup_db.py` script should only be run during initial setup or when resetting the database
- SSL certificates and private keys should never be committed to version control
- Always verify `.gitignore` is properly configured before pushing sensitive directories
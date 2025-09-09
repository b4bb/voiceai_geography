# backend/server.py
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
import httpx
import os
from dotenv import load_dotenv
from typing import Optional, List
from pydantic import BaseModel
from database import get_db_connection, get_invitation_code, get_all_invitation_codes, increment_call_count
from auth import (
    create_access_token, get_current_admin, ACCESS_TOKEN_EXPIRE_MINUTES,
    jwt, ALGORITHM, SECRET_KEY, JWTError
)

# Load environment variables
load_dotenv()

# SSL Certificate paths from environment variables
SSL_KEYFILE = os.getenv("SSL_KEY_PATH")
SSL_CERTFILE = os.getenv("SSL_CERT_PATH")

app = FastAPI()

# Rate limiting middleware
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, window_size=60, max_requests=10):
        super().__init__(app)
        self.window_size = window_size  # seconds
        self.max_requests = max_requests
        self.requests = {}  # ip -> list of timestamps

    async def dispatch(self, request, call_next):
        # Skip rate limiting for static files and admin routes
        if request.url.path.startswith('/static') or request.url.path.startswith('/admin'):
            return await call_next(request)

        # Get client IP
        client_ip = request.client.host
        now = datetime.utcnow()

        # Initialize or clean up old requests
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        self.requests[client_ip] = [ts for ts in self.requests[client_ip] 
                                  if (now - ts).seconds < self.window_size]

        # Check rate limit
        if len(self.requests[client_ip]) >= self.max_requests:
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later."
            )

        # Add current request
        self.requests[client_ip].append(now)
        return await call_next(request)

app.add_middleware(RateLimitMiddleware)

# CORS middleware configuration
# Get allowed origins from environment variable
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
if not allowed_origins or allowed_origins[0] == "":
    allowed_origins = ["http://localhost:3000"]  # Default for development

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Pydantic models
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class RefreshRequest(BaseModel):
    refresh_token: str

class InvitationCodeBase(BaseModel):
    code: str

class InvitationCodeResponse(InvitationCodeBase):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: datetime
    expires_at: datetime
    max_calls: int
    call_count: int
    is_valid: bool

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Authentication endpoints
@app.post("/token", response_model=Token)
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    from auth import get_admin, verify_password
    from rate_limit import login_rate_limiter
    
    # Check rate limit before processing login
    login_rate_limiter.check_rate_limit(form_data.username, request)
    
    print(f"Login attempt for username: {form_data.username}")
    admin = get_admin(form_data.username)
    print(f"Admin lookup result: {admin}")
    
    if not admin:
        print("Admin not found")
        login_rate_limiter.record_attempt(form_data.username, request)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(form_data.password, admin["hashed_password"]):
        print("Password verification failed")
        login_rate_limiter.record_attempt(form_data.username, request)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Clear rate limit attempts on successful login
    login_rate_limiter.clear_attempts(form_data.username, request)
    
    # Generate both access and refresh tokens
    from auth import create_tokens
    return create_tokens(form_data.username)

# Token refresh endpoint
@app.post("/token/refresh", response_model=Token)
async def refresh_token(refresh_request: RefreshRequest):
    """Get a new access token using a refresh token"""
    try:
        # Verify the refresh token
        payload = jwt.decode(refresh_request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
            
        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
            
        # Check if the admin still exists
        admin = get_admin(username)
        if admin is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User no longer exists",
            )
            
        # Generate new tokens
        return create_tokens(username)
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

# Invitation code endpoints
@app.post("/api/validate-code")
async def validate_code(code_data: InvitationCodeBase):
    """Validate an invitation code"""
    code = get_invitation_code(code_data.code)
    if not code:
        raise HTTPException(status_code=404, detail="Invalid invitation code")
    
    if not code['is_valid']:
        if datetime.utcnow() >= code['expires_at']:
            raise HTTPException(status_code=400, detail="Invitation code has expired")
        else:
            raise HTTPException(status_code=400, detail="Maximum number of calls reached")
    
    return {
        "valid": True,
        "code": code['code'],
        "first_name": code.get('first_name'),
        "last_name": code.get('last_name')
    }

@app.post("/api/increment-code")
async def increment_code_usage(code_data: InvitationCodeBase):
    """Increment the call count for an invitation code"""
    success = increment_call_count(code_data.code)
    if not success:
        raise HTTPException(status_code=404, detail="Invalid invitation code")
    return {"success": True}

@app.get("/api/codes", response_model=List[InvitationCodeResponse])
async def list_codes(current_admin: str = Depends(get_current_admin)):
    """List all invitation codes (admin only)"""
    return get_all_invitation_codes()

# ElevenLabs API endpoints
@app.get("/api/signed-url")
async def get_signed_url():
    agent_id = os.getenv("AGENT_ID")
    xi_api_key = os.getenv("XI_API_KEY")
    
    if not agent_id or not xi_api_key:
        raise HTTPException(status_code=500, detail="Missing AGENT_ID or XI_API_KEY environment variables")
    
    url = f"https://api.elevenlabs.io/v1/convai/conversation/get_signed_url?agent_id={agent_id}"
    
    async with httpx.AsyncClient() as client:
        try:
            print(f"\n=== REQUEST ===\nURL: {url}\nHeaders: {{'xi-api-key': '*****'}}\n")
            
            response = await client.get(
                url,
                headers={
                    "xi-api-key": xi_api_key
                }
            )
            
            print(f"\n=== RESPONSE ===\nStatus: {response.status_code}\nHeaders: {dict(response.headers)}\nBody: {response.text}\n")
            
            response.raise_for_status()
            data = response.json()
            return {"signedUrl": data["signed_url"]}
            
        except httpx.HTTPError as e:
            print(f"Error from ElevenLabs API: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response content: {e.response.content}")
            raise HTTPException(status_code=500, detail=f"Failed to get signed URL: {str(e)}")

#API route for getting Agent ID, used for public agents
@app.get("/api/getAgentId")
def get_unsigned_url():
    agent_id = os.getenv("AGENT_ID")
    return {"agentId": agent_id}

# Serve admin page
@app.get("/admin")
async def serve_admin():
    # Try multiple possible paths for admin.html
    admin_paths = [
        "../frontend/dist/admin.html",  # Local development
        "../../dist/admin.html",        # Render deployment structure
        "../../../dist/admin.html",     # Alternative Render structure
        "dist/admin.html"               # If running from project root
    ]
    
    admin_path = None
    for path in admin_paths:
        if os.path.exists(path):
            admin_path = path
            break
    
    if not admin_path:
        raise HTTPException(
            status_code=500,
            detail="admin.html not found. Please ensure the frontend build was successful."
        )
    return FileResponse(admin_path)

# Mount static files from frontend build directory
# Try multiple possible paths for different deployment environments
static_paths = [
    "../frontend/dist",  # Local development
    "../../dist",        # Render deployment structure
    "../../../dist",     # Alternative Render structure
    "dist"               # If running from project root
]

static_dir = None
for path in static_paths:
    if os.path.exists(path):
        static_dir = path
        break

if static_dir:
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
else:
    print("Warning: No static directory found. Static files will not be served.")

# Serve index.html for root path
@app.get("/")
async def serve_index():
    # Try multiple possible paths for index.html
    index_paths = [
        "../frontend/dist/index.html",  # Local development
        "../../dist/index.html",        # Render deployment structure
        "../../../dist/index.html",     # Alternative Render structure
        "dist/index.html"               # If running from project root
    ]
    
    index_path = None
    for path in index_paths:
        if os.path.exists(path):
            index_path = path
            break
    
    if not index_path:
        raise HTTPException(
            status_code=500,
            detail="index.html not found. Please ensure the frontend build was successful."
        )
    return FileResponse(index_path)
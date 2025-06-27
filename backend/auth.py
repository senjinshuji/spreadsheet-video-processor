from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from config import settings
from models import User
import httpx
from google.oauth2 import id_token
from google.auth.transport import requests

security = HTTPBearer(auto_error=False)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

async def verify_google_token(token: str) -> Optional[dict]:
    """Verify Google OAuth token"""
    try:
        # Verify the token with Google
        idinfo = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            settings.google_client_id
        )
        
        # Check if token is from our app
        if idinfo['aud'] != settings.google_client_id:
            return None
        
        return idinfo
    except Exception as e:
        print(f"Error verifying Google token: {e}")
        return None

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """Get current user from JWT token"""
    if not credentials:
        return None  # Anonymous access allowed
    
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        
        # Create user object from token data
        user = User(
            id=user_id,
            email=payload.get("email", ""),
            name=payload.get("name"),
            picture=payload.get("picture")
        )
        
        return user
        
    except JWTError:
        return None  # Invalid token, treat as anonymous

def require_user(current_user: Optional[User] = Depends(get_current_user)) -> User:
    """Require authenticated user"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user
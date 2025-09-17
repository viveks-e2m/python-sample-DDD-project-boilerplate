from fastapi import Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import select
from apps.user.domain.models import User
from database import SessionDep
from typing import Optional
import jwt
from datetime import datetime, timedelta
import os

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT access token
    
    Args:
        data (dict): Data to encode in the token
        expires_delta (timedelta, optional): Token expiration time
        
    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def set_auth_cookie(response: Response, token: str):
    """
    Set the authentication cookie
    
    Args:
        response (Response): FastAPI response object
        token (str): JWT token to store in cookie
    """
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

def clear_auth_cookie(response: Response):
    """
    Clear the authentication cookie
    
    Args:
        response (Response): FastAPI response object
    """
    response.delete_cookie("access_token")

async def get_current_user_from_cookie(request: Request, session: SessionDep) -> Optional[User]:
    """
    Get the current authenticated user from the cookie
    
    Args:
        request (Request): FastAPI request object
        session (SessionDep): Database session dependency
        
    Returns:
        User or None: The authenticated user or None if not authenticated
    """
    token = request.cookies.get("access_token")
    if not token:
        return None
        
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(payload)
        username: str = payload.get("sub")
        if username is None:
            return None
    except jwt.PyJWTError:
        return None
    
    # Retrieve user from database
    statement = select(User).where(User.username == username, User.is_active == True)
    user = session.exec(statement).first()
    
    return user
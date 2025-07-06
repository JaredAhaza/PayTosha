from passlib.context import CryptContext
from fastapi import HTTPException, Request
from uuid import UUID
import re

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_current_user_from_session(request: Request) -> UUID:
    """
    Extract user ID from session or request parameters.
    For now, we'll use a simple approach based on the current authentication system.
    """
    # Try to get username from query parameters (current system)
    username = request.query_params.get("username")
    if username:
        # Get user ID from database using username
        from app.utils.supabase_client import supabase
        try:
            user_response = supabase.table("users").select("id").eq("username", username).execute()
            if user_response.data:
                return UUID(user_response.data[0]["id"])
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid user session")
    
    # If no username in query params, try to get from path or other sources
    # This is a fallback for when the system is called directly
    raise HTTPException(status_code=401, detail="User session not found")

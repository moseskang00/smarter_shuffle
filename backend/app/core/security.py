from datetime import datetime, timedelta
from jose import jwt
from ..core.config import get_settings

settings = get_settings()

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create a JWT access token for API authentication"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SUPABASE_KEY, algorithm="HS256")
    return encoded_jwt 
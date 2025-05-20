import os

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from supabase import create_client, Client

load_dotenv()

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Smarter Shuffle"
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"
    
    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError(
            "SUPABASE_URL and SUPABASE_KEY must be set in .env file"
        )
    
    
    SPOTIFY_CLIENT_ID: str = os.getenv("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET: str = os.getenv("SPOTIFY_CLIENT_SECRET")
    SPOTIFY_REDIRECT_URI: str = os.getenv("SPOTIFY_REDIRECT_URI", 
        "http://127.0.0.1:8000/callback" if ENVIRONMENT == "development" 
        else "https://your-production-url.com/callback"
    )
    
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://127.0.0.1:3000",  # Local frontend
        "http://127.0.0.1:8000",  # Local backend
    ]
    if ENVIRONMENT == "production":
        BACKEND_CORS_ORIGINS.extend([
            "https://your-production-frontend.com", # public frontend
            "https://your-production-api.com", # public backend
        ])

    class Config:
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """
    Get settings with caching.
    Usage:
        settings = get_settings()
        print(settings.DATABASE_URL)
    """
    return Settings()

@lru_cache()
def get_supabase() -> Client:
    """
    Get Supabase client with caching.
    Usage:
        supabase = get_supabase()
        result = supabase.table('users').select("*").execute()
    """
    settings = get_settings()
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY) 
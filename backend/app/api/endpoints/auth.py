from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from spotipy.oauth2 import SpotifyOAuth
from spotipy import Spotify
from ...core.config import get_settings, get_supabase
from ...db.database import get_db
from ...models.user import User
from ...models.session import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
from datetime import datetime, timedelta, UTC
from ...core.config import get_supabase

router = APIRouter()
settings = get_settings()
supabase = get_supabase()

# Initialize SpotifyOAuth
sp_oauth = SpotifyOAuth(
    client_id=settings.SPOTIFY_CLIENT_ID,
    client_secret=settings.SPOTIFY_CLIENT_SECRET,
    redirect_uri=settings.SPOTIFY_REDIRECT_URI,
    scope="user-read-private user-read-email user-library-read playlist-read-private"
)


@router.get("/login")
async def spotify_login():
    auth_url = sp_oauth.get_authorize_url()
    return RedirectResponse(auth_url)

@router.get("/callback")
async def spotify_callback(code: Optional[str] = None, error: Optional[str] = None):
    if error:
        raise HTTPException(status_code=400, detail=f"Authorization failed: {error}")
    
    if not code:
        raise HTTPException(status_code=400, detail="No authorization code received")

    try:
        # Exchange the authorization code for tokens
        token_info = sp_oauth.get_access_token(code)
        print("Moses kang token info: ", token_info)
        
        # Initialize Spotify client with the access token
        sp = Spotify(auth=token_info["access_token"])
        
        # Get user information from Spotify
        spotify_user = sp.current_user()
        
        # Check if user already exists in Supabase
        user_result = supabase.table('Users').select("*").eq('spotify_id', spotify_user['id']).execute()
        
        # Initialize user variable
        user = None
        
        if not user_result.data:
            # Create new user
            new_user = User(
                spotify_id=spotify_user['id'],
                display_name=spotify_user['display_name'],
                email=spotify_user['email'],
                country=spotify_user.get('country'),
                created_at=datetime.now(UTC).timestamp(),
                updated_at=datetime.now(UTC).timestamp()
            )
            user_result = supabase.table('Users').insert(new_user.model_dump()).execute()
            user = user_result.data[0]
        else:
            user = user_result.data[0]
            # Update last login
            supabase.table('Users').update({'updated_at': datetime.now(UTC).timestamp()}).eq('id', user['id']).execute()
        
        if not user:
            raise HTTPException(status_code=500, detail="Failed to create or retrieve user")
        
        new_session = Session(
            user_id=user['id'],
            access_token=token_info["access_token"],
            refresh_token=token_info["refresh_token"],
            expires_at=datetime.now(UTC).timestamp() + timedelta(seconds=token_info["expires_in"])
        )
        session_result = supabase.table('Sessions').insert(new_session.model_dump()).execute()
        print(
            "Moses kang session result: ", 
            {
                "user_id": user['id'],  # Use Supabase user ID
                "access_token": token_info["access_token"],
                "refresh_token": token_info["refresh_token"],
                "expires_in": token_info["expires_in"],
                "token_type": token_info["token_type"],
                "display_name": user['display_name'],  # Use Supabase user data
                "email": user['email']  # Use Supabase user data
            }
        )
        return {
            "user_id": user['id'],  # Use Supabase user ID
            "access_token": token_info["access_token"],
            "refresh_token": token_info["refresh_token"],
            "expires_in": token_info["expires_in"],
            "token_type": token_info["token_type"],
            "display_name": user['display_name'],  # Use Supabase user data
            "email": user['email']  # Use Supabase user data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get access token: {str(e)}"
        )

@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """
    Refreshes the Spotify access token using the refresh token
    """
    try:
        # Refresh the token using SpotifyOAuth
        token_info = sp_oauth.refresh_access_token(refresh_token)
        
        # Find the session with this refresh token
        session_result = supabase.table('Sessions').select("*").eq('refresh_token', refresh_token).execute()
        
        if session_result.data:
            session = session_result.data[0]
            # Update session with new tokens
            supabase.table('Sessions').update({
                'access_token': token_info["access_token"],
                'expires_at': (datetime.now(UTC).timestamp() + timedelta(seconds=token_info["expires_in"]))
            }).eq('id', session['id']).execute()
        
        return {
            "access_token": token_info["access_token"],
            "expires_in": token_info["expires_in"],
            "token_type": token_info["token_type"],
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to refresh token: {str(e)}"
        ) 
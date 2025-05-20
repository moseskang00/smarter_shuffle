# havent looked at this file yet


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ...db.database import get_db
from ...models.song import Song
from ...models.listeningEvent import ListeningEvent
from ...models.session import Session
import spotipy
from datetime import datetime, timedelta
from typing import List
from pydantic import BaseModel

router = APIRouter()

class SpotifyTrack(BaseModel):
    id: str
    name: str
    artists: List[dict]
    album: dict
    duration_ms: int
    preview_url: str
    external_urls: dict

@router.post("/recently-played")
async def save_recently_played(
    access_token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetches user's recently played tracks from Spotify and saves them to the database
    """
    try:
        # Initialize Spotify client
        sp = spotipy.Spotify(auth=access_token)
        
        # Get recently played tracks
        results = sp.current_user_recently_played(limit=50)
        
        # Get audio features for all tracks
        track_ids = [item['track']['id'] for item in results['items']]
        audio_features = sp.audio_features(track_ids)
        
        # Create a dictionary of audio features for easy lookup
        features_dict = {f['id']: f for f in audio_features if f is not None}
        
        # Process each track
        for item in results['items']:
            track = item['track']
            played_at = datetime.fromisoformat(item['played_at'].replace('Z', '+00:00'))
            
            # Check if song already exists
            existing_song = await db.execute(
                select(Song).where(Song.spotify_id == track['id'])
            )
            song = existing_song.scalar_one_or_none()
            
            if not song:
                # Create new song
                features = features_dict.get(track['id'], {})
                song = Song(
                    spotify_id=track['id'],
                    title=track['name'],
                    artist=track['artists'][0]['name'],
                    album=track['album']['name'],
                    duration_ms=track['duration_ms'],
                    release_year=int(track['album']['release_date'][:4]) if track['album']['release_date'] else None,
                    preview_url=track['preview_url'],
                    spotify_url=track['external_urls']['spotify'],
                    # Audio features
                    danceability=features.get('danceability'),
                    energy=features.get('energy'),
                    tempo=features.get('tempo'),
                    valence=features.get('valence'),
                    acousticness=features.get('acousticness'),
                    instrumentalness=features.get('instrumentalness'),
                    mode=features.get('mode'),
                    time_signature=features.get('time_signature'),
                    cached_audio_features=features
                )
                db.add(song)
                await db.flush()  # Get the song_id without committing
            
            # Create listening event
            event = ListeningEvent(
                song_id=song.song_id,
                listened_at=played_at,
                duration_listened=track['duration_ms'],
                context_type=item.get('context', {}).get('type'),
                context_id=item.get('context', {}).get('uri')
            )
            db.add(event)
        
        await db.commit()
        return {"message": "Successfully saved recently played tracks"}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) 
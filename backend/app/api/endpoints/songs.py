# FLAG FOR CHECK

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from ...db.database import get_db
from ...db.models import Song, ListeningEvent
from pydantic import BaseModel

router = APIRouter()

class SongFeatures(BaseModel):
    song_id: str
    danceability: float
    energy: float
    tempo: float
    valence: float
    acousticness: float
    instrumentalness: float
    mode: int
    time_signature: int
    likability_score: float

    class Config:
        orm_mode = True

@router.get("/training-data/{user_id}", response_model=List[SongFeatures])
async def get_training_data(
    user_id: str,
    limit: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """
    Efficiently fetch training data for ML model:
    1. Gets recent listening events
    2. Joins with songs table to get features
    3. Returns formatted data for ML training
    """
    # Subquery to get latest events per song
    latest_events = (
        select(
            ListeningEvent.song_id,
            func.max(ListeningEvent.listened_at).label('latest_listen'),
            func.avg(ListeningEvent.likability_score).label('avg_likability')
        )
        .filter(ListeningEvent.user_id == user_id)
        .group_by(ListeningEvent.song_id)
        .order_by('latest_listen')
        .limit(limit)
        .subquery()
    )

    # Main query joining songs with their latest events
    query = (
        select(
            Song.spotify_id.label('song_id'),
            Song.danceability,
            Song.energy,
            Song.tempo,
            Song.valence,
            Song.acousticness,
            Song.instrumentalness,
            Song.mode,
            Song.time_signature,
            latest_events.c.avg_likability.label('likability_score')
        )
        .join(latest_events, Song.song_id == latest_events.c.song_id)
    )

    result = await db.execute(query)
    songs = result.all()

    if not songs:
        raise HTTPException(status_code=404, detail="No training data found")

    return songs 
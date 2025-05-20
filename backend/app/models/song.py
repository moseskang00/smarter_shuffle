from .database import Base
from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, ARRAY, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

import uuid

class Song(Base):
    __tablename__ = "songs"

    song_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    spotify_id = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    album = Column(String)
    duration_ms = Column(Integer)
    release_year = Column(Integer)
    genres = Column(ARRAY(String))
    
    # Audio features
    danceability = Column(Float)
    energy = Column(Float)
    tempo = Column(Float)
    valence = Column(Float)
    acousticness = Column(Float)
    instrumentalness = Column(Float)
    mode = Column(Integer)
    time_signature = Column(Integer)
    popularity = Column(Integer)
    preview_url = Column(String)
    spotify_url = Column(String)
    cached_audio_features = Column(JSONB)
    last_accessed = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

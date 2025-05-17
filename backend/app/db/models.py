from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, ARRAY, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from .database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    spotify_id = Column(String, unique=True, nullable=False)
    display_name = Column(String)
    email = Column(String, unique=True)
    country = Column(String(2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))

class Session(Base):
    __tablename__ = "sessions"

    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)
    token_expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

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

class ListeningEvent(Base):
    __tablename__ = "listening_events"

    event_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    song_id = Column(UUID(as_uuid=True), ForeignKey("songs.song_id", ondelete="CASCADE"), nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False)
    listened_at = Column(DateTime(timezone=True), server_default=func.now())
    duration_listened = Column(Integer, nullable=False)  # in milliseconds
    skip_time = Column(Integer)  # in milliseconds, NULL if not skipped
    likability_score = Column(Float)
    context_type = Column(String(50))
    context_id = Column(String) 
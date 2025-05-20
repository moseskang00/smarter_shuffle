from .database import Base
from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, ARRAY, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

import uuid

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
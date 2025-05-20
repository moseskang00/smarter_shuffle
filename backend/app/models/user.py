from .database import Base
from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, ARRAY, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    spotify_id = Column(String, unique=True, nullable=False)
    display_name = Column(String)
    email = Column(String, unique=True)
    country = Column(String(2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
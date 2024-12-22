from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime, timezone


class Base(DeclarativeBase):
    pass


class VoiceMessage(Base):
    __tablename__ = "voice_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    voice_url = Column(String, nullable=False)
    recognized_text = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

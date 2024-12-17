from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from core.models import VoiceMessage
from bot.config import config


engine = create_engine(config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def save_recognized_text(user_id, voice_url, recognized_text):
    session = SessionLocal()
    try:
        new_entry = VoiceMessage(
            user_id=user_id,
            voice_url=voice_url,
            recognized_text=recognized_text
        )
        session.add(new_entry)
        session.commit()
    finally:
        session.close()

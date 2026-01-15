"""
Transcription Model - Stores transcribed text from media files or pasted content
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import TimestampMixin
import enum


class TranscriptionSource(str, enum.Enum):
    MODEL = "model"
    PASTED = "pasted"


class Transcription(Base, TimestampMixin):
    """Transcription model"""
    __tablename__ = "transcriptions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    media_id = Column(Integer, ForeignKey("media.id"), nullable=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    model_used = Column(String(100), nullable=True)  # e.g., 'whisper-large', 'google-stt'
    source_type = Column(SQLEnum(TranscriptionSource), nullable=False, default=TranscriptionSource.MODEL)
    language = Column(String(10), default="en")
    duration_seconds = Column(Integer, nullable=True)
    word_count = Column(Integer, nullable=True)
    
    # Relationships
    media = relationship("Media", back_populates="transcriptions")
    
    def __repr__(self):
        return f"<Transcription(id={self.id}, title='{self.title}', source='{self.source_type}')>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "media_id": self.media_id,
            "title": self.title,
            "content": self.content,
            "model_used": self.model_used,
            "source_type": self.source_type.value,
            "language": self.language,
            "duration_seconds": self.duration_seconds,
            "word_count": self.word_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "media": self.media.to_dict() if self.media else None
        }

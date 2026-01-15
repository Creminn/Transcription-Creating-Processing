"""
Media Model - Stores uploaded/downloaded media files
"""
from sqlalchemy import Column, Integer, String, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import TimestampMixin
import enum


class MediaType(str, enum.Enum):
    MP4 = "mp4"
    MP3 = "mp3"
    WAV = "wav"
    M4A = "m4a"


class MediaSource(str, enum.Enum):
    UPLOAD = "upload"
    GDRIVE = "gdrive"
    CONVERTED = "converted"


class Media(Base, TimestampMixin):
    """Media file model"""
    __tablename__ = "media"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    filepath = Column(String(512), nullable=False)
    file_type = Column(SQLEnum(MediaType), nullable=False)
    source = Column(SQLEnum(MediaSource), nullable=False, default=MediaSource.UPLOAD)
    file_size = Column(Integer, nullable=True)  # Size in bytes
    duration = Column(Integer, nullable=True)  # Duration in seconds
    gdrive_link = Column(String(512), nullable=True)
    is_processed = Column(Boolean, default=False)
    
    # Relationships
    transcriptions = relationship("Transcription", back_populates="media", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Media(id={self.id}, filename='{self.filename}', type='{self.file_type}')>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "filepath": self.filepath,
            "file_type": self.file_type.value,
            "source": self.source.value,
            "file_size": self.file_size,
            "duration": self.duration,
            "gdrive_link": self.gdrive_link,
            "is_processed": self.is_processed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

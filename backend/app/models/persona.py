"""
Persona Model - Stores writing style personas for email personalization
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON
from app.database import Base
from app.models.base import TimestampMixin


class Persona(Base, TimestampMixin):
    """Persona model for email writing styles"""
    __tablename__ = "personas"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    sample_emails = Column(JSON, nullable=False, default=list)  # Array of sample email texts
    style_description = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Persona(id={self.id}, name='{self.name}')>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "sample_emails": self.sample_emails,
            "style_description": self.style_description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

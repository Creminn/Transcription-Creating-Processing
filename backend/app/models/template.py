"""
Email Template Model - Stores reusable email templates with placeholders
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, Enum as SQLEnum
from app.database import Base
from app.models.base import TimestampMixin
import enum


class TemplateCategory(str, enum.Enum):
    MEETING_NOTES = "meeting_notes"
    FOLLOW_UP = "follow_up"
    SUMMARY = "summary"
    TRAINING = "training"
    CUSTOM = "custom"


class EmailTemplate(Base, TimestampMixin):
    """Email template model"""
    __tablename__ = "email_templates"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    category = Column(SQLEnum(TemplateCategory), nullable=False, default=TemplateCategory.CUSTOM)
    template_content = Column(Text, nullable=False)
    placeholders = Column(JSON, nullable=False, default=list)  # Array of placeholder names used
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<EmailTemplate(id={self.id}, name='{self.name}', category='{self.category}')>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category.value,
            "template_content": self.template_content,
            "placeholders": self.placeholders,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

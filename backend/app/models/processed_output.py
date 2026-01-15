"""
Processed Output Model - Stores LLM-generated outputs from transcriptions
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import TimestampMixin


class ProcessedOutput(Base, TimestampMixin):
    """Processed output model"""
    __tablename__ = "processed_outputs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    prompt_type = Column(String(50), nullable=False)  # summary, email, training, weekly, custom
    transcription_ids = Column(JSON, nullable=False)  # Array of transcription IDs used
    persona_id = Column(Integer, ForeignKey("personas.id"), nullable=True)
    template_id = Column(Integer, ForeignKey("email_templates.id"), nullable=True)
    llm_model = Column(String(100), nullable=False)
    custom_prompt = Column(Text, nullable=True)
    input_tokens = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)
    output_content = Column(Text, nullable=False)
    
    # Relationships
    persona = relationship("Persona")
    template = relationship("EmailTemplate")
    
    def __repr__(self):
        return f"<ProcessedOutput(id={self.id}, prompt_type='{self.prompt_type}', model='{self.llm_model}')>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "prompt_type": self.prompt_type,
            "transcription_ids": self.transcription_ids,
            "persona_id": self.persona_id,
            "template_id": self.template_id,
            "llm_model": self.llm_model,
            "custom_prompt": self.custom_prompt,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "output_content": self.output_content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "persona": self.persona.to_dict() if self.persona else None,
            "template": self.template.to_dict() if self.template else None
        }

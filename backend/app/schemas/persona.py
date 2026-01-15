"""
Persona Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class PersonaBase(BaseModel):
    name: str = Field(..., description="Persona name")
    sample_emails: List[str] = Field(default=[], description="Sample emails for style analysis")
    style_description: str = Field(..., description="Description of writing style")


class PersonaCreate(PersonaBase):
    pass


class PersonaUpdate(BaseModel):
    name: Optional[str] = None
    sample_emails: Optional[List[str]] = None
    style_description: Optional[str] = None
    is_active: Optional[bool] = None


class PersonaResponse(BaseModel):
    id: int
    name: str
    sample_emails: List[str]
    style_description: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PersonaListResponse(BaseModel):
    personas: List[PersonaResponse]
    total: int

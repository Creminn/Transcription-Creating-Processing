"""
Email Template Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TemplateBase(BaseModel):
    name: str = Field(..., description="Template name")
    category: str = Field(default="custom", description="Template category")
    template_content: str = Field(..., description="Template content with placeholders")


class TemplateCreate(TemplateBase):
    pass


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    template_content: Optional[str] = None
    is_active: Optional[bool] = None


class TemplateResponse(BaseModel):
    id: int
    name: str
    category: str
    template_content: str
    placeholders: List[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TemplateListResponse(BaseModel):
    templates: List[TemplateResponse]
    total: int

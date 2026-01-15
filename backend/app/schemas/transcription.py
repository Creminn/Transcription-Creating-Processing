"""
Transcription Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TranscriptionBase(BaseModel):
    title: str
    content: str


class TranscriptionCreate(TranscriptionBase):
    media_id: Optional[int] = None
    model_used: Optional[str] = None
    source_type: str = "model"
    language: str = "en"
    duration_seconds: Optional[int] = None
    word_count: Optional[int] = None

    model_config = {"protected_namespaces": ()}


class TranscriptionPaste(BaseModel):
    title: str = Field(..., description="Title for the transcription")
    content: str = Field(..., description="Transcription text content")
    language: str = Field(default="en", description="Language of the transcription")


class TranscriptionResponse(BaseModel):
    id: int
    media_id: Optional[int] = None
    title: str
    content: str
    model_used: Optional[str] = None
    source_type: str
    language: str
    duration_seconds: Optional[int] = None
    word_count: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "protected_namespaces": ()}


class TranscriptionListResponse(BaseModel):
    transcriptions: List[TranscriptionResponse]
    total: int


class TranscriptionGenerateRequest(BaseModel):
    media_ids: List[int] = Field(..., description="List of media IDs to transcribe")
    model: str = Field(default="whisper-base", description="Transcription model to use")
    language: str = Field(default="en", description="Expected language")

"""
Media Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class MediaBase(BaseModel):
    filename: str
    original_filename: str


class MediaCreate(MediaBase):
    filepath: str
    file_type: str
    source: str = "upload"
    file_size: Optional[int] = None
    duration: Optional[int] = None
    gdrive_link: Optional[str] = None


class MediaUpdate(BaseModel):
    is_processed: Optional[bool] = None


class MediaResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    filepath: str
    file_type: str
    source: str
    file_size: Optional[int] = None
    duration: Optional[int] = None
    gdrive_link: Optional[str] = None
    is_processed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MediaListResponse(BaseModel):
    media: List[MediaResponse]
    total: int


class GDriveDownloadRequest(BaseModel):
    link: str = Field(..., description="Google Drive shareable link")


class ConvertRequest(BaseModel):
    target_format: str = Field(default="mp3", description="Target audio format")

"""
Settings Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class SettingsResponse(BaseModel):
    """Settings response with masked sensitive values"""
    # API Keys (masked)
    openai_api_key_set: bool = Field(description="Whether OpenAI API key is configured")
    google_gemini_api_key_set: bool = Field(description="Whether Gemini API key is configured")
    google_drive_configured: bool = Field(description="Whether Google Drive is configured")
    
    # Non-sensitive settings
    ollama_host: str = Field(description="Ollama server URL")
    whisper_model_size: str = Field(description="Default Whisper model size")
    whisper_device: str = Field(description="Whisper computation device")
    max_upload_size_mb: int = Field(description="Maximum upload size in MB")
    storage_path: str = Field(description="Storage directory path")


class SettingsUpdate(BaseModel):
    """Settings update request"""
    openai_api_key: Optional[str] = None
    google_gemini_api_key: Optional[str] = None
    google_service_account_file: Optional[str] = None
    google_drive_share_email: Optional[str] = None
    ollama_host: Optional[str] = None
    whisper_model_size: Optional[str] = None
    max_upload_size_mb: Optional[int] = None


class ModelInfo(BaseModel):
    """Model information"""
    id: str
    name: str
    type: str  # 'cloud' or 'local'
    available: bool = True


class ModelsResponse(BaseModel):
    """Available models response"""
    transcription_models: List[ModelInfo]
    llm_models: List[ModelInfo]

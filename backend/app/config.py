"""
Application configuration using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    debug: bool = Field(default=False)
    secret_key: str = Field(default="change-me-in-production")
    
    # Database
    database_url: str = Field(default="sqlite+aiosqlite:///./data/app.db")
    
    # Storage
    storage_path: str = Field(default="./storage")
    max_upload_size_mb: int = Field(default=500)
    
    # Google Drive
    google_service_account_file: Optional[str] = Field(default=None)
    google_drive_share_email: Optional[str] = Field(default=None)
    
    # OpenAI
    openai_api_key: Optional[str] = Field(default=None)
    
    # Google Cloud / Gemini
    google_application_credentials: Optional[str] = Field(default=None)
    google_gemini_api_key: Optional[str] = Field(default=None)
    
    # Ollama
    ollama_host: str = Field(default="http://localhost:11434")
    
    # Whisper
    whisper_model_size: str = Field(default="base")
    whisper_device: str = Field(default="cpu")
    whisper_remote_url: Optional[str] = Field(default=None)  # e.g., "http://100.x.x.x:8001"
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @property
    def storage_videos_path(self) -> Path:
        return Path(self.storage_path) / "videos"
    
    @property
    def storage_audio_path(self) -> Path:
        return Path(self.storage_path) / "audio"
    
    @property
    def storage_transcriptions_path(self) -> Path:
        return Path(self.storage_path) / "transcriptions"
    
    def ensure_storage_dirs(self):
        """Create storage directories if they don't exist"""
        self.storage_videos_path.mkdir(parents=True, exist_ok=True)
        self.storage_audio_path.mkdir(parents=True, exist_ok=True)
        self.storage_transcriptions_path.mkdir(parents=True, exist_ok=True)
        # Also ensure data directory for database
        Path("./data").mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()

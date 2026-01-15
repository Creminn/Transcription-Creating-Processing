"""
Settings API Router - Handles application settings
"""
from fastapi import APIRouter, HTTPException
from typing import List

from app.config import settings
from app.schemas.settings import SettingsResponse, SettingsUpdate, ModelsResponse, ModelInfo
from app.services.llm.llm_service import get_available_models as get_llm_models
from app.services.transcription.transcription_service import get_available_models as get_transcription_models

router = APIRouter()


@router.get("", response_model=SettingsResponse)
async def get_settings():
    """Get current application settings (sensitive values masked)"""
    return SettingsResponse(
        openai_api_key_set=bool(settings.openai_api_key and settings.openai_api_key != "sk-your-openai-api-key"),
        google_gemini_api_key_set=bool(settings.google_gemini_api_key and settings.google_gemini_api_key != "your-gemini-api-key"),
        google_drive_configured=bool(settings.google_service_account_file),
        ollama_host=settings.ollama_host,
        whisper_model_size=settings.whisper_model_size,
        whisper_device=settings.whisper_device,
        max_upload_size_mb=settings.max_upload_size_mb,
        storage_path=settings.storage_path
    )


@router.put("", response_model=SettingsResponse)
async def update_settings(update: SettingsUpdate):
    """
    Update application settings.
    
    Note: In a production environment, these would be persisted to a database
    or securely update environment variables. For now, this returns the current
    settings as changes require server restart.
    """
    # In a production app, you would update the settings here
    # For now, we'll just return a message that settings need to be updated in .env
    
    # Return current settings state
    return SettingsResponse(
        openai_api_key_set=bool(settings.openai_api_key and settings.openai_api_key != "sk-your-openai-api-key"),
        google_gemini_api_key_set=bool(settings.google_gemini_api_key and settings.google_gemini_api_key != "your-gemini-api-key"),
        google_drive_configured=bool(settings.google_service_account_file),
        ollama_host=settings.ollama_host,
        whisper_model_size=settings.whisper_model_size,
        whisper_device=settings.whisper_device,
        max_upload_size_mb=settings.max_upload_size_mb,
        storage_path=settings.storage_path
    )


@router.get("/models", response_model=ModelsResponse)
async def get_all_models():
    """Get all available transcription and LLM models"""
    # Get transcription models
    transcription_models_raw = get_transcription_models()
    transcription_models = [
        ModelInfo(
            id=m['id'],
            name=m['name'],
            type=m['type'],
            available=True
        )
        for m in transcription_models_raw
    ]
    
    # Get LLM models
    llm_models_raw = get_llm_models()
    llm_models = [
        ModelInfo(
            id=m['id'],
            name=m['name'],
            type=m['type'],
            available=True
        )
        for m in llm_models_raw
    ]
    
    return ModelsResponse(
        transcription_models=transcription_models,
        llm_models=llm_models
    )

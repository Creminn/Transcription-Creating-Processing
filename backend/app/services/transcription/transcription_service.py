"""
Main Transcription Service - Orchestrates different transcription backends
"""
import asyncio
from typing import Optional, Tuple, List, Dict
from pathlib import Path

from app.services.transcription.whisper_local import transcribe_with_whisper_local
from app.services.transcription.whisper_api import transcribe_with_whisper_api
from app.services.transcription.whisper_remote import transcribe_with_whisper_remote
from app.services.transcription.google_stt import transcribe_with_google_stt, format_language_code
from app.config import settings


TRANSCRIPTION_MODELS = {
    'whisper-tiny': {'backend': 'whisper_local', 'size': 'tiny'},
    'whisper-base': {'backend': 'whisper_local', 'size': 'base'},
    'whisper-small': {'backend': 'whisper_local', 'size': 'small'},
    'whisper-medium': {'backend': 'whisper_local', 'size': 'medium'},
    'whisper-large': {'backend': 'whisper_local', 'size': 'large'},
    'whisper-api': {'backend': 'whisper_api'},
    'google-stt': {'backend': 'google_stt'},
    # Remote Whisper models (if WHISPER_REMOTE_URL is configured)
    'whisper-remote-tiny': {'backend': 'whisper_remote', 'size': 'tiny'},
    'whisper-remote-base': {'backend': 'whisper_remote', 'size': 'base'},
    'whisper-remote-small': {'backend': 'whisper_remote', 'size': 'small'},
    'whisper-remote-medium': {'backend': 'whisper_remote', 'size': 'medium'},
    'whisper-remote-large': {'backend': 'whisper_remote', 'size': 'large'},
}


async def transcribe(
    audio_path: str,
    model: str = 'whisper-base',
    language: str = 'en'
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Transcribe audio using specified model
    
    Args:
        audio_path: Path to audio file
        model: Model identifier (whisper-base, whisper-api, google-stt, etc.)
        language: Language code
    
    Returns:
        Tuple of (success, transcription_text, error_message)
    """
    model_config = TRANSCRIPTION_MODELS.get(model)
    if not model_config:
        return False, None, f"Unknown model: {model}"
    
    backend = model_config['backend']
    
    if backend == 'whisper_local':
        model_size = model_config.get('size', 'base')
        return await transcribe_with_whisper_local(audio_path, model_size, language)
    
    elif backend == 'whisper_remote':
        if not settings.whisper_remote_url:
            return False, None, "Whisper remote URL not configured. Set WHISPER_REMOTE_URL in .env"
        model_size = model_config.get('size', 'base')
        return await transcribe_with_whisper_remote(audio_path, model_size, language)
    
    elif backend == 'whisper_api':
        return await transcribe_with_whisper_api(audio_path, language)
    
    elif backend == 'google_stt':
        lang_code = format_language_code(language)
        return await transcribe_with_google_stt(audio_path, lang_code)
    
    return False, None, f"Unknown backend: {backend}"


async def transcribe_parallel(
    audio_paths: List[str],
    model: str = 'whisper-base',
    language: str = 'en',
    prioritize_audio: bool = True
) -> List[Dict]:
    """
    Transcribe multiple files in parallel with optional prioritization
    
    Args:
        audio_paths: List of audio file paths
        model: Model to use
        language: Language code
        prioritize_audio: If True, process MP3/audio files before videos
    
    Returns:
        List of result dictionaries with path, success, text, error
    """
    # Sort files if prioritization is enabled
    if prioritize_audio:
        audio_files = []
        video_files = []
        
        for path in audio_paths:
            ext = Path(path).suffix.lower()
            if ext in ['.mp3', '.wav', '.m4a', '.flac', '.ogg']:
                audio_files.append(path)
            else:
                video_files.append(path)
        
        # Audio first, then video
        sorted_paths = audio_files + video_files
    else:
        sorted_paths = audio_paths
    
    # Create tasks
    async def process_file(path: str) -> Dict:
        success, text, error = await transcribe(path, model, language)
        return {
            'path': path,
            'success': success,
            'text': text,
            'error': error
        }
    
    # Run in parallel (but audio files will complete first due to typically smaller size)
    tasks = [process_file(path) for path in sorted_paths]
    results = await asyncio.gather(*tasks)
    
    return list(results)


def get_available_models() -> List[Dict]:
    """Get list of available transcription models"""
    models = [
        {'id': 'whisper-tiny', 'name': 'Whisper Tiny (Local)', 'type': 'local'},
        {'id': 'whisper-base', 'name': 'Whisper Base (Local)', 'type': 'local'},
        {'id': 'whisper-small', 'name': 'Whisper Small (Local)', 'type': 'local'},
        {'id': 'whisper-medium', 'name': 'Whisper Medium (Local)', 'type': 'local'},
        {'id': 'whisper-large', 'name': 'Whisper Large (Local)', 'type': 'local'},
        {'id': 'whisper-api', 'name': 'Whisper API (OpenAI)', 'type': 'cloud'},
        {'id': 'google-stt', 'name': 'Google Speech-to-Text', 'type': 'cloud'},
    ]
    
    # Add remote Whisper models if configured
    if settings.whisper_remote_url:
        models.extend([
            {'id': 'whisper-remote-tiny', 'name': 'Whisper Tiny (Remote)', 'type': 'remote'},
            {'id': 'whisper-remote-base', 'name': 'Whisper Base (Remote)', 'type': 'remote'},
            {'id': 'whisper-remote-small', 'name': 'Whisper Small (Remote)', 'type': 'remote'},
            {'id': 'whisper-remote-medium', 'name': 'Whisper Medium (Remote)', 'type': 'remote'},
            {'id': 'whisper-remote-large', 'name': 'Whisper Large (Remote)', 'type': 'remote'},
        ])
    
    return models

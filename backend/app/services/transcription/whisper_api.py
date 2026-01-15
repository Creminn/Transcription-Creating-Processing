"""
OpenAI Whisper API Transcription Service
"""
from typing import Optional, Tuple
from pathlib import Path
from app.config import settings


async def transcribe_with_whisper_api(
    audio_path: str,
    language: str = None
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Transcribe audio using OpenAI Whisper API
    
    Args:
        audio_path: Path to audio file
        language: Language code (e.g., 'en', 'tr')
    
    Returns:
        Tuple of (success, transcription_text, error_message)
    """
    try:
        # Check API key
        if not settings.openai_api_key:
            return False, None, "OpenAI API key not configured"
        
        # Verify file exists
        file_path = Path(audio_path)
        if not file_path.exists():
            return False, None, "Audio file not found"
        
        # Check file size (max 25MB for Whisper API)
        file_size = file_path.stat().st_size
        if file_size > 25 * 1024 * 1024:
            return False, None, "File too large for Whisper API (max 25MB)"
        
        # Import OpenAI client
        try:
            from openai import OpenAI
        except ImportError:
            return False, None, "OpenAI package not installed"
        
        client = OpenAI(api_key=settings.openai_api_key)
        
        # Transcribe
        with open(audio_path, 'rb') as audio_file:
            kwargs = {'model': 'whisper-1', 'file': audio_file}
            if language:
                kwargs['language'] = language
            
            transcript = client.audio.transcriptions.create(**kwargs)
        
        text = transcript.text.strip() if transcript.text else ''
        
        if not text:
            return False, None, "Transcription resulted in empty text"
        
        return True, text, None
        
    except Exception as e:
        return False, None, str(e)

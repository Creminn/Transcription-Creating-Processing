"""
Remote Whisper Transcription Service
Connects to a Whisper API server (e.g., via Tailscale)
"""
from typing import Optional, Tuple
from pathlib import Path
import httpx
from app.config import settings


async def transcribe_with_whisper_remote(
    audio_path: str,
    model_size: str = None,
    language: str = None
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Transcribe audio using remote Whisper API server
    
    Args:
        audio_path: Path to audio file
        model_size: Whisper model size (tiny, base, small, medium, large)
        language: Language code (e.g., 'en', 'tr')
    
    Returns:
        Tuple of (success, transcription_text, error_message)
    """
    try:
        # Check if remote URL is configured
        if not settings.whisper_remote_url:
            return False, None, "Whisper remote URL not configured"
        
        # Verify file exists
        file_path = Path(audio_path)
        if not file_path.exists():
            return False, None, f"Audio file not found: {audio_path}"
        
        # Use default model size if not specified
        if model_size is None:
            model_size = settings.whisper_model_size
        
        # Determine device (use CPU as default for remote, or check settings)
        device = getattr(settings, 'whisper_device', 'cpu')
        
        # Read file content
        with open(audio_path, 'rb') as f:
            file_content = f.read()
        
        # Prepare form data
        files = {
            'file': (file_path.name, file_content, 'audio/mpeg')
        }
        data = {
            'model_size': model_size,
            'device': device
        }
        if language:
            data['language'] = language
        
        # Make request to remote Whisper server
        remote_url = settings.whisper_remote_url.rstrip('/')
        transcribe_url = f"{remote_url}/transcribe"
        
        async with httpx.AsyncClient(timeout=600.0) as client:  # 10 min timeout for large files
            response = await client.post(
                transcribe_url,
                files=files,
                data=data
            )
            response.raise_for_status()
            result = response.json()
        
        if not result.get('success'):
            return False, None, result.get('error', 'Transcription failed')
        
        text = result.get('text', '').strip()
        
        if not text:
            return False, None, "Transcription resulted in empty text"
        
        return True, text, None
        
    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error from Whisper server: {e.response.status_code} - {e.response.text}"
        return False, None, error_msg
    except httpx.RequestError as e:
        error_msg = f"Connection error to Whisper server: {str(e)}"
        return False, None, error_msg
    except Exception as e:
        return False, None, f"Transcription failed: {str(e)}"


async def transcribe_with_whisper_remote_url(
    audio_url: str,
    model_size: str = None,
    language: str = None
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Transcribe audio from URL using remote Whisper API server
    Useful when audio file is accessible via Tailscale network
    
    Args:
        audio_url: URL to audio file (can be Tailscale IP)
        model_size: Whisper model size
        language: Language code
    
    Returns:
        Tuple of (success, transcription_text, error_message)
    """
    try:
        # Check if remote URL is configured
        if not settings.whisper_remote_url:
            return False, None, "Whisper remote URL not configured"
        
        # Use default model size if not specified
        if model_size is None:
            model_size = settings.whisper_model_size
        
        # Determine device
        device = getattr(settings, 'whisper_device', 'cpu')
        
        # Prepare form data
        data = {
            'audio_url': audio_url,
            'model_size': model_size,
            'device': device
        }
        if language:
            data['language'] = language
        
        # Make request to remote Whisper server
        remote_url = settings.whisper_remote_url.rstrip('/')
        transcribe_url = f"{remote_url}/transcribe/url"
        
        async with httpx.AsyncClient(timeout=600.0) as client:
            response = await client.post(
                transcribe_url,
                data=data
            )
            response.raise_for_status()
            result = response.json()
        
        if not result.get('success'):
            return False, None, result.get('error', 'Transcription failed')
        
        text = result.get('text', '').strip()
        
        if not text:
            return False, None, "Transcription resulted in empty text"
        
        return True, text, None
        
    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error from Whisper server: {e.response.status_code} - {e.response.text}"
        return False, None, error_msg
    except httpx.RequestError as e:
        error_msg = f"Connection error to Whisper server: {str(e)}"
        return False, None, error_msg
    except Exception as e:
        return False, None, f"Transcription failed: {str(e)}"

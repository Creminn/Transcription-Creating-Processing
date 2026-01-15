"""
Google Speech-to-Text Transcription Service
"""
from typing import Optional, Tuple
from pathlib import Path
from app.config import settings


async def transcribe_with_google_stt(
    audio_path: str,
    language: str = 'en-US'
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Transcribe audio using Google Speech-to-Text API
    
    Args:
        audio_path: Path to audio file
        language: Language code (e.g., 'en-US', 'tr-TR')
    
    Returns:
        Tuple of (success, transcription_text, error_message)
    """
    try:
        # Check credentials
        creds_file = settings.google_application_credentials
        if not creds_file or not Path(creds_file).exists():
            return False, None, "Google Cloud credentials not configured"
        
        # Verify file exists
        file_path = Path(audio_path)
        if not file_path.exists():
            return False, None, "Audio file not found"
        
        # Import Google Speech client
        try:
            from google.cloud import speech
            import os
        except ImportError:
            return False, None, "Google Cloud Speech package not installed"
        
        # Set credentials environment variable
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_file
        
        client = speech.SpeechClient()
        
        # Read audio file
        with open(audio_path, 'rb') as audio_file:
            content = audio_file.read()
        
        # Determine encoding based on file extension
        extension = file_path.suffix.lower()
        if extension == '.mp3':
            encoding = speech.RecognitionConfig.AudioEncoding.MP3
        elif extension == '.wav':
            encoding = speech.RecognitionConfig.AudioEncoding.LINEAR16
        elif extension == '.flac':
            encoding = speech.RecognitionConfig.AudioEncoding.FLAC
        elif extension == '.m4a':
            encoding = speech.RecognitionConfig.AudioEncoding.MP3  # May need conversion
        else:
            encoding = speech.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED
        
        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=encoding,
            language_code=language,
            enable_automatic_punctuation=True,
        )
        
        # For long audio, use long running recognize
        file_size = file_path.stat().st_size
        
        if file_size > 10 * 1024 * 1024:  # > 10MB, use async
            operation = client.long_running_recognize(config=config, audio=audio)
            response = operation.result(timeout=600)  # 10 min timeout
        else:
            response = client.recognize(config=config, audio=audio)
        
        # Collect results
        transcripts = []
        for result in response.results:
            if result.alternatives:
                transcripts.append(result.alternatives[0].transcript)
        
        text = ' '.join(transcripts).strip()
        
        if not text:
            return False, None, "Transcription resulted in empty text"
        
        return True, text, None
        
    except Exception as e:
        return False, None, str(e)


def format_language_code(lang: str) -> str:
    """Convert short language code to Google format"""
    mapping = {
        'en': 'en-US',
        'tr': 'tr-TR',
        'de': 'de-DE',
        'fr': 'fr-FR',
        'es': 'es-ES',
        'it': 'it-IT',
        'ja': 'ja-JP',
        'zh': 'zh-CN',
    }
    return mapping.get(lang, lang)

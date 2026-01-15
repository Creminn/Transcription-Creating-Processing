"""
Local Whisper Transcription Service
"""
from typing import Optional, Tuple
from pathlib import Path
from app.config import settings


_model = None
_model_size = None


def load_whisper_model(model_size: str = None):
    """Load Whisper model (lazy loading)"""
    global _model, _model_size
    
    if model_size is None:
        model_size = settings.whisper_model_size
    
    if _model is None or _model_size != model_size:
        try:
            import whisper
            import torch
            
            # Determine device - force CPU if CUDA not available or if GPU model fails
            device = settings.whisper_device
            
            # Check if CUDA is actually available
            if device == "gpu" or device == "cuda":
                if not torch.cuda.is_available():
                    print(f"WARNING: GPU requested but CUDA not available, falling back to CPU")
                    device = "cpu"
                else:
                    device = "cuda"
            
            try:
                _model = whisper.load_model(model_size, device=device)
                _model_size = model_size
                print(f"Successfully loaded Whisper {model_size} model on {device}")
            except RuntimeError as e:
                # If loading fails with GPU-related error, try CPU
                if "gpu" in str(e).lower() or "cuda" in str(e).lower():
                    print(f"WARNING: Failed to load model on {device}, retrying with CPU")
                    print(f"Error was: {str(e)}")
                    
                    # Clear the cache and reload
                    import os
                    import shutil
                    cache_dir = os.path.expanduser("~/.cache/whisper")
                    if os.path.exists(cache_dir):
                        print(f"Clearing Whisper cache: {cache_dir}")
                        shutil.rmtree(cache_dir)
                    
                    # Try loading again with CPU
                    _model = whisper.load_model(model_size, device="cpu")
                    _model_size = model_size
                    print(f"Successfully loaded Whisper {model_size} model on CPU (after cache clear)")
                else:
                    raise
                    
        except ImportError:
            raise RuntimeError("Whisper is not installed. Run: pip install openai-whisper")
        except Exception as e:
            raise RuntimeError(f"Failed to load Whisper model: {str(e)}")
    
    return _model


async def transcribe_with_whisper_local(
    audio_path: str,
    model_size: str = None,
    language: str = None
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Transcribe audio using local Whisper model
    
    Args:
        audio_path: Path to audio file
        model_size: Whisper model size (tiny, base, small, medium, large)
        language: Language code (e.g., 'en', 'tr')
    
    Returns:
        Tuple of (success, transcription_text, error_message)
    """
    try:
        # Verify file exists
        if not Path(audio_path).exists():
            error_msg = f"Audio file not found: {audio_path}"
            print(f"ERROR: {error_msg}")
            return False, None, error_msg
        
        print(f"Starting transcription for: {audio_path}")
        print(f"Model size: {model_size}, Language: {language}")
        
        # Load model
        model = load_whisper_model(model_size)
        print(f"Model loaded successfully")
        
        # Transcribe
        options = {}
        if language:
            options['language'] = language
        
        print(f"Running transcription with options: {options}")
        result = model.transcribe(audio_path, **options)
        print(f"Transcription completed")
        
        text = result.get('text', '').strip()
        
        if not text:
            error_msg = "Transcription resulted in empty text"
            print(f"ERROR: {error_msg}")
            return False, None, error_msg
        
        print(f"Transcription successful, text length: {len(text)}")
        return True, text, None
        
    except Exception as e:
        error_msg = f"Transcription failed: {str(e)}"
        print(f"ERROR: {error_msg}")
        import traceback
        traceback.print_exc()
        return False, None, str(e)


def get_available_models() -> list:
    """Get list of available Whisper model sizes"""
    return ['tiny', 'base', 'small', 'medium', 'large']

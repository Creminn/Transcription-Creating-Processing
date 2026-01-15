"""
Standalone Whisper API Server
Host this on your remote server and connect via Tailscale
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
import uvicorn
import os
import tempfile
from pathlib import Path
import whisper
import torch

app = FastAPI(title="Whisper Transcription API", version="1.0.0")

# CORS configuration - adjust as needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model cache
_model_cache = {}
_model_sizes = ['tiny', 'base', 'small', 'medium', 'large']


def load_model(model_size: str = "base", device: str = "cpu"):
    """Load Whisper model with caching"""
    cache_key = f"{model_size}_{device}"
    
    if cache_key not in _model_cache:
        try:
            # Check if CUDA is available
            if device in ["gpu", "cuda"]:
                if not torch.cuda.is_available():
                    print(f"WARNING: GPU requested but CUDA not available, using CPU")
                    device = "cpu"
                else:
                    device = "cuda"
            
            print(f"Loading Whisper model: {model_size} on {device}")
            model = whisper.load_model(model_size, device=device)
            _model_cache[cache_key] = model
            print(f"Successfully loaded Whisper {model_size} model on {device}")
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to load Whisper model: {str(e)}"
            )
    
    return _model_cache[cache_key]


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Whisper Transcription API",
        "available_models": _model_sizes
    }


@app.get("/health")
async def health():
    """Health check with model info"""
    return {
        "status": "healthy",
        "loaded_models": list(_model_cache.keys()),
        "cuda_available": torch.cuda.is_available() if torch else False
    }


@app.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    model_size: str = Form(default="base"),
    language: Optional[str] = Form(default=None),
    device: str = Form(default="cpu")
):
    """
    Transcribe audio file using Whisper
    
    Args:
        file: Audio file (MP3, WAV, M4A, etc.)
        model_size: Whisper model size (tiny, base, small, medium, large)
        language: Language code (optional, e.g., 'en', 'tr')
        device: Device to use ('cpu' or 'cuda')
    
    Returns:
        JSON with transcription text
    """
    if model_size not in _model_sizes:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid model size. Must be one of: {', '.join(_model_sizes)}"
        )
    
    # Save uploaded file to temporary location
    temp_file = None
    try:
        # Create temp file
        suffix = Path(file.filename).suffix if file.filename else ".tmp"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            temp_file = tmp.name
            content = await file.read()
            tmp.write(content)
        
        # Load model
        model = load_model(model_size, device)
        
        # Transcribe
        options = {}
        if language:
            options['language'] = language
        
        print(f"Transcribing file: {file.filename} with model: {model_size}")
        result = model.transcribe(temp_file, **options)
        
        text = result.get('text', '').strip()
        
        if not text:
            raise HTTPException(
                status_code=500,
                detail="Transcription resulted in empty text"
            )
        
        return {
            "success": True,
            "text": text,
            "language": result.get('language'),
            "model_size": model_size
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}"
        )
    finally:
        # Clean up temp file
        if temp_file and os.path.exists(temp_file):
            os.unlink(temp_file)


@app.post("/transcribe/url")
async def transcribe_from_url(
    audio_url: str = Form(...),
    model_size: str = Form(default="base"),
    language: Optional[str] = Form(default=None),
    device: str = Form(default="cpu")
):
    """
    Transcribe audio from a URL (useful for Tailscale network)
    
    Args:
        audio_url: URL to audio file (can be Tailscale IP)
        model_size: Whisper model size
        language: Language code (optional)
        device: Device to use ('cpu' or 'cuda')
    
    Returns:
        JSON with transcription text
    """
    if model_size not in _model_sizes:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid model size. Must be one of: {', '.join(_model_sizes)}"
        )
    
    try:
        import requests
        
        # Download file
        response = requests.get(audio_url, timeout=300)  # 5 min timeout
        response.raise_for_status()
        
        # Save to temp file
        suffix = Path(audio_url).suffix or ".tmp"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            temp_file = tmp.name
            tmp.write(response.content)
        
        # Load model and transcribe
        model = load_model(model_size, device)
        
        options = {}
        if language:
            options['language'] = language
        
        print(f"Transcribing from URL: {audio_url} with model: {model_size}")
        result = model.transcribe(temp_file, **options)
        
        text = result.get('text', '').strip()
        
        if not text:
            raise HTTPException(
                status_code=500,
                detail="Transcription resulted in empty text"
            )
        
        return {
            "success": True,
            "text": text,
            "language": result.get('language'),
            "model_size": model_size
        }
    
    except requests.RequestException as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to download audio from URL: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}"
        )
    finally:
        # Clean up temp file
        if 'temp_file' in locals() and os.path.exists(temp_file):
            os.unlink(temp_file)


if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("WHISPER_HOST", "0.0.0.0")
    port = int(os.getenv("WHISPER_PORT", "8001"))
    
    print(f"Starting Whisper API server on {host}:{port}")
    print(f"CUDA available: {torch.cuda.is_available() if torch else False}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )

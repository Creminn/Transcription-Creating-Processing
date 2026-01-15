"""
Google Gemini Service
"""
from typing import Optional, Tuple, Dict
from app.config import settings


async def generate_with_gemini(
    prompt: str,
    model: str = "gemini-pro",
    system_prompt: Optional[str] = None,
    max_tokens: int = 4000,
    temperature: float = 0.7
) -> Tuple[bool, Optional[str], Optional[Dict], Optional[str]]:
    """
    Generate text using Google Gemini models
    
    Args:
        prompt: User prompt
        model: Model name (gemini-pro, etc.)
        system_prompt: Optional system message
        max_tokens: Maximum tokens in response
        temperature: Temperature for generation
    
    Returns:
        Tuple of (success, generated_text, token_usage, error_message)
    """
    try:
        if not settings.google_gemini_api_key:
            return False, None, None, "Google Gemini API key not configured"
        
        try:
            import google.generativeai as genai
        except ImportError:
            return False, None, None, "Google GenerativeAI package not installed"
        
        genai.configure(api_key=settings.google_gemini_api_key)
        
        # Create model
        generation_config = {
            'temperature': temperature,
            'max_output_tokens': max_tokens,
        }
        
        gemini_model = genai.GenerativeModel(
            model_name=model,
            generation_config=generation_config
        )
        
        # Build prompt
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        # Generate
        response = gemini_model.generate_content(full_prompt)
        
        content = response.text if response.text else None
        
        # Gemini doesn't provide detailed token counts in the same way
        usage = {
            'input_tokens': None,
            'output_tokens': None
        }
        
        return True, content, usage, None
        
    except Exception as e:
        return False, None, None, str(e)


def get_available_models() -> list:
    """Get available Gemini models"""
    return [
        {'id': 'gemini-pro', 'name': 'Gemini Pro', 'context_length': 32000},
        {'id': 'gemini-1.5-pro', 'name': 'Gemini 1.5 Pro', 'context_length': 1000000},
    ]

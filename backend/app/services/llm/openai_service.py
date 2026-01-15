"""
OpenAI GPT Service
"""
from typing import Optional, Tuple, Dict
from app.config import settings


async def generate_with_openai(
    prompt: str,
    model: str = "gpt-4",
    system_prompt: Optional[str] = None,
    max_tokens: int = 4000,
    temperature: float = 0.7
) -> Tuple[bool, Optional[str], Optional[Dict], Optional[str]]:
    """
    Generate text using OpenAI GPT models
    
    Args:
        prompt: User prompt
        model: Model name (gpt-4, gpt-3.5-turbo, etc.)
        system_prompt: Optional system message
        max_tokens: Maximum tokens in response
        temperature: Temperature for generation
    
    Returns:
        Tuple of (success, generated_text, token_usage, error_message)
    """
    try:
        if not settings.openai_api_key:
            return False, None, None, "OpenAI API key not configured"
        
        try:
            from openai import OpenAI
        except ImportError:
            return False, None, None, "OpenAI package not installed"
        
        client = OpenAI(api_key=settings.openai_api_key)
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        content = response.choices[0].message.content if response.choices else None
        
        usage = {
            'input_tokens': response.usage.prompt_tokens if response.usage else None,
            'output_tokens': response.usage.completion_tokens if response.usage else None
        }
        
        return True, content, usage, None
        
    except Exception as e:
        return False, None, None, str(e)


def get_available_models() -> list:
    """Get available OpenAI models"""
    return [
        {'id': 'gpt-4', 'name': 'GPT-4', 'context_length': 8192},
        {'id': 'gpt-4-turbo', 'name': 'GPT-4 Turbo', 'context_length': 128000},
        {'id': 'gpt-3.5-turbo', 'name': 'GPT-3.5 Turbo', 'context_length': 16385},
    ]

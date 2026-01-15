"""
Main LLM Service - Orchestrates different LLM backends
"""
from typing import Optional, Tuple, Dict, List

from app.services.llm.openai_service import generate_with_openai
from app.services.llm.gemini_service import generate_with_gemini
from app.services.llm.ollama_service import generate_with_ollama


# Model to backend mapping
LLM_MODELS = {
    'gpt-4': {'backend': 'openai', 'model': 'gpt-4'},
    'gpt-4-turbo': {'backend': 'openai', 'model': 'gpt-4-turbo'},
    'gpt-3.5-turbo': {'backend': 'openai', 'model': 'gpt-3.5-turbo'},
    'gemini-pro': {'backend': 'gemini', 'model': 'gemini-pro'},
    'gemini-1.5-pro': {'backend': 'gemini', 'model': 'gemini-1.5-pro'},
    'llama2': {'backend': 'ollama', 'model': 'llama2'},
    'llama2:13b': {'backend': 'ollama', 'model': 'llama2:13b'},
    'mistral': {'backend': 'ollama', 'model': 'mistral'},
    'mixtral': {'backend': 'ollama', 'model': 'mixtral'},
    'codellama': {'backend': 'ollama', 'model': 'codellama'},
}


async def generate(
    prompt: str,
    model: str = 'gpt-4',
    system_prompt: Optional[str] = None,
    max_tokens: int = 4000,
    temperature: float = 0.7
) -> Tuple[bool, Optional[str], Optional[Dict], Optional[str]]:
    """
    Generate text using specified LLM model
    
    Args:
        prompt: User prompt
        model: Model identifier
        system_prompt: Optional system message
        max_tokens: Maximum tokens in response
        temperature: Temperature for generation
    
    Returns:
        Tuple of (success, generated_text, token_usage, error_message)
    """
    model_config = LLM_MODELS.get(model)
    
    if not model_config:
        # Try using the model name directly with Ollama
        return await generate_with_ollama(
            prompt, model, system_prompt, max_tokens, temperature
        )
    
    backend = model_config['backend']
    actual_model = model_config['model']
    
    if backend == 'openai':
        return await generate_with_openai(
            prompt, actual_model, system_prompt, max_tokens, temperature
        )
    elif backend == 'gemini':
        return await generate_with_gemini(
            prompt, actual_model, system_prompt, max_tokens, temperature
        )
    elif backend == 'ollama':
        return await generate_with_ollama(
            prompt, actual_model, system_prompt, max_tokens, temperature
        )
    
    return False, None, None, f"Unknown backend: {backend}"


def get_available_models() -> List[Dict]:
    """Get list of all available LLM models"""
    return [
        {'id': 'gpt-4', 'name': 'GPT-4 (OpenAI)', 'type': 'cloud'},
        {'id': 'gpt-4-turbo', 'name': 'GPT-4 Turbo (OpenAI)', 'type': 'cloud'},
        {'id': 'gpt-3.5-turbo', 'name': 'GPT-3.5 Turbo (OpenAI)', 'type': 'cloud'},
        {'id': 'gemini-pro', 'name': 'Gemini Pro (Google)', 'type': 'cloud'},
        {'id': 'gemini-1.5-pro', 'name': 'Gemini 1.5 Pro (Google)', 'type': 'cloud'},
        {'id': 'llama2', 'name': 'Llama 2 (Ollama)', 'type': 'local'},
        {'id': 'llama2:13b', 'name': 'Llama 2 13B (Ollama)', 'type': 'local'},
        {'id': 'mistral', 'name': 'Mistral 7B (Ollama)', 'type': 'local'},
        {'id': 'mixtral', 'name': 'Mixtral 8x7B (Ollama)', 'type': 'local'},
    ]

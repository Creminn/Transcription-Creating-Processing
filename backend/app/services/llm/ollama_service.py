"""
Ollama Local LLM Service
"""
from typing import Optional, Tuple, Dict
import httpx
from app.config import settings


async def generate_with_ollama(
    prompt: str,
    model: str = "llama2",
    system_prompt: Optional[str] = None,
    max_tokens: int = 4000,
    temperature: float = 0.7
) -> Tuple[bool, Optional[str], Optional[Dict], Optional[str]]:
    """
    Generate text using Ollama local models
    
    Args:
        prompt: User prompt
        model: Model name (llama2, mistral, etc.)
        system_prompt: Optional system message
        max_tokens: Maximum tokens in response
        temperature: Temperature for generation
    
    Returns:
        Tuple of (success, generated_text, token_usage, error_message)
    """
    try:
        ollama_host = settings.ollama_host.rstrip('/')
        
        # Build request
        request_data = {
            'model': model,
            'prompt': prompt,
            'stream': False,
            'options': {
                'temperature': temperature,
                'num_predict': max_tokens
            }
        }
        
        if system_prompt:
            request_data['system'] = system_prompt
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{ollama_host}/api/generate",
                json=request_data
            )
            
            if response.status_code != 200:
                return False, None, None, f"Ollama returned status {response.status_code}"
            
            data = response.json()
            content = data.get('response', '')
            
            usage = {
                'input_tokens': data.get('prompt_eval_count'),
                'output_tokens': data.get('eval_count')
            }
            
            return True, content, usage, None
        
    except httpx.ConnectError:
        return False, None, None, f"Could not connect to Ollama at {settings.ollama_host}"
    except Exception as e:
        return False, None, None, str(e)


async def list_ollama_models() -> Tuple[bool, Optional[list], Optional[str]]:
    """List available models in Ollama"""
    try:
        ollama_host = settings.ollama_host.rstrip('/')
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{ollama_host}/api/tags")
            
            if response.status_code != 200:
                return False, None, f"Ollama returned status {response.status_code}"
            
            data = response.json()
            models = data.get('models', [])
            
            return True, [{'id': m['name'], 'name': m['name']} for m in models], None
            
    except httpx.ConnectError:
        return False, None, f"Could not connect to Ollama at {settings.ollama_host}"
    except Exception as e:
        return False, None, str(e)


def get_available_models() -> list:
    """Get commonly available Ollama models"""
    return [
        {'id': 'llama2', 'name': 'Llama 2', 'context_length': 4096},
        {'id': 'llama2:13b', 'name': 'Llama 2 13B', 'context_length': 4096},
        {'id': 'mistral', 'name': 'Mistral 7B', 'context_length': 8192},
        {'id': 'mixtral', 'name': 'Mixtral 8x7B', 'context_length': 32000},
        {'id': 'codellama', 'name': 'Code Llama', 'context_length': 16384},
        {'id': 'phi', 'name': 'Phi-2', 'context_length': 2048},
    ]

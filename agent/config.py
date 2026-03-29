"""
Configuration — Load .env config (OLLAMA_HOST, model).
"""

import os
from pathlib import Path
from typing import Optional

from .logger import setup_logger

logger = setup_logger(__name__)

ENV_PATH = Path('./.env')


def load_env() -> dict:
    """Load environment variables from .env file.
    
    Returns:
        Dictionary of environment variables
    """
    env_vars = {}
    
    if ENV_PATH.exists():
        try:
            with open(ENV_PATH, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
            logger.debug(f"Loaded {len(env_vars)} variables from .env")
        except Exception as e:
            logger.warning(f"Failed to load .env: {e}")
    
    return env_vars


def get_ollama_host() -> str:
    """Get Ollama host from environment.
    
    Returns:
        Ollama host URL (default: http://localhost:11434)
    """
    env_vars = load_env()
    return env_vars.get('OLLAMA_HOST', 'http://localhost:11434')


def get_ollama_model(env_key: str = 'OLLAMA_MODEL', default: str = 'mistral:latest') -> str:
    """Get Ollama model from environment.
    
    Args:
        env_key: Environment variable name
        default: Default model if not set
        
    Returns:
        Model name
    """
    env_vars = load_env()
    model = env_vars.get(env_key) or os.environ.get(env_key)
    return model if model else default


def get_ollama_timeout() -> int:
    """Get Ollama timeout from environment.
    
    Returns:
        Timeout in seconds (default: 120)
    """
    env_vars = load_env()
    try:
        return int(env_vars.get('OLLAMA_TIMEOUT', '120000')) // 1000
    except ValueError:
        return 120


def get_ollama_max_tokens() -> int:
    """Get Ollama max tokens from environment.
    
    Returns:
        Max tokens (default: 4096)
    """
    env_vars = load_env()
    try:
        return int(env_vars.get('OLLAMA_MAX_TOKENS', '4096'))
    except ValueError:
        return 4096

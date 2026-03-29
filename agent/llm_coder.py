#!/usr/bin/env python3
"""
LLM Coder — Send task to codellama:7b via Ollama API.
"""

import json
import urllib.request
import urllib.error
from typing import Optional, Dict, Any

from .logger import setup_logger
from .config import get_ollama_host, get_ollama_model

logger = setup_logger(__name__)


class LLMDcoder:
    """Generate code using codellama:7b via Ollama API."""

    def __init__(self):
        """Initialize LLM coder."""
        self.host = get_ollama_host()
        self.model = get_ollama_model('OLLAMA_CODE_MODEL', 'codellama:7b')
        self.timeout = 120  # seconds

    def generate_code(self, task: Dict[str, Any]) -> Optional[str]:
        """Generate code for task using codellama:7b.
        
        Args:
            task: Task dictionary with id, name, desc
            
        Returns:
            Generated code string or None
        """
        prompt = self._build_prompt(task)
        
        try:
            response = self._call_ollama(prompt)
            if response:
                logger.info(f"Generated code for task {task['id']}")
                return response
            else:
                logger.error(f"No code generated for task {task['id']}")
                return None
                
        except Exception as e:
            logger.error(f"LLM generation failed for task {task['id']}: {e}")
            return None

    def _build_prompt(self, task: Dict[str, Any]) -> str:
        """Build prompt for code generation.
        
        Args:
            task: Task dictionary
            
        Returns:
            Prompt string
        """
        task_id = task.get('id', 'unknown')
        task_name = task.get('name', '')
        task_desc = task.get('desc', '')
        layer = task.get('layer', 'general')

        # Determine language from task
        language = self._detect_language(task)

        prompt = f"""You are an expert software engineer. Generate clean, production-ready code for the following task:

Task ID: {task_id}
Task Name: {task_name}
Layer: {layer}
Description: {task_desc}

Requirements:
1. Write complete, working code (no placeholders or TODOs)
2. Include proper error handling
3. Follow best practices for {language}
4. Include docstrings/comments
5. Do not include markdown code fences

Generate the code now:"""

        return prompt

    def _detect_language(self, task: Dict[str, Any]) -> str:
        """Detect programming language from task.
        
        Args:
            task: Task dictionary
            
        Returns:
            Language name
        """
        task_id = task.get('id', '').lower()
        
        if 'rust' in task_id or 'backend' in task_id:
            return 'Rust'
        elif 'python' in task_id or 'agent' in task_id:
            return 'Python'
        elif 'test' in task_id:
            return 'TypeScript'
        else:
            return 'TypeScript'  # Default

    def _call_ollama(self, prompt: str) -> Optional[str]:
        """Call Ollama API for code generation.
        
        Args:
            prompt: Prompt string
            
        Returns:
            Generated code string or None
        """
        url = f"{self.host}/api/generate"
        
        data = {
            'model': self.model,
            'prompt': prompt,
            'stream': False,
            'options': {
                'temperature': 0.7,
                'top_p': 0.9,
                'num_predict': 2048
            }
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get('response', '')

        except urllib.error.URLError as e:
            logger.error(f"Ollama API error: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Ollama response: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error calling Ollama: {e}")
            return None


# Convenience function for direct usage
def generate_code_from_llm(task: Dict[str, Any]) -> Optional[str]:
    """Generate code using LLM (codellama:7b).
    
    Args:
        task: Task dictionary
        
    Returns:
        Generated code string or None
    """
    coder = LLMDcoder()
    return coder.generate_code(task)

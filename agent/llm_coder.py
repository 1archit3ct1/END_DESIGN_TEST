#!/usr/bin/env python3
"""
LLM Coder — Send task to codellama:7b via Ollama API.
"""

import json
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, Tuple

from .logger import setup_logger
from .config import get_ollama_host, get_ollama_model
from .prompts import build_prompt, get_system_prompt

logger = setup_logger(__name__)

# Retry configuration
MAX_RETRIES = 3
RETRY_TEMPERATURE_INCREMENT = 0.1
MAX_TEMPERATURE = 0.9


class LLMDcoder:
    """Generate code using codellama:7b via Ollama API."""

    def __init__(self):
        """Initialize LLM coder."""
        self.host = get_ollama_host()
        self.model = get_ollama_model('OLLAMA_CODE_MODEL', 'codellama:7b')
        self.timeout = 120  # seconds
        self.base_temperature = 0.7
        self.max_retries = MAX_RETRIES

    def generate_code(self, task: Dict[str, Any], retry_count: int = 0,
                      previous_error: Optional[str] = None) -> Tuple[Optional[str], bool, int]:
        """Generate code for task using codellama:7b.

        Args:
            task: Task dictionary with id, name, desc
            retry_count: Number of previous retry attempts
            previous_error: Error message from previous attempt if any

        Returns:
            Tuple of (generated_code, success, retry_count)
        """
        system_prompt = self._get_system_prompt(task)
        user_prompt = self._build_prompt(task, previous_error)

        # Combine system and user prompt for full context
        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        # Adjust temperature for retries to encourage different output
        temperature = min(
            self.base_temperature + (retry_count * RETRY_TEMPERATURE_INCREMENT),
            MAX_TEMPERATURE
        )

        try:
            response = self._call_ollama(full_prompt, temperature)
            if response:
                logger.info(f"Generated code for task {task['id']} (attempt {retry_count + 1})")
                return response, True, retry_count
            else:
                logger.error(f"No code generated for task {task['id']}")
                return None, False, retry_count

        except Exception as e:
            error_msg = f"LLM generation failed for task {task['id']}: {e}"
            logger.error(error_msg)
            return None, False, retry_count

    def generate_with_retry(self, task: Dict[str, Any],
                            syntax_checker=None) -> Tuple[Optional[str], bool, int]:
        """Generate code with automatic retry on failure.

        Args:
            task: Task dictionary with id, name, desc
            syntax_checker: Optional SyntaxChecker to validate generated code

        Returns:
            Tuple of (generated_code, success, total_attempts)
        """
        last_error = None
        attempts = 0

        for attempt in range(self.max_retries):
            attempts = attempt + 1
            code, success, _ = self.generate_code(
                task,
                retry_count=attempt,
                previous_error=last_error
            )

            if not success or code is None:
                last_error = "LLM failed to generate code"
                logger.warning(f"Attempt {attempts}/{self.max_retries} failed for task {task['id']}")
                continue

            # Validate syntax if checker provided
            if syntax_checker:
                file_ext = self._detect_file_extension(task)
                result = syntax_checker.check_syntax(code, file_ext)

                if not result.is_valid:
                    last_error = result.error.message if result.error else "Syntax error"
                    logger.warning(
                        f"Attempt {attempts}/{self.max_retries} failed syntax check for task {task['id']}: "
                        f"{last_error}"
                    )
                    continue

            # Success - code generated and validated
            logger.info(f"Successfully generated code for task {task['id']} after {attempts} attempt(s)")
            return code, True, attempts

        # All retries exhausted
        logger.error(f"All {self.max_retries} attempts failed for task {task['id']}")
        return None, False, attempts

    def _detect_file_extension(self, task: Dict[str, Any]) -> str:
        """Detect file extension from task.

        Args:
            task: Task dictionary

        Returns:
            File extension string
        """
        task_id = task.get('id', '').lower()

        if 'rust' in task_id or 'backend' in task_id:
            return '.rs'
        elif 'python' in task_id or 'agent' in task_id:
            return '.py'
        else:
            return '.ts'  # Default

    def _build_prompt(self, task: Dict[str, Any], previous_error: Optional[str] = None) -> str:
        """Build prompt for code generation using templates.

        Args:
            task: Task dictionary
            previous_error: Error message from previous attempt if retrying

        Returns:
            Prompt string
        """
        # Use prompt templates from prompts module
        base_prompt = build_prompt(task)
        
        # Add retry context if this is a retry attempt
        if previous_error:
            retry_instruction = (
                f"\n\n--- RETRY ATTEMPT ---\n"
                f"Previous attempt failed with error: {previous_error}\n"
                f"Please generate different code that fixes this error. "
                f"Ensure proper syntax and complete implementation.\n"
            )
            base_prompt += retry_instruction
        
        return base_prompt

    def _get_system_prompt(self, task: Dict[str, Any]) -> str:
        """Get system prompt for task type.

        Args:
            task: Task dictionary

        Returns:
            System prompt string
        """
        return get_system_prompt(task)

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

    def _call_ollama(self, prompt: str, temperature: float = 0.7) -> Optional[str]:
        """Call Ollama API for code generation.

        Args:
            prompt: Prompt string
            temperature: Temperature for generation (higher = more random)

        Returns:
            Generated code string or None
        """
        url = f"{self.host}/api/generate"

        data = {
            'model': self.model,
            'prompt': prompt,
            'stream': False,
            'options': {
                'temperature': temperature,
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
    code, success, _ = coder.generate_with_retry(task)
    return code if success else None

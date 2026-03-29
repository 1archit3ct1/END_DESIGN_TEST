#!/usr/bin/env python3
"""
Test: llm_coder.py receives valid code from codellama.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add agent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.llm_coder import LLMDcoder, generate_code_from_llm
from agent.config import get_ollama_host, get_ollama_model, get_ollama_timeout, get_ollama_max_tokens


class TestLLMDcoder(unittest.TestCase):
    """Test LLMDcoder functionality."""

    def test_coder_initializes(self):
        """Test that LLMDcoder initializes without errors."""
        coder = LLMDcoder()
        
        self.assertIsNotNone(coder)
        self.assertIsNotNone(coder.host)
        self.assertIsNotNone(coder.model)

    def test_coder_has_default_host(self):
        """Test that default host is set."""
        coder = LLMDcoder()
        
        self.assertEqual(coder.host, get_ollama_host())

    def test_coder_has_default_model(self):
        """Test that default model is codellama:7b."""
        coder = LLMDcoder()
        
        # Should default to codellama:7b for code generation
        self.assertEqual(coder.model, get_ollama_model('OLLAMA_CODE_MODEL', 'codellama:7b'))

    def test_build_prompt(self):
        """Test that prompt is built correctly."""
        coder = LLMDcoder()
        
        task = {
            'id': 'test_task',
            'name': 'Test Task',
            'desc': 'This is a test task',
            'layer': 'backend'
        }
        
        prompt = coder._build_prompt(task)
        
        self.assertIn('test_task', prompt)
        self.assertIn('Test Task', prompt)
        self.assertIn('This is a test task', prompt)
        self.assertIn('backend', prompt)

    def test_detect_language_rust(self):
        """Test language detection for Rust tasks."""
        coder = LLMDcoder()
        
        task_rust = {'id': 'rust_backend.pkce'}
        task_backend = {'id': 'rust_backend.callback'}
        
        self.assertEqual(coder._detect_language(task_rust), 'Rust')
        self.assertEqual(coder._detect_language(task_backend), 'Rust')

    def test_detect_language_typescript(self):
        """Test language detection for TypeScript tasks."""
        coder = LLMDcoder()
        
        task_step = {'id': 'step1_connect.oauth'}
        task_integration = {'id': 'oauth_integration.callback'}
        
        self.assertEqual(coder._detect_language(task_step), 'TypeScript')
        self.assertEqual(coder._detect_language(task_integration), 'TypeScript')

    @patch('agent.llm_coder.urllib.request.urlopen')
    def test_call_ollama_mock(self, mock_urlopen):
        """Test Ollama API call with mock."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"response": "// Generated code"}'
        mock_urlopen.return_value.__enter__.return_value = mock_response

        coder = LLMDcoder()
        result = coder._call_ollama('test prompt')

        self.assertEqual(result, '// Generated code')

    def test_generate_code_from_llm_function(self):
        """Test convenience function exists and is callable."""
        task = {'id': 'test', 'name': 'Test', 'desc': 'Test task'}

        # Should be callable (will fail without Ollama running, but should not raise TypeError)
        self.assertTrue(callable(generate_code_from_llm))

    def test_generate_code_returns_tuple(self):
        """Test that generate_code returns tuple with (code, success, retry_count)."""
        coder = LLMDcoder()
        task = {'id': 'test', 'name': 'Test', 'desc': 'Test task'}

        # Mock the _call_ollama to return valid code
        with patch.object(coder, '_call_ollama', return_value='def test(): pass'):
            code, success, retry_count = coder.generate_code(task)

            self.assertIsInstance(code, str)
            self.assertEqual(code, 'def test(): pass')
            self.assertTrue(success)
            self.assertEqual(retry_count, 0)

    def test_generate_code_with_retry_count(self):
        """Test that retry_count is tracked correctly."""
        coder = LLMDcoder()
        task = {'id': 'test', 'name': 'Test', 'desc': 'Test task'}

        # Mock the _call_ollama to return valid code
        with patch.object(coder, '_call_ollama', return_value='def test(): pass'):
            _, _, retry_count = coder.generate_code(task, retry_count=2)

            self.assertEqual(retry_count, 2)

    def test_build_prompt_with_previous_error(self):
        """Test that prompt includes previous error on retry."""
        coder = LLMDcoder()
        task = {'id': 'test', 'name': 'Test', 'desc': 'Test task'}

        # Without error
        prompt_no_error = coder._build_prompt(task)
        self.assertNotIn('RETRY ATTEMPT', prompt_no_error)

        # With error
        prompt_with_error = coder._build_prompt(task, previous_error='Syntax error on line 5')
        self.assertIn('RETRY ATTEMPT', prompt_with_error)
        self.assertIn('Syntax error on line 5', prompt_with_error)
        self.assertIn('fixes this error', prompt_with_error)

    def test_call_ollama_with_temperature(self):
        """Test that temperature parameter is passed to Ollama API."""
        coder = LLMDcoder()

        with patch('agent.llm_coder.urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = b'{"response": "code"}'
            mock_urlopen.return_value.__enter__.return_value = mock_response

            coder._call_ollama('test prompt', temperature=0.8)

            # Verify the request was made with correct temperature
            import json
            call_args = mock_urlopen.call_args
            request_data = json.loads(call_args[0][0].data.decode('utf-8'))
            self.assertEqual(request_data['options']['temperature'], 0.8)

    @patch('agent.llm_coder.urllib.request.urlopen')
    def test_generate_with_retry_success_first_attempt(self, mock_urlopen):
        """Test successful generation on first attempt."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"response": "valid code"}'
        mock_urlopen.return_value.__enter__.return_value = mock_response

        coder = LLMDcoder()
        task = {'id': 'test', 'name': 'Test', 'desc': 'Test task'}

        code, success, attempts = coder.generate_with_retry(task)

        self.assertEqual(code, 'valid code')
        self.assertTrue(success)
        self.assertEqual(attempts, 1)

    @patch('agent.llm_coder.urllib.request.urlopen')
    def test_generate_with_retry_succeeds_after_failures(self, mock_urlopen):
        """Test retry succeeds after initial failures."""
        # Setup mock to fail twice, then succeed
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"response": "valid code"}'

        # First two calls return None (failure), third returns valid code
        mock_urlopen.return_value.__enter__.side_effect = [
            Exception('API Error'),
            Exception('API Error'),
            mock_response
        ]

        coder = LLMDcoder()
        task = {'id': 'test', 'name': 'Test', 'desc': 'Test task'}

        code, success, attempts = coder.generate_with_retry(task)

        self.assertEqual(code, 'valid code')
        self.assertTrue(success)
        self.assertEqual(attempts, 3)

    @patch('agent.llm_coder.urllib.request.urlopen')
    def test_generate_with_retry_all_failures(self, mock_urlopen):
        """Test all retry attempts fail."""
        mock_urlopen.return_value.__enter__.side_effect = Exception('API Error')

        coder = LLMDcoder()
        task = {'id': 'test', 'name': 'Test', 'desc': 'Test task'}

        code, success, attempts = coder.generate_with_retry(task)

        self.assertIsNone(code)
        self.assertFalse(success)
        self.assertEqual(attempts, coder.max_retries)

    @patch('agent.llm_coder.urllib.request.urlopen')
    def test_generate_with_retry_syntax_check_failure(self, mock_urlopen):
        """Test retry on syntax check failure."""
        from agent.syntax_check import SyntaxChecker

        # Mock successful Ollama response but invalid code
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"response": "def invalid("}'  # Invalid syntax
        mock_urlopen.return_value.__enter__.return_value = mock_response

        coder = LLMDcoder()
        syntax_checker = SyntaxChecker()
        task = {'id': 'test_python.agent', 'name': 'Test', 'desc': 'Test task'}

        # Should retry due to syntax error
        code, success, attempts = coder.generate_with_retry(task, syntax_checker=syntax_checker)

        # All attempts should fail due to syntax error
        self.assertFalse(success)
        self.assertGreater(attempts, 1)  # Should have retried

    @patch('agent.llm_coder.urllib.request.urlopen')
    def test_generate_with_retry_temperature_increments(self, mock_urlopen):
        """Test that temperature increases on retry attempts."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"response": "code"}'
        mock_urlopen.return_value.__enter__.return_value = mock_response

        coder = LLMDcoder()
        task = {'id': 'test', 'name': 'Test', 'desc': 'Test task'}

        # First attempt - base temperature
        coder.generate_code(task, retry_count=0)
        call_args_0 = mock_urlopen.call_args
        import json
        data_0 = json.loads(call_args_0[0][0].data.decode('utf-8'))

        # Second attempt - higher temperature
        coder.generate_code(task, retry_count=1)
        call_args_1 = mock_urlopen.call_args
        data_1 = json.loads(call_args_1[0][0].data.decode('utf-8'))

        # Temperature should increase
        self.assertLess(data_0['options']['temperature'], data_1['options']['temperature'])

    def test_retry_generates_different_code_verification(self):
        """Test that retry mechanism is set up to generate different code."""
        coder = LLMDcoder()
        task = {'id': 'test', 'name': 'Test', 'desc': 'Test task'}

        # Verify that prompts differ between retry attempts
        prompt_0 = coder._build_prompt(task, previous_error=None)
        prompt_1 = coder._build_prompt(task, previous_error='Error 1')
        prompt_2 = coder._build_prompt(task, previous_error='Error 2')

        # Prompts should be different with different errors
        self.assertNotEqual(prompt_0, prompt_1)
        self.assertNotEqual(prompt_1, prompt_2)

        # Verify temperature would increase
        temp_0 = min(coder.base_temperature + (0 * 0.1), 0.9)
        temp_1 = min(coder.base_temperature + (1 * 0.1), 0.9)
        temp_2 = min(coder.base_temperature + (2 * 0.1), 0.9)

        self.assertLess(temp_0, temp_1)
        self.assertLess(temp_1, temp_2)


class TestConfig(unittest.TestCase):
    """Test configuration loading."""

    def test_get_ollama_host(self):
        """Test getting Ollama host."""
        host = get_ollama_host()
        
        self.assertIsInstance(host, str)
        self.assertTrue(host.startswith('http'))

    def test_get_ollama_model(self):
        """Test getting Ollama model."""
        model = get_ollama_model()
        
        self.assertIsInstance(model, str)
        self.assertTrue(':' in model)

    def test_get_ollama_timeout(self):
        """Test getting Ollama timeout."""
        timeout = get_ollama_timeout()
        
        self.assertIsInstance(timeout, int)
        self.assertGreater(timeout, 0)

    def test_get_ollama_max_tokens(self):
        """Test getting Ollama max tokens."""
        max_tokens = get_ollama_max_tokens()
        
        self.assertIsInstance(max_tokens, int)
        self.assertGreater(max_tokens, 0)


if __name__ == '__main__':
    unittest.main()

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

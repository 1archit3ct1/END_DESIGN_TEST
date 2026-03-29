"""
Test LLM Coder — LLM generation tests.
"""

import pytest
from unittest.mock import patch, MagicMock

from agent.llm_coder import LLMDcoder, generate_code_from_llm


class TestLLMDcoder:
    """Test LLM Coder functionality."""

    @pytest.fixture
    def coder(self):
        """Create LLMDcoder instance."""
        return LLMDcoder()

    @pytest.fixture
    def sample_task(self):
        """Create sample task."""
        return {
            'id': 'test.task',
            'name': 'Test Task',
            'desc': 'Test description'
        }

    def test_initialization(self, coder):
        """Test coder initializes correctly."""
        assert coder.max_retries == 3
        assert coder.base_temperature == 0.7
        assert coder.timeout == 120

    def test_detect_file_extension_rust(self, coder):
        """Test file extension detection for Rust."""
        task = {'id': 'rust_backend.auth'}
        ext = coder._detect_file_extension(task)
        assert ext == '.rs'

    def test_detect_file_extension_python(self, coder):
        """Test file extension detection for Python."""
        task = {'id': 'agent.python'}
        ext = coder._detect_file_extension(task)
        assert ext == '.py'

    def test_detect_file_extension_default(self, coder):
        """Test default file extension."""
        task = {'id': 'ui.component'}
        ext = coder._detect_file_extension(task)
        assert ext == '.ts'

    def test_build_prompt(self, coder, sample_task):
        """Test prompt building."""
        prompt = coder._build_prompt(sample_task)
        
        assert 'Test Task' in prompt
        assert 'Test description' in prompt

    def test_build_prompt_with_retry(self, coder, sample_task):
        """Test prompt building with retry context."""
        error = "Previous error message"
        prompt = coder._build_prompt(sample_task, previous_error=error)
        
        assert 'RETRY ATTEMPT' in prompt
        assert error in prompt

    def test_detect_language_rust(self, coder):
        """Test language detection for Rust."""
        task = {'id': 'rust_backend.module'}
        lang = coder._detect_language(task)
        assert lang == 'Rust'

    def test_detect_language_python(self, coder):
        """Test language detection for Python."""
        task = {'id': 'agent.module'}
        lang = coder._detect_language(task)
        assert lang == 'Python'

    def test_detect_language_default(self, coder):
        """Test default language detection."""
        task = {'id': 'ui.component'}
        lang = coder._detect_language(task)
        assert lang == 'TypeScript'

    @patch('agent.llm_coder.urllib.request.urlopen')
    def test_call_ollama_success(self, mock_urlopen, coder):
        """Test successful Ollama API call."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"response": "generated code"}'
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = coder._call_ollama("test prompt")
        
        assert result == "generated code"

    @patch('agent.llm_coder.urllib.request.urlopen')
    def test_call_ollama_error(self, mock_urlopen, coder):
        """Test Ollama API error handling."""
        import urllib.error
        mock_urlopen.side_effect = urllib.error.URLError("Connection error")
        
        result = coder._call_ollama("test prompt")
        
        assert result is None

    @patch('agent.llm_coder.urllib.request.urlopen')
    def test_call_ollama_json_error(self, mock_urlopen, coder):
        """Test Ollama JSON parse error handling."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'invalid json'
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = coder._call_ollama("test prompt")
        
        assert result is None

    @patch.object(LLMDcoder, '_call_ollama', return_value='export const x = 1;')
    def test_generate_code_success(self, mock_call, coder, sample_task):
        """Test successful code generation."""
        code, success, retry_count = coder.generate_code(sample_task)
        
        assert success is True
        assert code == 'export const x = 1;'
        assert retry_count == 0

    @patch.object(LLMDcoder, '_call_ollama', return_value=None)
    def test_generate_code_failure(self, mock_call, coder, sample_task):
        """Test failed code generation."""
        code, success, retry_count = coder.generate_code(sample_task)
        
        assert success is False
        assert code is None

    @patch.object(LLMDcoder, '_call_ollama', side_effect=['invalid{', 'valid code'])
    def test_generate_with_retry_success(self, mock_call, coder, sample_task):
        """Test successful generation after retry."""
        from agent.syntax_check import SyntaxChecker
        syntax_checker = SyntaxChecker()
        
        code, success, attempts = coder.generate_with_retry(sample_task, syntax_checker)
        
        assert success is True
        assert attempts == 2

    @patch.object(LLMDcoder, '_call_ollama', return_value='invalid{{')
    def test_generate_with_retry_all_failures(self, mock_call, coder, sample_task):
        """Test all retry attempts fail."""
        from agent.syntax_check import SyntaxChecker
        syntax_checker = SyntaxChecker()
        
        code, success, attempts = coder.generate_with_retry(sample_task, syntax_checker)
        
        assert success is False
        assert attempts == 3  # Max retries

    def test_generate_with_retry_no_syntax_checker(self, coder, sample_task):
        """Test generation without syntax checker."""
        with patch.object(LLMDcoder, '_call_ollama', return_value='valid code'):
            code, success, attempts = coder.generate_with_retry(sample_task)
            
            assert success is True
            assert attempts == 1


class TestGenerateCodeFromLLM:
    """Test convenience function."""

    @patch('agent.llm_coder.LLMDcoder')
    def test_generate_code_from_llm_success(self, mock_coder_class):
        """Test successful code generation via convenience function."""
        mock_coder = MagicMock()
        mock_coder.generate_with_retry.return_value = ('code', True, 1)
        mock_coder_class.return_value = mock_coder
        
        task = {'id': 'test.task'}
        result = generate_code_from_llm(task)
        
        assert result == 'code'

    @patch('agent.llm_coder.LLMDcoder')
    def test_generate_code_from_llm_failure(self, mock_coder_class):
        """Test failed code generation via convenience function."""
        mock_coder = MagicMock()
        mock_coder.generate_with_retry.return_value = (None, False, 3)
        mock_coder_class.return_value = mock_coder
        
        task = {'id': 'test.task'}
        result = generate_code_from_llm(task)
        
        assert result is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

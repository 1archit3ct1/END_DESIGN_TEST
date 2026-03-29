"""
Test Template Coder — Template generation tests.
"""

import pytest

from agent.template_coder import TemplateCoder


class TestTemplateCoder:
    """Test Template Coder functionality."""

    @pytest.fixture
    def coder(self):
        """Create TemplateCoder instance."""
        return TemplateCoder()

    @pytest.fixture
    def sample_task(self):
        """Create sample task."""
        return {
            'id': 'rust_backend.pkce_rfc7636',
            'name': 'PKCE Implementation',
            'desc': 'SHA256 + base64url encoding'
        }

    def test_initialization(self, coder):
        """Test coder initializes correctly."""
        assert coder.templates is not None

    def test_generate_code_pkce(self, coder, sample_task):
        """Test PKCE template generation."""
        code = coder.generate_code(sample_task)
        
        assert code is not None
        assert 'PKCE' in code or 'pkce' in code

    def test_generate_code_unknown(self, coder):
        """Test unknown template returns None."""
        task = {'id': 'unknown.task', 'name': 'Unknown', 'desc': 'Test'}
        code = coder.generate_code(task)
        
        assert code is None

    def test_generate_imports_rust(self, coder):
        """Test Rust import generation."""
        imports = coder.generate_imports('rust', ['serde', 'tokio', 'json'])
        
        assert 'use serde' in imports
        assert 'use tokio' in imports
        assert 'use serde_json' in imports

    def test_generate_imports_typescript(self, coder):
        """Test TypeScript import generation."""
        imports = coder.generate_imports('typescript', ['react', 'axios'])
        
        assert "import React" in imports
        assert "import axios" in imports

    def test_generate_imports_python(self, coder):
        """Test Python import generation."""
        imports = coder.generate_imports('python', ['requests', 'json', 'typing'])
        
        assert 'import requests' in imports
        assert 'import json' in imports
        assert 'from typing' in imports

    def test_get_import_for_module(self, coder):
        """Test getting specific import."""
        imp = coder.get_import_for_module('rust', 'serde')
        
        assert imp is not None
        assert 'use serde' in imp

    def test_generate_fallback_rust(self, coder):
        """Test Rust fallback generation."""
        task = {'id': 'test.task', 'name': 'Test Module', 'desc': 'Test'}
        code = coder.generate_fallback_code(task, language='rust')
        
        assert 'pub struct' in code
        assert 'impl' in code

    def test_generate_fallback_typescript(self, coder):
        """Test TypeScript fallback generation."""
        task = {'id': 'test.task', 'name': 'Test Component', 'desc': 'Test'}
        code = coder.generate_fallback_code(task, language='typescript')
        
        assert 'export class' in code
        assert 'Promise' in code

    def test_generate_fallback_python(self, coder):
        """Test Python fallback generation."""
        task = {'id': 'test.task', 'name': 'Test Service', 'desc': 'Test'}
        code = coder.generate_fallback_code(task, language='python')
        
        assert 'class' in code
        assert 'def ' in code

    def test_to_pascal_case(self, coder):
        """Test PascalCase conversion."""
        assert coder._to_pascal_case('test_module') == 'TestModule'
        assert coder._to_pascal_case('oauth-callback') == 'OauthCallback'

    def test_to_snake_case(self, coder):
        """Test snake_case conversion."""
        assert coder._to_snake_case('TestModule') == 'testmodule'
        assert coder._to_snake_case('OAuthCallback') == 'oauthcallback'

    def test_detect_language_rust(self, coder):
        """Test Rust language detection."""
        task = {'id': 'rust_backend.auth'}
        lang = coder._detect_language(task)
        assert lang == 'rust'

    def test_detect_language_python(self, coder):
        """Test Python language detection."""
        task = {'id': 'agent.python'}
        lang = coder._detect_language(task)
        assert lang == 'python'

    def test_detect_language_default(self, coder):
        """Test default language detection."""
        task = {'id': 'ui.component'}
        lang = coder._detect_language(task)
        assert lang == 'typescript'


class TestTemplateCoderIntegration:
    """Integration tests for Template Coder."""

    def test_full_template_workflow(self):
        """Test complete template workflow."""
        coder = TemplateCoder()
        
        task = {'id': 'rust_backend.pkce_rfc7636', 'name': 'PKCE', 'desc': 'RFC 7636'}
        
        # Generate code
        code = coder.generate_code(task)
        
        # Verify output
        assert code is not None
        assert len(code) > 0
        assert 'generate_code_verifier' in code


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

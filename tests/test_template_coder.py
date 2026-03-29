#!/usr/bin/env python3
"""
Test: template_coder.py generates valid code from template.
"""

import sys
import unittest
from pathlib import Path

# Add agent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.template_coder import TemplateCoder


class TestTemplateCoder(unittest.TestCase):
    """Test TemplateCoder functionality."""

    def test_coder_initializes(self):
        """Test that TemplateCoder initializes without errors."""
        coder = TemplateCoder()
        
        self.assertIsNotNone(coder)
        self.assertIsNotNone(coder.templates)

    def test_generate_code_with_template(self):
        """Test code generation with known template."""
        coder = TemplateCoder()
        
        task = {
            'id': 'rust_backend.pkce_rfc7636',
            'name': 'PKCE Implementation',
            'desc': 'RFC 7636 compliant'
        }
        
        code = coder.generate_code(task)
        
        self.assertIsNotNone(code)
        self.assertIn('generate_code_verifier', code)
        self.assertIn('generate_code_challenge', code)

    def test_generate_code_no_template(self):
        """Test code generation with unknown template returns None."""
        coder = TemplateCoder()
        
        task = {
            'id': 'unknown_task',
            'name': 'Unknown',
            'desc': 'Unknown task'
        }
        
        code = coder.generate_code(task)
        
        self.assertIsNone(code)

    def test_template_pkce(self):
        """Test PKCE template generates valid Rust code."""
        coder = TemplateCoder()
        
        task = {'id': 'rust_backend.pkce_rfc7636'}
        code = coder.generate_code(task)
        
        self.assertIn('pub fn generate_code_verifier', code)
        self.assertIn('pub fn generate_code_challenge', code)
        self.assertIn('pub fn verify_pkce', code)
        self.assertIn('use sha2', code)
        self.assertIn('use base64', code)

    def test_template_callback_server(self):
        """Test callback server template generates valid Rust code."""
        coder = TemplateCoder()
        
        task = {'id': 'rust_backend.callback_server'}
        code = coder.generate_code(task)
        
        self.assertIn('pub struct CallbackServer', code)
        self.assertIn('pub fn new', code)
        self.assertIn('pub fn wait_for_callback', code)
        self.assertIn('use tiny_http', code)

    def test_template_oauth_callback(self):
        """Test OAuth callback template generates valid TypeScript code."""
        coder = TemplateCoder()
        
        task = {'id': 'oauth_integration.callback_server'}
        code = coder.generate_code(task)
        
        self.assertIn('export class OAuthCallbackServer', code)
        self.assertIn('public async waitForCallback', code)
        self.assertIn('import http', code)

    def test_template_token_keychain(self):
        """Test token keychain template generates valid Rust code."""
        coder = TemplateCoder()
        
        task = {'id': 'oauth_integration.token_keychain'}
        code = coder.generate_code(task)
        
        self.assertIn('pub struct TokenKeychain', code)
        self.assertIn('pub fn store_token', code)
        self.assertIn('pub fn get_token', code)
        self.assertIn('pub fn delete_token', code)
        self.assertIn('use keyring', code)


class TestTemplateContent(unittest.TestCase):
    """Test template content quality."""

    def setUp(self):
        """Set up test fixtures."""
        self.coder = TemplateCoder()

    def test_pkce_has_tests(self):
        """Test PKCE template includes tests."""
        task = {'id': 'rust_backend.pkce_rfc7636'}
        code = self.coder.generate_code(task)
        
        self.assertIn('#[cfg(test)]', code)
        self.assertIn('mod tests', code)
        self.assertIn('fn test_', code)

    def test_callback_server_has_error_handling(self):
        """Test callback server template includes error handling."""
        task = {'id': 'rust_backend.callback_server'}
        code = self.coder.generate_code(task)
        
        self.assertIn('Result<', code)
        self.assertIn('Box<dyn std::error::Error>', code)

    def test_oauth_callback_has_typescript_types(self):
        """Test OAuth callback template includes TypeScript types."""
        task = {'id': 'oauth_integration.callback_server'}
        code = self.coder.generate_code(task)
        
        self.assertIn('interface CallbackResponse', code)
        self.assertIn(': Promise<', code)
        self.assertIn(': string', code)

    def test_keychain_has_serialization(self):
        """Test token keychain template includes serialization."""
        task = {'id': 'oauth_integration.token_keychain'}
        code = self.coder.generate_code(task)

        self.assertIn('Serialize', code)
        self.assertIn('Deserialize', code)
        self.assertIn('serde_json', code)


class TestFallbackCodeGeneration(unittest.TestCase):
    """Test fallback code generation when LLM fails."""

    def setUp(self):
        """Set up test fixtures."""
        self.coder = TemplateCoder()

    def test_fallback_generates_rust_code(self):
        """Test fallback generates valid Rust code."""
        task = {
            'id': 'rust_backend.test_feature',
            'name': 'Test Feature',
            'desc': 'A test feature implementation'
        }

        code = self.coder.generate_fallback_code(task)

        self.assertIsNotNone(code)
        self.assertIn('pub struct', code)
        self.assertIn('impl', code)
        self.assertIn('pub fn new', code)
        self.assertIn('pub fn execute', code)
        self.assertIn('Result<', code)
        self.assertIn('#[cfg(test)]', code)
        self.assertIn('mod tests', code)

    def test_fallback_generates_typescript_code(self):
        """Test fallback generates valid TypeScript code."""
        task = {
            'id': 'ui_integration.test_component',
            'name': 'Test Component',
            'desc': 'A test component'
        }

        code = self.coder.generate_fallback_code(task)

        self.assertIsNotNone(code)
        self.assertIn('export class', code)
        self.assertIn('constructor()', code)
        self.assertIn('public async execute', code)
        self.assertIn('Promise<void>', code)
        self.assertIn('export interface', code)

    def test_fallback_generates_python_code(self):
        """Test fallback generates valid Python code."""
        task = {
            'id': 'agent_python.test_module',
            'name': 'Test Module',
            'desc': 'A test module'
        }

        code = self.coder.generate_fallback_code(task)

        self.assertIsNotNone(code)
        self.assertIn('class', code)
        self.assertIn('def __init__', code)
        self.assertIn('def execute', code)
        self.assertIn('NotImplementedError', code)
        self.assertIn('from typing import', code)

    def test_fallback_contains_task_metadata(self):
        """Test fallback code contains task metadata."""
        task = {
            'id': 'rust_backend.custom_task',
            'name': 'Custom Feature',
            'desc': 'Custom implementation description'
        }

        code = self.coder.generate_fallback_code(task)

        self.assertIn('rust_backend.custom_task', code)
        self.assertIn('Custom Feature', code)
        self.assertIn('Custom implementation description', code)
        self.assertIn('TODO', code)

    def test_fallback_has_valid_rust_syntax(self):
        """Test that Rust fallback has valid syntax."""
        from agent.syntax_check import SyntaxChecker

        task = {
            'id': 'rust_backend.feature',
            'name': 'Feature',
            'desc': 'Description'
        }

        code = self.coder.generate_fallback_code(task)
        checker = SyntaxChecker()
        result = checker.check_syntax(code, '.rs')

        self.assertTrue(result.is_valid)

    def test_fallback_has_valid_typescript_syntax(self):
        """Test that TypeScript fallback has valid syntax."""
        from agent.syntax_check import SyntaxChecker

        task = {
            'id': 'ui_component.feature',
            'name': 'Feature',
            'desc': 'Description'
        }

        code = self.coder.generate_fallback_code(task)
        checker = SyntaxChecker()
        result = checker.check_syntax(code, '.ts')

        self.assertTrue(result.is_valid)

    def test_fallback_has_valid_python_syntax(self):
        """Test that Python fallback has valid syntax."""
        from agent.syntax_check import SyntaxChecker

        task = {
            'id': 'agent_python.feature',
            'name': 'Feature',
            'desc': 'Description'
        }

        code = self.coder.generate_fallback_code(task)
        checker = SyntaxChecker()
        result = checker.check_syntax(code, '.py')

        self.assertTrue(result.is_valid)

    def test_fallback_language_override(self):
        """Test fallback with explicit language override."""
        task = {
            'id': 'unknown.task',
            'name': 'Test',
            'desc': 'Test'
        }

        # Force Rust
        code_rust = self.coder.generate_fallback_code(task, language='rust')
        self.assertIn('pub struct', code_rust)

        # Force TypeScript
        code_ts = self.coder.generate_fallback_code(task, language='typescript')
        self.assertIn('export class', code_ts)

        # Force Python
        code_py = self.coder.generate_fallback_code(task, language='python')
        self.assertIn('class', code_py)

    def test_fallback_detects_language_from_task_id(self):
        """Test that language is auto-detected from task ID."""
        # Rust backend task
        rust_task = {'id': 'rust_backend.feature', 'name': 'Test', 'desc': 'Test'}
        code_rust = self.coder.generate_fallback_code(rust_task)
        self.assertIn('pub struct', code_rust)

        # Python agent task
        python_task = {'id': 'agent_python.feature', 'name': 'Test', 'desc': 'Test'}
        code_python = self.coder.generate_fallback_code(python_task)
        self.assertIn('class', code_python)

        # Default TypeScript
        default_task = {'id': 'ui.feature', 'name': 'Test', 'desc': 'Test'}
        code_default = self.coder.generate_fallback_code(default_task)
        self.assertIn('export class', code_default)

    def test_fallback_contains_placeholder_notice(self):
        """Test fallback code contains placeholder notice."""
        task = {
            'id': 'test.task',
            'name': 'Test',
            'desc': 'Description'
        }

        code = self.coder.generate_fallback_code(task)

        self.assertIn('Auto-generated fallback code', code)
        self.assertIn('LLM generation failed', code)
        self.assertIn('placeholder', code)

    def test_pascal_case_conversion(self):
        """Test PascalCase conversion utility."""
        self.assertEqual(self.coder._to_pascal_case('test_feature'), 'TestFeature')
        self.assertEqual(self.coder._to_pascal_case('rust_backend.pkce'), 'RustBackendPkce')
        self.assertEqual(self.coder._to_pascal_case('oauth_integration'), 'OauthIntegration')

    def test_snake_case_conversion(self):
        """Test snake_case conversion utility."""
        self.assertEqual(self.coder._to_snake_case('TestFeature'), 'testfeature')
        self.assertEqual(self.coder._to_snake_case('Test Feature'), 'test_feature')

    def test_fallback_code_is_different_from_template(self):
        """Test that fallback code differs from template code."""
        task = {'id': 'rust_backend.pkce_rfc7636'}

        # Template code
        template_code = self.coder.generate_code(task)

        # Fallback code
        fallback_code = self.coder.generate_fallback_code(task)

        # Both should exist but be different
        self.assertIsNotNone(template_code)
        self.assertIsNotNone(fallback_code)
        self.assertNotEqual(template_code, fallback_code)

        # Template should have specific PKCE functions
        self.assertIn('generate_code_verifier', template_code)

        # Fallback should be generic
        self.assertNotIn('generate_code_verifier', fallback_code)
        self.assertIn('execute', fallback_code)


if __name__ == '__main__':
    unittest.main()

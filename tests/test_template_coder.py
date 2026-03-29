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


if __name__ == '__main__':
    unittest.main()

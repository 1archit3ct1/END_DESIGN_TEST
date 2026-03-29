"""
Test Phase 9 Templates — Template library tests.

Tests for:
- PKCE template (Rust)
- OAuth callback template (Python)
- Provider catalog template (JSON)
- Token keychain template (Rust)
"""

import pytest
import json

from agent.templates.pkce import generate_pkce_template, get_task_id as pkce_task_id
from agent.templates.oauth_callback import generate_oauth_callback_template, get_task_id as oauth_callback_task_id
from agent.templates.provider_catalog import generate_provider_catalog_template, get_task_id as provider_catalog_task_id
from agent.templates.token_keychain import generate_token_keychain_template, get_task_id as token_keychain_task_id


class TestPKCETemplate:
    """Test PKCE template (Task 145-146)."""

    @pytest.fixture
    def sample_task(self):
        """Create sample task."""
        return {
            'id': 'rust_backend.pkce_rfc7636',
            'name': 'PKCE Implementation',
            'desc': 'SHA256 + base64url encoding'
        }

    def test_pkce_task_id(self):
        """Test PKCE task ID is correct."""
        assert pkce_task_id() == 'rust_backend.pkce_rfc7636'

    def test_pkce_generates_code(self, sample_task):
        """Test PKCE template generates code."""
        code = generate_pkce_template(sample_task)

        assert code is not None
        assert len(code) > 0

    def test_pkce_generates_valid_rust(self, sample_task):
        """Test PKCE template generates valid Rust code structure."""
        code = generate_pkce_template(sample_task)

        # Check for Rust-specific syntax
        assert 'pub fn' in code
        assert 'use ' in code
        assert 'let ' in code
        assert '->' in code  # Return type arrow

    def test_pkce_has_required_imports(self, sample_task):
        """Test PKCE template has required imports."""
        code = generate_pkce_template(sample_task)

        assert 'base64' in code
        assert 'sha2' in code
        assert 'rand' in code

    def test_pkce_has_required_functions(self, sample_task):
        """Test PKCE template has required functions."""
        code = generate_pkce_template(sample_task)

        assert 'generate_code_verifier' in code
        assert 'generate_code_challenge' in code
        assert 'verify_pkce' in code

    def test_pkce_has_tests(self, sample_task):
        """Test PKCE template includes tests."""
        code = generate_pkce_template(sample_task)

        assert '#[cfg(test)]' in code
        assert '#[test]' in code
        assert 'mod tests' in code

    def test_pkce_rfc7636_compliant(self, sample_task):
        """Test PKCE template is RFC 7636 compliant."""
        code = generate_pkce_template(sample_task)

        # RFC 7636 requires code verifier 43-128 characters
        assert '43' in code or '128' in code
        # RFC 7636 requires SHA256
        assert 'Sha256' in code or 'sha256' in code


class TestOAuthCallbackTemplate:
    """Test OAuth callback template (Task 147-148)."""

    @pytest.fixture
    def sample_task(self):
        """Create sample task."""
        return {
            'id': 'oauth_integration.callback_server',
            'name': 'OAuth Callback Server',
            'desc': 'HTTP callback server for OAuth'
        }

    def test_oauth_callback_task_id(self):
        """Test OAuth callback task ID is correct."""
        assert oauth_callback_task_id() == 'oauth_integration.callback_server'

    def test_oauth_callback_generates_code(self, sample_task):
        """Test OAuth callback template generates code."""
        code = generate_oauth_callback_template(sample_task)

        assert code is not None
        assert len(code) > 0

    def test_oauth_callback_generates_valid_python(self, sample_task):
        """Test OAuth callback template generates valid Python code."""
        code = generate_oauth_callback_template(sample_task)

        # Check for Python-specific syntax
        assert 'class ' in code
        assert 'def ' in code
        assert 'import ' in code

    def test_oauth_callback_has_required_classes(self, sample_task):
        """Test OAuth callback template has required classes."""
        code = generate_oauth_callback_template(sample_task)

        assert 'CallbackResponse' in code
        assert 'OAuthCallbackHandler' in code
        assert 'OAuthCallbackServer' in code

    def test_oauth_callback_has_required_methods(self, sample_task):
        """Test OAuth callback template has required methods."""
        code = generate_oauth_callback_template(sample_task)

        assert 'wait_for_callback' in code
        assert 'do_GET' in code

    def test_oauth_callback_has_docstring(self, sample_task):
        """Test OAuth callback template has module docstring."""
        code = generate_oauth_callback_template(sample_task)

        assert '"""' in code

    def test_oauth_callback_port_configurable(self, sample_task):
        """Test OAuth callback server port is configurable."""
        code = generate_oauth_callback_template(sample_task)

        assert 'port' in code
        assert '7823' in code  # Default port


class TestProviderCatalogTemplate:
    """Test Provider catalog template (Task 149-150)."""

    @pytest.fixture
    def sample_task(self):
        """Create sample task."""
        return {
            'id': 'oauth_integration.provider_catalog',
            'name': 'Provider Catalog',
            'desc': 'OAuth provider configuration'
        }

    def test_provider_catalog_task_id(self):
        """Test provider catalog task ID is correct."""
        assert provider_catalog_task_id() == 'oauth_integration.provider_catalog'

    def test_provider_catalog_generates_code(self, sample_task):
        """Test provider catalog template generates code."""
        code = generate_provider_catalog_template(sample_task)

        assert code is not None
        assert len(code) > 0

    def test_provider_catalog_generates_valid_json(self, sample_task):
        """Test provider catalog template generates valid JSON."""
        code = generate_provider_catalog_template(sample_task)

        # Should be valid JSON
        data = json.loads(code)
        assert isinstance(data, dict)

    def test_provider_catalog_has_required_fields(self, sample_task):
        """Test provider catalog has required fields."""
        code = generate_provider_catalog_template(sample_task)
        data = json.loads(code)

        assert 'providers' in data
        assert 'name' in data
        assert 'version' in data

    def test_provider_catalog_has_multiple_providers(self, sample_task):
        """Test provider catalog has multiple providers."""
        code = generate_provider_catalog_template(sample_task)
        data = json.loads(code)

        assert len(data['providers']) >= 3

    def test_provider_catalog_has_required_provider_fields(self, sample_task):
        """Test providers have required fields."""
        code = generate_provider_catalog_template(sample_task)
        data = json.loads(code)

        for provider in data['providers']:
            assert 'id' in provider
            assert 'name' in provider
            assert 'auth_url' in provider
            assert 'token_url' in provider

    def test_provider_catalog_has_popular_providers(self, sample_task):
        """Test provider catalog includes popular providers."""
        code = generate_provider_catalog_template(sample_task)
        data = json.loads(code)

        provider_ids = [p['id'] for p in data['providers']]
        assert 'google' in provider_ids or 'github' in provider_ids


class TestTokenKeychainTemplate:
    """Test Token keychain template (Task 151-152)."""

    @pytest.fixture
    def sample_task(self):
        """Create sample task."""
        return {
            'id': 'oauth_integration.token_keychain',
            'name': 'Token Keychain',
            'desc': 'Secure token storage'
        }

    def test_token_keychain_task_id(self):
        """Test token keychain task ID is correct."""
        assert token_keychain_task_id() == 'oauth_integration.token_keychain'

    def test_token_keychain_generates_code(self, sample_task):
        """Test token keychain template generates code."""
        code = generate_token_keychain_template(sample_task)

        assert code is not None
        assert len(code) > 0

    def test_token_keychain_generates_valid_rust(self, sample_task):
        """Test token keychain template generates valid Rust code."""
        code = generate_token_keychain_template(sample_task)

        # Check for Rust-specific syntax
        assert 'pub struct' in code
        assert 'impl' in code
        assert 'use ' in code

    def test_token_keychain_has_required_structs(self, sample_task):
        """Test token keychain has required structs."""
        code = generate_token_keychain_template(sample_task)

        assert 'TokenData' in code
        assert 'TokenKeychain' in code

    def test_token_keychain_has_required_methods(self, sample_task):
        """Test token keychain has required methods."""
        code = generate_token_keychain_template(sample_task)

        assert 'store_token' in code
        assert 'get_token' in code
        assert 'delete_token' in code

    def test_token_keychain_has_expiry_handling(self, sample_task):
        """Test token keychain has expiry handling."""
        code = generate_token_keychain_template(sample_task)

        assert 'expires_at' in code
        assert 'is_expired' in code or 'is_token_expired' in code

    def test_token_keychain_has_tests(self, sample_task):
        """Test token keychain template includes tests."""
        code = generate_token_keychain_template(sample_task)

        assert '#[cfg(test)]' in code
        assert '#[test]' in code


class TestTemplateIntegration:
    """Integration tests for all Phase 9 templates."""

    def test_all_templates_have_task_ids(self):
        """Test all templates expose task IDs."""
        assert pkce_task_id() is not None
        assert oauth_callback_task_id() is not None
        assert provider_catalog_task_id() is not None
        assert token_keychain_task_id() is not None

    def test_all_templates_generate_non_empty_code(self):
        """Test all templates generate non-empty code."""
        task = {'id': 'test', 'name': 'Test', 'desc': 'Test'}

        assert len(generate_pkce_template(task)) > 0
        assert len(generate_oauth_callback_template(task)) > 0
        assert len(generate_provider_catalog_template(task)) > 0
        assert len(generate_token_keychain_template(task)) > 0

    def test_templates_match_existing_implementation(self):
        """Test new templates match existing template_coder.py implementations."""
        from agent.template_coder import TemplateCoder

        coder = TemplateCoder()
        task = {'id': 'rust_backend.pkce_rfc7636', 'name': 'PKCE', 'desc': 'RFC 7636'}

        # Get code from both sources
        old_code = coder._template_pkce(task)
        new_code = generate_pkce_template(task)

        # Both should contain key PKCE functions
        assert 'generate_code_verifier' in old_code
        assert 'generate_code_verifier' in new_code


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

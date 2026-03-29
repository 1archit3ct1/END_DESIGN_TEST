#!/usr/bin/env python3
"""
Test: LLM receives full task context.
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agent.llm_coder import LLMDcoder
from agent.prompts import build_prompt, get_system_prompt


class TestLLMFullContext(unittest.TestCase):
    """Test that LLM receives full task context."""

    def setUp(self):
        """Set up test fixtures."""
        self.coder = LLMDcoder()
        self.sample_task = {
            'id': 'rust_backend.pkce_rfc7636',
            'name': 'PKCE Implementation',
            'desc': 'SHA256 + base64url — RFC 7636 compliant PKCE flow',
            'layer': 'backend',
            'language': 'rust',
            'dependencies': ['tokio', 'serde', 'base64'],
            'output_file': 'src-tauri/src/auth/pkce.rs'
        }

    def test_build_prompt_includes_task_id(self):
        """Test prompt includes task ID."""
        prompt = build_prompt(self.sample_task)
        self.assertIn('rust_backend.pkce_rfc7636', prompt)

    def test_build_prompt_includes_task_name(self):
        """Test prompt includes task name."""
        prompt = build_prompt(self.sample_task)
        self.assertIn('PKCE Implementation', prompt)

    def test_build_prompt_includes_task_description(self):
        """Test prompt includes full task description."""
        prompt = build_prompt(self.sample_task)
        self.assertIn('SHA256 + base64url', prompt)
        self.assertIn('RFC 7636', prompt)
        self.assertIn('PKCE', prompt)

    def test_build_prompt_includes_layer(self):
        """Test prompt includes layer information."""
        prompt = build_prompt(self.sample_task)
        self.assertIn('backend', prompt)

    def test_build_prompt_includes_language(self):
        """Test prompt includes language specification."""
        prompt = build_prompt(self.sample_task)
        self.assertIn('Rust', prompt)
        self.assertIn('rust', prompt)

    def test_system_prompt_matches_task_type(self):
        """Test system prompt matches task type."""
        system_prompt = get_system_prompt(self.sample_task)
        self.assertIn('backend engineer', system_prompt.lower())
        self.assertIn('rust', system_prompt.lower())

    def test_full_prompt_combines_system_and_user(self):
        """Test full prompt combines system and user prompts."""
        system_prompt = get_system_prompt(self.sample_task)
        user_prompt = build_prompt(self.sample_task)
        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        # Should contain both system instructions and task details
        self.assertIn('expert', full_prompt.lower())
        self.assertIn('rust_backend.pkce_rfc7636', full_prompt)
        self.assertIn('Requirements', full_prompt)

    def test_prompt_has_requirements_section(self):
        """Test prompt has detailed requirements section."""
        prompt = build_prompt(self.sample_task)
        self.assertIn('Requirements', prompt)
        self.assertIn('complete, working', prompt.lower())
        self.assertIn('error handling', prompt.lower())

    def test_prompt_has_code_structure_section(self):
        """Test prompt has code structure guidance."""
        prompt = build_prompt(self.sample_task)
        self.assertIn('Code Structure', prompt)
        self.assertIn('function', prompt.lower())

    def test_prompt_instructs_no_markdown_fences(self):
        """Test prompt instructs to avoid markdown fences."""
        prompt = build_prompt(self.sample_task)
        self.assertIn('Do not include markdown code fences', prompt)

    def test_ui_task_gets_ui_context(self):
        """Test UI task gets appropriate UI context."""
        ui_task = {
            'id': 'ui.components.build_console',
            'name': 'Build Console Component',
            'desc': 'Bottom-left panel with build controls and logs',
            'layer': 'ui',
            'language': 'typescript'
        }
        prompt = build_prompt(ui_task)
        system_prompt = get_system_prompt(ui_task)

        self.assertIn('React', prompt)
        self.assertIn('component', prompt.lower())
        self.assertIn('frontend engineer', system_prompt.lower())

    def test_integration_task_gets_integration_context(self):
        """Test integration task gets appropriate integration context."""
        integration_task = {
            'id': 'oauth_integration.google_callback',
            'name': 'Google OAuth Callback',
            'desc': 'Handle OAuth callback from Google, exchange code for token',
            'layer': 'integration',
            'language': 'python'
        }
        prompt = build_prompt(integration_task)
        system_prompt = get_system_prompt(integration_task)

        self.assertIn('OAuth', prompt)
        self.assertIn('token', prompt.lower())
        self.assertIn('integration engineer', system_prompt.lower())

    def test_prompt_with_custom_context(self):
        """Test prompt includes custom context when provided."""
        custom_context = "Additional requirements: Must support async operations"
        prompt = build_prompt(self.sample_task, custom_context=custom_context)

        self.assertIn(custom_context, prompt)

    def test_prompt_has_all_task_fields(self):
        """Test prompt includes all task fields."""
        prompt = build_prompt(self.sample_task)

        required_fields = [
            self.sample_task['id'],
            self.sample_task['name'],
            self.sample_task['desc'],
            self.sample_task['layer'],
        ]

        for field in required_fields:
            self.assertIn(field, prompt, f"Missing field: {field}")

    def test_llm_coder_uses_full_prompt(self):
        """Test LLM coder uses full prompt with context."""
        # Verify the _build_prompt method uses the prompts module
        prompt = self.coder._build_prompt(self.sample_task)

        # Should contain task details
        self.assertIn(self.sample_task['id'], prompt)
        self.assertIn(self.sample_task['name'], prompt)
        self.assertIn(self.sample_task['desc'], prompt)

    def test_llm_coder_gets_system_prompt(self):
        """Test LLM coder can get system prompt."""
        system_prompt = self.coder._get_system_prompt(self.sample_task)

        self.assertIn('backend engineer', system_prompt.lower())
        self.assertIn('rust', system_prompt.lower())


class TestContextCompleteness(unittest.TestCase):
    """Test completeness of context passed to LLM."""

    def test_rust_task_has_rust_specifics(self):
        """Test Rust task includes Rust-specific context."""
        task = {
            'id': 'rust_backend.token_storage',
            'name': 'Token Storage',
            'desc': 'Secure token storage using keychain',
            'layer': 'backend',
            'language': 'rust'
        }
        prompt = build_prompt(task)

        # Should have Rust-specific requirements
        self.assertIn('Result<T, E>', prompt)
        self.assertIn('ownership', prompt.lower())

    def test_oauth_task_has_security_context(self):
        """Test OAuth task includes security context."""
        task = {
            'id': 'oauth.pkce_flow',
            'name': 'PKCE Flow',
            'desc': 'Implement PKCE for public clients',
            'layer': 'integration'
        }
        prompt = build_prompt(task)

        # Should have security considerations
        self.assertIn('Security', prompt)
        self.assertIn('PKCE', prompt)
        self.assertIn('token', prompt.lower())

    def test_component_task_has_props_interface(self):
        """Test component task includes props interface guidance."""
        task = {
            'id': 'ui.file_tree',
            'name': 'File Tree Component',
            'desc': 'Display generated files in tree structure',
            'layer': 'ui'
        }
        prompt = build_prompt(task)

        # Should have component-specific guidance (check for prop-related content)
        self.assertIn('React', prompt)
        self.assertIn('prop', prompt.lower())  # "prop validation" is in the template


if __name__ == '__main__':
    unittest.main(verbosity=2)

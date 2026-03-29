#!/usr/bin/env python3
"""
Test: Prompt templates contain required context.
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agent.prompts import (
    get_task_type,
    get_prompt_template,
    build_prompt,
    get_system_prompt,
    TaskType,
    BACKEND_TEMPLATE,
    INTEGRATION_TEMPLATE,
    UI_TEMPLATE,
    RUST_BACKEND_TEMPLATE,
    OAUTH_INTEGRATION_TEMPLATE,
    COMPONENT_TEMPLATE,
    BACKEND_SYSTEM_PROMPT,
    INTEGRATION_SYSTEM_PROMPT,
    UI_SYSTEM_PROMPT,
)


class TestTaskTypeDetection(unittest.TestCase):
    """Test task type detection logic."""

    def test_detect_backend_task_from_layer(self):
        """Test backend detection from layer."""
        task = {'id': 'task1', 'layer': 'backend'}
        self.assertEqual(get_task_type(task), TaskType.BACKEND)

    def test_detect_backend_task_from_id(self):
        """Test backend detection from task ID."""
        task = {'id': 'rust_backend.pkce', 'layer': 'general'}
        self.assertEqual(get_task_type(task), TaskType.BACKEND)

    def test_detect_python_backend(self):
        """Test Python backend detection."""
        task = {'id': 'python_agent.core', 'layer': 'general'}
        self.assertEqual(get_task_type(task), TaskType.BACKEND)

    def test_detect_integration_task_from_layer(self):
        """Test integration detection from layer."""
        task = {'id': 'task1', 'layer': 'integration'}
        self.assertEqual(get_task_type(task), TaskType.INTEGRATION)

    def test_detect_integration_task_from_id(self):
        """Test integration detection from task ID."""
        task = {'id': 'oauth_integration.callback', 'layer': 'general'}
        self.assertEqual(get_task_type(task), TaskType.INTEGRATION)

    def test_detect_ui_task_from_layer(self):
        """Test UI detection from layer."""
        task = {'id': 'task1', 'layer': 'ui'}
        self.assertEqual(get_task_type(task), TaskType.UI)

    def test_detect_ui_task_from_id(self):
        """Test UI detection from task ID."""
        task = {'id': 'ui.components.header', 'layer': 'general'}
        self.assertEqual(get_task_type(task), TaskType.UI)

    def test_detect_component_task(self):
        """Test component task detection."""
        task = {'id': 'build_console.jsx', 'layer': 'general'}
        self.assertEqual(get_task_type(task), TaskType.UI)

    def test_default_to_general(self):
        """Test default task type."""
        task = {'id': 'unknown_task', 'layer': 'unknown'}
        self.assertEqual(get_task_type(task), TaskType.GENERAL)


class TestPromptTemplateSelection(unittest.TestCase):
    """Test prompt template selection logic."""

    def test_select_backend_template(self):
        """Test backend template selection."""
        task = {'id': 'rust_backend.pkce', 'layer': 'backend'}
        template = get_prompt_template(task)
        self.assertIn('Rust code', template)

    def test_select_rust_backend_template(self):
        """Test Rust-specific backend template."""
        task = {'id': 'rust_backend.pkce', 'language': 'rust'}
        template = get_prompt_template(task)
        self.assertEqual(template, RUST_BACKEND_TEMPLATE)

    def test_select_integration_template(self):
        """Test integration template selection."""
        task = {'id': 'oauth_integration.callback', 'layer': 'integration'}
        template = get_prompt_template(task)
        self.assertIn('integration code', template)

    def test_select_oauth_template(self):
        """Test OAuth-specific integration template."""
        task = {'id': 'oauth.callback', 'layer': 'integration'}
        template = get_prompt_template(task)
        self.assertEqual(template, OAUTH_INTEGRATION_TEMPLATE)

    def test_select_ui_template(self):
        """Test UI template selection."""
        task = {'id': 'ui.components.header', 'layer': 'ui'}
        template = get_prompt_template(task)
        self.assertIn('React component', template)

    def test_select_component_template(self):
        """Test component-specific UI template."""
        task = {'id': 'build_console.component', 'layer': 'ui'}
        template = get_prompt_template(task)
        self.assertEqual(template, COMPONENT_TEMPLATE)


class TestPromptContent(unittest.TestCase):
    """Test that prompts contain required context."""

    def test_backend_template_has_requirements(self):
        """Test backend template contains requirements."""
        required = ['Task ID', 'Task Name', 'Description', 'Requirements']
        for item in required:
            self.assertIn(item, BACKEND_TEMPLATE)

    def test_backend_template_has_code_structure(self):
        """Test backend template has code structure section."""
        self.assertIn('Code Structure', BACKEND_TEMPLATE)

    def test_rust_template_has_rust_specifics(self):
        """Test Rust template has Rust-specific requirements."""
        self.assertIn('Result<T, E>', RUST_BACKEND_TEMPLATE)
        self.assertIn('snake_case', RUST_BACKEND_TEMPLATE)
        self.assertIn('#[cfg(test)]', RUST_BACKEND_TEMPLATE)

    def test_integration_template_has_security(self):
        """Test integration template has security considerations."""
        self.assertIn('Security', INTEGRATION_TEMPLATE)
        self.assertIn('authentication', INTEGRATION_TEMPLATE.lower())

    def test_oauth_template_has_oauth_flow(self):
        """Test OAuth template has OAuth flow steps."""
        self.assertIn('OAuth 2.0', OAUTH_INTEGRATION_TEMPLATE)
        self.assertIn('PKCE', OAUTH_INTEGRATION_TEMPLATE)
        self.assertIn('token refresh', OAUTH_INTEGRATION_TEMPLATE.lower())

    def test_ui_template_has_react_requirements(self):
        """Test UI template has React requirements."""
        self.assertIn('React component', UI_TEMPLATE)
        self.assertIn('hooks', UI_TEMPLATE)
        self.assertIn('PropTypes', UI_TEMPLATE)

    def test_component_template_has_props_interface(self):
        """Test component template has props interface."""
        self.assertIn('Props', COMPONENT_TEMPLATE)
        self.assertIn('TypeScript', COMPONENT_TEMPLATE)


class TestBuildPrompt(unittest.TestCase):
    """Test complete prompt building."""

    def test_build_prompt_with_task_data(self):
        """Test prompt contains task data."""
        task = {
            'id': 'rust_backend.pkce_rfc7636',
            'name': 'PKCE Implementation',
            'desc': 'SHA256 + base64url — RFC 7636 compliant',
            'layer': 'backend',
            'language': 'rust'
        }
        prompt = build_prompt(task)

        self.assertIn('rust_backend.pkce_rfc7636', prompt)
        self.assertIn('PKCE Implementation', prompt)
        self.assertIn('SHA256 + base64url', prompt)
        self.assertIn('backend', prompt)

    def test_build_prompt_with_custom_context(self):
        """Test prompt includes custom context."""
        task = {'id': 'task1', 'name': 'Test', 'desc': 'Test desc', 'layer': 'backend'}
        custom = "Additional context here"
        prompt = build_prompt(task, custom_context=custom)

        self.assertIn(custom, prompt)

    def test_build_prompt_no_markdown_fences(self):
        """Test prompt instructs to avoid markdown fences."""
        task = {'id': 'task1', 'name': 'Test', 'desc': 'Test desc', 'layer': 'backend'}
        prompt = build_prompt(task)

        self.assertIn('Do not include markdown code fences', prompt)


class TestSystemPrompts(unittest.TestCase):
    """Test system prompts for different task types."""

    def test_backend_system_prompt(self):
        """Test backend system prompt."""
        task = {'id': 'rust_backend.pkce', 'language': 'rust'}
        prompt = get_system_prompt(task)

        self.assertIn('backend engineer', prompt.lower())
        self.assertIn('rust', prompt.lower())

    def test_integration_system_prompt(self):
        """Test integration system prompt."""
        task = {'id': 'oauth.callback'}
        prompt = get_system_prompt(task)

        self.assertIn('integration engineer', prompt.lower())
        self.assertIn('OAuth', prompt)

    def test_ui_system_prompt(self):
        """Test UI system prompt."""
        task = {'id': 'ui.components.header'}
        prompt = get_system_prompt(task)

        self.assertIn('frontend engineer', prompt.lower())
        self.assertIn('React', prompt)


class TestTemplateCoverage(unittest.TestCase):
    """Test that all task types have appropriate templates."""

    def test_all_task_types_covered(self):
        """Test all task types return a template."""
        tasks = [
            {'id': 'rust_backend.pkce', 'layer': 'backend'},
            {'id': 'python_agent.core', 'layer': 'backend'},
            {'id': 'oauth.callback', 'layer': 'integration'},
            {'id': 'data.sync', 'layer': 'integration'},
            {'id': 'ui.components.header', 'layer': 'ui'},
            {'id': 'build_console.jsx', 'layer': 'ui'},
            {'id': 'unknown_task', 'layer': 'general'},
        ]

        for task in tasks:
            template = get_prompt_template(task)
            self.assertIsInstance(template, str)
            self.assertGreater(len(template), 100)  # Template should be substantial

    def test_templates_have_required_sections(self):
        """Test all templates have required sections."""
        templates = [
            BACKEND_TEMPLATE,
            INTEGRATION_TEMPLATE,
            UI_TEMPLATE,
            RUST_BACKEND_TEMPLATE,
            OAUTH_INTEGRATION_TEMPLATE,
        ]

        for template in templates:
            self.assertIn('Task ID', template)
            self.assertIn('Requirements', template)
            self.assertIn('Generate', template)


if __name__ == '__main__':
    unittest.main(verbosity=2)

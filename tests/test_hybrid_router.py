#!/usr/bin/env python3
"""
Test: hybrid_router.py routes known tasks to templates.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add agent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.hybrid_router import HybridRouter


class TestHybridRouter(unittest.TestCase):
    """Test HybridRouter functionality."""

    def test_router_initializes(self):
        """Test that HybridRouter initializes without errors."""
        router = HybridRouter()
        
        self.assertIsNotNone(router)
        self.assertIsNotNone(router.TEMPLATE_TASKS)

    def test_route_to_template(self):
        """Test that known tasks are routed to templates."""
        router = HybridRouter()
        
        # Mock the template generation
        with patch.object(router, '_generate_from_template') as mock_template:
            mock_template.return_value = "// Template code"
            
            task = {'id': 'rust_backend.pkce_rfc7636'}
            code = router.generate_code(task)
            
            mock_template.assert_called_once()
            self.assertEqual(code, "// Template code")

    def test_route_to_llm(self):
        """Test that unknown tasks are routed to LLM."""
        router = HybridRouter()
        
        # Mock the LLM generation
        with patch.object(router, '_generate_from_llm') as mock_llm:
            mock_llm.return_value = "// LLM code"
            
            task = {'id': 'unknown_custom_task'}
            code = router.generate_code(task)
            
            mock_llm.assert_called_once()
            self.assertEqual(code, "// LLM code")

    def test_template_task_ids(self):
        """Test that template task IDs are defined."""
        router = HybridRouter()
        
        self.assertIn('rust_backend.pkce_rfc7636', router.TEMPLATE_TASKS)
        self.assertIn('rust_backend.callback_server', router.TEMPLATE_TASKS)
        self.assertIn('oauth_integration.callback_server', router.TEMPLATE_TASKS)
        self.assertIn('oauth_integration.token_keychain', router.TEMPLATE_TASKS)

    def test_generate_from_template_returns_code(self):
        """Test that template generation returns code."""
        router = HybridRouter()
        
        task = {
            'id': 'rust_backend.pkce_rfc7636',
            'desc': 'PKCE implementation'
        }
        
        code = router._generate_from_template(task)
        
        self.assertIsNotNone(code)
        self.assertIsInstance(code, str)
        self.assertGreater(len(code), 0)

    def test_generate_from_llm_returns_code(self):
        """Test that LLM generation returns code (placeholder)."""
        router = HybridRouter()
        
        task = {
            'id': 'custom_task',
            'desc': 'Custom implementation'
        }
        
        code = router._generate_from_llm(task)
        
        self.assertIsNotNone(code)
        self.assertIsInstance(code, str)
        # Note: This is a placeholder, will be replaced with actual LLM call


class TestHybridRouterIntegration(unittest.TestCase):
    """Test HybridRouter integration with template and LLM coders."""

    def setUp(self):
        """Set up test fixtures."""
        self.router = HybridRouter()

    def test_template_task_generates_rust_code(self):
        """Test that PKCE task generates Rust code."""
        task = {'id': 'rust_backend.pkce_rfc7636', 'desc': 'RFC 7636'}
        code = self.router.generate_code(task)
        
        self.assertIn('//', code)  # Comment syntax
        self.assertIn('pkce', code.lower())

    def test_template_task_generates_callback_server_code(self):
        """Test that callback server task generates code."""
        task = {'id': 'rust_backend.callback_server', 'desc': 'Callback server'}
        code = self.router.generate_code(task)
        
        self.assertIn('//', code)
        self.assertIn('callback', code.lower())

    def test_unknown_task_generates_placeholder(self):
        """Test that unknown task generates placeholder code."""
        task = {'id': 'unknown_task', 'desc': 'Unknown'}
        code = self.router.generate_code(task)
        
        self.assertIn('//', code)
        self.assertIn('unknown_task', code)


if __name__ == '__main__':
    unittest.main()

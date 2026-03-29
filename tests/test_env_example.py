#!/usr/bin/env python3
"""
Test: .env.example contains all required environment variables.
"""

import sys
import unittest
from pathlib import Path

# Add agent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestEnvExample(unittest.TestCase):
    """Test .env.example content."""

    def setUp(self):
        """Set up test fixtures."""
        self.env_example_path = Path('./output/.env.example')
        self.env_content = None

        if self.env_example_path.exists():
            with open(self.env_example_path, 'r', encoding='utf-8') as f:
                self.env_content = f.read()

    def test_env_example_exists(self):
        """Test that .env.example exists."""
        self.assertTrue(self.env_example_path.exists())

    def test_env_example_not_empty(self):
        """Test that .env.example is not empty."""
        self.assertIsNotNone(self.env_content)
        self.assertGreater(len(self.env_content), 0)

    def test_env_example_has_oauth_client_id(self):
        """Test that .env.example has OAuth client ID."""
        self.assertIn('VITE_OAUTH_CLIENT_ID', self.env_content)

    def test_env_example_has_oauth_client_secret(self):
        """Test that .env.example has OAuth client secret."""
        self.assertIn('VITE_OAUTH_CLIENT_SECRET', self.env_content)

    def test_env_example_has_oauth_redirect_uri(self):
        """Test that .env.example has OAuth redirect URI."""
        self.assertIn('VITE_OAUTH_REDIRECT_URI', self.env_content)

    def test_env_example_has_oauth_scope(self):
        """Test that .env.example has OAuth scope."""
        self.assertIn('VITE_OAUTH_SCOPE', self.env_content)

    def test_env_example_has_oauth_provider(self):
        """Test that .env.example has OAuth provider."""
        self.assertIn('VITE_OAUTH_PROVIDER', self.env_content)

    def test_env_example_has_app_port(self):
        """Test that .env.example has app port."""
        self.assertIn('VITE_APP_PORT', self.env_content)

    def test_env_example_has_app_name(self):
        """Test that .env.example has app name."""
        self.assertIn('VITE_APP_NAME', self.env_content)

    def test_env_example_has_debug_mode(self):
        """Test that .env.example has debug mode."""
        self.assertIn('VITE_DEBUG_MODE', self.env_content)

    def test_env_example_has_api_url(self):
        """Test that .env.example has API URL."""
        self.assertIn('VITE_API_URL', self.env_content)

    def test_env_example_has_session_secret(self):
        """Test that .env.example has session secret."""
        self.assertIn('VITE_SESSION_SECRET', self.env_content)

    def test_env_example_has_log_level(self):
        """Test that .env.example has log level."""
        self.assertIn('VITE_LOG_LEVEL', self.env_content)

    def test_env_example_has_pkce_enabled(self):
        """Test that .env.example has PKCE enabled flag."""
        self.assertIn('VITE_ENABLE_PKCE', self.env_content)

    def test_env_example_has_comments(self):
        """Test that .env.example has comments explaining variables."""
        self.assertIn('#', self.env_content)

    def test_env_example_has_sections(self):
        """Test that .env.example has organized sections."""
        self.assertIn('OAuth', self.env_content)
        self.assertIn('Application', self.env_content)
        self.assertIn('Security', self.env_content)


if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python3
"""
Test: README.md contains project name and setup instructions.
"""

import sys
import unittest
from pathlib import Path

# Add agent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestReadmeMd(unittest.TestCase):
    """Test README.md content."""

    def setUp(self):
        """Set up test fixtures."""
        self.readme_path = Path('./output/README.md')
        self.readme_content = None

        if self.readme_path.exists():
            with open(self.readme_path, 'r', encoding='utf-8') as f:
                self.readme_content = f.read()

    def test_readme_exists(self):
        """Test that README.md exists."""
        self.assertTrue(self.readme_path.exists())

    def test_readme_not_empty(self):
        """Test that README.md is not empty."""
        self.assertIsNotNone(self.readme_content)
        self.assertGreater(len(self.readme_content), 0)

    def test_readme_has_project_name(self):
        """Test that README.md contains project name."""
        self.assertIn('NextAura', self.readme_content)
        self.assertIn('Hybrid', self.readme_content)

    def test_readme_has_installation_section(self):
        """Test that README.md has installation instructions."""
        self.assertIn('Installation', self.readme_content)
        self.assertIn('npm install', self.readme_content)

    def test_readme_has_prerequisites_section(self):
        """Test that README.md has prerequisites section."""
        self.assertIn('Prerequisites', self.readme_content)
        self.assertIn('Node.js', self.readme_content)

    def test_readme_has_development_section(self):
        """Test that README.md has development instructions."""
        self.assertIn('Development', self.readme_content)
        self.assertIn('npm run dev', self.readme_content)

    def test_readme_has_build_section(self):
        """Test that README.md has build instructions."""
        self.assertIn('Building', self.readme_content)
        self.assertIn('npm run build', self.readme_content)

    def test_readme_has_testing_section(self):
        """Test that README.md has testing instructions."""
        self.assertIn('Testing', self.readme_content)
        self.assertIn('npm run test', self.readme_content)

    def test_readme_has_project_structure(self):
        """Test that README.md has project structure section."""
        self.assertIn('Project Structure', self.readme_content)
        self.assertIn('src/', self.readme_content)

    def test_readme_has_environment_variables(self):
        """Test that README.md has environment variables section."""
        self.assertIn('Environment Variables', self.readme_content)
        self.assertIn('.env', self.readme_content)

    def test_readme_has_license_section(self):
        """Test that README.md has license section."""
        self.assertIn('License', self.readme_content)

    def test_readme_mentions_tauri(self):
        """Test that README.md mentions Tauri."""
        self.assertIn('Tauri', self.readme_content)

    def test_readme_mentions_react(self):
        """Test that README.md mentions React."""
        self.assertIn('React', self.readme_content)

    def test_readme_mentions_typescript(self):
        """Test that README.md mentions TypeScript."""
        self.assertIn('TypeScript', self.readme_content)


if __name__ == '__main__':
    unittest.main()

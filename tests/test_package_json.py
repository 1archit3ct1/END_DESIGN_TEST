#!/usr/bin/env python3
"""
Test: package.json is valid JSON with required fields.
"""

import sys
import unittest
import json
from pathlib import Path

# Add agent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestPackageJson(unittest.TestCase):
    """Test package.json validity and content."""

    def setUp(self):
        """Set up test fixtures."""
        self.package_json_path = Path('./output/package.json')
        self.package_data = None

        if self.package_json_path.exists():
            with open(self.package_json_path, 'r', encoding='utf-8') as f:
                self.package_data = json.load(f)

    def test_package_json_exists(self):
        """Test that package.json exists."""
        self.assertTrue(self.package_json_path.exists())

    def test_package_json_is_valid_json(self):
        """Test that package.json is valid JSON."""
        self.assertIsNotNone(self.package_data)
        self.assertIsInstance(self.package_data, dict)

    def test_package_json_has_name(self):
        """Test that package.json has name field."""
        self.assertIn('name', self.package_data)
        self.assertIsInstance(self.package_data['name'], str)
        self.assertGreater(len(self.package_data['name']), 0)

    def test_package_json_has_version(self):
        """Test that package.json has version field."""
        self.assertIn('version', self.package_data)
        self.assertIsInstance(self.package_data['version'], str)
        # Check semver format
        version_parts = self.package_data['version'].split('.')
        self.assertGreaterEqual(len(version_parts), 2)

    def test_package_json_has_description(self):
        """Test that package.json has description field."""
        self.assertIn('description', self.package_data)
        self.assertIsInstance(self.package_data['description'], str)
        self.assertGreater(len(self.package_data['description']), 0)

    def test_package_json_has_scripts(self):
        """Test that package.json has scripts field."""
        self.assertIn('scripts', self.package_data)
        self.assertIsInstance(self.package_data['scripts'], dict)
        # Check for required scripts
        required_scripts = ['dev', 'build', 'test']
        for script in required_scripts:
            self.assertIn(script, self.package_data['scripts'])

    def test_package_json_has_dependencies(self):
        """Test that package.json has dependencies field."""
        self.assertIn('dependencies', self.package_data)
        self.assertIsInstance(self.package_data['dependencies'], dict)
        # Should have react
        self.assertIn('react', self.package_data['dependencies'])

    def test_package_json_has_dev_dependencies(self):
        """Test that package.json has devDependencies field."""
        self.assertIn('devDependencies', self.package_data)
        self.assertIsInstance(self.package_data['devDependencies'], dict)
        # Should have typescript
        self.assertIn('typescript', self.package_data['devDependencies'])

    def test_package_json_has_license(self):
        """Test that package.json has license field."""
        self.assertIn('license', self.package_data)
        self.assertIsInstance(self.package_data['license'], str)

    def test_package_json_has_author(self):
        """Test that package.json has author field."""
        self.assertIn('author', self.package_data)
        self.assertIsInstance(self.package_data['author'], str)

    def test_package_json_has_engines(self):
        """Test that package.json has engines field."""
        self.assertIn('engines', self.package_data)
        self.assertIsInstance(self.package_data['engines'], dict)
        self.assertIn('node', self.package_data['engines'])

    def test_package_json_has_keywords(self):
        """Test that package.json has keywords field."""
        self.assertIn('keywords', self.package_data)
        self.assertIsInstance(self.package_data['keywords'], list)
        self.assertGreater(len(self.package_data['keywords']), 0)


if __name__ == '__main__':
    unittest.main()

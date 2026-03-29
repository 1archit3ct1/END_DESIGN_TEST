#!/usr/bin/env python3
"""
Test: template_loader.py loads templates from disk.
"""

import sys
import unittest
import tempfile
import shutil
from pathlib import Path

# Add agent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.template_loader import TemplateLoader, load_project_template, load_output_template


class TestTemplateLoader(unittest.TestCase):
    """Test TemplateLoader functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_templates_dir = Path(tempfile.mkdtemp())
        # Create test template files
        (self.test_templates_dir / 'test_template.py').write_text('# Test template\nprint("hello")')
        (self.test_templates_dir / 'test_template.json').write_text('{"key": "value"}')

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_templates_dir, ignore_errors=True)

    def test_loader_initializes(self):
        """Test that TemplateLoader initializes without errors."""
        loader = TemplateLoader()
        self.assertIsNotNone(loader)
        self.assertIsNotNone(loader.templates_dir)

    def test_loader_with_custom_dir(self):
        """Test that TemplateLoader accepts custom templates directory."""
        loader = TemplateLoader(templates_dir=self.test_templates_dir)
        self.assertEqual(loader.templates_dir, self.test_templates_dir)

    def test_load_template_exists(self):
        """Test loading an existing template."""
        loader = TemplateLoader(templates_dir=self.test_templates_dir)
        content = loader.load_template('test_template.py')

        self.assertIsNotNone(content)
        self.assertIn('Test template', content)

    def test_load_template_not_exists(self):
        """Test loading a non-existing template returns None."""
        loader = TemplateLoader(templates_dir=self.test_templates_dir)
        content = loader.load_template('nonexistent_template.py')

        self.assertIsNone(content)

    def test_load_json_template(self):
        """Test loading a JSON template."""
        loader = TemplateLoader(templates_dir=self.test_templates_dir)
        data = loader.load_json_template('test_template.json')

        self.assertIsNotNone(data)
        self.assertIsInstance(data, dict)
        self.assertEqual(data.get('key'), 'value')

    def test_load_json_template_invalid(self):
        """Test loading an invalid JSON template returns None."""
        (self.test_templates_dir / 'invalid.json').write_text('{invalid json}')
        loader = TemplateLoader(templates_dir=self.test_templates_dir)
        data = loader.load_json_template('invalid.json')

        self.assertIsNone(data)

    def test_list_templates(self):
        """Test listing available templates."""
        loader = TemplateLoader(templates_dir=self.test_templates_dir)
        templates = loader.list_templates()

        self.assertIsInstance(templates, list)
        self.assertIn('test_template.py', templates)
        self.assertIn('test_template.json', templates)

    def test_list_templates_empty_dir(self):
        """Test listing templates from empty directory."""
        empty_dir = Path(tempfile.mkdtemp())
        try:
            loader = TemplateLoader(templates_dir=empty_dir)
            templates = loader.list_templates()
            self.assertEqual(templates, [])
        finally:
            shutil.rmtree(empty_dir, ignore_errors=True)

    def test_clear_cache(self):
        """Test clearing template cache."""
        loader = TemplateLoader(templates_dir=self.test_templates_dir)
        # Load template to cache
        loader.load_template('test_template.py')
        # Clear cache
        loader.clear_cache()
        # Cache should be empty
        self.assertEqual(loader._template_cache, {})

    def test_get_template_path_exists(self):
        """Test getting path to existing template."""
        loader = TemplateLoader(templates_dir=self.test_templates_dir)
        path = loader.get_template_path('test_template.py')

        self.assertIsNotNone(path)
        self.assertTrue(path.exists())

    def test_get_template_path_not_exists(self):
        """Test getting path to non-existing template."""
        loader = TemplateLoader(templates_dir=self.test_templates_dir)
        path = loader.get_template_path('nonexistent.py')

        self.assertIsNone(path)


class TestTemplateLoaderOutputTemplates(unittest.TestCase):
    """Test TemplateLoader output template functionality."""

    def test_load_output_template_package_json(self):
        """Test loading output package.json template."""
        content = load_output_template('package.json')

        self.assertIsNotNone(content)
        self.assertIn('"name"', content)
        self.assertIn('nextaura', content.lower())

    def test_load_output_template_readme(self):
        """Test loading output README.md template."""
        content = load_output_template('README.md')

        self.assertIsNotNone(content)
        self.assertIn('NextAura', content)

    def test_load_output_template_cargo_toml(self):
        """Test loading output Cargo.toml template."""
        content = load_output_template('Cargo.toml')

        self.assertIsNotNone(content)
        self.assertIn('[package]', content)

    def test_load_output_template_tsconfig(self):
        """Test loading output tsconfig.json template."""
        content = load_output_template('tsconfig.json')

        self.assertIsNotNone(content)
        self.assertIn('compilerOptions', content)

    def test_list_output_templates(self):
        """Test listing output templates."""
        loader = TemplateLoader()
        templates = loader.list_output_templates()

        self.assertIsInstance(templates, list)
        self.assertGreater(len(templates), 0)
        self.assertIn('package.json', templates)


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions."""

    def test_load_project_template_function(self):
        """Test load_project_template convenience function."""
        # Should be callable (may return None if no templates exist)
        result = load_project_template('nonexistent.py')
        self.assertIsNone(result)

    def test_load_output_template_function(self):
        """Test load_output_template convenience function."""
        result = load_output_template('package.json')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)


if __name__ == '__main__':
    unittest.main()

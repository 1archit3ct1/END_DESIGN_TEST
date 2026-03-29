#!/usr/bin/env python3
"""
Test: tsconfig.json is valid TypeScript configuration.
"""

import sys
import unittest
import json
from pathlib import Path

# Add agent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestTsConfigJson(unittest.TestCase):
    """Test tsconfig.json validity and content."""

    def setUp(self):
        """Set up test fixtures."""
        self.tsconfig_path = Path('./output/tsconfig.json')
        self.tsconfig_data = None

        if self.tsconfig_path.exists():
            with open(self.tsconfig_path, 'r', encoding='utf-8') as f:
                self.tsconfig_data = json.load(f)

    def test_tsconfig_exists(self):
        """Test that tsconfig.json exists."""
        self.assertTrue(self.tsconfig_path.exists())

    def test_tsconfig_is_valid_json(self):
        """Test that tsconfig.json is valid JSON."""
        self.assertIsNotNone(self.tsconfig_data)
        self.assertIsInstance(self.tsconfig_data, dict)

    def test_tsconfig_has_compiler_options(self):
        """Test that tsconfig.json has compilerOptions."""
        self.assertIn('compilerOptions', self.tsconfig_data)
        self.assertIsInstance(self.tsconfig_data['compilerOptions'], dict)

    def test_tsconfig_has_target(self):
        """Test that tsconfig.json has target."""
        compiler_options = self.tsconfig_data['compilerOptions']
        self.assertIn('target', compiler_options)
        self.assertIn(compiler_options['target'], ['ES2020', 'ES2021', 'ES2022', 'ESNext'])

    def test_tsconfig_has_module(self):
        """Test that tsconfig.json has module."""
        compiler_options = self.tsconfig_data['compilerOptions']
        self.assertIn('module', compiler_options)
        self.assertIn(compiler_options['module'], ['ESNext', 'ES2020', 'CommonJS'])

    def test_tsconfig_has_jsx(self):
        """Test that tsconfig.json has jsx for React."""
        compiler_options = self.tsconfig_data['compilerOptions']
        self.assertIn('jsx', compiler_options)
        self.assertEqual(compiler_options['jsx'], 'react-jsx')

    def test_tsconfig_has_strict_mode(self):
        """Test that tsconfig.json has strict mode enabled."""
        compiler_options = self.tsconfig_data['compilerOptions']
        self.assertIn('strict', compiler_options)
        self.assertTrue(compiler_options['strict'])

    def test_tsconfig_has_module_resolution(self):
        """Test that tsconfig.json has moduleResolution."""
        compiler_options = self.tsconfig_data['compilerOptions']
        self.assertIn('moduleResolution', compiler_options)

    def test_tsconfig_has_skip_lib_check(self):
        """Test that tsconfig.json has skipLibCheck."""
        compiler_options = self.tsconfig_data['compilerOptions']
        self.assertIn('skipLibCheck', compiler_options)

    def test_tsconfig_has_resolve_json_module(self):
        """Test that tsconfig.json has resolveJsonModule."""
        compiler_options = self.tsconfig_data['compilerOptions']
        self.assertIn('resolveJsonModule', compiler_options)

    def test_tsconfig_has_isolated_modules(self):
        """Test that tsconfig.json has isolatedModules."""
        compiler_options = self.tsconfig_data['compilerOptions']
        self.assertIn('isolatedModules', compiler_options)

    def test_tsconfig_has_include(self):
        """Test that tsconfig.json has include."""
        self.assertIn('include', self.tsconfig_data)
        self.assertIsInstance(self.tsconfig_data['include'], list)
        self.assertIn('src', self.tsconfig_data['include'])

    def test_tsconfig_has_path_aliases(self):
        """Test that tsconfig.json has path aliases."""
        compiler_options = self.tsconfig_data['compilerOptions']
        self.assertIn('paths', compiler_options)
        paths = compiler_options['paths']
        self.assertIn('@/*', paths)


if __name__ == '__main__':
    unittest.main()

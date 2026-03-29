#!/usr/bin/env python3
"""
Test: Docstrings follow project conventions.
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agent.docstring_generator import (
    DocstringGenerator,
    DocstringStyle,
    generate_docstring,
    generate_jsdoc,
)


class TestGoogleDocstringGeneration(unittest.TestCase):
    """Test Google-style docstring generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = DocstringGenerator(DocstringStyle.GOOGLE)

    def test_generate_simple_docstring(self):
        """Test generating simple docstring."""
        params = []
        docstring = self.generator.generate_function_docstring(
            'greet', params, return_type='str', description='Say hello'
        )

        self.assertIn('"""', docstring)
        self.assertIn('Say hello', docstring)
        self.assertIn('Returns:', docstring)

    def test_generate_docstring_with_params(self):
        """Test generating docstring with parameters."""
        params = [
            {'name': 'name', 'type': 'str', 'description': 'Person name'},
            {'name': 'age', 'type': 'int', 'description': 'Person age'},
        ]
        docstring = self.generator.generate_function_docstring(
            'greet', params, return_type='str', description='Say hello'
        )

        self.assertIn('Args:', docstring)
        self.assertIn('name (str): Person name', docstring)
        self.assertIn('age (int): Person age', docstring)

    def test_generate_docstring_with_raises(self):
        """Test generating docstring with raises."""
        params = []
        raises = ['ValueError', 'TypeError']
        docstring = self.generator.generate_function_docstring(
            'process', params, return_type='None',
            description='Process data', raises=raises
        )

        self.assertIn('Raises:', docstring)
        self.assertIn('ValueError:', docstring)
        self.assertIn('TypeError:', docstring)

    def test_generate_docstring_no_description(self):
        """Test generating docstring without description."""
        params = []
        docstring = self.generator.generate_function_docstring(
            'helper', params, return_type='None'
        )

        self.assertIn('"""', docstring)
        self.assertIn('Returns:', docstring)


class TestNumpyDocstringGeneration(unittest.TestCase):
    """Test NumPy-style docstring generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = DocstringGenerator(DocstringStyle.NUMPY)

    def test_generate_numpy_docstring(self):
        """Test generating NumPy-style docstring."""
        params = [
            {'name': 'name', 'type': 'str', 'description': 'Person name'},
        ]
        docstring = self.generator.generate_function_docstring(
            'greet', params, return_type='str', description='Say hello'
        )

        self.assertIn('Parameters', docstring)
        self.assertIn('----------', docstring)
        self.assertIn('name : str', docstring)

    def test_generate_numpy_returns(self):
        """Test generating NumPy-style returns section."""
        params = []
        docstring = self.generator.generate_function_docstring(
            'get_value', params, return_type='int', description='Get value'
        )

        self.assertIn('Returns', docstring)
        self.assertIn('-------', docstring)
        self.assertIn('int', docstring)

    def test_generate_numpy_raises(self):
        """Test generating NumPy-style raises section."""
        params = []
        raises = ['ValueError']
        docstring = self.generator.generate_function_docstring(
            'validate', params, return_type='bool',
            description='Validate input', raises=raises
        )

        self.assertIn('Raises', docstring)
        self.assertIn('------', docstring)
        self.assertIn('ValueError', docstring)


class TestRstDocstringGeneration(unittest.TestCase):
    """Test reStructuredText docstring generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = DocstringGenerator(DocstringStyle.RST)

    def test_generate_rst_docstring(self):
        """Test generating RST-style docstring."""
        params = [
            {'name': 'name', 'type': 'str', 'description': 'Person name'},
        ]
        docstring = self.generator.generate_function_docstring(
            'greet', params, return_type='str', description='Say hello'
        )

        self.assertIn(':param name:', docstring)
        self.assertIn(':type name:', docstring)
        self.assertIn(':return:', docstring)
        self.assertIn(':rtype:', docstring)

    def test_generate_rst_raises(self):
        """Test generating RST-style raises."""
        params = []
        raises = ['ValueError']
        docstring = self.generator.generate_function_docstring(
            'validate', params, return_type='bool',
            description='Validate', raises=raises
        )

        self.assertIn(':raises ValueError:', docstring)


class TestJSDocGeneration(unittest.TestCase):
    """Test JSDoc comment generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = DocstringGenerator(DocstringStyle.JSDOC)

    def test_generate_jsdoc(self):
        """Test generating JSDoc comment."""
        params = [
            {'name': 'name', 'type': 'string', 'description': 'Person name'},
        ]
        docstring = self.generator.generate_function_docstring(
            'greet', params, return_type='string', description='Say hello'
        )

        self.assertIn('/**', docstring)
        self.assertIn('*/', docstring)
        self.assertIn('@param {string} name', docstring)
        self.assertIn('@returns {string}', docstring)

    def test_generate_jsdoc_optional_param(self):
        """Test generating JSDoc with optional parameter."""
        params = [
            {'name': 'callback', 'type': 'Function', 'description': 'Callback', 'optional': True},
        ]
        docstring = self.generator.generate_function_docstring(
            'process', params, return_type='void', description='Process'
        )

        self.assertIn('@param {Function} callback=', docstring)

    def test_generate_jsdoc_throws(self):
        """Test generating JSDoc with throws."""
        params = []
        raises = ['Error']
        docstring = self.generator.generate_function_docstring(
            'validate', params, return_type='boolean',
            description='Validate', raises=raises
        )

        self.assertIn('@throws {Error}', docstring)


class TestClassDocstringGeneration(unittest.TestCase):
    """Test class docstring generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = DocstringGenerator(DocstringStyle.GOOGLE)

    def test_generate_google_class_docstring(self):
        """Test generating Google-style class docstring."""
        attributes = [
            {'name': 'name', 'type': 'str', 'description': 'Instance name'},
            {'name': 'value', 'type': 'int', 'description': 'Instance value'},
        ]
        docstring = self.generator.generate_class_docstring(
            'MyClass', 'A sample class', attributes
        )

        self.assertIn('"""', docstring)
        self.assertIn('Attributes:', docstring)
        self.assertIn('name (str): Instance name', docstring)
        self.assertIn('value (int): Instance value', docstring)

    def test_generate_numpy_class_docstring(self):
        """Test generating NumPy-style class docstring."""
        self.generator = DocstringGenerator(DocstringStyle.NUMPY)
        attributes = [
            {'name': 'name', 'type': 'str', 'description': 'Instance name'},
        ]
        docstring = self.generator.generate_class_docstring(
            'MyClass', 'A sample class', attributes
        )

        self.assertIn('Attributes', docstring)
        self.assertIn('----------', docstring)
        self.assertIn('name : str', docstring)

    def test_generate_jsdoc_class(self):
        """Test generating JSDoc class comment."""
        self.generator = DocstringGenerator(DocstringStyle.JSDOC)
        attributes = [
            {'name': 'name', 'type': 'string', 'description': 'Instance name'},
        ]
        docstring = self.generator.generate_class_docstring(
            'MyClass', 'A sample class', attributes
        )

        self.assertIn('/**', docstring)
        self.assertIn('*/', docstring)
        self.assertIn('@property {string} name', docstring)


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions."""

    def test_generate_docstring(self):
        """Test generate_docstring convenience function."""
        params = [
            {'name': 'name', 'type': 'str', 'description': 'Name'},
        ]
        docstring = generate_docstring('greet', params, 'str', 'Say hello')

        self.assertIn('"""', docstring)
        self.assertIn('Args:', docstring)

    def test_generate_jsdoc(self):
        """Test generate_jsdoc convenience function."""
        params = [
            {'name': 'name', 'type': 'string', 'description': 'Name'},
        ]
        docstring = generate_jsdoc('greet', params, 'string', 'Say hello')

        self.assertIn('/**', docstring)
        self.assertIn('@param', docstring)


class TestDocstringConventions(unittest.TestCase):
    """Test that docstrings follow project conventions."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = DocstringGenerator(DocstringStyle.GOOGLE)

    def test_docstring_has_opening_triple_quotes(self):
        """Test docstring has opening triple quotes."""
        params = []
        docstring = self.generator.generate_function_docstring('test', params)
        self.assertTrue(docstring.startswith('"""'))

    def test_docstring_has_closing_triple_quotes(self):
        """Test docstring has closing triple quotes."""
        params = []
        docstring = self.generator.generate_function_docstring('test', params)
        self.assertTrue(docstring.endswith('"""'))

    def test_docstring_indentation_consistent(self):
        """Test docstring indentation is consistent."""
        params = [
            {'name': 'param1', 'type': 'str', 'description': 'Description'},
        ]
        docstring = self.generator.generate_function_docstring('test', params, 'str', 'Test')

        lines = docstring.split('\n')
        # All lines after Args should be indented
        args_idx = next((i for i, line in enumerate(lines) if 'Args:' in line), None)
        if args_idx:
            # Check that param lines are indented with 4 spaces
            param_line = lines[args_idx + 1]
            self.assertTrue(param_line.startswith('    '))

    def test_jsdoc_has_proper_tags(self):
        """Test JSDoc has proper tags."""
        self.generator = DocstringGenerator(DocstringStyle.JSDOC)
        params = [
            {'name': 'name', 'type': 'string', 'description': 'Name'},
        ]
        docstring = self.generator.generate_function_docstring('test', params, 'string', 'Test')

        self.assertIn('@param', docstring)
        self.assertIn('@returns', docstring)

    def test_docstring_preserves_param_order(self):
        """Test docstring preserves parameter order."""
        params = [
            {'name': 'first', 'type': 'str', 'description': 'First'},
            {'name': 'second', 'type': 'int', 'description': 'Second'},
            {'name': 'third', 'type': 'bool', 'description': 'Third'},
        ]
        docstring = self.generator.generate_function_docstring('test', params)

        first_pos = docstring.find('first')
        second_pos = docstring.find('second')
        third_pos = docstring.find('third')

        self.assertLess(first_pos, second_pos)
        self.assertLess(second_pos, third_pos)


class TestDocstringEdgeCases(unittest.TestCase):
    """Test docstring generation edge cases."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = DocstringGenerator()

    def test_empty_params_list(self):
        """Test docstring with empty params list."""
        params = []
        docstring = self.generator.generate_function_docstring('test', params)

        self.assertNotIn('Args:', docstring)

    def test_param_without_description(self):
        """Test docstring with param without description."""
        params = [
            {'name': 'value', 'type': 'int'},
        ]
        docstring = self.generator.generate_function_docstring('test', params)

        self.assertIn('value (int):', docstring)

    def test_param_without_type(self):
        """Test docstring with param without type."""
        params = [
            {'name': 'value', 'description': 'A value'},
        ]
        docstring = self.generator.generate_function_docstring('test', params)

        self.assertIn('value (Any):', docstring)

    def test_no_return_type(self):
        """Test docstring without return type."""
        params = []
        docstring = self.generator.generate_function_docstring(
            'test', params, return_type=None
        )

        self.assertNotIn('Returns:', docstring)


if __name__ == '__main__':
    unittest.main(verbosity=2)

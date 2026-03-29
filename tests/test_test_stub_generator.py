#!/usr/bin/env python3
"""
Test: Test stubs are valid test files.
"""

import unittest
import sys
import os
import ast

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agent.test_stub_generator import (
    TestStubGenerator,
    TestFramework,
    generate_pytest_stub,
    generate_vitest_stub,
    generate_rust_test_stub,
)


class TestPytestStubGeneration(unittest.TestCase):
    """Test pytest stub generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = TestStubGenerator(TestFramework.PYTEST)

    def test_generate_function_test_stub(self):
        """Test generating pytest stub for functions."""
        functions = [
            {'name': 'add', 'params': ['a', 'b'], 'return_type': 'int'},
            {'name': 'subtract', 'params': ['a', 'b'], 'return_type': 'int'},
        ]
        stub = self.generator.generate_test_stub('math_ops.py', functions)

        self.assertIn('import pytest', stub)
        self.assertIn('from math_ops import add, subtract', stub)
        self.assertIn('def test_add():', stub)
        self.assertIn('def test_subtract():', stub)

    def test_generate_class_test_stub(self):
        """Test generating pytest stub for class."""
        functions = [
            {'name': 'get_name', 'params': [], 'return_type': 'str'},
            {'name': 'set_name', 'params': ['name'], 'return_type': 'None'},
        ]
        stub = self.generator.generate_test_stub('user.py', functions, class_name='User')

        self.assertIn('class TestUser:', stub)
        self.assertIn('def setup_method(self):', stub)
        self.assertIn('self.instance = User()', stub)
        self.assertIn('def test_get_name(self):', stub)
        self.assertIn('def test_set_name(self):', stub)

    def test_skip_private_methods(self):
        """Test that private methods are skipped."""
        functions = [
            {'name': 'public_method', 'params': [], 'return_type': 'None'},
            {'name': '_private_method', 'params': [], 'return_type': 'None'},
            {'name': '__dunder_method', 'params': [], 'return_type': 'None'},
        ]
        stub = self.generator.generate_test_stub('test.py', functions)

        self.assertIn('test_public_method', stub)
        self.assertNotIn('test__private_method', stub)
        # __dunder methods should be included (they're special)

    def test_generate_import_test_stub(self):
        """Test generating import test stub."""
        imports = ['os', 'sys', 'json']
        stub = self.generator.generate_import_test_stub('module.py', imports)

        self.assertIn('import pytest', stub)
        self.assertIn('def test_import_os():', stub)
        self.assertIn('def test_import_sys():', stub)
        self.assertIn('def test_import_json():', stub)


class TestVitestStubGeneration(unittest.TestCase):
    """Test vitest stub generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = TestStubGenerator(TestFramework.VITEST)

    def test_generate_function_test_stub(self):
        """Test generating vitest stub for functions."""
        functions = [
            {'name': 'add', 'params': ['a', 'b'], 'return_type': 'number'},
        ]
        stub = self.generator.generate_test_stub('math_ops.ts', functions)

        self.assertIn("import { describe, it, expect", stub)
        self.assertIn("describe('math_ops.ts'", stub)
        self.assertIn("it('should add'", stub)

    def test_generate_class_test_stub(self):
        """Test generating vitest stub for class."""
        functions = [
            {'name': 'getName', 'params': [], 'return_type': 'string'},
        ]
        stub = self.generator.generate_test_stub('user.ts', functions, class_name='User')

        self.assertIn("describe('User'", stub)
        self.assertIn("describe('constructor'", stub)
        self.assertIn("should create instance", stub)
        self.assertIn("describe('getName'", stub)

    def test_skip_private_methods(self):
        """Test that private methods are skipped."""
        functions = [
            {'name': 'publicMethod', 'params': [], 'return_type': 'void'},
            {'name': '_privateMethod', 'params': [], 'return_type': 'void'},
        ]
        stub = self.generator.generate_test_stub('test.ts', functions)

        self.assertIn('publicMethod', stub)
        self.assertNotIn('_privateMethod', stub)


class TestJestStubGeneration(unittest.TestCase):
    """Test jest stub generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = TestStubGenerator(TestFramework.JEST)

    def test_generate_jest_stub(self):
        """Test generating jest stub."""
        functions = [
            {'name': 'add', 'params': ['a', 'b'], 'return_type': 'number'},
        ]
        stub = self.generator.generate_test_stub('math_ops.ts', functions)

        # Should not have vitest import
        self.assertNotIn("from 'vitest'", stub)
        # Should have jest-style globals comment or no import
        self.assertIn("describe('math_ops.ts'", stub)


class TestRustTestStubGeneration(unittest.TestCase):
    """Test Rust test stub generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = TestStubGenerator(TestFramework.RUST)

    def test_generate_rust_test_stub(self):
        """Test generating Rust test stub."""
        functions = [
            {'name': 'add', 'params': ['a: i32', 'b: i32'], 'return_type': 'i32'},
            {'name': 'subtract', 'params': ['a: i32', 'b: i32'], 'return_type': 'i32'},
        ]
        stub = self.generator.generate_test_stub('math_ops.rs', functions)

        self.assertIn('#[cfg(test)]', stub)
        self.assertIn('mod tests {', stub)
        self.assertIn('use super::*;', stub)
        self.assertIn('#[test]', stub)
        self.assertIn('fn test_add()', stub)
        self.assertIn('fn test_subtract()', stub)

    def test_generate_rust_class_test_stub(self):
        """Test generating Rust test stub for struct."""
        functions = [
            {'name': 'get_name', 'params': ['&self'], 'return_type': '&str'},
        ]
        stub = self.generator.generate_test_stub('user.rs', functions, class_name='User')

        self.assertIn('// Tests for User', stub)
        self.assertIn('fn test_get_name()', stub)


class TestStubValidity(unittest.TestCase):
    """Test that generated stubs are valid code."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = TestStubGenerator(TestFramework.PYTEST)

    def test_pytest_stub_is_valid_python(self):
        """Test that pytest stub is valid Python syntax."""
        functions = [
            {'name': 'add', 'params': ['a', 'b'], 'return_type': 'int'},
            {'name': 'subtract', 'params': ['a', 'b'], 'return_type': 'int'},
        ]
        stub = self.generator.generate_test_stub('math_ops.py', functions)

        # Try to parse as Python AST
        try:
            ast.parse(stub)
            valid = True
        except SyntaxError:
            valid = False

        self.assertTrue(valid, "Generated pytest stub should be valid Python")

    def test_class_test_stub_is_valid_python(self):
        """Test that class test stub is valid Python."""
        functions = [
            {'name': 'get_value', 'params': [], 'return_type': 'int'},
        ]
        stub = self.generator.generate_test_stub('counter.py', functions, class_name='Counter')

        try:
            ast.parse(stub)
            valid = True
        except SyntaxError:
            valid = False

        self.assertTrue(valid, "Generated class test stub should be valid Python")

    def test_import_test_stub_is_valid_python(self):
        """Test that import test stub is valid Python."""
        imports = ['os', 'sys']
        stub = self.generator.generate_import_test_stub('module.py', imports)

        try:
            ast.parse(stub)
            valid = True
        except SyntaxError:
            valid = False

        self.assertTrue(valid, "Generated import test stub should be valid Python")


class TestNameConversion(unittest.TestCase):
    """Test function name to test name conversion."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = TestStubGenerator()

    def test_func_to_test_name_snake(self):
        """Test snake_case conversion."""
        self.assertEqual(self.generator._func_to_test_name('add'), 'test_add')
        self.assertEqual(self.generator._func_to_test_name('add_numbers'), 'test_add_numbers')
        self.assertEqual(self.generator._func_to_test_name('_private'), 'test_private')

    def test_func_to_test_name_camel(self):
        """Test camelCase conversion."""
        self.assertEqual(self.generator._func_to_test_name('add', camel=True), 'test_add')
        self.assertEqual(self.generator._func_to_test_name('add_numbers', camel=True), 'test_addNumbers')
        self.assertEqual(self.generator._func_to_test_name('get_user_name', camel=True), 'test_getUserName')

    def test_rust_test_name(self):
        """Test Rust test name conversion."""
        self.assertEqual(self.generator._rust_test_name('add'), 'test_add')
        self.assertEqual(self.generator._rust_test_name('add_numbers'), 'test_add_numbers')
        self.assertEqual(self.generator._rust_test_name('_private'), 'test_private')


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions."""

    def test_generate_pytest_stub(self):
        """Test generate_pytest_stub function."""
        functions = [{'name': 'test_func', 'params': [], 'return_type': 'None'}]
        stub = generate_pytest_stub('module.py', functions)

        self.assertIn('import pytest', stub)
        self.assertIn('def test_test_func():', stub)

    def test_generate_vitest_stub(self):
        """Test generate_vitest_stub function."""
        functions = [{'name': 'testFunc', 'params': [], 'return_type': 'void'}]
        stub = generate_vitest_stub('module.ts', functions)

        self.assertIn('vitest', stub)
        self.assertIn('describe', stub)

    def test_generate_rust_test_stub(self):
        """Test generate_rust_test_stub function."""
        functions = [{'name': 'test_func', 'params': [], 'return_type': 'i32'}]
        stub = generate_rust_test_stub('module.rs', functions)

        self.assertIn('#[cfg(test)]', stub)
        self.assertIn('#[test]', stub)


class TestStubContent(unittest.TestCase):
    """Test stub content quality."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = TestStubGenerator(TestFramework.PYTEST)

    def test_stub_has_todo_comment(self):
        """Test that stub has TODO comment."""
        functions = [{'name': 'func', 'params': [], 'return_type': 'None'}]
        stub = self.generator.generate_test_stub('module.py', functions)

        self.assertIn('TODO', stub)

    def test_stub_has_docstring(self):
        """Test that stub has docstring."""
        functions = [{'name': 'func', 'params': [], 'return_type': 'None'}]
        stub = self.generator.generate_test_stub('module.py', functions)

        self.assertIn('"""', stub)

    def test_stub_references_source_file(self):
        """Test that stub references source file."""
        functions = [{'name': 'func', 'params': [], 'return_type': 'None'}]
        stub = self.generator.generate_test_stub('my_module.py', functions)

        self.assertIn('my_module', stub)

    def test_stub_has_test_marker(self):
        """Test that stub has test marker."""
        functions = [{'name': 'func', 'params': [], 'return_type': 'None'}]
        stub = self.generator.generate_test_stub('module.py', functions)

        self.assertIn('test_', stub)


if __name__ == '__main__':
    unittest.main(verbosity=2)

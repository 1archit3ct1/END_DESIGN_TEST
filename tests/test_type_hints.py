#!/usr/bin/env python3
"""
Test: Type hints are valid TypeScript/Python.
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agent.type_hint_generator import (
    TypeHintGenerator,
    generate_python_type_hint,
    generate_typescript_type_hint,
)


class TestPythonTypeHintGeneration(unittest.TestCase):
    """Test Python type hint generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = TypeHintGenerator()

    def test_generate_string_type(self):
        """Test generating string type hint."""
        hint = self.generator.generate_python_type_hint('name', 'string')
        self.assertEqual(hint, 'name: str')

    def test_generate_number_type(self):
        """Test generating number type hint."""
        hint = self.generator.generate_python_type_hint('count', 'number')
        self.assertEqual(hint, 'count: int')

    def test_generate_float_type(self):
        """Test generating float type hint."""
        hint = self.generator.generate_python_type_hint('value', 'float')
        self.assertEqual(hint, 'value: float')

    def test_generate_boolean_type(self):
        """Test generating boolean type hint."""
        hint = self.generator.generate_python_type_hint('active', 'boolean')
        self.assertEqual(hint, 'active: bool')

    def test_generate_list_type(self):
        """Test generating list type hint."""
        hint = self.generator.generate_python_type_hint('items', 'list')
        self.assertEqual(hint, 'items: List')

    def test_generate_dict_type(self):
        """Test generating dict type hint."""
        hint = self.generator.generate_python_type_hint('data', 'dict')
        self.assertEqual(hint, 'data: Dict')

    def test_generate_optional_type(self):
        """Test generating optional type hint."""
        hint = self.generator.generate_python_type_hint('name', 'string', is_optional=True)
        self.assertEqual(hint, 'name: Optional[str]')

    def test_generate_generic_type(self):
        """Test generating generic type hint."""
        hint = self.generator.generate_python_type_hint('data', 'Any')
        self.assertEqual(hint, 'data: Any')


class TestPythonReturnHintGeneration(unittest.TestCase):
    """Test Python return type hint generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = TypeHintGenerator()

    def test_generate_string_return(self):
        """Test generating string return type."""
        hint = self.generator.generate_python_return_hint('string')
        self.assertEqual(hint, ' -> str')

    def test_generate_number_return(self):
        """Test generating number return type."""
        hint = self.generator.generate_python_return_hint('number')
        self.assertEqual(hint, ' -> int')

    def test_generate_optional_return(self):
        """Test generating optional return type."""
        hint = self.generator.generate_python_return_hint('string', is_optional=True)
        self.assertEqual(hint, ' -> Optional[str]')

    def test_generate_none_return(self):
        """Test generating None return type."""
        hint = self.generator.generate_python_return_hint('none')
        self.assertEqual(hint, ' -> None')


class TestTypeScriptTypeHintGeneration(unittest.TestCase):
    """Test TypeScript type hint generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = TypeHintGenerator()

    def test_generate_string_type(self):
        """Test generating string type hint."""
        hint = self.generator.generate_typescript_type_hint('name', 'string')
        self.assertEqual(hint, 'name: string')

    def test_generate_number_type(self):
        """Test generating number type hint."""
        hint = self.generator.generate_typescript_type_hint('count', 'number')
        self.assertEqual(hint, 'count: number')

    def test_generate_boolean_type(self):
        """Test generating boolean type hint."""
        hint = self.generator.generate_typescript_type_hint('active', 'boolean')
        self.assertEqual(hint, 'active: boolean')

    def test_generate_array_type(self):
        """Test generating array type hint."""
        hint = self.generator.generate_typescript_type_hint('items', 'array')
        self.assertEqual(hint, 'items: Array')

    def test_generate_optional_type(self):
        """Test generating optional type hint."""
        hint = self.generator.generate_typescript_type_hint('name', 'string', is_optional=True)
        self.assertEqual(hint, 'name?: string')

    def test_generate_any_type(self):
        """Test generating any type hint."""
        hint = self.generator.generate_typescript_type_hint('data', 'any')
        self.assertEqual(hint, 'data: any')

    def test_generate_void_type(self):
        """Test generating void type hint."""
        hint = self.generator.generate_typescript_type_hint('callback', 'void')
        self.assertEqual(hint, 'callback: void')


class TestTypeScriptReturnHintGeneration(unittest.TestCase):
    """Test TypeScript return type hint generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = TypeHintGenerator()

    def test_generate_string_return(self):
        """Test generating string return type."""
        hint = self.generator.generate_typescript_return_hint('string')
        self.assertEqual(hint, ': string')

    def test_generate_number_return(self):
        """Test generating number return type."""
        hint = self.generator.generate_typescript_return_hint('number')
        self.assertEqual(hint, ': number')

    def test_generate_promise_return(self):
        """Test generating promise return type."""
        hint = self.generator.generate_typescript_return_hint('promise')
        self.assertEqual(hint, ': Promise')

    def test_generate_void_return(self):
        """Test generating void return type."""
        hint = self.generator.generate_typescript_return_hint('void')
        self.assertEqual(hint, ': void')


class TestGenericTypeConversion(unittest.TestCase):
    """Test generic type conversion."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = TypeHintGenerator()

    def test_python_list_generic(self):
        """Test Python List<T> conversion."""
        result = self.generator._convert_to_python_type('List<string>')
        self.assertEqual(result, 'List[str]')

    def test_python_dict_generic(self):
        """Test Python Dict<K, V> conversion."""
        result = self.generator._convert_to_python_type('Dict<string, number>')
        self.assertEqual(result, 'Dict[str, int]')

    def test_python_union_type(self):
        """Test Python Union type conversion."""
        result = self.generator._convert_to_python_type('Union<string, number>')
        self.assertEqual(result, 'Union[str, int]')

    def test_python_tuple_type(self):
        """Test Python Tuple type conversion."""
        result = self.generator._convert_to_python_type('Tuple[str, int]')
        self.assertEqual(result, 'Tuple[str, int]')

    def test_typescript_array_generic(self):
        """Test TypeScript Array<T> conversion."""
        result = self.generator._convert_to_ts_type('Array<string>')
        self.assertEqual(result, 'Array<string>')

    def test_typescript_promise_generic(self):
        """Test TypeScript Promise<T> conversion."""
        result = self.generator._convert_to_ts_type('Promise<string>')
        self.assertEqual(result, 'Promise<string>')

    def test_typescript_union_type(self):
        """Test TypeScript union type conversion."""
        result = self.generator._convert_to_ts_type('Union<string, number>')
        self.assertEqual(result, 'string | number')


class TestFunctionSignatureGeneration(unittest.TestCase):
    """Test complete function signature generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = TypeHintGenerator()

    def test_python_function_signature(self):
        """Test Python function signature generation."""
        params = [
            {'name': 'name', 'type': 'string'},
            {'name': 'age', 'type': 'number'},
        ]
        signature = self.generator.generate_python_function_signature(
            'greet', params, 'string'
        )

        self.assertIn('def greet(', signature)
        self.assertIn('name: str', signature)
        self.assertIn('age: int', signature)
        self.assertIn('-> str', signature)

    def test_python_function_with_optional_params(self):
        """Test Python function with optional parameters."""
        params = [
            {'name': 'name', 'type': 'string', 'optional': True},
        ]
        signature = self.generator.generate_python_function_signature(
            'greet', params, 'None'
        )

        self.assertIn('name: Optional[str]', signature)

    def test_typescript_function_signature(self):
        """Test TypeScript function signature generation."""
        params = [
            {'name': 'name', 'type': 'string'},
            {'name': 'age', 'type': 'number'},
        ]
        signature = self.generator.generate_typescript_function_signature(
            'greet', params, 'string'
        )

        self.assertIn('function greet(', signature)
        self.assertIn('name: string', signature)
        self.assertIn('age: number', signature)
        self.assertIn(': string', signature)

    def test_typescript_function_with_optional_params(self):
        """Test TypeScript function with optional parameters."""
        params = [
            {'name': 'name', 'type': 'string', 'optional': True},
        ]
        signature = self.generator.generate_typescript_function_signature(
            'greet', params, 'void'
        )

        self.assertIn('name?: string', signature)


class TestInterfaceGeneration(unittest.TestCase):
    """Test interface/class generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = TypeHintGenerator()

    def test_python_class_generation(self):
        """Test Python class generation with type hints."""
        fields = [
            {'name': 'name', 'type': 'string'},
            {'name': 'age', 'type': 'number'},
        ]
        class_def = self.generator.generate_python_interface('User', fields)

        self.assertIn('class User:', class_def)
        self.assertIn('name: str', class_def)
        self.assertIn('age: int', class_def)
        self.assertIn('def __init__', class_def)

    def test_typescript_interface_generation(self):
        """Test TypeScript interface generation."""
        fields = [
            {'name': 'name', 'type': 'string'},
            {'name': 'age', 'type': 'number'},
        ]
        interface_def = self.generator.generate_typescript_interface('User', fields)

        self.assertIn('export interface User', interface_def)
        self.assertIn('name: string;', interface_def)
        self.assertIn('age: number;', interface_def)

    def test_typescript_interface_with_optional_fields(self):
        """Test TypeScript interface with optional fields."""
        fields = [
            {'name': 'name', 'type': 'string'},
            {'name': 'email', 'type': 'string', 'optional': True},
        ]
        interface_def = self.generator.generate_typescript_interface('User', fields)

        self.assertIn('name: string;', interface_def)
        self.assertIn('email?: string;', interface_def)


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions."""

    def test_generate_python_type_hint(self):
        """Test Python type hint convenience function."""
        hint = generate_python_type_hint('name', 'string')
        self.assertEqual(hint, 'name: str')

    def test_generate_typescript_type_hint(self):
        """Test TypeScript type hint convenience function."""
        hint = generate_typescript_type_hint('name', 'string')
        self.assertEqual(hint, 'name: string')


class TestTypeHintValidity(unittest.TestCase):
    """Test that generated type hints are valid."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = TypeHintGenerator()

    def test_python_type_hint_syntax(self):
        """Test Python type hint syntax is valid."""
        hint = self.generator.generate_python_type_hint('value', 'string')

        # Should have format: name: type
        self.assertRegex(hint, r'^\w+:\s*\w+$')

    def test_python_optional_hint_syntax(self):
        """Test Python optional type hint syntax."""
        hint = self.generator.generate_python_type_hint('value', 'string', is_optional=True)

        # Should have Optional wrapper
        self.assertIn('Optional[', hint)

    def test_typescript_type_hint_syntax(self):
        """Test TypeScript type hint syntax is valid."""
        hint = self.generator.generate_typescript_type_hint('value', 'string')

        # Should have format: name: type
        self.assertRegex(hint, r'^\w+:\s*\w+$')

    def test_typescript_optional_hint_syntax(self):
        """Test TypeScript optional type hint syntax."""
        hint = self.generator.generate_typescript_type_hint('value', 'string', is_optional=True)

        # Should have ? marker
        self.assertIn('?:', hint)


if __name__ == '__main__':
    unittest.main(verbosity=2)

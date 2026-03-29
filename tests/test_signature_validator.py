#!/usr/bin/env python3
"""
Test: Function signatures match expected format.
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agent.signature_validator import SignatureValidator, validate_function_signatures


class TestPythonSignatureValidation(unittest.TestCase):
    """Test Python function signature validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.validator = SignatureValidator()

    def test_valid_python_function(self):
        """Test valid Python function signature."""
        code = '''
def hello(name: str) -> str:
    return f"Hello, {name}"
'''
        is_valid, functions = self.validator._validate_python(code)

        self.assertTrue(is_valid)
        self.assertEqual(len(functions), 1)
        self.assertEqual(functions[0]['name'], 'hello')
        self.assertEqual(functions[0]['args'], 'name: str')
        self.assertEqual(functions[0]['return_type'], 'str')

    def test_python_function_without_return_type(self):
        """Test Python function without return type."""
        code = '''
def greet(name):
    print(f"Hello, {name}")
'''
        is_valid, functions = self.validator._validate_python(code)

        self.assertTrue(is_valid)
        self.assertEqual(len(functions), 1)
        self.assertEqual(functions[0]['name'], 'greet')
        self.assertIsNone(functions[0]['return_type'])

    def test_python_function_with_multiple_args(self):
        """Test Python function with multiple arguments."""
        code = '''
def add(a: int, b: int) -> int:
    return a + b
'''
        is_valid, functions = self.validator._validate_python(code)

        self.assertTrue(is_valid)
        self.assertEqual(len(functions), 1)
        self.assertEqual(functions[0]['args'], 'a: int, b: int')

    def test_python_multiple_functions(self):
        """Test code with multiple Python functions."""
        code = '''
def func1() -> None:
    pass

def func2(x: int) -> int:
    return x * 2

def func3(a: str, b: str) -> str:
    return a + b
'''
        is_valid, functions = self.validator._validate_python(code)

        self.assertTrue(is_valid)
        self.assertEqual(len(functions), 3)
        self.assertEqual(functions[0]['name'], 'func1')
        self.assertEqual(functions[1]['name'], 'func2')
        self.assertEqual(functions[2]['name'], 'func3')

    def test_python_method_in_class(self):
        """Test Python method in class."""
        code = '''
class MyClass:
    def method(self, arg: str) -> bool:
        return True
'''
        is_valid, functions = self.validator._validate_python(code)

        self.assertTrue(is_valid)
        self.assertEqual(len(functions), 1)
        self.assertEqual(functions[0]['name'], 'method')


class TestRustSignatureValidation(unittest.TestCase):
    """Test Rust function signature validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.validator = SignatureValidator()

    def test_valid_rust_function(self):
        """Test valid Rust function signature."""
        code = '''
fn hello(name: &str) -> String {
    format!("Hello, {}", name)
}
'''
        is_valid, functions = self.validator._validate_rust(code)

        self.assertTrue(is_valid)
        self.assertEqual(len(functions), 1)
        self.assertEqual(functions[0]['name'], 'hello')
        self.assertEqual(functions[0]['args'], 'name: &str')
        self.assertEqual(functions[0]['return_type'], 'String')

    def test_rust_pub_function(self):
        """Test Rust pub function."""
        code = '''
pub fn process_data(data: Vec<u8>) -> Result<(), Error> {
    Ok(())
}
'''
        is_valid, functions = self.validator._validate_rust(code)

        self.assertTrue(is_valid)
        self.assertEqual(len(functions), 1)
        self.assertEqual(functions[0]['name'], 'process_data')
        self.assertIn('Vec<u8>', functions[0]['args'])

    def test_rust_function_without_return(self):
        """Test Rust function without return type."""
        code = '''
fn log_message(msg: &str) {
    println!("{}", msg);
}
'''
        is_valid, functions = self.validator._validate_rust(code)

        self.assertTrue(is_valid)
        self.assertEqual(len(functions), 1)
        self.assertIsNone(functions[0]['return_type'])

    def test_rust_multiple_functions(self):
        """Test Rust code with multiple functions."""
        code = '''
fn add(a: i32, b: i32) -> i32 {
    a + b
}

pub fn subtract(a: i32, b: i32) -> i32 {
    a - b
}

fn multiply(a: i32, b: i32) -> i32 {
    a * b
}
'''
        is_valid, functions = self.validator._validate_rust(code)

        self.assertTrue(is_valid)
        self.assertEqual(len(functions), 3)


class TestTypeScriptSignatureValidation(unittest.TestCase):
    """Test TypeScript function signature validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.validator = SignatureValidator()

    def test_valid_typescript_function(self):
        """Test valid TypeScript function signature."""
        code = '''
function greet(name: string): string {
    return `Hello, ${name}`;
}
'''
        is_valid, functions = self.validator._validate_typescript(code)

        self.assertTrue(is_valid)
        self.assertEqual(len(functions), 1)
        self.assertEqual(functions[0]['name'], 'greet')
        self.assertEqual(functions[0]['return_type'], 'string')

    def test_typescript_arrow_function(self):
        """Test TypeScript arrow function."""
        code = '''
const add = (a: number, b: number): number => {
    return a + b;
};
'''
        is_valid, functions = self.validator._validate_typescript(code)

        self.assertTrue(is_valid)
        self.assertEqual(len(functions), 1)
        self.assertEqual(functions[0]['name'], 'add')
        self.assertEqual(functions[0]['type'], 'arrow')

    def test_typescript_async_function(self):
        """Test TypeScript async function."""
        code = '''
async function fetchData(url: string): Promise<Response> {
    return await fetch(url);
}
'''
        is_valid, functions = self.validator._validate_typescript(code)

        self.assertTrue(is_valid)
        self.assertEqual(len(functions), 1)
        self.assertEqual(functions[0]['name'], 'fetchData')

    def test_typescript_export_function(self):
        """Test TypeScript exported function."""
        code = '''
export function helper(x: number): boolean {
    return x > 0;
}
'''
        is_valid, functions = self.validator._validate_typescript(code)

        self.assertTrue(is_valid)
        self.assertEqual(len(functions), 1)
        self.assertEqual(functions[0]['name'], 'helper')

    def test_typescript_multiple_functions(self):
        """Test TypeScript with multiple functions."""
        code = '''
function func1(): void {}
const func2 = (x: number): number => x * 2;
export async function func3(): Promise<string> { return ""; }
'''
        is_valid, functions = self.validator._validate_typescript(code)

        self.assertTrue(is_valid)
        self.assertEqual(len(functions), 3)


class TestSignatureValidatorHelpers(unittest.TestCase):
    """Test helper methods of SignatureValidator."""

    def setUp(self):
        """Set up test fixtures."""
        self.validator = SignatureValidator()

    def test_check_function_exists(self):
        """Test checking if function exists."""
        code = '''
def hello() -> None:
    pass

def world() -> None:
    pass
'''
        exists = self.validator.check_function_exists(code, 'python', 'hello')
        not_exists = self.validator.check_function_exists(code, 'python', 'missing')

        self.assertTrue(exists)
        self.assertFalse(not_exists)

    def test_get_function_names(self):
        """Test getting function names."""
        code = '''
def func_a() -> None: pass
def func_b() -> None: pass
def func_c() -> None: pass
'''
        names = self.validator.get_function_names(code, 'python')

        self.assertEqual(len(names), 3)
        self.assertIn('func_a', names)
        self.assertIn('func_b', names)
        self.assertIn('func_c', names)


class TestValidateFunctionSignaturesFunction(unittest.TestCase):
    """Test convenience validate_function_signatures function."""

    def test_validate_python(self):
        """Test validate_function_signatures with Python."""
        code = 'def test() -> None: pass'
        is_valid, functions = validate_function_signatures(code, 'python')

        self.assertTrue(is_valid)
        self.assertEqual(len(functions), 1)

    def test_validate_rust(self):
        """Test validate_function_signatures with Rust."""
        code = 'fn test() -> i32 { 0 }'
        is_valid, functions = validate_function_signatures(code, 'rust')

        self.assertTrue(is_valid)
        self.assertEqual(len(functions), 1)

    def test_validate_typescript(self):
        """Test validate_function_signatures with TypeScript."""
        code = 'function test(): void {}'
        is_valid, functions = validate_function_signatures(code, 'typescript')

        self.assertTrue(is_valid)
        self.assertEqual(len(functions), 1)

    def test_validate_unknown_language(self):
        """Test validate_function_signatures with unknown language."""
        code = 'some code'
        is_valid, functions = validate_function_signatures(code, 'unknown')

        self.assertTrue(is_valid)
        self.assertEqual(functions, [])


class TestSignatureValidationEdgeCases(unittest.TestCase):
    """Test edge cases in signature validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.validator = SignatureValidator()

    def test_empty_code(self):
        """Test validation with empty code."""
        is_valid, functions = self.validator.validate_signatures('', 'python')
        self.assertTrue(is_valid)
        self.assertEqual(len(functions), 0)

    def test_code_without_functions(self):
        """Test code without functions."""
        code = 'x = 1\ny = 2'
        is_valid, functions = self.validator.validate_signatures(code, 'python')
        self.assertTrue(is_valid)
        self.assertEqual(len(functions), 0)

    def test_nested_functions(self):
        """Test nested functions."""
        code = '''
def outer() -> None:
    def inner() -> None:
        pass
'''
        is_valid, functions = self.validator.validate_signatures(code, 'python')
        self.assertTrue(is_valid)
        self.assertEqual(len(functions), 2)  # Both outer and inner should be found

    def test_function_with_generics(self):
        """Test function with generic types."""
        code = '''
fn process<T>(item: T) -> T {
    item
}
'''
        is_valid, functions = self.validator.validate_signatures(code, 'rust')
        self.assertTrue(is_valid)
        self.assertEqual(len(functions), 1)

    def test_function_with_default_args(self):
        """Test function with default arguments."""
        code = '''
def greet(name: str = "World") -> str:
    return f"Hello, {name}"
'''
        is_valid, functions = self.validator.validate_signatures(code, 'python')
        self.assertTrue(is_valid)
        self.assertEqual(len(functions), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)

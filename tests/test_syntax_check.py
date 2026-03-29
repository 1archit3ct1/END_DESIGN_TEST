"""
Tests for syntax_check.py — Syntax error detection.
"""

import pytest
from agent.syntax_check import SyntaxChecker, SyntaxErrorInfo, SyntaxCheckResult


class TestSyntaxErrorInfo:
    """Test SyntaxErrorInfo class."""

    def test_create_error_info(self):
        """Test creating SyntaxErrorInfo."""
        error = SyntaxErrorInfo(
            message="Unexpected token",
            line=10,
            column=5,
            error_type="syntax"
        )
        assert error.message == "Unexpected token"
        assert error.line == 10
        assert error.column == 5
        assert error.error_type == "syntax"

    def test_error_info_to_dict(self):
        """Test converting SyntaxErrorInfo to dictionary."""
        error = SyntaxErrorInfo(
            message="Unclosed brace",
            line=15,
            column=3,
            error_type="syntax"
        )
        result = error.to_dict()
        assert result == {
            'message': "Unclosed brace",
            'line': 15,
            'column': 3,
            'error_type': "syntax"
        }

    def test_error_info_optional_fields(self):
        """Test SyntaxErrorInfo with optional fields."""
        error = SyntaxErrorInfo(message="Generic error")
        assert error.message == "Generic error"
        assert error.line is None
        assert error.column is None
        assert error.error_type == "syntax"


class TestSyntaxCheckResult:
    """Test SyntaxCheckResult class."""

    def test_create_valid_result(self):
        """Test creating valid syntax check result."""
        result = SyntaxCheckResult(is_valid=True)
        assert result.is_valid is True
        assert result.error is None

    def test_create_invalid_result(self):
        """Test creating invalid syntax check result."""
        error = SyntaxErrorInfo(message="Syntax error", line=5)
        result = SyntaxCheckResult(is_valid=False, error=error)
        assert result.is_valid is False
        assert result.error is not None
        assert result.error.message == "Syntax error"

    def test_result_to_dict_valid(self):
        """Test converting valid result to dictionary."""
        result = SyntaxCheckResult(is_valid=True)
        d = result.to_dict()
        assert d == {'is_valid': True, 'error': None}

    def test_result_to_dict_invalid(self):
        """Test converting invalid result to dictionary."""
        error = SyntaxErrorInfo(message="Error", line=10, column=5)
        result = SyntaxCheckResult(is_valid=False, error=error)
        d = result.to_dict()
        assert d['is_valid'] is False
        assert d['error']['message'] == "Error"
        assert d['error']['line'] == 10


class TestSyntaxCheckerPython:
    """Test Python syntax checking."""

    def setup_method(self):
        """Set up test fixtures."""
        self.checker = SyntaxChecker()

    def test_valid_python_syntax(self):
        """Test valid Python code passes syntax check."""
        code = """
def hello():
    print("Hello, World!")

class MyClass:
    def __init__(self):
        self.value = 0
"""
        result = self.checker.check_syntax(code, '.py')
        assert result.is_valid is True
        assert result.error is None

    def test_invalid_python_syntax_missing_colon(self):
        """Test Python syntax error detected - missing colon."""
        code = """
def hello()
    print("Hello")
"""
        result = self.checker.check_syntax(code, '.py')
        assert result.is_valid is False
        assert result.error is not None
        assert result.error.line is not None
        assert "syntax" in result.error.error_type

    def test_invalid_python_syntax_unclosed_paren(self):
        """Test Python syntax error detected - unclosed parenthesis."""
        code = """
print("Hello"
"""
        result = self.checker.check_syntax(code, '.py')
        assert result.is_valid is False
        assert result.error is not None

    def test_invalid_python_syntax_indent_error(self):
        """Test Python syntax error detected - indentation error."""
        code = """
def hello():
print("Hello")
"""
        result = self.checker.check_syntax(code, '.py')
        assert result.is_valid is False
        assert result.error is not None


class TestSyntaxCheckerJavaScript:
    """Test JavaScript/TypeScript syntax checking."""

    def setup_method(self):
        """Set up test fixtures."""
        self.checker = SyntaxChecker()

    def test_valid_javascript_syntax(self):
        """Test valid JavaScript code passes syntax check."""
        code = """
function hello() {
    console.log("Hello, World!");
}

class MyClass {
    constructor() {
        this.value = 0;
    }
}
"""
        result = self.checker.check_syntax(code, '.ts')
        assert result.is_valid is True
        assert result.error is None

    def test_invalid_javascript_unclosed_brace(self):
        """Test JavaScript syntax error detected - unclosed brace."""
        code = """
function hello() {
    console.log("Hello");

"""
        result = self.checker.check_syntax(code, '.js')
        assert result.is_valid is False
        assert result.error is not None
        assert "Unclosed" in result.error.message

    def test_invalid_javascript_unexpected_closing_brace(self):
        """Test JavaScript syntax error detected - unexpected closing brace."""
        code = """
function hello() {
    console.log("Hello");
}
}
"""
        result = self.checker.check_syntax(code, '.jsx')
        assert result.is_valid is False
        assert result.error is not None
        assert result.error.line is not None

    def test_invalid_javascript_mismatched_braces(self):
        """Test JavaScript syntax error detected - mismatched braces."""
        code = """
function hello() {
    console.log("Hello";
}
"""
        result = self.checker.check_syntax(code, '.ts')
        assert result.is_valid is False
        assert result.error is not None


class TestSyntaxCheckerRust:
    """Test Rust syntax checking."""

    def setup_method(self):
        """Set up test fixtures."""
        self.checker = SyntaxChecker()

    def test_valid_rust_syntax(self):
        """Test valid Rust code passes syntax check."""
        code = """
fn hello() {
    println!("Hello, World!");
}

struct MyClass {
    value: i32,
}

impl MyClass {
    fn new() -> Self {
        MyClass { value: 0 }
    }
}
"""
        result = self.checker.check_syntax(code, '.rs')
        assert result.is_valid is True
        assert result.error is None

    def test_invalid_rust_unclosed_brace(self):
        """Test Rust syntax error detected - unclosed brace."""
        code = """
fn hello() {
    println!("Hello");

"""
        result = self.checker.check_syntax(code, '.rs')
        assert result.is_valid is False
        assert result.error is not None
        assert "Unclosed" in result.error.message

    def test_invalid_rust_unexpected_closing_brace(self):
        """Test Rust syntax error detected - unexpected closing brace."""
        code = """
fn hello() {
    println!("Hello");
}
}
"""
        result = self.checker.check_syntax(code, '.rs')
        assert result.is_valid is False
        assert result.error is not None


class TestSyntaxCheckerEdgeCases:
    """Test edge cases for syntax checking."""

    def setup_method(self):
        """Set up test fixtures."""
        self.checker = SyntaxChecker()

    def test_unknown_extension(self):
        """Test unknown file extension returns valid."""
        code = "some code"
        result = self.checker.check_syntax(code, '.unknown')
        assert result.is_valid is True

    def test_empty_code(self):
        """Test empty code passes syntax check."""
        result = self.checker.check_syntax('', '.py')
        assert result.is_valid is True

    def test_error_contains_line_number(self):
        """Test that error contains line number for Python."""
        code = """
def valid():
    pass

def invalid(
    x = 1
"""
        result = self.checker.check_syntax(code, '.py')
        assert result.is_valid is False
        assert result.error is not None
        assert result.error.line is not None
        assert result.error.line >= 1

    def test_error_position_tracking_javascript(self):
        """Test that error tracks position in JavaScript."""
        code = """
function test() {
    if (true) {
        console.log("test");
    }
}
}
"""
        result = self.checker.check_syntax(code, '.js')
        assert result.is_valid is False
        assert result.error is not None
        assert result.error.line is not None


class TestSyntaxErrorDetectionBeforeFileWrite:
    """Test that syntax errors are detected before file write."""

    def setup_method(self):
        """Set up test fixtures."""
        self.checker = SyntaxChecker()

    def test_syntax_check_prevents_invalid_write(self):
        """Test that invalid syntax is caught before hypothetical file write."""
        invalid_code = """
function broken() {
    return {
        name: "test"
    
}
"""
        result = self.checker.check_syntax(invalid_code, '.ts')
        
        # Should detect error before any file operation
        assert result.is_valid is False
        assert result.error is not None
        assert result.error.message is not None

    def test_valid_code_allows_write(self):
        """Test that valid code passes syntax check for file write."""
        valid_code = """
function working() {
    return {
        name: "test"
    };
}
"""
        result = self.checker.check_syntax(valid_code, '.ts')
        
        # Should allow file operation
        assert result.is_valid is True
        assert result.error is None

    def test_detailed_error_for_build_console(self):
        """Test that error details are available for build console display."""
        code = """
class Test {
    constructor() {
        this.value = 1;
    }
    
    method() {
        if (true) {
            return this.value;
        
    }
}
"""
        result = self.checker.check_syntax(code, '.js')
        
        assert result.is_valid is False
        assert result.error is not None
        
        # Error should have all details needed for build console
        error_dict = result.error.to_dict()
        assert 'message' in error_dict
        assert 'line' in error_dict
        assert 'column' in error_dict
        assert 'error_type' in error_dict

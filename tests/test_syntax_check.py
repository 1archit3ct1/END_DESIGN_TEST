"""
Test Syntax Check — Validation tests.
"""

import pytest

from agent.syntax_check import SyntaxChecker, SyntaxErrorInfo, SyntaxCheckResult


class TestSyntaxErrorInfo:
    """Test SyntaxErrorInfo class."""

    def test_initialization(self):
        """Test error info initialization."""
        error = SyntaxErrorInfo(
            message="Test error",
            line=10,
            column=5,
            error_type="syntax"
        )
        
        assert error.message == "Test error"
        assert error.line == 10
        assert error.column == 5
        assert error.error_type == "syntax"

    def test_to_dict(self):
        """Test converting to dictionary."""
        error = SyntaxErrorInfo(message="Error", line=1, column=2)
        result = error.to_dict()
        
        assert result['message'] == "Error"
        assert result['line'] == 1
        assert result['column'] == 2

    def test_optional_fields(self):
        """Test optional fields."""
        error = SyntaxErrorInfo(message="Error")
        
        assert error.line is None
        assert error.column is None


class TestSyntaxCheckResult:
    """Test SyntaxCheckResult class."""

    def test_valid_result(self):
        """Test valid result."""
        result = SyntaxCheckResult(is_valid=True)
        
        assert result.is_valid is True
        assert result.error is None

    def test_invalid_result(self):
        """Test invalid result."""
        error = SyntaxErrorInfo(message="Error")
        result = SyntaxCheckResult(is_valid=False, error=error)
        
        assert result.is_valid is False
        assert result.error is not None

    def test_to_dict_valid(self):
        """Test converting valid result to dictionary."""
        result = SyntaxCheckResult(is_valid=True)
        d = result.to_dict()
        
        assert d['is_valid'] is True
        assert d['error'] is None

    def test_to_dict_invalid(self):
        """Test converting invalid result to dictionary."""
        error = SyntaxErrorInfo(message="Error")
        result = SyntaxCheckResult(is_valid=False, error=error)
        d = result.to_dict()
        
        assert d['is_valid'] is False
        assert d['error'] is not None


class TestSyntaxChecker:
    """Test Syntax Checker functionality."""

    @pytest.fixture
    def checker(self):
        """Create SyntaxChecker instance."""
        return SyntaxChecker()

    def test_initialization(self, checker):
        """Test checker initializes correctly."""
        assert checker is not None

    # Python syntax tests
    def test_check_python_valid(self, checker):
        """Test valid Python syntax."""
        code = """
def hello():
    return "world"

class MyClass:
    pass
"""
        result = checker.check_syntax(code, '.py')
        
        assert result.is_valid is True
        assert result.error is None

    def test_check_python_invalid(self, checker):
        """Test invalid Python syntax."""
        code = "def invalid("
        result = checker.check_syntax(code, '.py')
        
        assert result.is_valid is False
        assert result.error is not None

    def test_check_python_empty(self, checker):
        """Test empty Python code."""
        result = checker.check_syntax("", '.py')
        
        assert result.is_valid is True

    # JavaScript/TypeScript syntax tests
    def test_check_javascript_valid(self, checker):
        """Test valid JavaScript syntax."""
        code = """
function hello() {
    return "world";
}

const obj = {
    key: 'value'
};
"""
        result = checker.check_syntax(code, '.ts')
        
        assert result.is_valid is True

    def test_check_javascript_invalid_braces(self, checker):
        """Test invalid JavaScript - unbalanced braces."""
        code = "function invalid() {"
        result = checker.check_syntax(code, '.ts')
        
        assert result.is_valid is False
        assert result.error is not None

    def test_check_javascript_invalid_parens(self, checker):
        """Test invalid JavaScript - unbalanced parentheses."""
        code = "const x = (1 + 2;"
        result = checker.check_syntax(code, '.ts')
        
        assert result.is_valid is False

    def test_check_javascript_invalid_brackets(self, checker):
        """Test invalid JavaScript - unbalanced brackets."""
        code = "const arr = [1, 2, 3;"
        result = checker.check_syntax(code, '.ts')
        
        assert result.is_valid is False

    def test_check_javascript_valid_nested(self, checker):
        """Test valid nested JavaScript."""
        code = """
function outer() {
    function inner() {
        return {
            data: [1, 2, 3]
        };
    }
    return inner();
}
"""
        result = checker.check_syntax(code, '.tsx')
        
        assert result.is_valid is True

    def test_check_typescript_valid(self, checker):
        """Test valid TypeScript syntax."""
        code = """
interface User {
    id: number;
    name: string;
}

const user: User = { id: 1, name: 'Test' };
"""
        result = checker.check_syntax(code, '.ts')
        
        assert result.is_valid is True

    def test_check_jsx_valid(self, checker):
        """Test valid JSX syntax."""
        code = """
const Component = () => {
    return <div>Hello</div>;
};
"""
        result = checker.check_syntax(code, '.jsx')
        
        assert result.is_valid is True

    # Rust syntax tests
    def test_check_rust_valid(self, checker):
        """Test valid Rust syntax."""
        code = """
fn main() {
    println!("Hello");
}

struct MyStruct {
    field: i32,
}
"""
        result = checker.check_syntax(code, '.rs')
        
        assert result.is_valid is True

    def test_check_rust_invalid_braces(self, checker):
        """Test invalid Rust - unbalanced braces."""
        code = "fn main() {"
        result = checker.check_syntax(code, '.rs')
        
        assert result.is_valid is False

    def test_check_rust_valid_struct(self, checker):
        """Test valid Rust struct."""
        code = """
pub struct User {
    pub id: u32,
    pub name: String,
}

impl User {
    pub fn new(id: u32, name: String) -> Self {
        Self { id, name }
    }
}
"""
        result = checker.check_syntax(code, '.rs')
        
        assert result.is_valid is True

    # Unknown extension tests
    def test_check_unknown_extension(self, checker):
        """Test unknown file extension."""
        code = "some code"
        result = checker.check_syntax(code, '.xyz')
        
        # Unknown extensions pass by default
        assert result.is_valid is True

    def test_check_empty_extension(self, checker):
        """Test empty file extension."""
        code = "some code"
        result = checker.check_syntax(code, '')
        
        assert result.is_valid is True

    # Edge cases
    def test_check_unicode(self, checker):
        """Test code with unicode characters."""
        code = """
const greeting = "你好世界";
const emoji = "👋";
"""
        result = checker.check_syntax(code, '.ts')
        
        assert result.is_valid is True

    def test_check_large_file(self, checker):
        """Test large file."""
        code = "\n".join([f"const line{i} = {i};" for i in range(1000)])
        result = checker.check_syntax(code, '.ts')
        
        assert result.is_valid is True


class TestSyntaxCheckerIntegration:
    """Integration tests for Syntax Checker."""

    def test_full_validation_workflow(self):
        """Test complete validation workflow."""
        checker = SyntaxChecker()
        
        # Valid code
        valid_code = "export const x = 1;"
        result = checker.check_syntax(valid_code, '.ts')
        assert result.is_valid is True
        
        # Invalid code
        invalid_code = "export const x = {"
        result = checker.check_syntax(invalid_code, '.ts')
        assert result.is_valid is False
        assert result.error is not None

    def test_multiple_languages(self):
        """Test validation across multiple languages."""
        checker = SyntaxChecker()
        
        tests = [
            ("def f(): pass", '.py', True),
            ("fn main() {}", '.rs', True),
            ("const x = 1;", '.ts', True),
            ("def invalid(", '.py', False),
            ("fn main() {", '.rs', False),
            ("const x = {", '.ts', False),
        ]
        
        for code, ext, expected in tests:
            result = checker.check_syntax(code, ext)
            assert result.is_valid == expected, f"Failed for {ext}: {code}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

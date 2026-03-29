#!/usr/bin/env python3
"""
Test: Generated code passes formatting check.
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agent.formatter import CodeFormatter, format_code


class TestCodeFormatterAvailability(unittest.TestCase):
    """Test formatter availability checks."""

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = CodeFormatter()

    def test_formatter_initializes(self):
        """Test formatter initializes correctly."""
        self.assertIsInstance(self.formatter, CodeFormatter)

    def test_get_formatter_status(self):
        """Test getting formatter status."""
        status = self.formatter.get_formatter_status()

        self.assertIn('black', status)
        self.assertIn('prettier', status)
        self.assertIn('rustfmt', status)
        self.assertIsInstance(status['black'], bool)
        self.assertIsInstance(status['prettier'], bool)
        self.assertIsInstance(status['rustfmt'], bool)


class TestPythonFormatting(unittest.TestCase):
    """Test Python code formatting."""

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = CodeFormatter()

    def test_format_python_code(self):
        """Test formatting Python code."""
        unformatted = '''def hello( ):
    x=1+2
    return x
'''
        formatted, success = self.formatter._format_python(unformatted)

        # Should return code (may or may not be formatted depending on black availability)
        self.assertIsInstance(formatted, str)
        self.assertGreater(len(formatted), 0)

    def test_format_python_preserves_logic(self):
        """Test formatting preserves code logic."""
        code = '''def add(a, b):
    return a + b
'''
        formatted, success = self.formatter._format_python(code)

        # Should contain original logic
        self.assertIn('def add', formatted)
        self.assertIn('return', formatted)

    def test_format_python_handles_syntax_error(self):
        """Test formatting handles syntax errors gracefully."""
        invalid_code = '''def broken(
    return invalid
'''
        formatted, success = self.formatter._format_python(invalid_code)

        # Should return original code on error
        self.assertEqual(formatted, invalid_code)


class TestJavaScriptFormatting(unittest.TestCase):
    """Test JavaScript/TypeScript code formatting."""

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = CodeFormatter()

    def test_format_typescript_code(self):
        """Test formatting TypeScript code."""
        unformatted = '''function add(a:number,b:number):number{return a+b;}'''
        formatted, success = self.formatter._format_javascript(unformatted, '.ts')

        # Should return code (may or may not be formatted depending on prettier availability)
        self.assertIsInstance(formatted, str)
        self.assertGreater(len(formatted), 0)

    def test_format_jsx_code(self):
        """Test formatting JSX code."""
        code = '''const Component = () => { return <div>Hello</div>; };'''
        formatted, success = self.formatter._format_javascript(code, '.jsx')

        self.assertIsInstance(formatted, str)
        self.assertIn('Component', formatted)

    def test_format_css_code(self):
        """Test formatting CSS code."""
        unformatted = '''.container{display:flex;align-items:center;}'''
        formatted, success = self.formatter._format_javascript(unformatted, '.css')

        self.assertIsInstance(formatted, str)
        self.assertGreater(len(formatted), 0)

    def test_format_json_code(self):
        """Test formatting JSON code."""
        unformatted = '''{"name":"test","version":"1.0.0"}'''
        formatted, success = self.formatter._format_javascript(unformatted, '.json')

        self.assertIsInstance(formatted, str)
        self.assertIn('name', formatted)

    def test_format_markdown_code(self):
        """Test formatting Markdown code."""
        code = '''# Header\nSome text with **bold** and *italic*.'''
        formatted, success = self.formatter._format_javascript(code, '.md')

        self.assertIsInstance(formatted, str)
        self.assertIn('# Header', formatted)

    def test_format_html_code(self):
        """Test formatting HTML code."""
        unformatted = '''<div class="test"><p>Hello</p></div>'''
        formatted, success = self.formatter._format_javascript(unformatted, '.html')

        self.assertIsInstance(formatted, str)
        self.assertIn('<div', formatted)


class TestRustFormatting(unittest.TestCase):
    """Test Rust code formatting."""

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = CodeFormatter()

    def test_format_rust_code(self):
        """Test formatting Rust code."""
        unformatted = '''fn main( ) { let x = 1 ; println ! ( "{}" , x ) ; }'''
        formatted, success = self.formatter._format_rust(unformatted)

        # Should return code (may or may not be formatted depending on rustfmt availability)
        self.assertIsInstance(formatted, str)
        self.assertGreater(len(formatted), 0)

    def test_format_rust_preserves_logic(self):
        """Test formatting preserves Rust code logic."""
        code = '''fn add(a: i32, b: i32) -> i32 {
    a + b
}
'''
        formatted, success = self.formatter._format_rust(code)

        # Should contain original logic
        self.assertIn('fn add', formatted)
        self.assertIn('a', formatted)
        self.assertIn('b', formatted)


class TestFormatCodeFunction(unittest.TestCase):
    """Test convenience format_code function."""

    def test_format_code_python(self):
        """Test format_code with Python."""
        code = 'def test( ): pass'
        formatted, success = format_code(code, '.py')

        self.assertIsInstance(formatted, str)

    def test_format_code_typescript(self):
        """Test format_code with TypeScript."""
        code = 'const x:number=1;'
        formatted, success = format_code(code, '.ts')

        self.assertIsInstance(formatted, str)

    def test_format_code_rust(self):
        """Test format_code with Rust."""
        code = 'fn main() { }'
        formatted, success = format_code(code, '.rs')

        self.assertIsInstance(formatted, str)

    def test_format_code_unknown_extension(self):
        """Test format_code with unknown extension."""
        code = 'some code'
        formatted, success = format_code(code, '.xyz')

        # Should return original code unchanged
        self.assertEqual(formatted, code)
        self.assertTrue(success)  # Unknown extensions pass by default


class TestFormattingIntegration(unittest.TestCase):
    """Test formatting integration with file writer."""

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = CodeFormatter()

    def test_format_before_write_python(self):
        """Test formatting Python code before writing."""
        unformatted = '''def hello( ):
    x=1
    return x
'''
        formatted, success = self.formatter.format_code(unformatted, '.py')

        self.assertIsInstance(formatted, str)
        self.assertGreater(len(formatted), 0)

    def test_format_before_write_typescript(self):
        """Test formatting TypeScript code before writing."""
        unformatted = '''function test( ):number{return 1;}'''
        formatted, success = self.formatter.format_code(unformatted, '.ts')

        self.assertIsInstance(formatted, str)
        self.assertIn('function', formatted)

    def test_format_before_write_rust(self):
        """Test formatting Rust code before writing."""
        unformatted = '''fn test( )->i32{return 1;}'''
        formatted, success = self.formatter.format_code(unformatted, '.rs')

        self.assertIsInstance(formatted, str)
        self.assertIn('fn', formatted)


class TestFormatterEdgeCases(unittest.TestCase):
    """Test formatter edge cases."""

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = CodeFormatter()

    def test_format_empty_code(self):
        """Test formatting empty code."""
        formatted, success = self.formatter.format_code('', '.py')

        self.assertEqual(formatted, '')
        self.assertTrue(success)

    def test_format_whitespace_only(self):
        """Test formatting whitespace-only code."""
        code = '   \n\n   '
        formatted, success = self.formatter.format_code(code, '.py')

        self.assertIsInstance(formatted, str)

    def test_format_very_long_code(self):
        """Test formatting long code."""
        code = 'def f():\n    pass\n' * 100
        formatted, success = self.formatter.format_code(code, '.py')

        self.assertIsInstance(formatted, str)
        self.assertGreater(len(formatted), 0)

    def test_format_unicode_code(self):
        """Test formatting code with unicode."""
        code = '''def hello():
    print("你好世界")
'''
        formatted, success = self.formatter.format_code(code, '.py')

        self.assertIsInstance(formatted, str)
        self.assertIn('你好', formatted)


if __name__ == '__main__':
    unittest.main(verbosity=2)

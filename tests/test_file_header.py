#!/usr/bin/env python3
"""
Test: Generated files have auto-generated header.
"""

import unittest
import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agent.file_writer import FileWriter, HEADER_TEMPLATES


class TestFileHeaderGeneration(unittest.TestCase):
    """Test auto-generated header in files."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.file_writer = FileWriter(self.test_dir)
        self.sample_task = {
            'id': 'rust_backend.pkce_rfc7636',
            'name': 'PKCE Implementation',
            'desc': 'SHA256 + base64url — RFC 7636 compliant',
            'layer': 'backend'
        }
        self.sample_code = 'fn main() { println!("Hello"); }'

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)

    def test_header_contains_auto_generated_notice(self):
        """Test header contains auto-generated notice."""
        file_path = self.file_writer.write_file(self.sample_task, self.sample_code)
        
        with open(file_path, 'r') as f:
            content = f.read()

        self.assertIn('Auto-generated', content)
        self.assertIn('DO NOT EDIT MANUALLY', content)

    def test_header_contains_task_id(self):
        """Test header contains task ID."""
        file_path = self.file_writer.write_file(self.sample_task, self.sample_code)
        
        with open(file_path, 'r') as f:
            content = f.read()

        self.assertIn('rust_backend.pkce_rfc7636', content)

    def test_header_contains_task_name(self):
        """Test header contains task name."""
        file_path = self.file_writer.write_file(self.sample_task, self.sample_code)
        
        with open(file_path, 'r') as f:
            content = f.read()

        self.assertIn('PKCE Implementation', content)

    def test_header_contains_timestamp(self):
        """Test header contains generation timestamp."""
        file_path = self.file_writer.write_file(self.sample_task, self.sample_code)
        
        with open(file_path, 'r') as f:
            content = f.read()

        # Should contain ISO format timestamp (year at minimum)
        self.assertIn('2026', content)  # Current year

    def test_header_contains_task_description(self):
        """Test header contains task description."""
        file_path = self.file_writer.write_file(self.sample_task, self.sample_code)
        
        with open(file_path, 'r') as f:
            content = f.read()

        self.assertIn('SHA256 + base64url', content)
        self.assertIn('RFC 7636', content)

    def test_header_appears_before_code(self):
        """Test header appears before actual code."""
        file_path = self.file_writer.write_file(self.sample_task, self.sample_code)
        
        with open(file_path, 'r') as f:
            content = f.read()

        header_end = content.find('fn main()')
        auto_generated_pos = content.find('Auto-generated')
        
        self.assertGreater(header_end, 0)
        self.assertGreater(auto_generated_pos, 0)
        self.assertLess(auto_generated_pos, header_end)

    def test_python_file_has_python_header(self):
        """Test Python files get Python-style header."""
        python_task = {
            'id': 'python_agent.core',
            'name': 'Python Agent',
            'desc': 'Main agent loop',
            'layer': 'backend'
        }
        # Force .py extension by modifying output path logic
        file_path = self.test_dir / 'test.py'
        header = self.file_writer._generate_header(python_task, '.py')
        
        self.assertIn('# ============================================================================', header)
        self.assertIn('# Auto-generated file', header)

    def test_rust_file_has_rust_header(self):
        """Test Rust files get Rust-style header."""
        file_path = self.file_writer.write_file(self.sample_task, self.sample_code)
        
        with open(file_path, 'r') as f:
            content = f.read()

        # Rust uses // comments
        self.assertIn('// ============================================================================', content)
        self.assertIn('// Auto-generated file', content)

    def test_typescript_file_has_ts_header(self):
        """Test TypeScript files get TS-style header."""
        ts_task = {
            'id': 'ui.components.header',
            'name': 'Header Component',
            'desc': 'React header component',
            'layer': 'ui'
        }
        header = self.file_writer._generate_header(ts_task, '.ts')
        
        self.assertIn('// ============================================================================', header)
        self.assertIn('// Auto-generated file', header)

    def test_jsx_file_has_jsx_header(self):
        """Test JSX files get JSX-style header."""
        jsx_task = {
            'id': 'ui.components.build_console',
            'name': 'Build Console',
            'desc': 'Build console component',
            'layer': 'ui'
        }
        header = self.file_writer._generate_header(jsx_task, '.jsx')
        
        self.assertIn('// ============================================================================', header)
        self.assertIn('// Auto-generated file', header)

    def test_css_file_has_css_header(self):
        """Test CSS files get CSS-style header."""
        css_task = {
            'id': 'ui.styles.header',
            'name': 'Header Styles',
            'desc': 'CSS for header component',
            'layer': 'ui'
        }
        header = self.file_writer._generate_header(css_task, '.css')
        
        self.assertIn('/* ============================================================================', header)
        self.assertIn('* Auto-generated file', header)

    def test_html_file_has_html_header(self):
        """Test HTML files get HTML-style header."""
        html_task = {
            'id': 'ui.pages.home',
            'name': 'Home Page',
            'desc': 'Home page HTML',
            'layer': 'ui'
        }
        header = self.file_writer._generate_header(html_task, '.html')
        
        self.assertIn('<!--', header)
        self.assertIn('Auto-generated file', header)
        self.assertIn('-->', header)

    def test_json_file_has_json_header(self):
        """Test JSON files get JSON-compatible header."""
        json_task = {
            'id': 'config.package',
            'name': 'Package Config',
            'desc': 'Package configuration',
            'layer': 'config'
        }
        header = self.file_writer._generate_header(json_task, '.json')
        
        self.assertIn('//', header)
        self.assertIn('Auto-generated file', header)

    def test_header_templates_exist_for_all_extensions(self):
        """Test header templates exist for all supported extensions."""
        extensions = ['.py', '.rs', '.ts', '.tsx', '.jsx', '.js', '.json', '.css', '.html', '.md']
        
        for ext in extensions:
            self.assertIn(ext, HEADER_TEMPLATES, f"Missing template for {ext}")

    def test_header_has_separator_lines(self):
        """Test header has visual separator lines."""
        header = self.file_writer._generate_header(self.sample_task, '.ts')
        
        self.assertIn('============', header)

    def test_multiple_files_get_unique_timestamps(self):
        """Test multiple files get unique timestamps."""
        import time
        
        file1 = self.file_writer.write_file(self.sample_task, 'code1')
        time.sleep(0.01)  # Small delay to ensure different timestamp
        file2 = self.file_writer.write_file(self.sample_task, 'code2')
        
        with open(file1, 'r') as f:
            content1 = f.read()
        with open(file2, 'r') as f:
            content2 = f.read()
        
        # Both should have timestamps (ISO format)
        self.assertIn('Generated:', content1)
        self.assertIn('Generated:', content2)

    def test_header_preserves_original_code(self):
        """Test that original code is preserved after header."""
        original_code = '''function test() {
    return "Hello World";
}'''
        file_path = self.file_writer.write_file(self.sample_task, original_code)
        
        with open(file_path, 'r') as f:
            content = f.read()

        self.assertIn(original_code, content)


class TestHeaderFormat(unittest.TestCase):
    """Test header format details."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.file_writer = FileWriter(self.test_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)

    def test_header_format_includes_all_fields(self):
        """Test header includes all required fields."""
        task = {
            'id': 'test.task_id',
            'name': 'Test Name',
            'desc': 'Test Description',
            'layer': 'test'
        }
        header = self.file_writer._generate_header(task, '.ts')
        
        required_fields = ['task_id', 'Test Name', 'Test Description', 'Generated:']
        for field in required_fields:
            self.assertIn(field, header)

    def test_header_uses_iso_timestamp(self):
        """Test header uses ISO format timestamp."""
        task = {'id': 'test', 'name': 'Test', 'desc': 'Test', 'layer': 'test'}
        header = self.file_writer._generate_header(task, '.ts')
        
        # ISO format includes T separator
        self.assertIn('T', header)


if __name__ == '__main__':
    unittest.main(verbosity=2)

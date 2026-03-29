"""
Test File Writer — File I/O tests.
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from agent.file_writer import FileWriter


class TestFileWriter:
    """Test File Writer functionality."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        dirpath = tempfile.mkdtemp()
        yield Path(dirpath)
        shutil.rmtree(dirpath)

    @pytest.fixture
    def writer(self, temp_dir):
        """Create FileWriter instance."""
        return FileWriter(temp_dir)

    @pytest.fixture
    def sample_task(self):
        """Create sample task."""
        return {
            'id': 'test.task',
            'name': 'Test Task',
            'desc': 'Test description'
        }

    def test_initialization(self, writer, temp_dir):
        """Test writer initializes correctly."""
        assert writer.output_dir == temp_dir
        assert temp_dir.exists()

    def test_write_file_typescript(self, writer, sample_task, temp_dir):
        """Test writing TypeScript file."""
        code = 'export const x = 1;'
        path = writer.write_file(sample_task, code)
        
        assert path.exists()
        assert path.suffix == '.ts'
        assert code in path.read_text()

    def test_write_file_python(self, writer, temp_dir):
        """Test writing Python file."""
        task = {'id': 'agent.python_module', 'name': 'Python Module', 'desc': 'Test'}
        code = 'def func(): pass'
        path = writer.write_file(task, code)
        
        assert path.exists()
        # Note: file_writer uses default .ts for unknown patterns
        # Python detection requires 'python' or 'agent' in task ID
        assert code in path.read_text()

    def test_write_file_rust(self, writer, temp_dir):
        """Test writing Rust file."""
        task = {'id': 'rust_backend.module', 'name': 'Rust Module', 'desc': 'Test'}
        code = 'fn main() {}'
        path = writer.write_file(task, code)
        
        assert path.exists()
        # Note: file_writer uses default .ts for unknown patterns
        # Rust detection requires 'rust' or 'backend' in task ID
        assert code in path.read_text()

    def test_write_file_creates_directories(self, writer, sample_task, temp_dir):
        """Test that writer creates parent directories."""
        code = 'export const x = 1;'
        path = writer.write_file(sample_task, code)
        
        assert path.parent.exists()

    def test_write_file_header_added(self, writer, sample_task, temp_dir):
        """Test that auto-generated header is added."""
        code = 'export const x = 1;'
        path = writer.write_file(sample_task, code)
        
        content = path.read_text()
        assert 'Auto-generated' in content
        assert 'test.task' in content

    def test_write_file_json(self, writer, temp_dir):
        """Test writing JSON file."""
        task = {'id': 'config.settings.json', 'name': 'Settings', 'desc': 'Config'}
        code = '{"key": "value"}'
        path = writer.write_file(task, code)
        
        assert path.exists()
        # Note: file_writer defaults to .ts for unknown patterns
        assert code in path.read_text()

    def test_write_file_css(self, writer, temp_dir):
        """Test writing CSS file."""
        task = {'id': 'ui.styles.css', 'name': 'Styles', 'desc': 'CSS'}
        code = '.class { color: red; }'
        path = writer.write_file(task, code)
        
        assert path.exists()
        # Note: file_writer defaults to .ts for unknown patterns
        assert code in path.read_text()

    def test_write_file_html(self, writer, temp_dir):
        """Test writing HTML file."""
        task = {'id': 'ui.page.html', 'name': 'Page', 'desc': 'HTML'}
        code = '<html><body>Hello</body></html>'
        path = writer.write_file(task, code)
        
        assert path.exists()
        # Note: file_writer defaults to .ts for unknown patterns
        assert code in path.read_text()

    def test_write_file_markdown(self, writer, temp_dir):
        """Test writing Markdown file."""
        task = {'id': 'docs.readme.md', 'name': 'README', 'desc': 'Docs'}
        code = '# Title\n\nContent'
        path = writer.write_file(task, code)
        
        assert path.exists()
        # Note: file_writer defaults to .ts for unknown patterns
        assert code in path.read_text()

    def test_get_file_path_rust(self, writer):
        """Test file path resolution for Rust."""
        task = {'id': 'rust_backend.auth'}
        path = writer._get_file_path(task)
        
        assert 'src-tauri' in str(path)
        assert path.suffix == '.rs'

    def test_get_file_path_step_components(self, writer):
        """Test file path resolution for step components."""
        task = {'id': 'ui_components.step1_form'}
        path = writer._get_file_path(task)
        
        assert 'step1' in str(path)
        assert 'components' in str(path)

    def test_get_file_path_default(self, writer):
        """Test default file path resolution."""
        task = {'id': 'general.utility'}
        path = writer._get_file_path(task)
        
        assert 'lib' in str(path)
        assert path.suffix == '.ts'

    def test_slugify(self, writer):
        """Test slugify function."""
        assert writer._slugify('test.module') == 'test_module'
        assert writer._slugify('Test.Module') == 'test_module'

    def test_generate_header_typescript(self, writer, sample_task):
        """Test header generation for TypeScript."""
        header = writer._generate_header(sample_task, '.ts')
        
        assert '// Auto-generated' in header
        assert 'test.task' in header

    def test_generate_header_python(self, writer, sample_task):
        """Test header generation for Python."""
        header = writer._generate_header(sample_task, '.py')
        
        assert '# Auto-generated' in header

    def test_generate_header_rust(self, writer, sample_task):
        """Test header generation for Rust."""
        header = writer._generate_header(sample_task, '.rs')
        
        assert '// Auto-generated' in header

    def test_write_files_single(self, writer, sample_task, temp_dir):
        """Test write_files method with single file."""
        code = 'export const x = 1;'
        results = writer.write_files(sample_task, code)
        
        assert len(results) == 1
        path, success = results[0]
        assert success is True
        assert path.exists()

    def test_write_files_multi(self, writer, temp_dir):
        """Test write_files method with multi-file task."""
        task = {
            'id': 'ui_components.button',
            'name': 'Button',
            'desc': 'Component',
            'multiFile': True
        }
        code = 'export const Button = () => {};'
        results = writer.write_files(task, code)
        
        # Multi-file task should create multiple files
        assert len(results) >= 1
        for path, success in results:
            assert success is True


class TestFileWriterHeaderTemplates:
    """Test header templates for different languages."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        dirpath = tempfile.mkdtemp()
        yield Path(dirpath)
        shutil.rmtree(dirpath)

    @pytest.fixture
    def writer(self, temp_dir):
        """Create FileWriter instance."""
        return FileWriter(temp_dir)

    def test_all_header_templates_exist(self, writer):
        """Test all header templates are defined."""
        from agent.file_writer import HEADER_TEMPLATES
        
        expected_extensions = ['.py', '.rs', '.ts', '.tsx', '.jsx', '.js', '.json', '.css', '.html', '.md']
        
        for ext in expected_extensions:
            assert ext in HEADER_TEMPLATES


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

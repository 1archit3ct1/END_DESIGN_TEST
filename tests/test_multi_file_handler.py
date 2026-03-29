"""
Test Multi-File Handler — Multi-file task support tests.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import json

from agent.multi_file_handler import MultiFileHandler, FileSpec
from agent.file_writer import FileWriter


class TestMultiFileHandler:
    """Test multi-file task support."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        dirpath = tempfile.mkdtemp()
        yield Path(dirpath)
        shutil.rmtree(dirpath)

    @pytest.fixture
    def handler(self, temp_dir):
        """Create multi-file handler instance."""
        return MultiFileHandler(temp_dir)

    @pytest.fixture
    def file_writer(self, temp_dir):
        """Create file writer instance."""
        return FileWriter(temp_dir)

    def test_detect_multi_file_task_explicit_flag(self, handler):
        """Test detection of multi-file task via explicit flag."""
        task = {'id': 'test.task', 'multiFile': True}
        assert handler.detect_multi_file_task(task) is True

    def test_detect_multi_file_task_files_array(self, handler):
        """Test detection of multi-file task via files array."""
        task = {
            'id': 'test.task',
            'files': ['file1.ts', 'file2.ts', 'file3.ts']
        }
        assert handler.detect_multi_file_task(task) is True

    def test_detect_multi_file_task_component_pattern(self, handler):
        """Test detection of component pattern multi-file task."""
        task = {'id': 'ui_components.oauth_button'}
        assert handler.detect_multi_file_task(task) is True

    def test_detect_multi_file_task_rust_backend_pattern(self, handler):
        """Test detection of rust_backend pattern multi-file task."""
        task = {'id': 'rust_backend.pkce_rfc7636'}
        assert handler.detect_multi_file_task(task) is True

    def test_detect_multi_file_task_api_pattern(self, handler):
        """Test detection of api pattern multi-file task."""
        task = {'id': 'api.user_endpoint'}
        assert handler.detect_multi_file_task(task) is True

    def test_detect_multi_file_task_hook_pattern(self, handler):
        """Test detection of hook pattern multi-file task."""
        task = {'id': 'hooks.use_auth'}
        assert handler.detect_multi_file_task(task) is True

    def test_detect_single_file_task(self, handler):
        """Test that regular tasks are not detected as multi-file."""
        task = {'id': 'general.utility_function'}
        assert handler.detect_multi_file_task(task) is False

    def test_get_file_specs_from_files_array(self, handler):
        """Test building file specs from explicit files array."""
        task = {
            'id': 'test.task',
            'files': [
                {'path': 'src/main.ts', 'description': 'Main file', 'primary': True},
                {'path': 'src/types.ts', 'description': 'Types'},
                {'path': 'tests/main.test.ts', 'description': 'Tests'}
            ]
        }
        code = "// Generated code"
        specs = handler.get_file_specs(task, code)
        
        assert len(specs) == 3
        assert specs[0].path == 'src/main.ts'
        assert specs[0].is_primary is True
        assert specs[0].description == 'Main file'
        assert specs[1].path == 'src/types.ts'
        assert specs[1].is_primary is False

    def test_get_file_specs_from_embedded_markers(self, handler):
        """Test parsing embedded file markers from code."""
        task = {'id': 'test.task'}
        code = """// FILE: src/main.ts
export const main = () => {};

// FILE: src/types.ts
export type MyType = string;

// FILE: tests/main.test.ts
import { main } from '../src/main';
"""
        specs = handler.get_file_specs(task, code)
        
        assert len(specs) == 3
        assert specs[0].path == 'src/main.ts'
        assert 'export const main' in specs[0].code
        assert specs[1].path == 'src/types.ts'
        assert 'export type MyType' in specs[1].code

    def test_get_file_specs_default_multi_file(self, handler):
        """Test default multi-file structure generation."""
        task = {'id': 'ui_components.button'}
        code = "// Button component code"
        specs = handler.get_file_specs(task, code)
        
        # Should generate component, test, and styles files
        assert len(specs) == 3
        assert any(spec.path.endswith('.tsx') for spec in specs)
        assert any(spec.path.endswith('.test.tsx') for spec in specs)
        assert any(spec.path.endswith('.styles.css') for spec in specs)

    def test_generate_stub_test_file(self, handler):
        """Test stub generation for test files."""
        task = {'id': 'test.task', 'name': 'Test Task'}
        stub = handler._generate_stub(task, 'tests/test_task.test.ts')
        
        assert 'import { describe, it, expect }' in stub
        assert 'vitest' in stub
        assert 'Test Task' in stub

    def test_generate_stub_styles_file(self, handler):
        """Test stub generation for CSS files."""
        task = {'id': 'test.task'}
        stub = handler._generate_stub(task, 'src/component.styles.css')
        
        assert '/* Styles for test.task */' in stub

    def test_generate_stub_types_file(self, handler):
        """Test stub generation for TypeScript type files."""
        task = {'id': 'test.task'}
        stub = handler._generate_stub(task, 'src/user.types.ts')

        assert '// Type definitions for test.task' in stub
        assert 'interface' in stub

    def test_generate_stub_rust_tests_file(self, handler):
        """Test stub generation for Rust test files."""
        task = {'id': 'rust_backend.test'}
        stub = handler._generate_stub(task, 'src-tauri/tests/test_tests.rs')
        
        assert '#[cfg(test)]' in stub
        assert 'mod tests' in stub

    def test_write_multi_files_component(self, handler, file_writer, temp_dir):
        """Test writing multiple files for component task."""
        task = {'id': 'ui_components.oauth_button', 'name': 'OAuth Button'}
        code = "// OAuth Button component"
        
        results = handler.write_multi_files(task, code, file_writer)
        
        # Should write 3 files: component, test, styles
        assert len(results) == 3
        
        # Check all files were created
        for path, success in results:
            assert success is True
            assert path.exists()
        
        # Verify primary file has content
        primary_path = temp_dir / "src" / "components" / "ui_components_oauth_button.tsx"
        assert primary_path.exists()
        content = primary_path.read_text()
        assert "OAuth Button component" in content

    def test_write_multi_files_rust_backend(self, handler, file_writer, temp_dir):
        """Test writing multiple files for rust_backend task."""
        task = {'id': 'rust_backend.auth_module', 'name': 'Auth Module'}
        code = "// Rust auth module"
        
        results = handler.write_multi_files(task, code, file_writer)
        
        # Should write 2 files: module and tests
        assert len(results) == 2
        
        for path, success in results:
            assert success is True
            assert path.exists()

    def test_write_files_method_single_file(self, file_writer, temp_dir):
        """Test write_files method with single file task."""
        task = {'id': 'general.utility'}
        code = "// Utility function"
        
        results = file_writer.write_files(task, code)
        
        assert len(results) == 1
        path, success = results[0]
        assert success is True
        assert path.exists()

    def test_write_files_method_multi_file(self, file_writer, temp_dir):
        """Test write_files method with multi-file task."""
        task = {
            'id': 'api.user_api',
            'name': 'User API',
            'files': [
                {'path': 'src/api/user.ts', 'primary': True},
                {'path': 'src/api/user.types.ts', 'primary': False}
            ]
        }
        code = "// User API code"
        
        results = file_writer.write_files(task, code)
        
        # Should write multiple files
        assert len(results) >= 2
        
        for path, success in results:
            assert success is True
            assert path.exists()

    def test_file_specs_with_empty_files_array(self, handler):
        """Test handling of empty files array."""
        task = {'id': 'test.task', 'files': []}
        code = "// Code"
        specs = handler.get_file_specs(task, code)
        
        # Should fall back to default behavior
        assert len(specs) >= 1

    def test_file_specs_with_string_files_array(self, handler):
        """Test handling of files array with string entries."""
        task = {
            'id': 'test.task',
            'files': ['file1.ts', 'file2.ts']
        }
        code = "// Code"
        specs = handler.get_file_specs(task, code)
        
        assert len(specs) == 2
        assert specs[0].path == 'file1.ts'
        assert specs[0].is_primary is True
        assert specs[1].path == 'file2.ts'
        assert specs[1].is_primary is False

    def test_embedded_file_markers_with_triple_slash(self, handler):
        """Test parsing /// FILE: markers."""
        task = {'id': 'test.task'}
        code = """/// FILE: src/index.ts
export const index = 1;

/// FILE: src/utils.ts
export const util = 2;
"""
        specs = handler.get_file_specs(task, code)
        
        assert len(specs) == 2
        assert specs[0].path == 'src/index.ts'
        assert 'export const index' in specs[0].code

    def test_embedded_file_markers_with_double_slash(self, handler):
        """Test parsing // FILE: markers."""
        task = {'id': 'test.task'}
        code = """// FILE: src/main.py
def main(): pass

// FILE: src/helper.py
def helper(): pass
"""
        specs = handler.get_file_specs(task, code)
        
        assert len(specs) == 2
        assert specs[0].path == 'src/main.py'

    def test_embedded_file_markers_with_hash(self, handler):
        """Test parsing # FILE: markers."""
        task = {'id': 'test.task'}
        code = """# FILE: src/script.py
print('hello')

# FILE: tests/test_script.py
def test_script(): pass
"""
        specs = handler.get_file_specs(task, code)
        
        assert len(specs) == 2
        assert specs[0].path == 'src/script.py'

    def test_multi_file_task_state_tracking(self, temp_dir):
        """Test that multi-file tasks track all generated files."""
        from agent.state_manager import StateManager
        
        # Create a test task_status.json
        task_status = {
            'version': '1.0',
            'tasks': [
                {
                    'id': 'ui_components.button',
                    'name': 'Button Component',
                    'status': 'pending',
                    'multiFile': True
                }
            ]
        }
        
        status_path = temp_dir / 'task_status.json'
        with open(status_path, 'w') as f:
            json.dump(task_status, f)
        
        state_manager = StateManager(status_path)
        
        # Mark task done with multiple files
        file_paths = [
            'src/components/button.tsx',
            'src/components/button.test.tsx',
            'src/components/button.styles.css'
        ]
        
        result = state_manager.mark_task_done(
            'ui_components.button',
            file_paths=file_paths,
            test_passed=True
        )
        
        assert result is True
        
        # Verify state was saved
        tasks = state_manager.load_tasks()
        task = next(t for t in tasks if t['id'] == 'ui_components.button')
        
        assert task['status'] == 'done'
        assert 'generatedFiles' in task
        assert len(task['generatedFiles']) == 3
        assert task['testPassed'] is True


class TestFileSpecDataclass:
    """Test FileSpec dataclass."""

    def test_file_spec_defaults(self):
        """Test FileSpec default values."""
        spec = FileSpec(path='test.ts', code='export const x = 1;')
        
        assert spec.path == 'test.ts'
        assert spec.code == 'export const x = 1;'
        assert spec.description == ''
        assert spec.is_primary is False

    def test_file_spec_with_all_fields(self):
        """Test FileSpec with all fields set."""
        spec = FileSpec(
            path='src/main.ts',
            code='export const main = 1;',
            description='Main entry point',
            is_primary=True
        )
        
        assert spec.path == 'src/main.ts'
        assert spec.code == 'export const main = 1;'
        assert spec.description == 'Main entry point'
        assert spec.is_primary is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

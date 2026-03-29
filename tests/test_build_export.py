"""
Tests for build_export.py — Partial build export functionality.
"""

import pytest
import tempfile
import json
import zipfile
import shutil
from pathlib import Path
import sys

# Add agent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.build_export import BuildExporter, export_build
from agent.state_manager import StateManager


class TestBuildExporter:
    """Test BuildExporter class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.temp_dir) / 'output'
        self.output_dir.mkdir()
        self.export_dir = Path(self.temp_dir) / 'exports'
        self.export_dir.mkdir()

        # Create some test files in output directory
        (self.output_dir / 'src').mkdir()
        (self.output_dir / 'src' / 'test.py').write_text('# Test file')
        (self.output_dir / 'package.json').write_text('{"name": "test"}')

    def teardown_method(self):
        """Clean up test fixtures."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def _create_state_manager(self) -> StateManager:
        """Create a StateManager with test tasks."""
        task_status_path = Path(self.temp_dir) / 'task_status.json'
        tasks = [
            {'id': 'task1', 'name': 'Task 1', 'status': 'done', 'generatedFile': 'file1.py'},
            {'id': 'task2', 'name': 'Task 2', 'status': 'failed', 'generatedFile': None},
            {'id': 'task3', 'name': 'Task 3', 'status': 'pending', 'generatedFile': None},
        ]
        data = {
            'version': '1.0',
            'meta': {'loopActive': True, 'completedAt': None},
            'tasks': tasks
        }
        with open(task_status_path, 'w') as f:
            json.dump(data, f)
        return StateManager(task_status_path)

    def test_exporter_initializes(self):
        """Test BuildExporter initializes correctly."""
        exporter = BuildExporter(self.output_dir)

        assert exporter.output_dir == self.output_dir
        assert exporter.export_dir.exists()

    def test_export_as_zip(self):
        """Test exporting build as ZIP file."""
        exporter = BuildExporter(self.output_dir)
        exporter.export_dir = self.export_dir

        zip_path = exporter._export_as_zip('test_export', True, None)

        assert zip_path is not None
        assert zip_path.exists()
        assert zip_path.suffix == '.zip'

        # Verify ZIP contents
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            assert any('test.py' in name for name in names)
            assert any('package.json' in name for name in names)

    def test_export_as_directory(self):
        """Test exporting build as directory."""
        exporter = BuildExporter(self.output_dir)
        exporter.export_dir = self.export_dir

        dir_path = exporter._export_as_directory('test_export_dir', True, None)

        assert dir_path is not None
        assert dir_path.exists()
        assert dir_path.is_dir()

        # Verify directory contents
        assert (dir_path / 'src' / 'test.py').exists()
        assert (dir_path / 'package.json').exists()

    def test_export_with_manifest(self):
        """Test exporting build with manifest."""
        exporter = BuildExporter(self.output_dir)
        exporter.export_dir = self.export_dir
        state_manager = self._create_state_manager()

        zip_path = exporter._export_as_zip('test_with_manifest', True, state_manager)

        assert zip_path is not None

        # Verify manifest in ZIP
        with zipfile.ZipFile(zip_path, 'r') as zf:
            assert 'manifest.json' in zf.namelist()

            with zf.open('manifest.json') as mf:
                manifest = json.loads(mf.read())
                assert 'version' in manifest
                assert 'statistics' in manifest
                assert 'tasks' in manifest

    def test_create_build_manifest(self):
        """Test creating build manifest."""
        exporter = BuildExporter(self.output_dir)
        state_manager = self._create_state_manager()

        manifest = exporter._create_build_manifest(state_manager, include_incomplete=True)

        assert manifest['version'] == '1.0'
        assert 'exported_at' in manifest
        assert 'statistics' in manifest
        assert manifest['statistics']['total_tasks'] == 3
        assert manifest['statistics']['completed'] == 1
        assert manifest['statistics']['failed'] == 1
        assert manifest['statistics']['pending'] == 1

    def test_create_build_manifest_exclude_incomplete(self):
        """Test creating manifest excluding incomplete tasks."""
        exporter = BuildExporter(self.output_dir)
        state_manager = self._create_state_manager()

        manifest = exporter._create_build_manifest(state_manager, include_incomplete=False)

        # Should only include completed tasks
        assert len(manifest['tasks']) == 1
        assert manifest['tasks'][0]['id'] == 'task1'

    def test_create_export_readme(self):
        """Test creating export README."""
        exporter = BuildExporter(self.output_dir)
        state_manager = self._create_state_manager()

        readme = exporter._create_export_readme(state_manager, files_added=5)

        assert '# Build Export' in readme
        assert 'Total Tasks' in readme
        assert 'Completion Rate' in readme
        assert '5' in readme  # files_added

    def test_export_partial_build(self):
        """Test partial build export convenience method."""
        exporter = BuildExporter(self.output_dir)
        exporter.export_dir = self.export_dir
        state_manager = self._create_state_manager()

        zip_path = exporter.export_partial_build(state_manager)

        assert zip_path is not None
        assert zip_path.exists()

    def test_get_export_history(self):
        """Test getting export history."""
        exporter = BuildExporter(self.output_dir)
        exporter.export_dir = self.export_dir

        # Create some exports
        exporter._export_as_zip('build_export_test1', True, None)
        exporter._export_as_zip('build_export_test2', True, None)

        history = exporter.get_export_history()

        assert len(history) >= 2
        assert all('filename' in h for h in history)
        assert all('path' in h for h in history)
        assert all('size' in h for h in history)

    def test_cleanup_old_exports(self):
        """Test cleaning up old exports."""
        exporter = BuildExporter(self.output_dir)
        exporter.export_dir = self.export_dir

        # Create an export
        exporter._export_as_zip('build_export_test', True, None)

        # Cleanup with 0 days keep (should delete everything)
        deleted = exporter.cleanup_old_exports(keep_days=0)

        assert deleted >= 1

    def test_export_nonexistent_output_dir(self):
        """Test exporting with nonexistent output directory."""
        nonexistent_dir = Path(self.temp_dir) / 'nonexistent'
        exporter = BuildExporter(nonexistent_dir)

        result = exporter.export_build(export_format='zip')

        assert result is None

    def test_export_unknown_format(self):
        """Test exporting with unknown format."""
        exporter = BuildExporter(self.output_dir)
        exporter.export_dir = self.export_dir

        result = exporter.export_build(export_format='unknown')

        assert result is None


class TestExportBuildConvenience:
    """Test export_build convenience function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.temp_dir) / 'output'
        self.output_dir.mkdir()
        (self.output_dir / 'test.txt').write_text('test')

    def teardown_method(self):
        """Clean up test fixtures."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_export_build_function(self):
        """Test export_build convenience function."""
        result = export_build(self.output_dir, export_format='zip')

        assert result is not None
        assert result.exists()
        assert result.suffix == '.zip'


class TestPartialBuildExport:
    """Test partial build export scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.temp_dir) / 'output'
        self.output_dir.mkdir()
        self.export_dir = Path(self.temp_dir) / 'exports'
        self.export_dir.mkdir()

        # Create partial build output
        (self.output_dir / 'src').mkdir()
        (self.output_dir / 'src' / 'completed.py').write_text('# Completed')
        # Some files missing (partial build)

    def teardown_method(self):
        """Clean up test fixtures."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_export_partial_build_with_failures(self):
        """Test exporting partial build with failed tasks."""
        exporter = BuildExporter(self.output_dir)
        exporter.export_dir = self.export_dir

        # Create state manager with failures
        task_status_path = Path(self.temp_dir) / 'task_status.json'
        tasks = [
            {'id': 'task1', 'name': 'Task 1', 'status': 'done'},
            {'id': 'task2', 'name': 'Task 2', 'status': 'failed'},
            {'id': 'task3', 'name': 'Task 3', 'status': 'blocked'},
        ]
        data = {
            'version': '1.0',
            'meta': {'loopActive': False, 'completedAt': None},
            'tasks': tasks
        }
        with open(task_status_path, 'w') as f:
            json.dump(data, f)
        state_manager = StateManager(task_status_path)

        zip_path = exporter.export_partial_build(state_manager)

        assert zip_path is not None
        assert zip_path.exists()

        # Verify manifest indicates partial build
        with zipfile.ZipFile(zip_path, 'r') as zf:
            with zf.open('manifest.json') as mf:
                manifest = json.loads(mf.read())
                assert manifest['build_status'] == 'partial'
                assert manifest['statistics']['failed'] == 2

    def test_export_readme_indicates_partial_build(self):
        """Test that README indicates partial build status."""
        exporter = BuildExporter(self.output_dir)
        exporter.export_dir = self.export_dir

        task_status_path = Path(self.temp_dir) / 'task_status.json'
        tasks = [
            {'id': 'task1', 'name': 'Task 1', 'status': 'done'},
            {'id': 'task2', 'name': 'Task 2', 'status': 'failed'},
        ]
        data = {
            'version': '1.0',
            'meta': {'loopActive': False, 'completedAt': None},
            'tasks': tasks
        }
        with open(task_status_path, 'w') as f:
            json.dump(data, f)
        state_manager = StateManager(task_status_path)

        readme = exporter._create_export_readme(state_manager)

        assert 'Partial' in readme
        assert 'Some tasks may not have completed successfully' in readme

    def test_export_includes_all_generated_files(self):
        """Test that export includes all generated files even with failures."""
        exporter = BuildExporter(self.output_dir)
        exporter.export_dir = self.export_dir

        zip_path = exporter.export_build(export_format='zip', include_incomplete=True)

        assert zip_path is not None

        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            # Should include all files regardless of task status
            assert any('completed.py' in name for name in names)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

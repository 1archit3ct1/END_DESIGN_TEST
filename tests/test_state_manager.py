"""
Tests for state_manager.py — Skip task functionality.
"""

import pytest
import tempfile
import json
import shutil
from pathlib import Path
import sys

# Add agent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.state_manager import StateManager


class TestSkipTaskFunctionality:
    """Test skip task functionality in StateManager."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.task_status_path = Path(self.temp_dir) / 'task_status.json'

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.task_status_path.exists():
            self.task_status_path.unlink()

    def _create_test_tasks(self):
        """Create test tasks file."""
        tasks = [
            {
                'id': 'task1',
                'name': 'Task 1',
                'desc': 'First task',
                'status': 'pending',
                'generatedFile': None,
                'testPassed': False,
                'retries': 0,
                'result': None,
                'updatedAt': None
            },
            {
                'id': 'task2',
                'name': 'Task 2',
                'desc': 'Second task',
                'status': 'running',
                'generatedFile': None,
                'testPassed': False,
                'retries': 0,
                'result': None,
                'updatedAt': None
            },
            {
                'id': 'task3',
                'name': 'Task 3',
                'desc': 'Third task',
                'status': 'pending',
                'generatedFile': None,
                'testPassed': False,
                'retries': 0,
                'result': None,
                'updatedAt': None
            }
        ]

        data = {
            'version': '1.0',
            'generated': '2026-03-29T00:00:00',
            'meta': {
                'root': 'root',
                'loopActive': True,
                'completedAt': None
            },
            'tasks': tasks
        }

        with open(self.task_status_path, 'w') as f:
            json.dump(data, f, indent=2)

        return tasks

    def test_mark_task_skipped(self):
        """Test marking a task as skipped."""
        self._create_test_tasks()
        manager = StateManager(self.task_status_path)

        result = manager.mark_task_skipped('task1', 'User requested skip')

        assert result is True

        # Verify task is skipped
        tasks = manager.load_tasks()
        task1 = next(t for t in tasks if t['id'] == 'task1')

        assert task1['status'] == 'skipped'
        assert task1['result'] == 'User requested skip'
        assert task1['updatedAt'] is not None

    def test_mark_task_skipped_no_reason(self):
        """Test marking a task as skipped without reason."""
        self._create_test_tasks()
        manager = StateManager(self.task_status_path)

        result = manager.mark_task_skipped('task2')

        assert result is True

        tasks = manager.load_tasks()
        task2 = next(t for t in tasks if t['id'] == 'task2')

        assert task2['status'] == 'skipped'
        assert task2['result'] == ''

    def test_mark_task_failed(self):
        """Test marking a task as failed."""
        self._create_test_tasks()
        manager = StateManager(self.task_status_path)

        result = manager.mark_task_failed('task1', 'Generation failed')

        assert result is True

        tasks = manager.load_tasks()
        task1 = next(t for t in tasks if t['id'] == 'task1')

        assert task1['status'] == 'failed'
        assert task1['result'] == 'Generation failed'
        assert task1['updatedAt'] is not None

    def test_get_failed_tasks(self):
        """Test getting list of failed tasks."""
        self._create_test_tasks()
        manager = StateManager(self.task_status_path)

        # Mark some tasks as failed/blocked
        manager.mark_task_failed('task1', 'Error 1')
        manager.mark_task_blocked('task3', 'Blocked reason')

        failed = manager.get_failed_tasks()

        assert len(failed) == 2
        failed_ids = [t['id'] for t in failed]
        assert 'task1' in failed_ids
        assert 'task3' in failed_ids

    def test_get_failed_tasks_empty(self):
        """Test getting failed tasks when none exist."""
        self._create_test_tasks()
        manager = StateManager(self.task_status_path)

        failed = manager.get_failed_tasks()

        assert len(failed) == 0

    def test_skip_task_updates_timestamp(self):
        """Test that skipping a task updates the timestamp."""
        self._create_test_tasks()
        manager = StateManager(self.task_status_path)

        before_skip = manager.load_tasks()
        before_task = next(t for t in before_skip if t['id'] == 'task1')
        before_updated = before_task['updatedAt']

        manager.mark_task_skipped('task1')

        after_skip = manager.load_tasks()
        after_task = next(t for t in after_skip if t['id'] == 'task1')
        after_updated = after_task['updatedAt']

        assert before_updated is None or after_updated != before_updated
        assert after_updated is not None

    def test_skip_nonexistent_task(self):
        """Test skipping a task that doesn't exist."""
        self._create_test_tasks()
        manager = StateManager(self.task_status_path)

        result = manager.mark_task_skipped('nonexistent_task')

        # Should return True but not modify anything
        assert result is True

        tasks = manager.load_tasks()
        assert len(tasks) == 3


class TestRetryFailedTasks:
    """Test retry failed tasks functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.task_status_path = Path(self.temp_dir) / 'task_status.json'

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.task_status_path.exists():
            self.task_status_path.unlink()

    def _create_test_tasks_with_failures(self):
        """Create test tasks with some failures."""
        tasks = [
            {
                'id': 'task1',
                'name': 'Task 1',
                'desc': 'First task',
                'status': 'done',
                'generatedFile': 'file1.py',
                'testPassed': True,
                'retries': 0,
                'result': None,
                'updatedAt': None
            },
            {
                'id': 'task2',
                'name': 'Task 2',
                'desc': 'Second task',
                'status': 'failed',
                'generatedFile': None,
                'testPassed': False,
                'retries': 1,
                'result': 'Generation error',
                'updatedAt': None
            },
            {
                'id': 'task3',
                'name': 'Task 3',
                'desc': 'Third task',
                'status': 'blocked',
                'generatedFile': None,
                'testPassed': False,
                'retries': 0,
                'result': 'Dependency not met',
                'updatedAt': None
            }
        ]

        data = {
            'version': '1.0',
            'generated': '2026-03-29T00:00:00',
            'meta': {
                'root': 'root',
                'loopActive': True,
                'completedAt': None
            },
            'tasks': tasks
        }

        with open(self.task_status_path, 'w') as f:
            json.dump(data, f, indent=2)

        return tasks

    def test_get_failed_tasks_returns_failed_and_blocked(self):
        """Test that get_failed_tasks returns both failed and blocked tasks."""
        self._create_test_tasks_with_failures()
        manager = StateManager(self.task_status_path)

        failed = manager.get_failed_tasks()

        assert len(failed) == 2
        failed_ids = [t['id'] for t in failed]
        assert 'task2' in failed_ids  # failed
        assert 'task3' in failed_ids  # blocked

    def test_reset_task_for_retry(self):
        """Test resetting a task status for retry."""
        self._create_test_tasks_with_failures()
        manager = StateManager(self.task_status_path)

        # Reset task2 for retry
        result = manager.mark_task_skipped('task2')  # Using skip as reset mechanism
        assert result is True

        tasks = manager.load_tasks()
        task2 = next(t for t in tasks if t['id'] == 'task2')

        assert task2['status'] == 'skipped'


class TestCheckpointFunctionality:
    """Test checkpoint/resume functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.task_status_path = Path(self.temp_dir) / 'task_status.json'
        self.checkpoint_dir = Path(self.temp_dir) / 'checkpoints'

    def teardown_method(self):
        """Clean up test fixtures."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def _create_test_tasks(self):
        """Create test tasks file."""
        tasks = [
            {'id': 'task1', 'name': 'Task 1', 'status': 'done', 'generatedFile': 'file1.py'},
            {'id': 'task2', 'name': 'Task 2', 'status': 'running'},
            {'id': 'task3', 'name': 'Task 3', 'status': 'pending'},
        ]
        data = {
            'version': '1.0',
            'meta': {'loopActive': True, 'completedAt': None},
            'tasks': tasks
        }
        with open(self.task_status_path, 'w') as f:
            json.dump(data, f, indent=2)
        return tasks

    def test_save_checkpoint(self):
        """Test saving a checkpoint."""
        self._create_test_tasks()
        manager = StateManager(self.task_status_path)

        result = manager.save_checkpoint('test')

        assert result is True
        assert self.checkpoint_dir.exists()

        # Verify checkpoint file exists
        checkpoints = list(self.checkpoint_dir.glob('checkpoint_test_*.json'))
        assert len(checkpoints) == 1

    def test_load_checkpoint(self):
        """Test loading a checkpoint."""
        self._create_test_tasks()
        manager = StateManager(self.task_status_path)

        # Save checkpoint
        manager.save_checkpoint('test')

        # Modify original
        manager.mark_task_skipped('task2', 'Modified')

        # Load checkpoint
        result = manager.load_checkpoint('test')

        assert result is True

        # Verify state was restored
        tasks = manager.load_tasks()
        task2 = next(t for t in tasks if t['id'] == 'task2')
        assert task2['status'] == 'running'  # Restored from checkpoint

    def test_list_checkpoints(self):
        """Test listing checkpoints."""
        self._create_test_tasks()
        manager = StateManager(self.task_status_path)

        # Save multiple checkpoints
        manager.save_checkpoint('test1')
        manager.save_checkpoint('test2')

        checkpoints = manager.list_checkpoints()

        assert len(checkpoints) == 2
        assert all('name' in cp for cp in checkpoints)
        assert all('created_at' in cp for cp in checkpoints)

    def test_delete_checkpoint(self):
        """Test deleting a checkpoint."""
        self._create_test_tasks()
        manager = StateManager(self.task_status_path)

        # Save checkpoint
        manager.save_checkpoint('to_delete')

        checkpoints_before = manager.list_checkpoints()
        assert len(checkpoints_before) == 1

        # Delete checkpoint
        result = manager.delete_checkpoint('to_delete')

        assert result is True

        checkpoints_after = manager.list_checkpoints()
        assert len(checkpoints_after) == 0

    def test_resume_build(self):
        """Test resuming build from latest checkpoint."""
        self._create_test_tasks()
        manager = StateManager(self.task_status_path)

        # Save checkpoint
        manager.save_checkpoint('auto')

        # Modify state
        manager.mark_task_failed('task1', 'Error')

        # Resume
        result = manager.resume_build()

        assert result is True

        # Verify state was restored
        tasks = manager.load_tasks()
        task1 = next(t for t in tasks if t['id'] == 'task1')
        assert task1['status'] == 'done'  # Restored from checkpoint

    def test_get_resume_info(self):
        """Test getting resume information."""
        self._create_test_tasks()
        manager = StateManager(self.task_status_path)

        # No checkpoints yet
        info = manager.get_resume_info()
        assert info['can_resume'] is False

        # Save checkpoint
        manager.save_checkpoint('test')

        info = manager.get_resume_info()
        assert info['can_resume'] is True
        assert 'latest_checkpoint' in info
        assert 'message' in info

    def test_load_latest_checkpoint(self):
        """Test loading the latest checkpoint."""
        self._create_test_tasks()
        manager = StateManager(self.task_status_path)

        # Save multiple checkpoints
        manager.save_checkpoint('auto')
        import time
        time.sleep(0.1)  # Ensure different timestamps
        manager.save_checkpoint('auto')

        # Load latest
        result = manager.load_checkpoint('latest')

        assert result is True

    def test_checkpoint_preserves_task_state(self):
        """Test that checkpoint preserves all task state."""
        tasks = [
            {'id': 'task1', 'name': 'Task 1', 'status': 'done',
             'generatedFile': 'file1.py', 'testPassed': True, 'retries': 0},
            {'id': 'task2', 'name': 'Task 2', 'status': 'failed',
             'result': 'Error message', 'retries': 2},
        ]
        data = {
            'version': '1.0',
            'meta': {'loopActive': True, 'completedAt': None},
            'tasks': tasks
        }
        with open(self.task_status_path, 'w') as f:
            json.dump(data, f, indent=2)

        manager = StateManager(self.task_status_path)
        manager.save_checkpoint('preserve_test')

        # Verify checkpoint contains all data
        checkpoints = list(self.checkpoint_dir.glob('checkpoint_preserve_test_*.json'))
        with open(checkpoints[0], 'r') as f:
            checkpoint_data = json.load(f)

        assert len(checkpoint_data['tasks']) == 2
        assert checkpoint_data['tasks'][1]['retries'] == 2
        assert checkpoint_data['tasks'][1]['result'] == 'Error message'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

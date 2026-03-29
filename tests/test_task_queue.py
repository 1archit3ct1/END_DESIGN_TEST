"""
Test Task Queue — Task ordering tests.
"""

import pytest
from collections import deque

from agent.task_queue import TaskQueue


class TestTaskQueue:
    """Test Task Queue functionality."""

    @pytest.fixture
    def queue(self):
        """Create TaskQueue instance."""
        return TaskQueue()

    @pytest.fixture
    def sample_tasks(self):
        """Create sample task list."""
        return [
            {'id': 'task1', 'name': 'Task 1', 'status': 'pending'},
            {'id': 'task2', 'name': 'Task 2', 'status': 'pending'},
            {'id': 'task3', 'name': 'Task 3', 'status': 'done'},
            {'id': 'task4', 'name': 'Task 4', 'status': 'pending'},
        ]

    def test_initialization(self, queue):
        """Test queue initializes correctly."""
        assert queue.tasks == []
        assert queue.queue == deque()
        assert queue.is_empty() is True

    def test_load_tasks(self, queue, sample_tasks):
        """Test loading tasks into queue."""
        queue.load_tasks(sample_tasks)
        
        assert len(queue.tasks) == 4
        assert len(queue.queue) == 3  # Only pending tasks

    def test_load_tasks_empty(self, queue):
        """Test loading empty task list."""
        queue.load_tasks([])
        
        assert queue.tasks == []
        assert queue.is_empty() is True

    def test_get_next_pending_task(self, queue, sample_tasks):
        """Test getting next pending task."""
        queue.load_tasks(sample_tasks)
        
        task = queue.get_next_pending_task()
        
        assert task is not None
        assert task['id'] == 'task1'
        assert len(queue.queue) == 2

    def test_get_next_pending_task_empty(self, queue):
        """Test getting task from empty queue."""
        task = queue.get_next_pending_task()
        
        assert task is None

    def test_is_empty(self, queue):
        """Test empty check."""
        assert queue.is_empty() is True
        
        queue.load_tasks([{'id': 'task1', 'status': 'pending'}])
        assert queue.is_empty() is False

    def test_add_task(self, queue):
        """Test adding task to queue."""
        task = {'id': 'new_task', 'status': 'pending'}
        queue.add_task(task)
        
        assert len(queue.queue) == 1
        assert queue.queue[0]['id'] == 'new_task'

    def test_add_task_non_pending(self, queue):
        """Test adding non-pending task doesn't add to queue."""
        task = {'id': 'done_task', 'status': 'done'}
        queue.add_task(task)
        
        assert len(queue.queue) == 0

    def test_requeue_task(self, queue):
        """Test requeuing task for retry."""
        queue.load_tasks([{'id': 'task1', 'status': 'pending'}])
        queue.get_next_pending_task()  # Remove first task
        
        retry_task = {'id': 'retry_task', 'status': 'pending'}
        queue.requeue_task(retry_task)
        
        assert len(queue.queue) == 1
        assert queue.queue[0]['id'] == 'retry_task'  # Added to front

    def test_task_order_preserved(self, queue, sample_tasks):
        """Test that task order is preserved."""
        queue.load_tasks(sample_tasks)
        
        task1 = queue.get_next_pending_task()
        task2 = queue.get_next_pending_task()
        task4 = queue.get_next_pending_task()
        
        assert task1['id'] == 'task1'
        assert task2['id'] == 'task2'
        assert task4['id'] == 'task4'

    def test_only_pending_tasks_loaded(self, queue, sample_tasks):
        """Test that only pending tasks are added to queue."""
        queue.load_tasks(sample_tasks)
        
        for task in queue.queue:
            assert task['status'] == 'pending'

    def test_multiple_load_tasks(self, queue):
        """Test loading tasks multiple times."""
        tasks1 = [{'id': 'task1', 'status': 'pending'}]
        tasks2 = [{'id': 'task2', 'status': 'pending'}]
        
        queue.load_tasks(tasks1)
        queue.load_tasks(tasks2)
        
        # Second load replaces first
        assert len(queue.tasks) == 1
        assert queue.tasks[0]['id'] == 'task2'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

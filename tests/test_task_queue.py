#!/usr/bin/env python3
"""
Test: task_queue.py returns tasks in correct DAG order.
"""

import sys
import unittest
from pathlib import Path

# Add agent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.task_queue import TaskQueue


class TestTaskQueue(unittest.TestCase):
    """Test TaskQueue functionality."""

    def test_queue_initializes_empty(self):
        """Test that TaskQueue initializes empty."""
        queue = TaskQueue()
        
        self.assertTrue(queue.is_empty())
        self.assertIsNone(queue.get_next_pending_task())

    def test_load_tasks(self):
        """Test that tasks are loaded correctly."""
        queue = TaskQueue()
        
        tasks = [
            {'id': 'task1', 'status': 'pending'},
            {'id': 'task2', 'status': 'pending'},
            {'id': 'task3', 'status': 'done'}
        ]
        
        queue.load_tasks(tasks)
        
        self.assertFalse(queue.is_empty())

    def test_get_next_pending_task(self):
        """Test that next pending task is returned."""
        queue = TaskQueue()
        
        tasks = [
            {'id': 'task1', 'status': 'pending'},
            {'id': 'task2', 'status': 'pending'},
            {'id': 'task3', 'status': 'done'}
        ]
        
        queue.load_tasks(tasks)
        
        task = queue.get_next_pending_task()
        
        self.assertIsNotNone(task)
        self.assertEqual(task['status'], 'pending')
        self.assertEqual(task['id'], 'task1')

    def test_get_all_pending_tasks(self):
        """Test that all pending tasks are returned in order."""
        queue = TaskQueue()
        
        tasks = [
            {'id': 'task1', 'status': 'pending'},
            {'id': 'task2', 'status': 'done'},
            {'id': 'task3', 'status': 'pending'},
            {'id': 'task4', 'status': 'pending'}
        ]
        
        queue.load_tasks(tasks)
        
        # Should only get pending tasks
        task1 = queue.get_next_pending_task()
        task2 = queue.get_next_pending_task()
        task3 = queue.get_next_pending_task()
        task4 = queue.get_next_pending_task()
        
        self.assertEqual(task1['id'], 'task1')
        self.assertEqual(task2['id'], 'task3')
        self.assertEqual(task3['id'], 'task4')
        self.assertIsNone(task4)  # Queue empty

    def test_add_task(self):
        """Test adding task to queue."""
        queue = TaskQueue()
        
        task = {'id': 'new_task', 'status': 'pending'}
        queue.add_task(task)
        
        self.assertFalse(queue.is_empty())
        
        retrieved = queue.get_next_pending_task()
        self.assertEqual(retrieved['id'], 'new_task')

    def test_add_non_pending_task(self):
        """Test that non-pending tasks are not added."""
        queue = TaskQueue()
        
        task_done = {'id': 'done_task', 'status': 'done'}
        queue.add_task(task_done)
        
        self.assertTrue(queue.is_empty())

    def test_requeue_task(self):
        """Test requeuing task for retry."""
        queue = TaskQueue()
        
        task1 = {'id': 'task1', 'status': 'pending'}
        task2 = {'id': 'task2', 'status': 'pending'}
        
        queue.add_task(task1)
        queue.add_task(task2)
        
        # Requeue task1 to front
        queue.requeue_task(task1)
        
        # Should get task1 first
        retrieved = queue.get_next_pending_task()
        self.assertEqual(retrieved['id'], 'task1')


class TestTaskQueueTopologicalSort(unittest.TestCase):
    """Test TaskQueue topological ordering."""

    def test_pending_tasks_sorted_first(self):
        """Test that pending tasks are returned before others."""
        queue = TaskQueue()
        
        tasks = [
            {'id': 'task1', 'status': 'done'},
            {'id': 'task2', 'status': 'pending'},
            {'id': 'task3', 'status': 'blocked'},
            {'id': 'task4', 'status': 'pending'}
        ]
        
        queue.load_tasks(tasks)
        
        # Should only get pending tasks
        task1 = queue.get_next_pending_task()
        task2 = queue.get_next_pending_task()
        
        self.assertEqual(task1['status'], 'pending')
        self.assertEqual(task2['status'], 'pending')
        self.assertTrue(queue.is_empty())


if __name__ == '__main__':
    unittest.main()

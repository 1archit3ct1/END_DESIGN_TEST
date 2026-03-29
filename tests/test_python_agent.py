#!/usr/bin/env python3
"""
Test: python_agent.py initializes and runs without errors.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add agent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.python_agent import PythonAgent
from agent.state_manager import StateManager
from agent.task_queue import TaskQueue


class TestPythonAgent(unittest.TestCase):
    """Test PythonAgent initialization and basic functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_output_dir = Path('./test_output')
        self.test_output_dir.mkdir(exist_ok=True)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        # Clean up test output directory
        if self.test_output_dir.exists():
            shutil.rmtree(self.test_output_dir, ignore_errors=True)

    def test_agent_initializes(self):
        """Test that PythonAgent initializes without errors."""
        agent = PythonAgent(output_dir=str(self.test_output_dir))
        
        self.assertIsNotNone(agent)
        self.assertIsNotNone(agent.state_manager)
        self.assertIsNotNone(agent.task_queue)
        self.assertIsNotNone(agent.hybrid_router)
        self.assertIsNotNone(agent.file_writer)
        self.assertIsNotNone(agent.syntax_checker)
        self.assertFalse(agent.running)

    def test_agent_has_output_dir(self):
        """Test that output directory is set correctly."""
        agent = PythonAgent(output_dir=str(self.test_output_dir))
        
        self.assertEqual(agent.output_dir, self.test_output_dir)
        self.assertTrue(agent.output_dir.exists())

    def test_agent_stop(self):
        """Test that agent can be stopped."""
        agent = PythonAgent(output_dir=str(self.test_output_dir))
        agent.running = True
        agent.stop()
        
        self.assertFalse(agent.running)

    def test_get_file_extension_rust(self):
        """Test file extension detection for Rust tasks."""
        agent = PythonAgent(output_dir=str(self.test_output_dir))
        
        task_rust = {'id': 'rust_backend.pkce_rfc7636'}
        task_backend = {'id': 'rust_backend.callback_server'}
        
        self.assertEqual(agent._get_file_extension(task_rust), '.rs')
        self.assertEqual(agent._get_file_extension(task_backend), '.rs')

    def test_get_file_extension_typescript(self):
        """Test file extension detection for TypeScript tasks."""
        agent = PythonAgent(output_dir=str(self.test_output_dir))
        
        task_step1 = {'id': 'step1_connect.github_oauth'}
        task_integration = {'id': 'oauth_integration.callback'}
        
        self.assertIn(agent._get_file_extension(task_step1), ['.ts', '.tsx'])
        self.assertIn(agent._get_file_extension(task_integration), ['.ts', '.tsx'])

    def test_task_queue_integration(self):
        """Test that task queue loads tasks correctly."""
        agent = PythonAgent(output_dir=str(self.test_output_dir))
        
        tasks = [
            {'id': 'task1', 'status': 'pending'},
            {'id': 'task2', 'status': 'pending'},
            {'id': 'task3', 'status': 'done'}
        ]
        
        agent.task_queue.load_tasks(tasks)
        
        self.assertFalse(agent.task_queue.is_empty())
        
        # Get next pending task
        task = agent.task_queue.get_next_pending_task()
        self.assertIsNotNone(task)
        self.assertEqual(task['status'], 'pending')


class TestPythonAgentRun(unittest.TestCase):
    """Test PythonAgent run method."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_output_dir = Path('./test_output')
        self.test_output_dir.mkdir(exist_ok=True)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if self.test_output_dir.exists():
            shutil.rmtree(self.test_output_dir, ignore_errors=True)

    @patch('agent.python_agent.StateManager')
    @patch('agent.python_agent.HybridRouter')
    def test_process_task(self, mock_hybrid_router, mock_state_manager):
        """Test that process_task calls correct methods."""
        # Setup mocks
        mock_state_manager.return_value.load_tasks.return_value = []
        mock_state_manager.return_value.mark_task_running.return_value = True
        mock_state_manager.return_value.mark_task_done.return_value = True
        
        mock_hybrid_router.return_value.generate_code.return_value = "// Generated code"

        agent = PythonAgent(output_dir=str(self.test_output_dir))
        
        task = {'id': 'test_task', 'desc': 'Test task'}
        
        # This should not raise
        try:
            result = agent._process_task(task)
            # Result may be True or False depending on file writer
            self.assertIsInstance(result, bool)
        except Exception as e:
            self.fail(f"_process_task raised unexpected exception: {e}")


if __name__ == '__main__':
    unittest.main()

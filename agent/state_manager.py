"""
State Manager — Read/write task_status.json.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from .logger import setup_logger

logger = setup_logger(__name__)

TASK_STATUS_PATH = Path('./task_status.json')


class StateManager:
    """Manage task state in task_status.json."""

    def __init__(self, path: Optional[Path] = None):
        """Initialize state manager.
        
        Args:
            path: Path to task_status.json (default: ./task_status.json)
        """
        self.path = path or TASK_STATUS_PATH

    def load_tasks(self) -> List[Dict[str, Any]]:
        """Load tasks from task_status.json.
        
        Returns:
            List of task dictionaries
        """
        if not self.path.exists():
            logger.warning(f"task_status.json not found at {self.path}")
            return []

        try:
            with open(self.path, 'r') as f:
                data = json.load(f)
            return data.get('tasks', [])
        except Exception as e:
            logger.error(f"Failed to load tasks: {e}")
            return []

    def save_tasks(self, tasks: List[Dict[str, Any]]) -> bool:
        """Save tasks to task_status.json.
        
        Args:
            tasks: List of task dictionaries
            
        Returns:
            True if saved successfully
        """
        try:
            data = {
                'version': '1.0',
                'generated': datetime.now().isoformat(),
                'meta': {
                    'root': 'root',
                    'loopActive': True,
                    'completedAt': None
                },
                'tasks': tasks
            }

            with open(self.path, 'w') as f:
                json.dump(data, f, indent=2)

            logger.debug(f"Saved {len(tasks)} tasks to {self.path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save tasks: {e}")
            return False

    def initialize_tasks(self, tasks: List[Dict[str, Any]]) -> bool:
        """Initialize task_status.json with new tasks.
        
        Args:
            tasks: List of task dictionaries
            
        Returns:
            True if initialized successfully
        """
        return self.save_tasks(tasks)

    def mark_task_running(self, task_id: str) -> bool:
        """Mark task as running.
        
        Args:
            task_id: Task ID
            
        Returns:
            True if updated successfully
        """
        return self._update_task_status(task_id, 'running')

    def mark_task_done(self, task_id: str, file_path: str = None, test_passed: bool = True) -> bool:
        """Mark task as done.
        
        Args:
            task_id: Task ID
            file_path: Path to generated file
            test_passed: Whether task-specific test passed
            
        Returns:
            True if updated successfully
        """
        tasks = self.load_tasks()
        for task in tasks:
            if task['id'] == task_id:
                task['status'] = 'done'
                task['updatedAt'] = datetime.now().isoformat()
                if file_path:
                    task['generatedFile'] = file_path
                task['testPassed'] = test_passed
                break

        return self.save_tasks(tasks)

    def mark_task_blocked(self, task_id: str, error: str) -> bool:
        """Mark task as blocked.
        
        Args:
            task_id: Task ID
            error: Error message
            
        Returns:
            True if updated successfully
        """
        tasks = self.load_tasks()
        for task in tasks:
            if task['id'] == task_id:
                task['status'] = 'blocked'
                task['result'] = error
                task['retries'] = task.get('retries', 0) + 1
                task['updatedAt'] = datetime.now().isoformat()
                break

        return self.save_tasks(tasks)

    def _update_task_status(self, task_id: str, status: str) -> bool:
        """Update task status.
        
        Args:
            task_id: Task ID
            status: New status
            
        Returns:
            True if updated successfully
        """
        tasks = self.load_tasks()
        for task in tasks:
            if task['id'] == task_id:
                task['status'] = status
                task['updatedAt'] = datetime.now().isoformat()
                break

        return self.save_tasks(tasks)

    def finalize_build(self) -> bool:
        """Finalize build and mark as complete.
        
        Returns:
            True if finalized successfully
        """
        try:
            with open(self.path, 'r') as f:
                data = json.load(f)

            data['meta']['loopActive'] = False
            data['meta']['completedAt'] = datetime.now().isoformat()

            with open(self.path, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info("Build finalized")
            return True

        except Exception as e:
            logger.error(f"Failed to finalize build: {e}")
            return False

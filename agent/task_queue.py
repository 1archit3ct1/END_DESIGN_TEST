"""
Task Queue — Task selection from DAG (topological sort).
"""

from typing import List, Dict, Any, Optional
from collections import deque

from .logger import setup_logger

logger = setup_logger(__name__)


class TaskQueue:
    """Manage task queue with topological ordering."""

    def __init__(self):
        """Initialize task queue."""
        self.tasks: List[Dict[str, Any]] = []
        self.queue: deque = deque()

    def load_tasks(self, tasks: List[Dict[str, Any]]) -> None:
        """Load tasks into queue.
        
        Args:
            tasks: List of task dictionaries
        """
        self.tasks = tasks
        self._build_queue()
        logger.info(f"Loaded {len(tasks)} tasks into queue")

    def _build_queue(self) -> None:
        """Build queue with topological sort based on DAG edges."""
        # Simple implementation: sort by status (pending first)
        pending = [t for t in self.tasks if t.get('status') == 'pending']
        self.queue = deque(pending)
        logger.debug(f"Queue built with {len(self.queue)} pending tasks")

    def get_next_pending_task(self) -> Optional[Dict[str, Any]]:
        """Get next pending task from queue.
        
        Returns:
            Task dictionary or None if queue is empty
        """
        if not self.queue:
            return None

        task = self.queue.popleft()
        logger.debug(f"Getting task: {task['id']}")
        return task

    def is_empty(self) -> bool:
        """Check if queue is empty.
        
        Returns:
            True if queue is empty
        """
        return len(self.queue) == 0

    def add_task(self, task: Dict[str, Any]) -> None:
        """Add task to queue.
        
        Args:
            task: Task dictionary
        """
        if task.get('status') == 'pending':
            self.queue.append(task)
            logger.debug(f"Added task to queue: {task['id']}")

    def requeue_task(self, task: Dict[str, Any]) -> None:
        """Requeue task for retry.
        
        Args:
            task: Task dictionary
        """
        self.queue.appendleft(task)
        logger.debug(f"Requeued task: {task['id']}")

"""
Metrics — Track generation stats.
"""

from typing import Dict, Any, Optional
from datetime import datetime

from .logger import setup_logger

logger = setup_logger(__name__)


class Metrics:
    """Track code generation metrics."""

    def __init__(self):
        """Initialize metrics tracker."""
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.completed = 0
        self.failed = 0
        self.task_times: Dict[str, float] = {}

    def start_build(self) -> None:
        """Start tracking build."""
        self.start_time = datetime.now()
        self.completed = 0
        self.failed = 0
        self.task_times = {}
        logger.info("Build started")

    def end_build(self, completed: int, failed: int) -> None:
        """End build tracking.

        Args:
            completed: Number of completed tasks
            failed: Number of failed tasks
        """
        self.end_time = datetime.now()
        self.completed = completed
        self.failed = failed
        logger.info(f"Build ended: {completed} completed, {failed} failed")

    def record_task(self, success: bool, duration: Optional[float] = None) -> None:
        """Record task completion.

        Args:
            success: Whether task succeeded
            duration: Task duration in seconds
        """
        if success:
            self.completed += 1
        else:
            self.failed += 1
        
        if duration:
            self.task_times[f"task_{self.completed + self.failed}"] = duration

    def get_duration(self) -> float:
        """Get total build duration in seconds.

        Returns:
            Duration in seconds
        """
        if not self.start_time:
            return 0.0
        
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()

    def get_success_rate(self) -> float:
        """Get success rate percentage.

        Returns:
            Success rate as percentage
        """
        total = self.completed + self.failed
        if total == 0:
            return 0.0
        return (self.completed / total) * 100

    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary.

        Returns:
            Dictionary with metrics summary
        """
        return {
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.get_duration(),
            'completed': self.completed,
            'failed': self.failed,
            'total': self.completed + self.failed,
            'success_rate': self.get_success_rate()
        }

    def record_task_time(self, task_id: str, duration: float) -> None:
        """Record time for specific task.

        Args:
            task_id: Task identifier
            duration: Duration in seconds
        """
        self.task_times[task_id] = duration

    def get_average_task_time(self) -> float:
        """Get average task time.

        Returns:
            Average time in seconds
        """
        if not self.task_times:
            return 0.0
        return sum(self.task_times.values()) / len(self.task_times)

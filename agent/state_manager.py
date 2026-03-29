"""
State Manager — Read/write task_status.json.

Supports tracking multiple generated files per task.
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

    def mark_task_done(self, task_id: str, file_path: str = None, test_passed: bool = True, file_paths: List[str] = None) -> bool:
        """Mark task as done.

        Args:
            task_id: Task ID
            file_path: Path to generated file (single file, legacy)
            test_passed: Whether task-specific test passed
            file_paths: List of paths to generated files (multi-file support)

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
                if file_paths:
                    task['generatedFiles'] = file_paths
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

    def mark_task_skipped(self, task_id: str, reason: str = '') -> bool:
        """Mark task as skipped.

        Args:
            task_id: Task ID
            reason: Reason for skipping

        Returns:
            True if updated successfully
        """
        tasks = self.load_tasks()
        for task in tasks:
            if task['id'] == task_id:
                task['status'] = 'skipped'
                task['result'] = reason
                task['updatedAt'] = datetime.now().isoformat()
                break

        return self.save_tasks(tasks)

    def mark_task_failed(self, task_id: str, error: str = '') -> bool:
        """Mark task as failed.

        Args:
            task_id: Task ID
            error: Error message

        Returns:
            True if updated successfully
        """
        tasks = self.load_tasks()
        for task in tasks:
            if task['id'] == task_id:
                task['status'] = 'failed'
                task['result'] = error
                task['updatedAt'] = datetime.now().isoformat()
                break

        return self.save_tasks(tasks)

    def get_failed_tasks(self) -> list:
        """Get list of failed or blocked tasks.

        Returns:
            List of failed/blocked task dictionaries
        """
        tasks = self.load_tasks()
        return [t for t in tasks if t.get('status') in ('failed', 'blocked')]

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

    def save_checkpoint(self, checkpoint_name: str = 'auto') -> bool:
        """Save current state as checkpoint.

        Args:
            checkpoint_name: Name for checkpoint (default: 'auto')

        Returns:
            True if saved successfully
        """
        try:
            if not self.path.exists():
                return False

            # Create checkpoints directory
            checkpoint_dir = self.path.parent / 'checkpoints'
            checkpoint_dir.mkdir(exist_ok=True)

            # Generate checkpoint filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            checkpoint_path = checkpoint_dir / f'checkpoint_{checkpoint_name}_{timestamp}.json'

            # Copy current state
            with open(self.path, 'r') as f:
                data = json.load(f)

            # Add checkpoint metadata
            data['checkpoint'] = {
                'name': checkpoint_name,
                'created_at': datetime.now().isoformat(),
                'source': str(self.path)
            }

            with open(checkpoint_path, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Checkpoint saved: {checkpoint_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")
            return False

    def load_checkpoint(self, checkpoint_name: str = 'latest') -> bool:
        """Load state from checkpoint.

        Args:
            checkpoint_name: Name of checkpoint to load ('latest' for most recent)

        Returns:
            True if loaded successfully
        """
        try:
            checkpoint_dir = self.path.parent / 'checkpoints'

            if not checkpoint_dir.exists():
                logger.warning("No checkpoints directory found")
                return False

            # Find checkpoint file
            if checkpoint_name == 'latest':
                checkpoints = sorted(checkpoint_dir.glob('checkpoint_*.json'),
                                     key=lambda p: p.stat().st_mtime, reverse=True)
                if not checkpoints:
                    logger.warning("No checkpoints found")
                    return False
                checkpoint_path = checkpoints[0]
            else:
                # Find specific checkpoint
                checkpoints = list(checkpoint_dir.glob(f'checkpoint_{checkpoint_name}_*.json'))
                if not checkpoints:
                    logger.warning(f"Checkpoint '{checkpoint_name}' not found")
                    return False
                checkpoint_path = checkpoints[0]

            # Load checkpoint
            with open(checkpoint_path, 'r') as f:
                data = json.load(f)

            # Restore state (remove checkpoint metadata)
            if 'checkpoint' in data:
                del data['checkpoint']

            with open(self.path, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Checkpoint loaded: {checkpoint_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            return False

    def list_checkpoints(self) -> list:
        """List available checkpoints.

        Returns:
            List of checkpoint metadata dictionaries
        """
        checkpoints = []
        checkpoint_dir = self.path.parent / 'checkpoints'

        if not checkpoint_dir.exists():
            return checkpoints

        for checkpoint_path in sorted(checkpoint_dir.glob('checkpoint_*.json'),
                                       key=lambda p: p.stat().st_mtime, reverse=True):
            try:
                with open(checkpoint_path, 'r') as f:
                    data = json.load(f)

                checkpoint_info = data.get('checkpoint', {})
                checkpoints.append({
                    'name': checkpoint_info.get('name', 'unknown'),
                    'created_at': checkpoint_info.get('created_at', ''),
                    'path': str(checkpoint_path),
                    'task_count': len(data.get('tasks', [])),
                    'completed': sum(1 for t in data.get('tasks', []) if t.get('status') == 'done')
                })
            except Exception as e:
                logger.warning(f"Failed to read checkpoint {checkpoint_path}: {e}")

        return checkpoints

    def delete_checkpoint(self, checkpoint_name: str) -> bool:
        """Delete a checkpoint.

        Args:
            checkpoint_name: Name of checkpoint to delete

        Returns:
            True if deleted successfully
        """
        try:
            checkpoint_dir = self.path.parent / 'checkpoints'

            if not checkpoint_dir.exists():
                return False

            # Find and delete checkpoint
            checkpoints = list(checkpoint_dir.glob(f'checkpoint_{checkpoint_name}_*.json'))
            if not checkpoints:
                return False

            for checkpoint_path in checkpoints:
                checkpoint_path.unlink()
                logger.info(f"Checkpoint deleted: {checkpoint_path}")

            return True

        except Exception as e:
            logger.error(f"Failed to delete checkpoint: {e}")
            return False

    def resume_build(self) -> bool:
        """Resume build from latest checkpoint.

        Returns:
            True if resumed successfully
        """
        return self.load_checkpoint('latest')

    def get_resume_info(self) -> Dict[str, Any]:
        """Get information about resumable build.

        Returns:
            Dictionary with resume information
        """
        checkpoints = self.list_checkpoints()

        if not checkpoints:
            return {
                'can_resume': False,
                'message': 'No checkpoints available'
            }

        latest = checkpoints[0]
        tasks = self.load_tasks()
        pending = sum(1 for t in tasks if t.get('status') in ('pending', 'running'))
        failed = sum(1 for t in tasks if t.get('status') in ('failed', 'blocked'))

        return {
            'can_resume': True,
            'latest_checkpoint': latest,
            'total_checkpoints': len(checkpoints),
            'pending_tasks': pending,
            'failed_tasks': failed,
            'message': f"Can resume from {latest['created_at']} ({latest['completed']} tasks completed)"
        }

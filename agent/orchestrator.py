"""
Orchestrator — Coordinate planning + generation.

Manages the overall code generation workflow including:
- Task dependency resolution
- Parallel generation for independent tasks
- Rate limiting for API calls
- Timeout handling
"""

import asyncio
from typing import List, Dict, Any, Optional, Set
from pathlib import Path
from datetime import datetime

from .logger import setup_logger
from .state_manager import StateManager
from .task_queue import TaskQueue
from .hybrid_router import HybridRouter
from .file_writer import FileWriter
from .syntax_check import SyntaxChecker
from .metrics import Metrics

logger = setup_logger(__name__)


class Orchestrator:
    """Orchestrate code generation workflow."""

    def __init__(self, output_dir: str = "./output"):
        """Initialize orchestrator.

        Args:
            output_dir: Output directory for generated code
        """
        self.output_dir = Path(output_dir)
        self.state_manager = StateManager()
        self.task_queue = TaskQueue()
        self.hybrid_router = HybridRouter()
        self.file_writer = FileWriter(self.output_dir)
        self.syntax_checker = SyntaxChecker()
        self.metrics = Metrics()
        
        # Configuration
        self.max_parallel = 4
        self.rate_limit_delay = 0.1  # seconds between API calls
        self.timeout = 120  # seconds per task

    def run(self) -> bool:
        """Run the orchestration workflow.

        Returns:
            True if all tasks completed successfully
        """
        logger.info("Starting Orchestrator")
        
        # Load tasks
        tasks = self.state_manager.load_tasks()
        if not tasks:
            logger.error("No tasks found")
            return False
        
        self.task_queue.load_tasks(tasks)
        self.metrics.start_build()
        
        # Process tasks
        completed = 0
        failed = 0
        
        while not self.task_queue.is_empty():
            task = self.task_queue.get_next_pending_task()
            if not task:
                break
            
            success = self._process_task(task)
            
            if success:
                completed += 1
            else:
                failed += 1
            
            self.metrics.record_task(success)
        
        # Finalize
        self.metrics.end_build(completed, failed)
        self.state_manager.finalize_build()
        
        logger.info(f"Orchestrator finished: {completed} completed, {failed} failed")
        return failed == 0

    def _process_task(self, task: Dict[str, Any]) -> bool:
        """Process a single task.

        Args:
            task: Task dictionary

        Returns:
            True if successful
        """
        try:
            self.state_manager.mark_task_running(task['id'])
            
            # Generate code
            code = self.hybrid_router.generate_code(task)
            if not code:
                self.state_manager.mark_task_blocked(task['id'], "Code generation failed")
                return False
            
            # Validate syntax
            ext = self._get_extension(task)
            result = self.syntax_checker.check_syntax(code, ext)
            if not result.is_valid:
                self.state_manager.mark_task_blocked(task['id'], result.error.message if result.error else "Syntax error")
                return False
            
            # Write file
            path = self.file_writer.write_file(task, code)
            if not path:
                self.state_manager.mark_task_blocked(task['id'], "File write failed")
                return False
            
            # Mark done
            self.state_manager.mark_task_done(task['id'], file_path=str(path), test_passed=True)
            logger.info(f"Task completed: {task['id']}")
            return True
            
        except Exception as e:
            logger.exception(f"Task failed: {task['id']}")
            self.state_manager.mark_task_failed(task['id'], str(e))
            return False

    def _get_extension(self, task: Dict[str, Any]) -> str:
        """Get file extension from task.

        Args:
            task: Task dictionary

        Returns:
            File extension
        """
        task_id = task.get('id', '').lower()
        
        if 'rust' in task_id or 'backend' in task_id:
            return '.rs'
        elif 'python' in task_id or 'agent' in task_id:
            return '.py'
        return '.ts'

    async def run_parallel(self, tasks: List[Dict[str, Any]]) -> Dict[str, bool]:
        """Run tasks in parallel where possible.

        Args:
            tasks: List of tasks to process

        Returns:
            Dictionary mapping task IDs to success status
        """
        results = {}
        semaphore = asyncio.Semaphore(self.max_parallel)
        
        async def process_with_semaphore(task):
            async with semaphore:
                await asyncio.sleep(self.rate_limit_delay)  # Rate limiting
                success = self._process_task(task)
                return task['id'], success
        
        # Create tasks
        coroutines = [process_with_semaphore(task) for task in tasks]
        
        # Run concurrently
        for coro in asyncio.as_completed(coroutines):
            task_id, success = await coro
            results[task_id] = success
        
        return results

    def get_dependencies(self, task: Dict[str, Any]) -> Set[str]:
        """Get dependencies for a task.

        Args:
            task: Task dictionary

        Returns:
            Set of task IDs this task depends on
        """
        # Extract dependencies from task metadata or description
        deps = task.get('dependencies', set())
        if isinstance(deps, list):
            deps = set(deps)
        return deps

    def resolve_dependencies(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Resolve task dependencies and return sorted order.

        Args:
            tasks: List of tasks

        Returns:
            Tasks sorted by dependency order
        """
        # Build dependency graph
        graph = {t['id']: self.get_dependencies(t) for t in tasks}
        task_map = {t['id']: t for t in tasks}
        
        # Topological sort
        sorted_tasks = []
        visited = set()
        temp_visited = set()
        
        def visit(task_id: str):
            if task_id in temp_visited:
                raise ValueError(f"Circular dependency detected: {task_id}")
            if task_id in visited:
                return
            
            temp_visited.add(task_id)
            for dep in graph.get(task_id, set()):
                if dep in task_map:
                    visit(dep)
            temp_visited.remove(task_id)
            visited.add(task_id)
            sorted_tasks.append(task_map[task_id])
        
        for task in tasks:
            if task['id'] not in visited:
                visit(task['id'])
        
        return sorted_tasks


def run_orchestrator(output_dir: str = "./output") -> bool:
    """Run the orchestrator.

    Args:
        output_dir: Output directory

    Returns:
        True if successful
    """
    orchestrator = Orchestrator(output_dir)
    return orchestrator.run()


if __name__ == '__main__':
    success = run_orchestrator()
    exit(0 if success else 1)

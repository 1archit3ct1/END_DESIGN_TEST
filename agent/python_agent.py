#!/usr/bin/env python3
"""
Python Agent — Main agent loop entry point for NextAura Code Generator.

Orchestrates code generation from task_status.json using hybrid approach:
- Template-based generation for known patterns
- LLM-based generation (codellama:7b) for custom tasks
"""

import json
import argparse
from pathlib import Path
from typing import Optional

from .state_manager import StateManager
from .task_queue import TaskQueue
from .hybrid_router import HybridRouter
from .file_writer import FileWriter
from .syntax_check import SyntaxChecker
from .logger import setup_logger

logger = setup_logger(__name__)


class PythonAgent:
    """Main agent loop for code generation."""

    def __init__(self, output_dir: str = "./output", dag_path: Optional[str] = None):
        """Initialize the Python agent.
        
        Args:
            output_dir: Directory for generated code
            dag_path: Optional path to DAG JSON file
        """
        self.output_dir = Path(output_dir)
        self.dag_path = dag_path
        self.state_manager = StateManager()
        self.task_queue = TaskQueue()
        self.hybrid_router = HybridRouter()
        self.file_writer = FileWriter(self.output_dir)
        self.syntax_checker = SyntaxChecker()
        self.running = False

    def run(self) -> bool:
        """Run the agent loop until all tasks are complete.
        
        Returns:
            True if all tasks completed successfully, False otherwise
        """
        logger.info("Starting Python Agent loop")
        self.running = True

        # Load DAG if provided
        if self.dag_path:
            logger.info(f"Loading DAG from {self.dag_path}")
            self._load_dag(self.dag_path)

        # Initialize task queue from task_status.json
        tasks = self.state_manager.load_tasks()
        if not tasks:
            logger.error("No tasks found in task_status.json")
            return False

        self.task_queue.load_tasks(tasks)
        logger.info(f"Loaded {len(tasks)} tasks")

        # Main agent loop
        completed = 0
        failed = 0

        while self.running and not self.task_queue.is_empty():
            task = self.task_queue.get_next_pending_task()
            if not task:
                logger.warning("No pending tasks found")
                break

            logger.info(f"Processing task: {task['id']}")
            success = self._process_task(task)

            if success:
                completed += 1
            else:
                failed += 1
                logger.error(f"Task failed: {task['id']}")

        # Finalize build
        self._finalize_build(completed, failed)

        success = failed == 0
        logger.info(f"Agent loop finished: {completed} completed, {failed} failed")
        return success

    def _process_task(self, task: dict) -> bool:
        """Process a single task through the generation pipeline.
        
        Args:
            task: Task dictionary from task_status.json
            
        Returns:
            True if task completed successfully, False otherwise
        """
        try:
            # Mark task as running
            self.state_manager.mark_task_running(task['id'])

            # Route task to appropriate coder (template or LLM)
            code = self.hybrid_router.generate_code(task)
            if not code:
                logger.error(f"Code generation failed for task {task['id']}")
                self.state_manager.mark_task_blocked(task['id'], "Code generation failed")
                return False

            # Validate syntax
            file_ext = self._get_file_extension(task)
            if not self.syntax_checker.check_syntax(code, file_ext):
                logger.error(f"Syntax check failed for task {task['id']}")
                self.state_manager.mark_task_blocked(task['id'], "Syntax check failed")
                return False

            # Write file
            file_path = self.file_writer.write_file(task, code)
            if not file_path:
                logger.error(f"File write failed for task {task['id']}")
                self.state_manager.mark_task_blocked(task['id'], "File write failed")
                return False

            # Run task-specific test
            test_passed = self._run_task_test(task, file_path)

            # Mark task as done
            self.state_manager.mark_task_done(
                task['id'],
                file_path=str(file_path),
                test_passed=test_passed
            )

            logger.info(f"Task completed: {task['id']} → {file_path}")
            return True

        except Exception as e:
            logger.exception(f"Error processing task {task['id']}: {e}")
            self.state_manager.mark_task_blocked(task['id'], str(e))
            return False

    def _get_file_extension(self, task: dict) -> str:
        """Get file extension from task ID or description.
        
        Args:
            task: Task dictionary
            
        Returns:
            File extension (e.g., '.rs', '.py', '.ts')
        """
        task_id = task.get('id', '').lower()
        
        if 'rust' in task_id or 'backend' in task_id:
            return '.rs'
        elif 'python' in task_id or 'agent' in task_id:
            return '.py'
        elif 'test' in task_id:
            return '.test.ts'
        else:
            return '.ts'  # Default to TypeScript

    def _run_task_test(self, task: dict, file_path: Path) -> bool:
        """Run task-specific test after generation.
        
        Args:
            task: Task dictionary
            file_path: Path to generated file
            
        Returns:
            True if test passed, False otherwise
        """
        # TODO: Implement task-specific test runner
        # For now, return True as placeholder
        logger.debug(f"Running test for task {task['id']}")
        return True

    def _load_dag(self, dag_path: str) -> None:
        """Load DAG from JSON file and initialize task_status.json.
        
        Args:
            dag_path: Path to DAG JSON file
        """
        try:
            with open(dag_path, 'r') as f:
                dag_data = json.load(f)

            nodes = dag_data.get('nodes', [])
            tasks = []

            for node in nodes:
                tasks.append({
                    'id': node.get('id', 'unknown'),
                    'name': node.get('name', ''),
                    'desc': node.get('desc', ''),
                    'status': 'pending',
                    'layer': node.get('layer', 'general'),
                    'hash': None,
                    'retries': 0,
                    'result': None,
                    'updatedAt': None
                })

            self.state_manager.initialize_tasks(tasks)
            logger.info(f"Initialized {len(tasks)} tasks from DAG")

        except Exception as e:
            logger.error(f"Failed to load DAG: {e}")
            raise

    def _finalize_build(self, completed: int, failed: int) -> None:
        """Finalize the build and generate report.
        
        Args:
            completed: Number of completed tasks
            failed: Number of failed tasks
        """
        self.state_manager.finalize_build()
        
        total = completed + failed
        success_rate = (completed / total * 100) if total > 0 else 0
        
        logger.info(f"Build Summary: {completed}/{total} tasks ({success_rate:.1f}% success)")

    def stop(self) -> None:
        """Stop the agent loop gracefully."""
        logger.info("Stopping agent loop...")
        self.running = False


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(description='NextAura Python Code Agent')
    parser.add_argument('--dag', type=str, help='Path to DAG JSON file')
    parser.add_argument('--output', type=str, default='./output', help='Output directory')
    parser.add_argument('--resume', action='store_true', help='Resume interrupted build')
    parser.add_argument('--task', type=str, help='Generate specific task only')

    args = parser.parse_args()

    agent = PythonAgent(output_dir=args.output, dag_path=args.dag)

    try:
        success = agent.run()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        agent.stop()
        exit(1)
    except Exception as e:
        logger.exception(f"Agent failed: {e}")
        exit(1)


if __name__ == '__main__':
    main()

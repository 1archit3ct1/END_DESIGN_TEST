"""
Test Orchestrator — Integration tests.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from agent.orchestrator import Orchestrator, run_orchestrator
from agent.metrics import Metrics
from agent.hybrid_router import HybridRouter


class TestMetrics:
    """Test Metrics class."""

    @pytest.fixture
    def metrics(self):
        """Create Metrics instance."""
        return Metrics()

    def test_initialization(self, metrics):
        """Test metrics initializes correctly."""
        assert metrics.start_time is None
        assert metrics.end_time is None
        assert metrics.completed == 0
        assert metrics.failed == 0

    def test_start_build(self, metrics):
        """Test starting build."""
        metrics.start_build()
        
        assert metrics.start_time is not None
        assert metrics.completed == 0
        assert metrics.failed == 0

    def test_end_build(self, metrics):
        """Test ending build."""
        metrics.start_build()
        metrics.end_build(completed=10, failed=2)
        
        assert metrics.end_time is not None
        assert metrics.completed == 10
        assert metrics.failed == 2

    def test_record_task_success(self, metrics):
        """Test recording successful task."""
        metrics.start_build()
        metrics.record_task(success=True)
        
        assert metrics.completed == 1
        assert metrics.failed == 0

    def test_record_task_failure(self, metrics):
        """Test recording failed task."""
        metrics.start_build()
        metrics.record_task(success=False)
        
        assert metrics.completed == 0
        assert metrics.failed == 1

    def test_record_task_with_duration(self, metrics):
        """Test recording task with duration."""
        metrics.start_build()
        metrics.record_task(success=True, duration=1.5)
        
        assert len(metrics.task_times) == 1

    def test_get_duration(self, metrics):
        """Test getting duration."""
        metrics.start_build()
        duration = metrics.get_duration()
        
        assert duration >= 0

    def test_get_duration_no_start(self, metrics):
        """Test duration without start."""
        duration = metrics.get_duration()
        assert duration == 0.0

    def test_get_success_rate(self, metrics):
        """Test success rate calculation."""
        metrics.start_build()
        metrics.record_task(success=True)
        metrics.record_task(success=True)
        metrics.record_task(success=False)
        
        rate = metrics.get_success_rate()
        assert rate == pytest.approx(66.67, rel=0.1)

    def test_get_success_rate_zero(self, metrics):
        """Test success rate with no tasks."""
        rate = metrics.get_success_rate()
        assert rate == 0.0

    def test_get_summary(self, metrics):
        """Test getting summary."""
        metrics.start_build()
        metrics.record_task(success=True)
        metrics.end_build(1, 0)
        
        summary = metrics.get_summary()
        
        assert 'start_time' in summary
        assert 'end_time' in summary
        assert 'duration_seconds' in summary
        assert 'completed' in summary
        assert 'failed' in summary
        assert 'success_rate' in summary

    def test_record_task_time(self, metrics):
        """Test recording specific task time."""
        metrics.record_task_time('task1', 2.5)
        
        assert metrics.task_times['task1'] == 2.5

    def test_get_average_task_time(self, metrics):
        """Test average task time."""
        metrics.record_task_time('task1', 1.0)
        metrics.record_task_time('task2', 2.0)
        metrics.record_task_time('task3', 3.0)
        
        avg = metrics.get_average_task_time()
        assert avg == 2.0

    def test_get_average_task_time_empty(self, metrics):
        """Test average with no tasks."""
        avg = metrics.get_average_task_time()
        assert avg == 0.0


class TestOrchestrator:
    """Test Orchestrator class."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        dirpath = tempfile.mkdtemp()
        yield Path(dirpath)
        shutil.rmtree(dirpath)

    @pytest.fixture
    def orchestrator(self, temp_dir):
        """Create Orchestrator instance."""
        return Orchestrator(output_dir=str(temp_dir))

    @pytest.fixture
    def sample_tasks(self):
        """Create sample tasks."""
        return [
            {'id': 'task1', 'name': 'Task 1', 'desc': 'Test', 'status': 'pending'},
            {'id': 'task2', 'name': 'Task 2', 'desc': 'Test', 'status': 'pending'},
        ]

    def test_initialization(self, orchestrator, temp_dir):
        """Test orchestrator initializes correctly."""
        assert orchestrator.output_dir == temp_dir
        assert orchestrator.max_parallel == 4
        assert orchestrator.rate_limit_delay == 0.1
        assert orchestrator.timeout == 120

    def test_get_extension_rust(self, orchestrator):
        """Test extension detection for Rust."""
        task = {'id': 'rust_backend.auth'}
        ext = orchestrator._get_extension(task)
        assert ext == '.rs'

    def test_get_extension_python(self, orchestrator):
        """Test extension detection for Python."""
        task = {'id': 'agent.module'}
        ext = orchestrator._get_extension(task)
        assert ext == '.py'

    def test_get_extension_default(self, orchestrator):
        """Test default extension."""
        task = {'id': 'ui.component'}
        ext = orchestrator._get_extension(task)
        assert ext == '.ts'

    def test_get_dependencies_empty(self, orchestrator):
        """Test getting dependencies when none exist."""
        task = {'id': 'task1'}
        deps = orchestrator.get_dependencies(task)
        assert deps == set()

    def test_get_dependencies_set(self, orchestrator):
        """Test getting dependencies as set."""
        task = {'id': 'task1', 'dependencies': {'task2', 'task3'}}
        deps = orchestrator.get_dependencies(task)
        assert deps == {'task2', 'task3'}

    def test_get_dependencies_list(self, orchestrator):
        """Test getting dependencies as list."""
        task = {'id': 'task1', 'dependencies': ['task2', 'task3']}
        deps = orchestrator.get_dependencies(task)
        assert deps == {'task2', 'task3'}

    def test_resolve_dependencies_no_deps(self, orchestrator):
        """Test resolving when no dependencies."""
        tasks = [
            {'id': 'task1', 'dependencies': set()},
            {'id': 'task2', 'dependencies': set()},
        ]
        sorted_tasks = orchestrator.resolve_dependencies(tasks)
        
        assert len(sorted_tasks) == 2

    def test_resolve_dependencies_linear(self, orchestrator):
        """Test resolving linear dependencies."""
        tasks = [
            {'id': 'task1', 'dependencies': set()},
            {'id': 'task2', 'dependencies': {'task1'}},
            {'id': 'task3', 'dependencies': {'task2'}},
        ]
        sorted_tasks = orchestrator.resolve_dependencies(tasks)
        
        # task1 should come before task2, task2 before task3
        ids = [t['id'] for t in sorted_tasks]
        assert ids.index('task1') < ids.index('task2')
        assert ids.index('task2') < ids.index('task3')

    def test_resolve_dependencies_circular(self, orchestrator):
        """Test detecting circular dependencies."""
        tasks = [
            {'id': 'task1', 'dependencies': {'task2'}},
            {'id': 'task2', 'dependencies': {'task1'}},
        ]
        
        with pytest.raises(ValueError, match="Circular dependency"):
            orchestrator.resolve_dependencies(tasks)

    @patch('agent.orchestrator.HybridRouter')
    @patch('agent.orchestrator.SyntaxChecker')
    def test_process_task_success(self, mock_syntax_class, mock_router_class, orchestrator, sample_tasks):
        """Test processing task successfully."""
        # Setup mocks
        mock_router = MagicMock()
        mock_router.generate_code.return_value = 'export const x = 1;'
        mock_router_class.return_value = mock_router
        
        mock_syntax = MagicMock()
        mock_syntax.check_syntax.return_value = MagicMock(is_valid=True)
        mock_syntax_class.return_value = mock_syntax
        
        # Initialize tasks
        orchestrator.state_manager.initialize_tasks(sample_tasks)
        
        result = orchestrator._process_task(sample_tasks[0])
        
        assert result is True

    @patch.object(HybridRouter, 'generate_code', return_value=None)
    def test_process_task_code_generation_fails(self, mock_generate, orchestrator, sample_tasks):
        """Test processing task when code generation fails."""
        orchestrator.state_manager.initialize_tasks(sample_tasks)
        
        result = orchestrator._process_task(sample_tasks[0])
        
        assert result is False
        mock_generate.assert_called_once()


class TestRunOrchestrator:
    """Test run_orchestrator convenience function."""

    @patch('agent.orchestrator.Orchestrator')
    def test_run_orchestrator_success(self, mock_orch_class):
        """Test successful orchestrator run."""
        mock_orch = MagicMock()
        mock_orch.run.return_value = True
        mock_orch_class.return_value = mock_orch
        
        result = run_orchestrator()
        
        assert result is True

    @patch('agent.orchestrator.Orchestrator')
    def test_run_orchestrator_failure(self, mock_orch_class):
        """Test failed orchestrator run."""
        mock_orch = MagicMock()
        mock_orch.run.return_value = False
        mock_orch_class.return_value = mock_orch
        
        result = run_orchestrator()
        
        assert result is False


class TestOrchestratorIntegration:
    """Integration tests for Orchestrator."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        dirpath = tempfile.mkdtemp()
        yield Path(dirpath)
        shutil.rmtree(dirpath)

    def test_full_orchestration_workflow(self, temp_dir):
        """Test complete orchestration workflow."""
        orchestrator = Orchestrator(output_dir=str(temp_dir))
        
        # Setup tasks
        tasks = [
            {'id': 'test.task', 'name': 'Test', 'desc': 'Test task', 'status': 'pending'}
        ]
        orchestrator.state_manager.initialize_tasks(tasks)
        
        # Mock the generation
        with patch.object(type(orchestrator.hybrid_router), 'generate_code', return_value='export const x = 1;'):
            with patch.object(type(orchestrator.syntax_checker), 'check_syntax', return_value=MagicMock(is_valid=True)):
                result = orchestrator.run()
        
        assert result is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

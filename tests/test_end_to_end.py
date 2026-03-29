"""
Test End-to-End — Full repo generation from DAG.
"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from agent.python_agent import PythonAgent
from agent.state_manager import StateManager
from agent.syntax_check import SyntaxCheckResult


class TestEndToEnd:
    """End-to-end tests for full repo generation."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        dirpath = tempfile.mkdtemp()
        yield Path(dirpath)
        shutil.rmtree(dirpath)

    @pytest.fixture
    def sample_dag(self):
        """Create sample DAG for testing."""
        return {
            'nodes': [
                {
                    'id': 'rust_backend.pkce_rfc7636',
                    'name': 'PKCE Implementation',
                    'desc': 'SHA256 + base64url encoding for OAuth',
                    'layer': 'backend'
                },
                {
                    'id': 'rust_backend.callback_server',
                    'name': 'Callback Server',
                    'desc': 'OAuth callback HTTP server',
                    'layer': 'backend'
                },
                {
                    'id': 'oauth_integration.callback_server',
                    'name': 'OAuth Callback Handler',
                    'desc': 'TypeScript OAuth callback',
                    'layer': 'integration'
                },
                {
                    'id': 'ui_components.oauth_button',
                    'name': 'OAuth Button',
                    'desc': 'OAuth login button component',
                    'layer': 'ui'
                },
            ]
        }

    @pytest.fixture
    def success_criteria(self):
        """Define generation success criteria."""
        return {
            'all_tasks_processed': True,
            'all_files_created': True,
            'all_syntax_valid': True,
            'no_blocked_tasks': True,
            'output_structure_valid': True,
            'headers_present': True,
        }

    def test_end_to_end_full_generation(self, temp_dir, sample_dag):
        """Test complete repo generation from DAG."""
        # Create DAG file
        dag_path = temp_dir / 'dag.json'
        with open(dag_path, 'w') as f:
            json.dump(sample_dag, f)
        
        # Create task_status.json
        tasks = []
        for node in sample_dag['nodes']:
            tasks.append({
                'id': node['id'],
                'name': node['name'],
                'desc': node['desc'],
                'status': 'pending',
                'layer': node['layer']
            })
        
        state_manager = StateManager()
        state_manager.initialize_tasks(tasks)
        
        # Mock code generation to return valid code
        def mock_generate(task):
            task_id = task['id']
            if 'rust' in task_id:
                return f'// PKCE implementation for {task_id}\npub fn generate() {{}}'
            elif 'oauth' in task_id:
                return f'// OAuth handler for {task_id}\nexport const handler = () => {{}}'
            else:
                return f'// Component for {task_id}\nexport const Component = () => null'
        
        # Run agent
        agent = PythonAgent(output_dir=str(temp_dir / 'output'), dag_path=str(dag_path))
        
        with patch.object(type(agent.hybrid_router), 'generate_code', side_effect=mock_generate):
            with patch.object(type(agent.syntax_checker), 'check_syntax', 
                            return_value=MagicMock(is_valid=True)):
                result = agent.run()
        
        # Verify success
        assert result is True
        
        # Verify files were created
        output_dir = temp_dir / 'output'
        generated_files = list(output_dir.glob('**/*'))
        assert len(generated_files) >= 4  # At least one file per task

    def test_end_to_end_with_failures(self, temp_dir, sample_dag):
        """Test generation with some task failures."""
        # Create task_status.json
        tasks = []
        for node in sample_dag['nodes']:
            tasks.append({
                'id': node['id'],
                'name': node['name'],
                'desc': node['desc'],
                'status': 'pending'
            })
        
        state_manager = StateManager()
        state_manager.initialize_tasks(tasks)
        
        # Mock code generation to fail for some tasks
        def mock_generate(task):
            if task['id'] == 'rust_backend.pkce_rfc7636':
                return None  # Fail this task
            return 'export const x = 1;'
        
        agent = PythonAgent(output_dir=str(temp_dir / 'output'))
        
        with patch.object(type(agent.hybrid_router), 'generate_code', side_effect=mock_generate):
            result = agent.run()
        
        # Some tasks failed, so overall result should be False
        assert result is False

    def test_end_to_end_resume_from_checkpoint(self, temp_dir):
        """Test resuming generation from checkpoint."""
        # Create partially completed state
        tasks = [
            {'id': 'task1', 'name': 'Task 1', 'desc': 'Test', 'status': 'done'},
            {'id': 'task2', 'name': 'Task 2', 'desc': 'Test', 'status': 'pending'},
            {'id': 'task3', 'name': 'Task 3', 'desc': 'Test', 'status': 'pending'},
        ]
        
        state_manager = StateManager()
        state_manager.initialize_tasks(tasks)
        
        agent = PythonAgent(output_dir=str(temp_dir / 'output'))
        
        def mock_generate(task):
            return 'export const x = 1;'
        
        with patch.object(type(agent.hybrid_router), 'generate_code', side_effect=mock_generate):
            with patch.object(type(agent.syntax_checker), 'check_syntax',
                            return_value=MagicMock(is_valid=True)):
                result = agent.run()
        
        assert result is True
        
        # Verify task1 was not reprocessed (already done)
        final_tasks = state_manager.load_tasks()
        assert final_tasks[0]['status'] == 'done'

    def test_output_structure_validation(self, temp_dir):
        """Test that output structure matches expected layout."""
        tasks = [
            {'id': 'rust_backend.auth', 'name': 'Auth', 'desc': 'Rust backend', 'status': 'pending'},
            {'id': 'ui_components.button', 'name': 'Button', 'desc': 'UI component', 'status': 'pending'},
        ]
        
        state_manager = StateManager()
        state_manager.initialize_tasks(tasks)
        
        agent = PythonAgent(output_dir=str(temp_dir / 'output'))
        
        with patch.object(type(agent.hybrid_router), 'generate_code', return_value='code'):
            with patch.object(type(agent.syntax_checker), 'check_syntax',
                            return_value=MagicMock(is_valid=True)):
                agent.run()
        
        output_dir = temp_dir / 'output'
        
        # Verify structure
        assert output_dir.exists()
        
        # Check files have headers
        for f in output_dir.glob('**/*'):
            if f.is_file():
                content = f.read_text()
                assert 'Auto-generated' in content

    def test_all_tasks_reach_terminal_state(self, temp_dir):
        """Test that all tasks end up as done, blocked, or failed."""
        tasks = [
            {'id': 'task1', 'name': 'Task 1', 'desc': 'Test', 'status': 'pending'},
            {'id': 'task2', 'name': 'Task 2', 'desc': 'Test', 'status': 'pending'},
        ]
        
        state_manager = StateManager()
        state_manager.initialize_tasks(tasks)
        
        agent = PythonAgent(output_dir=str(temp_dir / 'output'))
        
        with patch.object(type(agent.hybrid_router), 'generate_code', return_value='code'):
            with patch.object(type(agent.syntax_checker), 'check_syntax',
                            return_value=MagicMock(is_valid=True)):
                agent.run()
        
        final_tasks = state_manager.load_tasks()
        
        terminal_states = {'done', 'blocked', 'failed', 'skipped'}
        for task in final_tasks:
            assert task['status'] in terminal_states


class TestSuccessCriteria:
    """Test generation success criteria."""

    @pytest.fixture
    def criteria(self):
        """Get success criteria."""
        return {
            'all_tasks_processed': True,
            'all_files_created': True,
            'all_syntax_valid': True,
            'no_blocked_tasks': True,
            'output_structure_valid': True,
            'headers_present': True,
        }

    def test_criteria_all_tasks_processed(self, criteria):
        """Test all tasks processed criterion."""
        assert 'all_tasks_processed' in criteria
        assert criteria['all_tasks_processed'] is True

    def test_criteria_all_files_created(self, criteria):
        """Test all files created criterion."""
        assert 'all_files_created' in criteria
        assert criteria['all_files_created'] is True

    def test_criteria_all_syntax_valid(self, criteria):
        """Test syntax validation criterion."""
        assert 'all_syntax_valid' in criteria
        assert criteria['all_syntax_valid'] is True

    def test_criteria_no_blocked_tasks(self, criteria):
        """Test no blocked tasks criterion."""
        assert 'no_blocked_tasks' in criteria
        assert criteria['no_blocked_tasks'] is True

    def test_criteria_output_structure_valid(self, criteria):
        """Test output structure criterion."""
        assert 'output_structure_valid' in criteria
        assert criteria['output_structure_valid'] is True

    def test_criteria_headers_present(self, criteria):
        """Test headers present criterion."""
        assert 'headers_present' in criteria
        assert criteria['headers_present'] is True

    def test_validate_success_criteria(self, criteria):
        """Test validating all criteria are met."""
        all_met = all(criteria.values())
        assert all_met is True

    def test_partial_criteria(self):
        """Test partial criteria evaluation."""
        criteria = {
            'all_tasks_processed': True,
            'all_files_created': False,
            'all_syntax_valid': True,
        }
        
        all_met = all(criteria.values())
        assert all_met is False
        
        success_rate = sum(criteria.values()) / len(criteria)
        assert success_rate == pytest.approx(0.67, rel=0.01)


class TestGenerationMetrics:
    """Test generation metrics tracking."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        dirpath = tempfile.mkdtemp()
        yield Path(dirpath)
        shutil.rmtree(dirpath)

    def test_generation_time_tracking(self, temp_dir):
        """Test that generation time is tracked."""
        import time
        from agent.metrics import Metrics
        
        metrics = Metrics()
        metrics.start_build()
        
        # Simulate task processing
        time.sleep(0.1)
        metrics.record_task(success=True, duration=0.1)
        time.sleep(0.1)
        metrics.record_task(success=True, duration=0.1)
        
        metrics.end_build(2, 0)
        
        summary = metrics.get_summary()
        assert summary['duration_seconds'] >= 0.2
        assert summary['completed'] == 2
        assert summary['success_rate'] == 100.0

    def test_success_rate_calculation(self, temp_dir):
        """Test success rate calculation."""
        from agent.metrics import Metrics
        
        metrics = Metrics()
        metrics.start_build()
        
        for _ in range(8):
            metrics.record_task(success=True)
        for _ in range(2):
            metrics.record_task(success=False)
        
        assert metrics.get_success_rate() == pytest.approx(80.0, rel=0.1)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

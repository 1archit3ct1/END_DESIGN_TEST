"""
Tests for logger.py — Build console error logging.
"""

import pytest
import tempfile
import json
from pathlib import Path
import sys
from unittest.mock import patch

# Add agent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.logger import (
    setup_logger,
    init_build_console_log,
    get_build_console_logs,
    clear_build_console_logs,
    log_error,
    log_task_progress,
    export_build_console_logs,
    BuildConsoleHandler,
    _write_logs_to_file
)


class TestBuildConsoleHandler:
    """Test BuildConsoleHandler class."""

    def test_handler_initializes(self):
        """Test BuildConsoleHandler initializes without errors."""
        handler = BuildConsoleHandler()
        assert handler is not None

    def test_handler_stores_logs(self):
        """Test that handler stores log records."""
        from agent.logger import _build_console_logs, _build_console_logs

        # Clear existing logs
        clear_build_console_logs()

        logger = setup_logger('test_handler')
        
        # Log a message
        logger.info("Test message")

        logs = get_build_console_logs()
        assert len(logs) > 0
        assert any('Test message' in log.get('message', '') for log in logs)


class TestBuildConsoleLogging:
    """Test build console logging functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        clear_build_console_logs()

    def test_log_error_creates_entry(self):
        """Test that log_error creates a log entry."""
        log_error(
            task_id='test_task_1',
            message='Test error message',
            error_type='syntax'
        )

        logs = get_build_console_logs()
        assert len(logs) > 0

        error_log = logs[-1]
        assert error_log['level'] == 'ERROR'
        assert error_log['task_id'] == 'test_task_1'
        assert error_log['message'] == 'Test error message'
        assert error_log['error_type'] == 'syntax'

    def test_log_error_with_extra_data(self):
        """Test log_error with extra data."""
        extra_data = {'line': 10, 'column': 5}

        log_error(
            task_id='test_task_2',
            message='Error with details',
            error_type='syntax',
            extra_data=extra_data
        )

        logs = get_build_console_logs()
        error_log = logs[-1]

        assert error_log['extra_data'] == extra_data

    def test_log_task_progress_creates_entry(self):
        """Test that log_task_progress creates a log entry."""
        log_task_progress(
            task_id='test_task_3',
            status='running',
            message='Task is running'
        )

        logs = get_build_console_logs()
        assert len(logs) > 0

        progress_log = logs[-1]
        assert progress_log['level'] == 'INFO'
        assert progress_log['task_id'] == 'test_task_3'
        assert progress_log['status'] == 'running'
        assert progress_log['message'] == 'Task is running'

    def test_log_task_progress_different_statuses(self):
        """Test logging different task statuses."""
        statuses = ['pending', 'running', 'done', 'failed']

        for status in statuses:
            log_task_progress(
                task_id=f'task_{status}',
                status=status,
                message=f'Task {status}'
            )

        logs = get_build_console_logs()
        logged_statuses = [log['status'] for log in logs if 'status' in log]

        assert all(status in logged_statuses for status in statuses)

    def test_clear_build_console_logs(self):
        """Test clearing build console logs."""
        log_error('task1', 'Error 1')
        log_task_progress('task2', 'running', 'Running')

        logs = get_build_console_logs()
        assert len(logs) > 0

        clear_build_console_logs()

        logs = get_build_console_logs()
        assert len(logs) == 0

    def test_export_build_console_logs(self):
        """Test exporting logs as JSON."""
        log_error('task1', 'Error 1', 'syntax')
        log_task_progress('task2', 'done', 'Completed')

        json_export = export_build_console_logs()

        # Should be valid JSON
        parsed = json.loads(json_export)
        assert isinstance(parsed, list)
        assert len(parsed) > 0

    def test_log_has_timestamp(self):
        """Test that log entries have timestamps."""
        log_error('task1', 'Test error')

        logs = get_build_console_logs()
        assert 'timestamp' in logs[-1]
        assert logs[-1]['timestamp'] is not None

    def test_multiple_errors_logged(self):
        """Test multiple errors are logged correctly."""
        errors = [
            ('task1', 'Error 1', 'syntax'),
            ('task2', 'Error 2', 'generation'),
            ('task3', 'Error 3', 'file_write'),
        ]

        for task_id, message, error_type in errors:
            log_error(task_id, message, error_type)

        logs = get_build_console_logs()
        assert len(logs) >= 3

        # Verify all errors are present
        error_messages = [log['message'] for log in logs if log['level'] == 'ERROR']
        assert all(msg in error_messages for _, msg, _ in errors)


class TestBuildConsoleFileLogging:
    """Test build console file logging."""

    def setup_method(self):
        """Set up test fixtures."""
        clear_build_console_logs()
        self.temp_dir = tempfile.mkdtemp()
        self.log_path = Path(self.temp_dir) / 'build_console.json'

    def teardown_method(self):
        """Clean up test fixtures."""
        clear_build_console_logs()

    def test_init_build_console_log(self):
        """Test initializing build console log file."""
        init_build_console_log(self.log_path)

        # File should exist
        assert self.log_path.exists()

        # Should be empty JSON array
        with open(self.log_path, 'r') as f:
            data = json.load(f)
            assert data == []

    def test_logs_written_to_file(self):
        """Test that logs are written to file."""
        init_build_console_log(self.log_path)

        log_error('task1', 'Test error', 'syntax')
        log_task_progress('task2', 'running', 'Running')

        # Read file and verify
        with open(self.log_path, 'r') as f:
            data = json.load(f)

        assert len(data) >= 2
        assert any(log.get('task_id') == 'task1' for log in data)

    def test_file_log_contains_error_details(self):
        """Test file log contains error details."""
        init_build_console_log(self.log_path)

        log_error(
            task_id='task_file_test',
            message='Detailed error',
            error_type='syntax',
            extra_data={'line': 10}
        )

        with open(self.log_path, 'r') as f:
            data = json.load(f)

        error_log = next(
            (log for log in data if log.get('task_id') == 'task_file_test'),
            None
        )

        assert error_log is not None
        assert error_log['error_type'] == 'syntax'
        assert error_log['extra_data'] == {'line': 10}


class TestErrorLoggingForBuildConsole:
    """Test error logging specifically for build console display."""

    def setup_method(self):
        """Set up test fixtures."""
        clear_build_console_logs()

    def test_syntax_error_logged(self):
        """Test syntax error is logged for build console."""
        log_error(
            task_id='rust_backend.pkce',
            message='Unclosed brace in Rust code',
            error_type='syntax',
            extra_data={'line': 15, 'column': 3}
        )

        logs = get_build_console_logs()
        syntax_error = next(
            (log for log in logs if log.get('error_type') == 'syntax'),
            None
        )

        assert syntax_error is not None
        assert syntax_error['task_id'] == 'rust_backend.pkce'
        assert 'Unclosed brace' in syntax_error['message']

    def test_generation_error_logged(self):
        """Test generation error is logged for build console."""
        log_error(
            task_id='ui_component.button',
            message='LLM failed to generate code after 3 retries',
            error_type='generation'
        )

        logs = get_build_console_logs()
        gen_error = next(
            (log for log in logs if log.get('error_type') == 'generation'),
            None
        )

        assert gen_error is not None
        assert 'LLM failed' in gen_error['message']

    def test_file_write_error_logged(self):
        """Test file write error is logged for build console."""
        log_error(
            task_id='agent.python_agent',
            message='Permission denied writing file',
            error_type='file_write',
            extra_data={'path': '/output/agent.py'}
        )

        logs = get_build_console_logs()
        file_error = next(
            (log for log in logs if log.get('error_type') == 'file_write'),
            None
        )

        assert file_error is not None
        assert 'Permission denied' in file_error['message']

    def test_error_log_structure(self):
        """Test error log has correct structure for UI."""
        log_error(
            task_id='test.task',
            message='Test error',
            error_type='test_error',
            extra_data={'key': 'value'}
        )

        logs = get_build_console_logs()
        error_log = logs[-1]

        # Verify all required fields for UI display
        assert 'timestamp' in error_log
        assert 'level' in error_log
        assert 'logger' in error_log
        assert 'message' in error_log
        assert 'task_id' in error_log
        assert 'error_type' in error_log
        assert 'extra_data' in error_log

        # Verify values
        assert error_log['level'] == 'ERROR'
        assert error_log['task_id'] == 'test.task'
        assert error_log['error_type'] == 'test_error'

    def test_get_build_console_logs_returns_copy(self):
        """Test that get_build_console_logs returns a copy."""
        log_error('task1', 'Error 1')

        logs1 = get_build_console_logs()
        logs2 = get_build_console_logs()

        # Should be different objects
        assert logs1 is not logs2

        # Modifying one shouldn't affect the other
        logs1.append({'fake': 'log'})
        assert len(logs2) < len(logs1)


class TestLoggerIntegration:
    """Test logger integration with build console."""

    def setup_method(self):
        """Set up test fixtures."""
        clear_build_console_logs()

    def test_standard_logger_also_logs_to_build_console(self):
        """Test that standard logger also logs to build console."""
        logger = setup_logger('integration_test')

        # Clear logs from setup
        clear_build_console_logs()

        logger.error("Integration test error")

        logs = get_build_console_logs()
        assert len(logs) > 0
        assert any('Integration test error' in log.get('message', '') for log in logs)

    def test_logger_level_filtering(self):
        """Test that different log levels are captured."""
        logger = setup_logger('level_test')

        clear_build_console_logs()

        # DEBUG won't be captured since logger is INFO level
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

        logs = get_build_console_logs()

        # INFO, WARNING, ERROR should be captured (not DEBUG)
        messages = [log.get('message', '') for log in logs]
        assert any('Info' in msg for msg in messages)
        assert any('Warning' in msg for msg in messages)
        assert any('Error' in msg for msg in messages)
        # DEBUG should NOT be captured
        assert not any('Debug' in msg for msg in messages)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

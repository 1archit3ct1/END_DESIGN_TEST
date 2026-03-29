"""
Tests for error_handler.py — Centralized error handling.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch

# Add agent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.error_handler import (
    ErrorType,
    ErrorSeverity,
    RecoveryStrategy,
    AgentError,
    ErrorHandler,
    get_error_handler,
    handle_exception,
    _classify_exception
)


class TestErrorTypeEnums:
    """Test ErrorType enum values."""

    def test_error_type_values(self):
        """Test all error types are defined."""
        assert ErrorType.SYNTAX_ERROR.value == "syntax"
        assert ErrorType.GENERATION_ERROR.value == "generation"
        assert ErrorType.FILE_WRITE_ERROR.value == "file_write"
        assert ErrorType.LLM_API_ERROR.value == "llm_api"
        assert ErrorType.VALIDATION_ERROR.value == "validation"
        assert ErrorType.DEPENDENCY_ERROR.value == "dependency"
        assert ErrorType.CONFIG_ERROR.value == "config"
        assert ErrorType.TIMEOUT_ERROR.value == "timeout"
        assert ErrorType.UNKNOWN_ERROR.value == "unknown"


class TestErrorSeverity:
    """Test ErrorSeverity enum values."""

    def test_severity_values(self):
        """Test all severity levels are defined."""
        assert ErrorSeverity.LOW.value == "low"
        assert ErrorSeverity.MEDIUM.value == "medium"
        assert ErrorSeverity.HIGH.value == "high"
        assert ErrorSeverity.CRITICAL.value == "critical"


class TestRecoveryStrategy:
    """Test RecoveryStrategy enum values."""

    def test_strategy_values(self):
        """Test all recovery strategies are defined."""
        assert RecoveryStrategy.RETRY.value == "retry"
        assert RecoveryStrategy.RETRY_WITH_MODIFIED_PROMPT.value == "retry_modified"
        assert RecoveryStrategy.USE_FALLBACK.value == "fallback"
        assert RecoveryStrategy.SKIP_TASK.value == "skip"
        assert RecoveryStrategy.ABORT_BUILD.value == "abort"
        assert RecoveryStrategy.MANUAL_INTERVENTION.value == "manual"


class TestAgentError:
    """Test AgentError dataclass."""

    def test_create_agent_error(self):
        """Test creating AgentError instance."""
        error = AgentError(
            error_type=ErrorType.SYNTAX_ERROR,
            severity=ErrorSeverity.MEDIUM,
            message="Test syntax error",
            task_id="test_task"
        )

        assert error.error_type == ErrorType.SYNTAX_ERROR
        assert error.severity == ErrorSeverity.MEDIUM
        assert error.message == "Test syntax error"
        assert error.task_id == "test_task"
        assert error.retry_count == 0
        assert error.max_retries == 3

    def test_agent_error_to_dict(self):
        """Test converting AgentError to dictionary."""
        error = AgentError(
            error_type=ErrorType.GENERATION_ERROR,
            severity=ErrorSeverity.HIGH,
            message="Generation failed",
            task_id="gen_task",
            extra_data={'attempt': 1}
        )

        d = error.to_dict()

        assert d['error_type'] == 'generation'
        assert d['severity'] == 'high'
        assert d['message'] == 'Generation failed'
        assert d['task_id'] == 'gen_task'
        assert d['extra_data']['attempt'] == 1
        assert 'timestamp' in d

    def test_agent_error_can_retry(self):
        """Test retry capability check."""
        error = AgentError(
            error_type=ErrorType.SYNTAX_ERROR,
            severity=ErrorSeverity.LOW,
            message="Error",
            retry_count=0,
            max_retries=3
        )

        assert error.can_retry() is True

        error.retry_count = 3
        assert error.can_retry() is False

    def test_agent_error_get_recovery_strategy(self):
        """Test getting recovery strategy from error."""
        # Syntax error should recommend retry with modified prompt
        error = AgentError(
            error_type=ErrorType.SYNTAX_ERROR,
            severity=ErrorSeverity.LOW,
            message="Error"
        )
        assert error.get_recovery_strategy() == RecoveryStrategy.RETRY_WITH_MODIFIED_PROMPT

        # Critical error should abort
        error_critical = AgentError(
            error_type=ErrorType.SYNTAX_ERROR,
            severity=ErrorSeverity.CRITICAL,
            message="Critical error"
        )
        assert error_critical.get_recovery_strategy() == RecoveryStrategy.ABORT_BUILD

    def test_agent_error_with_exception(self):
        """Test AgentError with original exception."""
        try:
            raise ValueError("Test exception")
        except ValueError as e:
            error = AgentError(
                error_type=ErrorType.VALIDATION_ERROR,
                severity=ErrorSeverity.MEDIUM,
                message="Validation failed",
                original_exception=e
            )

            assert error.original_exception is e
            assert error.stack_trace is not None
            assert "ValueError" in error.stack_trace


class TestErrorHandler:
    """Test ErrorHandler class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.handler = ErrorHandler(max_retries=3)

    def test_error_handler_initializes(self):
        """Test ErrorHandler initializes correctly."""
        assert self.handler.max_retries == 3
        assert len(self.handler.error_history) == 0
        assert len(self.handler.task_error_counts) == 0

    def test_handle_error_tracks_history(self):
        """Test that handling error tracks in history."""
        error = AgentError(
            error_type=ErrorType.SYNTAX_ERROR,
            severity=ErrorSeverity.LOW,
            message="Test error",
            task_id="task1"
        )

        strategy = self.handler.handle_error(error)

        assert len(self.handler.error_history) == 1
        assert self.handler.error_history[0] == error
        assert strategy is not None

    def test_handle_error_tracks_task_counts(self):
        """Test that task error counts are tracked."""
        error1 = AgentError(
            error_type=ErrorType.SYNTAX_ERROR,
            severity=ErrorSeverity.LOW,
            message="Error 1",
            task_id="task1"
        )

        error2 = AgentError(
            error_type=ErrorType.GENERATION_ERROR,
            severity=ErrorSeverity.LOW,
            message="Error 2",
            task_id="task1"
        )

        self.handler.handle_error(error1)
        self.handler.handle_error(error2)

        assert self.handler.task_error_counts['task1'] == 2

    def test_handle_syntax_error(self):
        """Test handling syntax error."""
        error = AgentError(
            error_type=ErrorType.SYNTAX_ERROR,
            severity=ErrorSeverity.LOW,
            message="Syntax error",
            task_id="task1",
            retry_count=0
        )

        strategy = self.handler.handle_error(error)

        assert strategy == RecoveryStrategy.RETRY_WITH_MODIFIED_PROMPT

    def test_handle_syntax_error_no_retries(self):
        """Test handling syntax error when no retries left."""
        error = AgentError(
            error_type=ErrorType.SYNTAX_ERROR,
            severity=ErrorSeverity.LOW,
            message="Syntax error",
            task_id="task1",
            retry_count=3,
            max_retries=3
        )

        strategy = self.handler.handle_error(error)

        assert strategy == RecoveryStrategy.USE_FALLBACK

    def test_handle_generation_error(self):
        """Test handling generation error."""
        error = AgentError(
            error_type=ErrorType.GENERATION_ERROR,
            severity=ErrorSeverity.LOW,
            message="Generation failed",
            task_id="task1"
        )

        strategy = self.handler.handle_error(error)

        assert strategy == RecoveryStrategy.RETRY_WITH_MODIFIED_PROMPT

    def test_handle_file_write_error(self):
        """Test handling file write error."""
        error = AgentError(
            error_type=ErrorType.FILE_WRITE_ERROR,
            severity=ErrorSeverity.MEDIUM,
            message="Cannot write file",
            task_id="task1"
        )

        strategy = self.handler.handle_error(error)

        assert strategy == RecoveryStrategy.RETRY

    def test_handle_llm_api_error(self):
        """Test handling LLM API error."""
        error = AgentError(
            error_type=ErrorType.LLM_API_ERROR,
            severity=ErrorSeverity.HIGH,
            message="LLM API unavailable",
            task_id="task1"
        )

        strategy = self.handler.handle_error(error)

        assert strategy == RecoveryStrategy.RETRY

    def test_handle_timeout_error(self):
        """Test handling timeout error."""
        error = AgentError(
            error_type=ErrorType.TIMEOUT_ERROR,
            severity=ErrorSeverity.MEDIUM,
            message="Request timed out",
            task_id="task1"
        )

        strategy = self.handler.handle_error(error)

        assert strategy == RecoveryStrategy.RETRY

    def test_create_error(self):
        """Test creating error via handler."""
        error = self.handler.create_error(
            error_type=ErrorType.SYNTAX_ERROR,
            message="Test error",
            task_id="task1"
        )

        assert isinstance(error, AgentError)
        assert error.error_type == ErrorType.SYNTAX_ERROR
        assert error.message == "Test error"
        assert error.task_id == "task1"

    def test_create_error_with_exception(self):
        """Test creating error with exception."""
        try:
            raise ValueError("Test exception")
        except ValueError as e:
            error = self.handler.create_error(
                error_type=ErrorType.VALIDATION_ERROR,
                message="Validation failed",
                task_id="task1",
                exception=e
            )

            assert error.original_exception is e

    def test_get_task_error_count(self):
        """Test getting task error count."""
        error = AgentError(
            error_type=ErrorType.SYNTAX_ERROR,
            severity=ErrorSeverity.LOW,
            message="Error",
            task_id="task1"
        )

        self.handler.handle_error(error)
        self.handler.handle_error(error)

        count = self.handler.get_task_error_count('task1')
        assert count == 2

    def test_get_error_summary(self):
        """Test getting error summary."""
        error1 = AgentError(
            error_type=ErrorType.SYNTAX_ERROR,
            severity=ErrorSeverity.LOW,
            message="Error 1",
            task_id="task1"
        )

        error2 = AgentError(
            error_type=ErrorType.GENERATION_ERROR,
            severity=ErrorSeverity.LOW,
            message="Error 2",
            task_id="task2"
        )

        self.handler.handle_error(error1)
        self.handler.handle_error(error2)

        summary = self.handler.get_error_summary()

        assert summary['total_errors'] == 2
        assert 'syntax' in summary['errors_by_type']
        assert 'generation' in summary['errors_by_type']
        assert 'task1' in summary['tasks_with_errors']
        assert 'task2' in summary['tasks_with_errors']

    def test_clear_history(self):
        """Test clearing error history."""
        error = AgentError(
            error_type=ErrorType.SYNTAX_ERROR,
            severity=ErrorSeverity.LOW,
            message="Error",
            task_id="task1"
        )

        self.handler.handle_error(error)
        assert len(self.handler.error_history) > 0

        self.handler.clear_history()

        assert len(self.handler.error_history) == 0
        assert len(self.handler.task_error_counts) == 0

    def test_export_errors(self):
        """Test exporting errors."""
        error = AgentError(
            error_type=ErrorType.SYNTAX_ERROR,
            severity=ErrorSeverity.LOW,
            message="Error",
            task_id="task1"
        )

        self.handler.handle_error(error)

        exported = self.handler.export_errors()

        assert isinstance(exported, list)
        assert len(exported) == 1
        assert exported[0]['error_type'] == 'syntax'


class TestExceptionClassification:
    """Test exception classification."""

    def test_classify_syntax_error(self):
        """Test classifying SyntaxError."""
        try:
            raise SyntaxError("Invalid syntax")
        except SyntaxError as e:
            error_type, message = _classify_exception(e, None)
            assert error_type == ErrorType.SYNTAX_ERROR

    def test_classify_timeout_error(self):
        """Test classifying TimeoutError."""
        try:
            raise TimeoutError("Request timed out")
        except TimeoutError as e:
            error_type, message = _classify_exception(e, None)
            assert error_type == ErrorType.TIMEOUT_ERROR

    def test_classify_file_write_error(self):
        """Test classifying file write errors."""
        # FileNotFoundError
        try:
            raise FileNotFoundError("File not found")
        except FileNotFoundError as e:
            error_type, message = _classify_exception(e, None)
            assert error_type == ErrorType.FILE_WRITE_ERROR

        # PermissionError
        try:
            raise PermissionError("Permission denied")
        except PermissionError as e:
            error_type, message = _classify_exception(e, None)
            assert error_type == ErrorType.FILE_WRITE_ERROR

    def test_classify_llm_api_error(self):
        """Test classifying LLM API errors."""
        try:
            raise ConnectionError("Connection failed")
        except ConnectionError as e:
            error_type, message = _classify_exception(e, None)
            assert error_type == ErrorType.LLM_API_ERROR

    def test_classify_validation_error(self):
        """Test classifying validation errors."""
        try:
            raise ValueError("Invalid value")
        except ValueError as e:
            error_type, message = _classify_exception(e, None)
            assert error_type == ErrorType.VALIDATION_ERROR

    def test_classify_unknown_error(self):
        """Test classifying unknown errors."""
        try:
            raise RuntimeError("Unknown error")
        except RuntimeError as e:
            error_type, message = _classify_exception(e, None)
            assert error_type == ErrorType.UNKNOWN_ERROR

    def test_classify_with_context(self):
        """Test classifying with context."""
        try:
            raise ValueError("Invalid value")
        except ValueError as e:
            error_type, message = _classify_exception(e, "test context")
            assert "test context" in message


class TestHandleException:
    """Test handle_exception convenience function."""

    def setup_method(self):
        """Set up test fixtures."""
        # Clear default handler
        import agent.error_handler as eh
        eh._default_handler = None

    def test_handle_exception_returns_strategy(self):
        """Test handle_exception returns recovery strategy."""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            strategy = handle_exception(e, task_id="task1")
            assert strategy in RecoveryStrategy

    def test_handle_exception_tracks_error(self):
        """Test handle_exception tracks error."""
        handler = get_error_handler()
        handler.clear_history()

        try:
            raise SyntaxError("Test syntax error")
        except SyntaxError as e:
            handle_exception(e, task_id="task1")

        assert len(handler.error_history) > 0


class TestErrorHandlingAllTypes:
    """Test that all error types are handled correctly."""

    def setup_method(self):
        """Set up test fixtures."""
        self.handler = ErrorHandler(max_retries=3)

    def test_all_error_types_handled(self):
        """Test all error types return a valid strategy."""
        error_types = [
            ErrorType.SYNTAX_ERROR,
            ErrorType.GENERATION_ERROR,
            ErrorType.FILE_WRITE_ERROR,
            ErrorType.LLM_API_ERROR,
            ErrorType.VALIDATION_ERROR,
            ErrorType.DEPENDENCY_ERROR,
            ErrorType.CONFIG_ERROR,
            ErrorType.TIMEOUT_ERROR,
            ErrorType.UNKNOWN_ERROR,
        ]

        for error_type in error_types:
            error = AgentError(
                error_type=error_type,
                severity=ErrorSeverity.LOW,
                message=f"Test {error_type.value} error",
                task_id="task1"
            )

            strategy = self.handler.handle_error(error)

            assert strategy is not None
            assert isinstance(strategy, RecoveryStrategy)

    def test_all_severity_levels_handled(self):
        """Test all severity levels are handled."""
        severity_levels = [
            ErrorSeverity.LOW,
            ErrorSeverity.MEDIUM,
            ErrorSeverity.HIGH,
            ErrorSeverity.CRITICAL,
        ]

        for severity in severity_levels:
            error = AgentError(
                error_type=ErrorType.SYNTAX_ERROR,
                severity=severity,
                message=f"Test {severity.value} severity error",
                task_id="task1"
            )

            strategy = self.handler.handle_error(error)

            assert strategy is not None

            # Critical should always abort
            if severity == ErrorSeverity.CRITICAL:
                assert strategy == RecoveryStrategy.ABORT_BUILD


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

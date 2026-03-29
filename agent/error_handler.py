"""
Error Handler — Centralized error handling for the agent system.

Provides error classification, recovery strategies, and error reporting.
"""

from enum import Enum
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
import traceback

from .logger import setup_logger, log_error, log_task_progress

logger = setup_logger(__name__)


class ErrorType(Enum):
    """Types of errors that can occur during code generation."""
    SYNTAX_ERROR = "syntax"
    GENERATION_ERROR = "generation"
    FILE_WRITE_ERROR = "file_write"
    LLM_API_ERROR = "llm_api"
    VALIDATION_ERROR = "validation"
    DEPENDENCY_ERROR = "dependency"
    CONFIG_ERROR = "config"
    TIMEOUT_ERROR = "timeout"
    UNKNOWN_ERROR = "unknown"


class ErrorSeverity(Enum):
    """Severity levels for errors."""
    LOW = "low"           # Can be ignored or auto-fixed
    MEDIUM = "medium"     # Should be addressed but build can continue
    HIGH = "high"         # Build should stop or retry
    CRITICAL = "critical" # Build cannot continue


class RecoveryStrategy(Enum):
    """Available recovery strategies for errors."""
    RETRY = "retry"
    RETRY_WITH_MODIFIED_PROMPT = "retry_modified"
    USE_FALLBACK = "fallback"
    SKIP_TASK = "skip"
    ABORT_BUILD = "abort"
    MANUAL_INTERVENTION = "manual"


@dataclass
class AgentError:
    """Represents an error that occurred during agent execution."""
    error_type: ErrorType
    severity: ErrorSeverity
    message: str
    task_id: Optional[str] = None
    original_exception: Optional[Exception] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    retry_count: int = 0
    max_retries: int = 3
    extra_data: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None

    def __post_init__(self):
        if self.original_exception and not self.stack_trace:
            self.stack_trace = traceback.format_exc()

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for serialization."""
        return {
            'error_type': self.error_type.value,
            'severity': self.severity.value,
            'message': self.message,
            'task_id': self.task_id,
            'timestamp': self.timestamp,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'extra_data': self.extra_data,
            'stack_trace': self.stack_trace
        }

    def can_retry(self) -> bool:
        """Check if error can be retried."""
        return self.retry_count < self.max_retries

    def get_recovery_strategy(self) -> RecoveryStrategy:
        """Get recommended recovery strategy based on error type."""
        strategy_map = {
            ErrorType.SYNTAX_ERROR: RecoveryStrategy.RETRY_WITH_MODIFIED_PROMPT,
            ErrorType.GENERATION_ERROR: RecoveryStrategy.RETRY_WITH_MODIFIED_PROMPT,
            ErrorType.FILE_WRITE_ERROR: RecoveryStrategy.RETRY,
            ErrorType.LLM_API_ERROR: RecoveryStrategy.RETRY,
            ErrorType.VALIDATION_ERROR: RecoveryStrategy.RETRY_WITH_MODIFIED_PROMPT,
            ErrorType.DEPENDENCY_ERROR: RecoveryStrategy.SKIP_TASK,
            ErrorType.CONFIG_ERROR: RecoveryStrategy.MANUAL_INTERVENTION,
            ErrorType.TIMEOUT_ERROR: RecoveryStrategy.RETRY,
            ErrorType.UNKNOWN_ERROR: RecoveryStrategy.USE_FALLBACK,
        }

        base_strategy = strategy_map.get(self.error_type, RecoveryStrategy.USE_FALLBACK)

        # Adjust based on severity
        if self.severity == ErrorSeverity.CRITICAL:
            return RecoveryStrategy.ABORT_BUILD
        elif self.severity == ErrorSeverity.HIGH and not self.can_retry():
            return RecoveryStrategy.USE_FALLBACK

        return base_strategy


class ErrorHandler:
    """Centralized error handler for the agent system."""

    def __init__(self, max_retries: int = 3):
        """Initialize error handler.

        Args:
            max_retries: Maximum number of retries per task
        """
        self.max_retries = max_retries
        self.error_history: List[AgentError] = []
        self.task_error_counts: Dict[str, int] = {}
        self._error_handlers: Dict[ErrorType, Callable] = {}
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register default error handlers."""
        self._error_handlers[ErrorType.SYNTAX_ERROR] = self._handle_syntax_error
        self._error_handlers[ErrorType.GENERATION_ERROR] = self._handle_generation_error
        self._error_handlers[ErrorType.FILE_WRITE_ERROR] = self._handle_file_write_error
        self._error_handlers[ErrorType.LLM_API_ERROR] = self._handle_llm_api_error
        self._error_handlers[ErrorType.TIMEOUT_ERROR] = self._handle_timeout_error

    def handle_error(self, error: AgentError) -> RecoveryStrategy:
        """Handle an error and return recommended recovery strategy.

        Args:
            error: AgentError instance

        Returns:
            Recommended RecoveryStrategy
        """
        # Check for critical severity first - should always abort
        if error.severity == ErrorSeverity.CRITICAL:
            return RecoveryStrategy.ABORT_BUILD

        # Track error
        self.error_history.append(error)

        if error.task_id:
            self.task_error_counts[error.task_id] = \
                self.task_error_counts.get(error.task_id, 0) + 1

        # Log to build console
        log_error(
            task_id=error.task_id or 'unknown',
            message=error.message,
            error_type=error.error_type.value,
            extra_data=error.to_dict()
        )

        # Log with appropriate level
        if error.severity == ErrorSeverity.HIGH:
            logger.error(f"High severity error: {error.message}")
        elif error.severity == ErrorSeverity.MEDIUM:
            logger.warning(f"Medium severity error: {error.message}")
        else:
            logger.info(f"Low severity error: {error.message}")

        # Call specific handler if registered
        handler = self._error_handlers.get(error.error_type)
        if handler:
            return handler(error)

        return error.get_recovery_strategy()

    def _handle_syntax_error(self, error: AgentError) -> RecoveryStrategy:
        """Handle syntax errors.

        Args:
            error: AgentError instance

        Returns:
            RecoveryStrategy
        """
        if error.can_retry():
            error.extra_data['suggestion'] = 'Retry with syntax validation'
            return RecoveryStrategy.RETRY_WITH_MODIFIED_PROMPT
        else:
            error.extra_data['suggestion'] = 'Use fallback template'
            return RecoveryStrategy.USE_FALLBACK

    def _handle_generation_error(self, error: AgentError) -> RecoveryStrategy:
        """Handle code generation errors.

        Args:
            error: AgentError instance

        Returns:
            RecoveryStrategy
        """
        if error.can_retry():
            error.extra_data['suggestion'] = 'Retry with modified prompt'
            return RecoveryStrategy.RETRY_WITH_MODIFIED_PROMPT
        else:
            error.extra_data['suggestion'] = 'Use fallback or skip'
            return RecoveryStrategy.USE_FALLBACK

    def _handle_file_write_error(self, error: AgentError) -> RecoveryStrategy:
        """Handle file write errors.

        Args:
            error: AgentError instance

        Returns:
            RecoveryStrategy
        """
        if error.can_retry():
            error.extra_data['suggestion'] = 'Retry file write'
            return RecoveryStrategy.RETRY
        else:
            error.extra_data['suggestion'] = 'Check disk space and permissions'
            return RecoveryStrategy.MANUAL_INTERVENTION

    def _handle_llm_api_error(self, error: AgentError) -> RecoveryStrategy:
        """Handle LLM API errors.

        Args:
            error: AgentError instance

        Returns:
            RecoveryStrategy
        """
        if error.can_retry():
            error.extra_data['suggestion'] = 'Retry LLM call with backoff'
            return RecoveryStrategy.RETRY
        else:
            error.extra_data['suggestion'] = 'Use fallback template'
            return RecoveryStrategy.USE_FALLBACK

    def _handle_timeout_error(self, error: AgentError) -> RecoveryStrategy:
        """Handle timeout errors.

        Args:
            error: AgentError instance

        Returns:
            RecoveryStrategy
        """
        if error.can_retry():
            error.extra_data['suggestion'] = 'Retry with increased timeout'
            return RecoveryStrategy.RETRY
        else:
            error.extra_data['suggestion'] = 'Skip or use fallback'
            return RecoveryStrategy.USE_FALLBACK

    def create_error(
        self,
        error_type: ErrorType,
        message: str,
        task_id: Optional[str] = None,
        exception: Optional[Exception] = None,
        severity: Optional[ErrorSeverity] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> AgentError:
        """Create an AgentError instance.

        Args:
            error_type: Type of error
            message: Error message
            task_id: Associated task ID
            exception: Original exception if any
            severity: Error severity (auto-determined if not provided)
            extra_data: Additional error data

        Returns:
            AgentError instance
        """
        # Auto-determine severity if not provided
        if severity is None:
            severity = self._determine_severity(error_type, exception)

        return AgentError(
            error_type=error_type,
            severity=severity,
            message=message,
            task_id=task_id,
            original_exception=exception,
            max_retries=self.max_retries,
            extra_data=extra_data or {}
        )

    def _determine_severity(
        self,
        error_type: ErrorType,
        exception: Optional[Exception]
    ) -> ErrorSeverity:
        """Determine error severity based on type and exception.

        Args:
            error_type: Type of error
            exception: Original exception if any

        Returns:
            ErrorSeverity level
        """
        # Critical errors that should abort build
        critical_exceptions = (KeyboardInterrupt, SystemExit, MemoryError)
        if exception and isinstance(exception, critical_exceptions):
            return ErrorSeverity.CRITICAL

        # High severity errors
        high_severity_types = {
            ErrorType.CONFIG_ERROR,
            ErrorType.DEPENDENCY_ERROR,
        }
        if error_type in high_severity_types:
            return ErrorSeverity.HIGH

        # Medium severity errors
        medium_severity_types = {
            ErrorType.FILE_WRITE_ERROR,
            ErrorType.VALIDATION_ERROR,
        }
        if error_type in medium_severity_types:
            return ErrorSeverity.MEDIUM

        # Default to low severity for retryable errors
        return ErrorSeverity.LOW

    def get_task_error_count(self, task_id: str) -> int:
        """Get error count for a specific task.

        Args:
            task_id: Task ID

        Returns:
            Number of errors for task
        """
        return self.task_error_counts.get(task_id, 0)

    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of all errors.

        Returns:
            Error summary dictionary
        """
        error_counts = {}
        for error in self.error_history:
            type_name = error.error_type.value
            error_counts[type_name] = error_counts.get(type_name, 0) + 1

        return {
            'total_errors': len(self.error_history),
            'errors_by_type': error_counts,
            'tasks_with_errors': list(self.task_error_counts.keys()),
            'critical_errors': sum(
                1 for e in self.error_history
                if e.severity == ErrorSeverity.CRITICAL
            ),
            'retryable_errors': sum(
                1 for e in self.error_history
                if e.can_retry()
            )
        }

    def clear_history(self):
        """Clear error history."""
        self.error_history.clear()
        self.task_error_counts.clear()

    def export_errors(self) -> List[Dict[str, Any]]:
        """Export all errors as list of dictionaries.

        Returns:
            List of error dictionaries
        """
        return [error.to_dict() for error in self.error_history]


# Convenience functions for direct usage
_default_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Get the default error handler instance.

    Returns:
        ErrorHandler instance
    """
    global _default_handler
    if _default_handler is None:
        _default_handler = ErrorHandler()
    return _default_handler


def handle_exception(
    exception: Exception,
    task_id: Optional[str] = None,
    context: Optional[str] = None
) -> RecoveryStrategy:
    """Handle an exception using the default error handler.

    Args:
        exception: Exception to handle
        task_id: Associated task ID
        context: Additional context about where error occurred

    Returns:
        Recommended RecoveryStrategy
    """
    handler = get_error_handler()

    # Classify exception
    error_type, message = _classify_exception(exception, context)

    error = handler.create_error(
        error_type=error_type,
        message=message,
        task_id=task_id,
        exception=exception
    )

    return handler.handle_error(error)


def _classify_exception(
    exception: Exception,
    context: Optional[str]
) -> tuple[ErrorType, str]:
    """Classify exception into error type and message.

    Args:
        exception: Exception to classify
        context: Additional context

    Returns:
        Tuple of (ErrorType, message)
    """
    message = str(exception) or exception.__class__.__name__
    if context:
        message = f"{context}: {message}"

    # Classify based on exception type
    if isinstance(exception, SyntaxError):
        return ErrorType.SYNTAX_ERROR, message
    elif isinstance(exception, (TimeoutError,)):
        return ErrorType.TIMEOUT_ERROR, message
    elif isinstance(exception, (ConnectionError, ConnectionRefusedError)):
        return ErrorType.LLM_API_ERROR, message
    elif isinstance(exception, (FileNotFoundError, PermissionError)):
        return ErrorType.FILE_WRITE_ERROR, message
    elif isinstance(exception, IOError):
        return ErrorType.FILE_WRITE_ERROR, message
    elif isinstance(exception, ValueError):
        return ErrorType.VALIDATION_ERROR, message
    else:
        return ErrorType.UNKNOWN_ERROR, message

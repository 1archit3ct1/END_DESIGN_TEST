"""
Logger setup for Python Agent.

Includes build console logging for UI integration.
"""

import logging
import sys
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


# Global list to store build console logs
_build_console_logs: List[Dict[str, Any]] = []
_build_console_log_path: Optional[Path] = None


class BuildConsoleHandler(logging.Handler):
    """Custom logging handler that stores logs for build console UI."""

    def emit(self, record: logging.LogRecord):
        """Store log entry for build console.

        Args:
            record: Log record to store
        """
        global _build_console_logs

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'task_id': getattr(record, 'task_id', None),
            'error_type': getattr(record, 'error_type', None) if record.levelname == 'ERROR' else None
        }

        _build_console_logs.append(log_entry)

        # Write to file if path is set
        if _build_console_log_path:
            _write_logs_to_file()


def _write_logs_to_file():
    """Write build console logs to file."""
    global _build_console_logs, _build_console_log_path

    if _build_console_log_path:
        try:
            with open(_build_console_log_path, 'w', encoding='utf-8') as f:
                json.dump(_build_console_logs, f, indent=2)
        except Exception as e:
            print(f"Failed to write build console logs: {e}")


def setup_logger(name: str) -> logging.Logger:
    """Set up logger with console and file handlers.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # File handler
    file_handler = logging.FileHandler('agent.log', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # Build console handler (for UI integration)
    build_console_handler = BuildConsoleHandler()
    build_console_handler.setLevel(logging.DEBUG)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Build console uses simpler format
    build_console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    build_console_handler.setFormatter(build_console_formatter)

    # Add handlers
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        logger.addHandler(build_console_handler)

    return logger


def init_build_console_log(log_path: Path):
    """Initialize build console log file.

    Args:
        log_path: Path to store build console logs
    """
    global _build_console_logs, _build_console_log_path

    _build_console_log_path = log_path
    _build_console_logs = []

    # Write initial empty array
    _write_logs_to_file()


def get_build_console_logs() -> List[Dict[str, Any]]:
    """Get all build console logs.

    Returns:
        List of log entries
    """
    return _build_console_logs.copy()


def clear_build_console_logs():
    """Clear build console logs."""
    global _build_console_logs

    _build_console_logs = []

    if _build_console_log_path:
        _write_logs_to_file()


def log_error(task_id: str, message: str, error_type: str = None,
              extra_data: Dict[str, Any] = None):
    """Log an error specifically for build console display.

    Args:
        task_id: Task ID associated with error
        message: Error message
        error_type: Type of error (syntax, generation, file_write, etc.)
        extra_data: Additional error data
    """
    global _build_console_logs

    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'level': 'ERROR',
        'logger': 'build_console',
        'message': message,
        'task_id': task_id,
        'error_type': error_type,
        'extra_data': extra_data or {}
    }

    _build_console_logs.append(log_entry)

    # Also log via standard logger
    logger = logging.getLogger('build_console')
    logger.error(f"[{task_id}] {message}", extra={
        'task_id': task_id,
        'error_type': error_type
    })

    if _build_console_log_path:
        _write_logs_to_file()


def log_task_progress(task_id: str, status: str, message: str):
    """Log task progress for build console display.

    Args:
        task_id: Task ID
        status: Task status (pending, running, done, failed)
        message: Progress message
    """
    global _build_console_logs

    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'level': 'INFO',
        'logger': 'build_console',
        'message': message,
        'task_id': task_id,
        'status': status
    }

    _build_console_logs.append(log_entry)

    logger = logging.getLogger('build_console')
    logger.info(f"[{task_id}] {message}", extra={'task_id': task_id})

    if _build_console_log_path:
        _write_logs_to_file()


def export_build_console_logs() -> str:
    """Export build console logs as JSON string.

    Returns:
        JSON string of logs
    """
    return json.dumps(_build_console_logs, indent=2)

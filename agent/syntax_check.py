"""
Syntax Checker — Validate generated code (Python + JS + Rust).
"""

import re
from typing import Optional, Dict, Any

from .logger import setup_logger

logger = setup_logger(__name__)


class SyntaxErrorInfo:
    """Information about a syntax error."""

    def __init__(self, message: str, line: Optional[int] = None,
                 column: Optional[int] = None, error_type: str = "syntax"):
        self.message = message
        self.line = line
        self.column = column
        self.error_type = error_type

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'message': self.message,
            'line': self.line,
            'column': self.column,
            'error_type': self.error_type
        }


class SyntaxCheckResult:
    """Result of a syntax check."""

    def __init__(self, is_valid: bool, error: Optional[SyntaxErrorInfo] = None):
        self.is_valid = is_valid
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'is_valid': self.is_valid,
            'error': self.error.to_dict() if self.error else None
        }


class SyntaxChecker:
    """Validate syntax of generated code."""

    def check_syntax(self, code: str, file_ext: str) -> SyntaxCheckResult:
        """Check syntax of generated code.

        Args:
            code: Generated code string
            file_ext: File extension (.py, .ts, .rs, etc.)

        Returns:
            SyntaxCheckResult with validation status and error details
        """
        if file_ext == '.py':
            return self._check_python_syntax(code)
        elif file_ext in ['.ts', '.tsx', '.js', '.jsx']:
            return self._check_javascript_syntax(code)
        elif file_ext == '.rs':
            return self._check_rust_syntax(code)
        else:
            logger.warning(f"Unknown file extension: {file_ext}, skipping syntax check")
            return SyntaxCheckResult(is_valid=True)

    def _check_python_syntax(self, code: str) -> SyntaxCheckResult:
        """Check Python syntax.

        Args:
            code: Python code string

        Returns:
            SyntaxCheckResult with validation status and error details
        """
        try:
            compile(code, '<string>', 'exec')
            logger.debug("Python syntax check passed")
            return SyntaxCheckResult(is_valid=True)
        except SyntaxError as e:
            error = SyntaxErrorInfo(
                message=str(e),
                line=e.lineno,
                column=e.offset,
                error_type="syntax"
            )
            logger.error(f"Python syntax error: {e}")
            return SyntaxCheckResult(is_valid=False, error=error)

    def _check_javascript_syntax(self, code: str) -> SyntaxCheckResult:
        """Check JavaScript/TypeScript syntax (basic validation).

        Args:
            code: JavaScript/TypeScript code string

        Returns:
            SyntaxCheckResult with validation status and error details
        """
        # Basic validation - check for balanced braces
        braces = {'{': '}', '(': ')', '[': ']'}
        stack = []
        line = 1
        column = 1

        for char in code:
            if char == '\n':
                line += 1
                column = 1
            else:
                column += 1

            if char in braces:
                stack.append((char, line, column))
            elif char in braces.values():
                if not stack:
                    error = SyntaxErrorInfo(
                        message=f"Unexpected '{char}' - no matching opening brace",
                        line=line,
                        column=column,
                        error_type="syntax"
                    )
                    logger.error(f"JavaScript syntax error: {error.message}")
                    return SyntaxCheckResult(is_valid=False, error=error)
                opening, open_line, open_col = stack.pop()
                if braces[opening] != char:
                    error = SyntaxErrorInfo(
                        message=f"Mismatched braces: expected '{braces[opening]}' but found '{char}'",
                        line=line,
                        column=column,
                        error_type="syntax"
                    )
                    logger.error(f"JavaScript syntax error: {error.message}")
                    return SyntaxCheckResult(is_valid=False, error=error)

        if stack:
            opening, open_line, open_col = stack[-1]
            error = SyntaxErrorInfo(
                message=f"Unclosed '{opening}' brace",
                line=open_line,
                column=open_col,
                error_type="syntax"
            )
            logger.error(f"JavaScript syntax error: {error.message}")
            return SyntaxCheckResult(is_valid=False, error=error)

        logger.debug("JavaScript syntax check passed")
        return SyntaxCheckResult(is_valid=True)

    def _check_rust_syntax(self, code: str) -> SyntaxCheckResult:
        """Check Rust syntax (basic validation).

        Args:
            code: Rust code string

        Returns:
            SyntaxCheckResult with validation status and error details
        """
        # Basic validation - check for balanced braces
        braces = {'{': '}', '(': ')', '[': ']'}
        stack = []
        line = 1
        column = 1

        for char in code:
            if char == '\n':
                line += 1
                column = 1
            else:
                column += 1

            if char in braces:
                stack.append((char, line, column))
            elif char in braces.values():
                if not stack:
                    error = SyntaxErrorInfo(
                        message=f"Unexpected '{char}' - no matching opening brace",
                        line=line,
                        column=column,
                        error_type="syntax"
                    )
                    logger.error(f"Rust syntax error: {error.message}")
                    return SyntaxCheckResult(is_valid=False, error=error)
                opening, open_line, open_col = stack.pop()
                if braces[opening] != char:
                    error = SyntaxErrorInfo(
                        message=f"Mismatched braces: expected '{braces[opening]}' but found '{char}'",
                        line=line,
                        column=column,
                        error_type="syntax"
                    )
                    logger.error(f"Rust syntax error: {error.message}")
                    return SyntaxCheckResult(is_valid=False, error=error)

        if stack:
            opening, open_line, open_col = stack[-1]
            error = SyntaxErrorInfo(
                message=f"Unclosed '{opening}' brace",
                line=open_line,
                column=open_col,
                error_type="syntax"
            )
            logger.error(f"Rust syntax error: {error.message}")
            return SyntaxCheckResult(is_valid=False, error=error)

        # Check for common Rust keywords
        if 'fn ' not in code and 'struct ' not in code and 'impl ' not in code:
            logger.warning("Rust code may be missing function/struct definitions")

        logger.debug("Rust syntax check passed")
        return SyntaxCheckResult(is_valid=True)

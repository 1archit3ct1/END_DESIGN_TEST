"""
Syntax Checker — Validate generated code (Python + JS + Rust).
"""

import re
from typing import Optional

from .logger import setup_logger

logger = setup_logger(__name__)


class SyntaxChecker:
    """Validate syntax of generated code."""

    def check_syntax(self, code: str, file_ext: str) -> bool:
        """Check syntax of generated code.
        
        Args:
            code: Generated code string
            file_ext: File extension (.py, .ts, .rs, etc.)
            
        Returns:
            True if syntax is valid
        """
        if file_ext == '.py':
            return self._check_python_syntax(code)
        elif file_ext in ['.ts', '.tsx', '.js', '.jsx']:
            return self._check_javascript_syntax(code)
        elif file_ext == '.rs':
            return self._check_rust_syntax(code)
        else:
            logger.warning(f"Unknown file extension: {file_ext}, skipping syntax check")
            return True

    def _check_python_syntax(self, code: str) -> bool:
        """Check Python syntax.
        
        Args:
            code: Python code string
            
        Returns:
            True if syntax is valid
        """
        try:
            compile(code, '<string>', 'exec')
            logger.debug("Python syntax check passed")
            return True
        except SyntaxError as e:
            logger.error(f"Python syntax error: {e}")
            return False

    def _check_javascript_syntax(self, code: str) -> bool:
        """Check JavaScript/TypeScript syntax (basic validation).
        
        Args:
            code: JavaScript/TypeScript code string
            
        Returns:
            True if syntax appears valid
        """
        # Basic validation - check for balanced braces
        braces = {'{': '}', '(': ')', '[': ']'}
        stack = []
        
        for char in code:
            if char in braces:
                stack.append(char)
            elif char in braces.values():
                if not stack:
                    logger.error("JavaScript syntax error: unbalanced braces")
                    return False
                opening = stack.pop()
                if braces[opening] != char:
                    logger.error("JavaScript syntax error: mismatched braces")
                    return False
        
        if stack:
            logger.error("JavaScript syntax error: unclosed braces")
            return False

        logger.debug("JavaScript syntax check passed")
        return True

    def _check_rust_syntax(self, code: str) -> bool:
        """Check Rust syntax (basic validation).
        
        Args:
            code: Rust code string
            
        Returns:
            True if syntax appears valid
        """
        # Basic validation - check for balanced braces
        braces = {'{': '}', '(': ')', '[': ']'}
        stack = []
        
        for char in code:
            if char in braces:
                stack.append(char)
            elif char in braces.values():
                if not stack:
                    logger.error("Rust syntax error: unbalanced braces")
                    return False
                opening = stack.pop()
                if braces[opening] != char:
                    logger.error("Rust syntax error: mismatched braces")
                    return False
        
        if stack:
            logger.error("Rust syntax error: unclosed braces")
            return False

        # Check for common Rust keywords
        if 'fn ' not in code and 'struct ' not in code and 'impl ' not in code:
            logger.warning("Rust code may be missing function/struct definitions")

        logger.debug("Rust syntax check passed")
        return True

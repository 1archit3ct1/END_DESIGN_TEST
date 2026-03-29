#!/usr/bin/env python3
"""
Code Formatter — Format generated code using prettier/black.

Supports:
- Python: black formatter
- JavaScript/TypeScript: prettier
- Rust: rustfmt (via cargo fmt)
"""

import subprocess
import tempfile
import os
from pathlib import Path
from typing import Optional, Tuple

from .logger import setup_logger

logger = setup_logger(__name__)


class CodeFormatter:
    """Format generated code using standard formatters."""

    def __init__(self):
        """Initialize code formatter."""
        self.black_available = self._check_black()
        self.prettier_available = self._check_prettier()
        self.rustfmt_available = self._check_rustfmt()

    def _check_black(self) -> bool:
        """Check if black is available."""
        try:
            result = subprocess.run(
                ['black', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("Black formatter not available")
            return False

    def _check_prettier(self) -> bool:
        """Check if prettier is available."""
        try:
            result = subprocess.run(
                ['npx', 'prettier', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("Prettier formatter not available")
            return False

    def _check_rustfmt(self) -> bool:
        """Check if rustfmt is available."""
        try:
            result = subprocess.run(
                ['rustfmt', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("Rustfmt formatter not available")
            return False

    def format_code(self, code: str, file_ext: str, file_path: Optional[str] = None) -> Tuple[str, bool]:
        """Format code using appropriate formatter.

        Args:
            code: Code string to format
            file_ext: File extension
            file_path: Optional file path for context

        Returns:
            Tuple of (formatted_code, success)
        """
        if file_ext == '.py':
            return self._format_python(code)
        elif file_ext in ['.ts', '.tsx', '.js', '.jsx', '.css', '.json', '.md', '.html']:
            return self._format_javascript(code, file_ext)
        elif file_ext == '.rs':
            return self._format_rust(code)
        else:
            logger.warning(f"No formatter for extension: {file_ext}")
            return code, True

    def _format_python(self, code: str) -> Tuple[str, bool]:
        """Format Python code using black.

        Args:
            code: Python code string

        Returns:
            Tuple of (formatted_code, success)
        """
        if not self.black_available:
            logger.info("Black not available, skipping Python formatting")
            return code, True

        try:
            result = subprocess.run(
                ['black', '-', '-q'],
                input=code,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                logger.debug("Python code formatted with black")
                return result.stdout, True
            else:
                logger.error(f"Black formatting error: {result.stderr}")
                return code, False

        except subprocess.TimeoutExpired:
            logger.error("Black formatting timed out")
            return code, False
        except Exception as e:
            logger.error(f"Black formatting failed: {e}")
            return code, False

    def _format_javascript(self, code: str, file_ext: str) -> Tuple[str, bool]:
        """Format JavaScript/TypeScript code using prettier.

        Args:
            code: Code string
            file_ext: File extension

        Returns:
            Tuple of (formatted_code, success)
        """
        if not self.prettier_available:
            logger.info("Prettier not available, skipping JS/TS formatting")
            return code, True

        # Map extension to prettier parser
        parser_map = {
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.js': 'babel',
            '.jsx': 'babel',
            '.css': 'css',
            '.json': 'json',
            '.md': 'markdown',
            '.html': 'html',
        }

        parser = parser_map.get(file_ext, 'babel')

        try:
            # Create temp file for prettier to determine parser
            with tempfile.NamedTemporaryFile(mode='w', suffix=file_ext, delete=False) as f:
                f.write(code)
                temp_path = f.name

            try:
                result = subprocess.run(
                    ['npx', 'prettier', '--write', temp_path, '--parser', parser],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    # Read formatted content
                    with open(temp_path, 'r') as f:
                        formatted_code = f.read()
                    logger.debug(f"Code formatted with prettier ({parser})")
                    return formatted_code, True
                else:
                    logger.error(f"Prettier formatting error: {result.stderr}")
                    return code, False

            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)

        except subprocess.TimeoutExpired:
            logger.error("Prettier formatting timed out")
            return code, False
        except Exception as e:
            logger.error(f"Prettier formatting failed: {e}")
            return code, False

    def _format_rust(self, code: str) -> Tuple[str, bool]:
        """Format Rust code using rustfmt.

        Args:
            code: Rust code string

        Returns:
            Tuple of (formatted_code, success)
        """
        if not self.rustfmt_available:
            logger.info("Rustfmt not available, skipping Rust formatting")
            return code, True

        try:
            result = subprocess.run(
                ['rustfmt', '--emit', 'stdout'],
                input=code,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                logger.debug("Rust code formatted with rustfmt")
                return result.stdout, True
            else:
                logger.error(f"Rustfmt formatting error: {result.stderr}")
                return code, False

        except subprocess.TimeoutExpired:
            logger.error("Rustfmt formatting timed out")
            return code, False
        except Exception as e:
            logger.error(f"Rustfmt formatting failed: {e}")
            return code, False

    def get_formatter_status(self) -> dict:
        """Get status of all formatters.

        Returns:
            Dictionary with formatter availability
        """
        return {
            'black': self.black_available,
            'prettier': self.prettier_available,
            'rustfmt': self.rustfmt_available,
        }


# Convenience function for direct usage
def format_code(code: str, file_ext: str) -> Tuple[str, bool]:
    """Format code using appropriate formatter.

    Args:
        code: Code string to format
        file_ext: File extension

    Returns:
        Tuple of (formatted_code, success)
    """
    formatter = CodeFormatter()
    return formatter.format_code(code, file_ext)

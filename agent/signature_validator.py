#!/usr/bin/env python3
"""
Function Signature Validator — Validate function signatures in generated code.

Supports:
- Python: def function_name(args) -> return_type
- Rust: fn function_name(args) -> ReturnType
- TypeScript: function name(args): ReturnType or const name = (args): ReturnType
"""

import re
from typing import Dict, Any, List, Tuple, Optional

from .logger import setup_logger

logger = setup_logger(__name__)


class SignatureValidator:
    """Validate function signatures in generated code."""

    # Python function pattern: def name(args) -> return_type:
    PYTHON_FUNC_PATTERN = re.compile(
        r'^\s*def\s+(\w+)\s*\(([^)]*)\)\s*(?:->\s*([\w\[\],\s]+))?\s*:',
        re.MULTILINE
    )

    # Rust function pattern: fn name(args) -> ReturnType (including generics)
    RUST_FUNC_PATTERN = re.compile(
        r'^\s*(?:pub\s+)?fn\s+(\w+)\s*(?:<[^>]*>)?\s*\(([^)]*)\)\s*(?:->\s*([\w<>:&,\s]+))?',
        re.MULTILINE
    )

    # TypeScript function pattern: function name(args): ReturnType
    TS_FUNC_PATTERN = re.compile(
        r'^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)\s*(?::\s*([\w<>|,\s]+))?',
        re.MULTILINE
    )

    # TypeScript arrow function pattern: const name = (args): ReturnType
    TS_ARROW_PATTERN = re.compile(
        r'^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(([^)]*)\)\s*(?::\s*([\w<>|,\s]+))?',
        re.MULTILINE
    )

    def validate_signatures(self, code: str, language: str) -> Tuple[bool, List[Dict[str, Any]]]:
        """Validate function signatures in code.

        Args:
            code: Code string to validate
            language: Programming language

        Returns:
            Tuple of (is_valid, list of function info dicts)
        """
        if language == 'python':
            return self._validate_python(code)
        elif language == 'rust':
            return self._validate_rust(code)
        elif language in ['typescript', 'javascript']:
            return self._validate_typescript(code)
        else:
            logger.warning(f"Unknown language: {language}, skipping validation")
            return True, []

    def _validate_python(self, code: str) -> Tuple[bool, List[Dict[str, Any]]]:
        """Validate Python function signatures.

        Args:
            code: Python code string

        Returns:
            Tuple of (is_valid, list of function info)
        """
        functions = []
        matches = self.PYTHON_FUNC_PATTERN.finditer(code)

        for match in matches:
            func_name = match.group(1)
            args = match.group(2).strip()
            return_type = match.group(3).strip() if match.group(3) else None

            func_info = {
                'name': func_name,
                'args': args,
                'return_type': return_type,
                'line': code[:match.start()].count('\n') + 1
            }

            # Validate function name
            if not func_name.isidentifier():
                logger.error(f"Invalid Python function name: {func_name}")
                return False, functions

            functions.append(func_info)

        logger.debug(f"Found {len(functions)} Python functions")
        return True, functions

    def _validate_rust(self, code: str) -> Tuple[bool, List[Dict[str, Any]]]:
        """Validate Rust function signatures.

        Args:
            code: Rust code string

        Returns:
            Tuple of (is_valid, list of function info)
        """
        functions = []
        matches = self.RUST_FUNC_PATTERN.finditer(code)

        for match in matches:
            func_name = match.group(1)
            args = match.group(2).strip()
            return_type = match.group(3).strip() if match.group(3) else None

            func_info = {
                'name': func_name,
                'args': args,
                'return_type': return_type,
                'line': code[:match.start()].count('\n') + 1
            }

            # Validate function name (snake_case convention)
            if not re.match(r'^[a-z_][a-z0-9_]*$', func_name):
                logger.warning(f"Rust function name may not follow snake_case: {func_name}")

            functions.append(func_info)

        logger.debug(f"Found {len(functions)} Rust functions")
        return True, functions

    def _validate_typescript(self, code: str) -> Tuple[bool, List[Dict[str, Any]]]:
        """Validate TypeScript function signatures.

        Args:
            code: TypeScript code string

        Returns:
            Tuple of (is_valid, list of function info)
        """
        functions = []

        # Check regular functions
        for match in self.TS_FUNC_PATTERN.finditer(code):
            func_name = match.group(1)
            args = match.group(2).strip()
            return_type = match.group(3).strip() if match.group(3) else None

            func_info = {
                'name': func_name,
                'args': args,
                'return_type': return_type,
                'type': 'function',
                'line': code[:match.start()].count('\n') + 1
            }
            functions.append(func_info)

        # Check arrow functions
        for match in self.TS_ARROW_PATTERN.finditer(code):
            func_name = match.group(1)
            args = match.group(2).strip()
            return_type = match.group(3).strip() if match.group(3) else None

            func_info = {
                'name': func_name,
                'args': args,
                'return_type': return_type,
                'type': 'arrow',
                'line': code[:match.start()].count('\n') + 1
            }
            functions.append(func_info)

        logger.debug(f"Found {len(functions)} TypeScript functions")
        return True, functions

    def check_function_exists(self, code: str, language: str, function_name: str) -> bool:
        """Check if a specific function exists in code.

        Args:
            code: Code string
            language: Programming language
            function_name: Name of function to find

        Returns:
            True if function exists
        """
        _, functions = self.validate_signatures(code, language)

        for func in functions:
            if func['name'] == function_name:
                return True
        return False

    def get_function_names(self, code: str, language: str) -> List[str]:
        """Get list of function names in code.

        Args:
            code: Code string
            language: Programming language

        Returns:
            List of function names
        """
        _, functions = self.validate_signatures(code, language)
        return [f['name'] for f in functions]


# Convenience function
def validate_function_signatures(code: str, language: str) -> Tuple[bool, List[Dict[str, Any]]]:
    """Validate function signatures in code.

    Args:
        code: Code string
        language: Programming language

    Returns:
        Tuple of (is_valid, list of function info)
    """
    validator = SignatureValidator()
    return validator.validate_signatures(code, language)

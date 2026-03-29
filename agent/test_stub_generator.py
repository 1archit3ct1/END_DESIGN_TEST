#!/usr/bin/env python3
"""
Test Stub Generator — Generate test stubs for generated code.

Supports:
- Python: pytest-style test stubs
- TypeScript: vitest/jest-style test stubs
- Rust: #[cfg(test)] module stubs
"""

from typing import Dict, Any, List, Optional
from enum import Enum

from .logger import setup_logger

logger = setup_logger(__name__)


class TestFramework(Enum):
    """Test framework enumeration."""
    PYTEST = "pytest"
    VITEST = "vitest"
    JEST = "jest"
    RUST = "rust"


class TestStubGenerator:
    """Generate test stubs for code files."""

    def __init__(self, framework: TestFramework = TestFramework.PYTEST):
        """Initialize test stub generator.

        Args:
            framework: Test framework to use
        """
        self.framework = framework

    def generate_test_stub(self, file_name: str, functions: List[Dict[str, Any]],
                           class_name: Optional[str] = None) -> str:
        """Generate test stub for a file.

        Args:
            file_name: Source file name
            functions: List of function dicts with 'name', 'params', 'return_type'
            class_name: Optional class name being tested

        Returns:
            Test stub code
        """
        if self.framework == TestFramework.PYTEST:
            return self._generate_pytest_stub(file_name, functions, class_name)
        elif self.framework == TestFramework.VITEST:
            return self._generate_vitest_stub(file_name, functions, class_name)
        elif self.framework == TestFramework.JEST:
            return self._generate_jest_stub(file_name, functions, class_name)
        elif self.framework == TestFramework.RUST:
            return self._generate_rust_test_stub(file_name, functions, class_name)
        else:
            logger.warning(f"Unknown framework: {self.framework}")
            return ""

    def _generate_pytest_stub(self, file_name: str, functions: List[Dict[str, Any]],
                              class_name: Optional[str]) -> str:
        """Generate pytest-style test stub."""
        module_name = file_name.replace('.py', '').replace('/', '.').replace('\\', '.')

        lines = [
            '#!/usr/bin/env python3',
            f'"""Test stub for {file_name}."""',
            '',
            'import pytest',
            f'from {module_name} import ' + (class_name if class_name else ', '.join(f['name'] for f in functions)),
            '',
            '',
        ]

        if class_name:
            # Generate class tests
            lines.append(f'class Test{class_name}:')
            lines.append(f'    """Tests for {class_name}."""')
            lines.append('')
            lines.append('    def setup_method(self):')
            lines.append(f'        """Set up test fixtures."""')
            lines.append(f'        self.instance = {class_name}()')
            lines.append('')

            for func in functions:
                func_name = func.get('name', 'unknown')
                if func_name.startswith('_') and not func_name.startswith('__'):
                    continue  # Skip private methods

                test_name = self._func_to_test_name(func_name)
                lines.append(f'    def {test_name}(self):')
                lines.append(f'        """Test {func_name}."""')
                lines.append(f'        # TODO: Implement test')
                lines.append(f'        pass')
                lines.append('')
        else:
            # Generate function tests
            for func in functions:
                func_name = func.get('name', 'unknown')
                if func_name.startswith('_') and not func_name.startswith('__'):
                    continue  # Skip private methods

                test_name = self._func_to_test_name(func_name)
                lines.append(f'def {test_name}():')
                lines.append(f'    """Test {func_name}."""')
                lines.append(f'    # TODO: Implement test')
                lines.append(f'    pass')
                lines.append('')

        return '\n'.join(lines)

    def _generate_vitest_stub(self, file_name: str, functions: List[Dict[str, Any]],
                              class_name: Optional[str]) -> str:
        """Generate vitest-style test stub."""
        import_name = file_name.replace('.ts', '').replace('.tsx', '').replace('/', '/').replace('\\', '/')

        # Filter out private methods for import
        public_functions = [f for f in functions if not f.get('name', '').startswith('_')]

        lines = [
            '/**',
            f' * Test stub for {file_name}',
            ' */',
            "import { describe, it, expect, beforeEach } from 'vitest';",
            f"import {{ {class_name if class_name else ', '.join(f['name'] for f in public_functions)} }} from './{import_name}';",
            '',
            '',
        ]

        if class_name:
            lines.append(f"describe('{class_name}', () => {{")
            lines.append('  describe(\'constructor\', () => {')
            lines.append('    it(\'should create instance\', () => {')
            lines.append('      // TODO: Implement test')
            lines.append('      const instance = new ' + class_name + '();')
            lines.append('      expect(instance).toBeDefined();')
            lines.append('    });')
            lines.append('  });')
            lines.append('')

            for func in functions:
                func_name = func.get('name', 'unknown')
                if func_name.startswith('_'):
                    continue

                test_name = self._func_to_test_name(func_name, camel=True)
                lines.append(f"  describe('{func_name}', () => {{")
                lines.append(f"    it('should {test_name.replace('test_', '')}', () => {{")
                lines.append('      // TODO: Implement test')
                lines.append('    });')
                lines.append('  });')
                lines.append('')

            lines.append('});')
        else:
            lines.append(f"describe('{file_name}', () => {{")
            for func in functions:
                func_name = func.get('name', 'unknown')
                if func_name.startswith('_'):
                    continue
                test_name = self._func_to_test_name(func_name, camel=True)
                lines.append(f"  it('should {test_name.replace('test_', '')}', () => {{")
                lines.append('    // TODO: Implement test')
                lines.append('  });')
                lines.append('')
            lines.append('});')

        return '\n'.join(lines)

    def _generate_jest_stub(self, file_name: str, functions: List[Dict[str, Any]],
                            class_name: Optional[str]) -> str:
        """Generate jest-style test stub."""
        # Jest is similar to vitest, just different import
        self.framework = TestFramework.VITEST
        vitest_stub = self._generate_vitest_stub(file_name, functions, class_name)
        self.framework = TestFramework.JEST

        # Replace vitest import with jest
        vitest_stub = vitest_stub.replace(
            "import { describe, it, expect, beforeEach } from 'vitest';",
            "// Jest globals are available globally"
        )

        return vitest_stub

    def _generate_rust_test_stub(self, file_name: str, functions: List[Dict[str, Any]],
                                  class_name: Optional[str]) -> str:
        """Generate Rust test stub."""
        lines = [
            '// Test stub generated for ' + file_name,
            '',
            '#[cfg(test)]',
            'mod tests {',
            '    use super::*;',
            '',
        ]

        if class_name:
            lines.append(f'    // Tests for {class_name}')
            lines.append('')

        for func in functions:
            func_name = func.get('name', 'unknown')
            test_name = self._rust_test_name(func_name)

            lines.append(f'    #[test]')
            lines.append(f'    fn {test_name}() {{')
            lines.append(f'        // TODO: Implement test')
            lines.append(f'        // {func_name}() should...')
            lines.append(f'    }}')
            lines.append('')

        lines.append('}')

        return '\n'.join(lines)

    def _func_to_test_name(self, func_name: str, camel: bool = False) -> str:
        """Convert function name to test name.

        Args:
            func_name: Original function name
            camel: Use camelCase instead of snake_case

        Returns:
            Test function name
        """
        # Remove leading underscores
        clean_name = func_name.lstrip('_')

        if camel:
            # Convert to camelCase
            parts = clean_name.split('_')
            return 'test_' + parts[0] + ''.join(p.capitalize() for p in parts[1:])
        else:
            return f'test_{clean_name}'

    def _rust_test_name(self, func_name: str) -> str:
        """Convert function name to Rust test name.

        Args:
            func_name: Original function name

        Returns:
            Rust test function name
        """
        clean_name = func_name.lstrip('_')
        return f'test_{clean_name}'

    def generate_import_test_stub(self, file_name: str, imports: List[str]) -> str:
        """Generate test stub for import validation.

        Args:
            file_name: Source file name
            imports: List of imports to test

        Returns:
            Test stub code
        """
        if self.framework == TestFramework.PYTEST:
            lines = [
                '"""Test that imports work correctly."""',
                '',
                'import pytest',
                '',
            ]

            for imp in imports:
                lines.append(f'def test_import_{imp.replace(".", "_")}():')
                lines.append(f'    """Test {imp} can be imported."""')
                lines.append(f'    from {imp} import *  # noqa')
                lines.append('')

            return '\n'.join(lines)

        elif self.framework in [TestFramework.VITEST, TestFramework.JEST]:
            lines = [
                '/** Test that imports work correctly. */',
                "import { describe, it, expect } from '" + ("vitest" if self.framework == TestFramework.VITEST else "jest") + "';",
                '',
            ]

            for imp in imports:
                lines.append(f"it('can import {imp}', () => {{")
                lines.append(f"  // TODO: Test import")
                lines.append('});')
                lines.append('')

            return '\n'.join(lines)

        return ''


# Convenience functions
def generate_pytest_stub(file_name: str, functions: List[Dict[str, Any]],
                         class_name: Optional[str] = None) -> str:
    """Generate pytest-style test stub."""
    generator = TestStubGenerator(TestFramework.PYTEST)
    return generator.generate_test_stub(file_name, functions, class_name)


def generate_vitest_stub(file_name: str, functions: List[Dict[str, Any]],
                         class_name: Optional[str] = None) -> str:
    """Generate vitest-style test stub."""
    generator = TestStubGenerator(TestFramework.VITEST)
    return generator.generate_test_stub(file_name, functions, class_name)


def generate_rust_test_stub(file_name: str, functions: List[Dict[str, Any]],
                            class_name: Optional[str] = None) -> str:
    """Generate Rust test stub."""
    generator = TestStubGenerator(TestFramework.RUST)
    return generator.generate_test_stub(file_name, functions, class_name)

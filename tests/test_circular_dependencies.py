"""
Test Circular Dependency Detection — Circular dependency tests.
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from agent.import_resolver import (
    ImportResolver, CircularDependencyInfo
)


class TestCircularDependencyDetection:
    """Test circular dependency detection."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        dirpath = tempfile.mkdtemp()
        yield Path(dirpath)
        shutil.rmtree(dirpath)

    @pytest.fixture
    def resolver(self, temp_dir):
        """Create import resolver instance."""
        return ImportResolver(temp_dir)

    def test_no_circular_dependencies(self, resolver, temp_dir):
        """Test detection when there are no circular dependencies."""
        # Create linear dependency: a -> b -> c
        resolver.register_file(
            temp_dir / 'src' / 'c.ts',
            'export const c = 1;'
        )
        resolver.register_file(
            temp_dir / 'src' / 'b.ts',
            '''
import { c } from "./c";
export const b = 1;
'''
        )
        resolver.register_file(
            temp_dir / 'src' / 'a.ts',
            '''
import { b } from "./b";
export const a = 1;
'''
        )

        cycles = resolver.detect_circular_dependencies()

        assert len(cycles) == 0

    def test_simple_circular_dependency_two_files(self, resolver, temp_dir):
        """Test detection of simple circular dependency between two files."""
        # Create circular dependency: a <-> b
        resolver.register_file(
            temp_dir / 'src' / 'a.ts',
            '''
import { b } from "./b";
export const a = 1;
'''
        )
        resolver.register_file(
            temp_dir / 'src' / 'b.ts',
            '''
import { a } from "./a";
export const b = 1;
'''
        )

        cycles = resolver.detect_circular_dependencies()

        assert len(cycles) == 1
        assert 'a.ts' in ' '.join(cycles[0].cycle)
        assert 'b.ts' in ' '.join(cycles[0].cycle)
        assert 'Circular dependency' in cycles[0].description

    def test_circular_dependency_three_files(self, resolver, temp_dir):
        """Test detection of circular dependency across three files."""
        # Create circular dependency: a -> b -> c -> a
        resolver.register_file(
            temp_dir / 'src' / 'a.ts',
            '''
import { c } from "./c";
export const a = 1;
'''
        )
        resolver.register_file(
            temp_dir / 'src' / 'b.ts',
            '''
import { a } from "./a";
export const b = 1;
'''
        )
        resolver.register_file(
            temp_dir / 'src' / 'c.ts',
            '''
import { b } from "./b";
export const c = 1;
'''
        )

        cycles = resolver.detect_circular_dependencies()

        assert len(cycles) == 1
        cycle_files = ' '.join(cycles[0].cycle)
        assert 'a.ts' in cycle_files
        assert 'b.ts' in cycle_files
        assert 'c.ts' in cycle_files

    def test_multiple_circular_dependencies(self, resolver, temp_dir):
        """Test detection of multiple independent circular dependencies."""
        # Create two independent cycles: a <-> b and x <-> y
        resolver.register_file(
            temp_dir / 'src' / 'a.ts',
            'import { b } from "./b"; export const a = 1;'
        )
        resolver.register_file(
            temp_dir / 'src' / 'b.ts',
            'import { a } from "./a"; export const b = 1;'
        )
        resolver.register_file(
            temp_dir / 'src' / 'x.ts',
            'import { y } from "./y"; export const x = 1;'
        )
        resolver.register_file(
            temp_dir / 'src' / 'y.ts',
            'import { x } from "./x"; export const y = 1;'
        )

        cycles = resolver.detect_circular_dependencies()

        assert len(cycles) == 2

    def test_self_import_detected(self, resolver, temp_dir):
        """Test that self-imports are detected as circular."""
        # File importing itself
        resolver.register_file(
            temp_dir / 'src' / 'a.ts',
            '''
import { a } from "./a";
export const a = 1;
'''
        )

        cycles = resolver.detect_circular_dependencies()

        # Self-import should be detected
        assert len(cycles) >= 1

    def test_complex_dependency_graph(self, resolver, temp_dir):
        """Test circular detection in complex dependency graph."""
        # Create: a -> b -> c -> d
        #              ^    |
        #              |    v
        #              f <- e
        resolver.register_file(
            temp_dir / 'src' / 'a.ts',
            'import { b } from "./b"; export const a = 1;'
        )
        resolver.register_file(
            temp_dir / 'src' / 'b.ts',
            'import { c } from "./c"; export const b = 1;'
        )
        resolver.register_file(
            temp_dir / 'src' / 'c.ts',
            'import { d } from "./d"; export const c = 1;'
        )
        resolver.register_file(
            temp_dir / 'src' / 'd.ts',
            'import { e } from "./e"; export const d = 1;'
        )
        resolver.register_file(
            temp_dir / 'src' / 'e.ts',
            'import { f } from "./f"; export const e = 1;'
        )
        resolver.register_file(
            temp_dir / 'src' / 'f.ts',
            'import { c } from "./c"; export const f = 1;'  # Creates cycle: c -> d -> e -> f -> c
        )

        cycles = resolver.detect_circular_dependencies()

        assert len(cycles) == 1
        cycle_files = ' '.join(cycles[0].cycle)
        assert 'c.ts' in cycle_files
        assert 'd.ts' in cycle_files
        assert 'e.ts' in cycle_files
        assert 'f.ts' in cycle_files

    def test_validate_imports_with_cycles(self, resolver, temp_dir):
        """Test combined validation with circular dependency detection."""
        # Create circular dependency
        resolver.register_file(
            temp_dir / 'src' / 'a.ts',
            'import { b } from "./b"; export const a = 1;'
        )
        resolver.register_file(
            temp_dir / 'src' / 'b.ts',
            'import { a } from "./a"; export const b = 1;'
        )

        result, cycles = resolver.validate_imports_with_cycles()

        assert len(cycles) == 1
        assert result.valid is False
        assert any('Circular dependency' in error for error in result.errors)

    def test_circular_dependency_in_subdirectory(self, resolver, temp_dir):
        """Test circular dependency detection across subdirectories."""
        # Create: src/a.ts -> src/components/b.tsx -> src/a.ts
        resolver.register_file(
            temp_dir / 'src' / 'a.ts',
            'import { Button } from "./components/Button"; export const a = 1;'
        )
        resolver.register_file(
            temp_dir / 'src' / 'components' / 'Button.tsx',
            'import { a } from "../a"; export const Button = () => null;'
        )

        cycles = resolver.detect_circular_dependencies()

        assert len(cycles) == 1

    def test_no_false_positives_with_shared_dependency(self, resolver, temp_dir):
        """Test no circular dependency when files share a common dependency."""
        # Create: a -> c, b -> c (no cycle)
        resolver.register_file(
            temp_dir / 'src' / 'c.ts',
            'export const c = 1;'
        )
        resolver.register_file(
            temp_dir / 'src' / 'a.ts',
            'import { c } from "./c"; export const a = 1;'
        )
        resolver.register_file(
            temp_dir / 'src' / 'b.ts',
            'import { c } from "./c"; export const b = 1;'
        )

        cycles = resolver.detect_circular_dependencies()

        assert len(cycles) == 0

    def test_empty_graph_no_cycles(self, resolver, temp_dir):
        """Test that empty graph returns no cycles."""
        cycles = resolver.detect_circular_dependencies()
        assert len(cycles) == 0

    def test_single_file_no_cycles(self, resolver, temp_dir):
        """Test that single file with no imports has no cycles."""
        resolver.register_file(
            temp_dir / 'src' / 'a.ts',
            'export const a = 1;'
        )

        cycles = resolver.detect_circular_dependencies()
        assert len(cycles) == 0

    def test_circular_dependency_info_content(self, resolver, temp_dir):
        """Test that CircularDependencyInfo contains expected content."""
        resolver.register_file(
            temp_dir / 'src' / 'a.ts',
            'import { b } from "./b"; export const a = 1;'
        )
        resolver.register_file(
            temp_dir / 'src' / 'b.ts',
            'import { a } from "./a"; export const b = 1;'
        )

        cycles = resolver.detect_circular_dependencies()

        assert len(cycles) == 1
        info = cycles[0]
        
        # Check cycle list
        assert isinstance(info.cycle, list)
        assert len(info.cycle) >= 2
        
        # Check description
        assert isinstance(info.description, str)
        assert '->' in info.description


class TestCircularDependencyInfo:
    """Test CircularDependencyInfo dataclass."""

    def test_circular_dependency_info_creation(self):
        """Test creating CircularDependencyInfo."""
        info = CircularDependencyInfo(
            cycle=['a.ts', 'b.ts', 'a.ts'],
            description='Circular dependency: a.ts -> b.ts -> a.ts'
        )

        assert info.cycle == ['a.ts', 'b.ts', 'a.ts']
        assert 'Circular dependency' in info.description


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

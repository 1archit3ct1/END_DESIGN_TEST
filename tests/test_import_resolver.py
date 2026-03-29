"""
Test Import Resolver — Cross-file import resolution tests.
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from agent.import_resolver import (
    ImportResolver, ImportInfo, ExportInfo, ImportResolutionResult
)


class TestImportResolver:
    """Test cross-file import resolution."""

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

    def test_extract_exports_typescript_named(self, resolver):
        """Test extracting named exports from TypeScript."""
        content = """
export const API_URL = 'https://api.example.com';
export function fetchData() {}
export class UserService {}
export interface User { id: number; }
"""
        exports = resolver._extract_exports(content, '.ts')
        
        assert 'API_URL' in exports.names
        assert 'fetchData' in exports.names
        assert 'UserService' in exports.names
        assert 'User' in exports.names
        assert exports.default_export is False

    def test_extract_exports_typescript_default(self, resolver):
        """Test extracting default export from TypeScript."""
        content = """
export default function MyComponent() {}
"""
        exports = resolver._extract_exports(content, '.ts')
        
        assert exports.default_export is True

    def test_extract_exports_typescript_list(self, resolver):
        """Test extracting export list from TypeScript."""
        content = """
const a = 1;
const b = 2;
export { a, b };
"""
        exports = resolver._extract_exports(content, '.ts')
        
        assert 'a' in exports.names
        assert 'b' in exports.names

    def test_extract_exports_python(self, resolver):
        """Test extracting exports from Python."""
        content = """
__all__ = ['public_func', 'PublicClass']

def public_func():
    pass

def _private_func():
    pass

class PublicClass:
    pass
"""
        exports = resolver._extract_exports(content, '.py')
        
        assert 'public_func' in exports.names
        assert 'PublicClass' in exports.names
        assert '_private_func' not in exports.names

    def test_extract_exports_python_no_all(self, resolver):
        """Test extracting exports from Python without __all__."""
        content = """
def public_function():
    pass

def _private_function():
    pass

class MyClass:
    pass
"""
        exports = resolver._extract_exports(content, '.py')
        
        assert 'public_function' in exports.names
        assert 'MyClass' in exports.names
        assert '_private_function' not in exports.names

    def test_extract_exports_rust(self, resolver):
        """Test extracting exports from Rust."""
        content = """
pub fn public_function() {}
pub struct PublicStruct;
fn private_function() {}
"""
        exports = resolver._extract_exports(content, '.rs')
        
        assert 'public_function' in exports.names
        assert 'PublicStruct' in exports.names

    def test_extract_imports_typescript_named(self, resolver):
        """Test extracting named imports from TypeScript."""
        content = """
import { useState, useEffect } from 'react';
import { Button } from './components/Button';
"""
        imports = resolver._extract_imports(content, '.ts')
        
        assert len(imports) == 2
        assert imports[0].source == 'react'
        assert 'useState' in imports[0].names
        assert 'useEffect' in imports[0].names
        assert imports[1].source == './components/Button'
        assert 'Button' in imports[1].names
        assert imports[1].is_relative is True

    def test_extract_imports_typescript_default(self, resolver):
        """Test extracting default import from TypeScript."""
        content = """
import React from 'react';
import App from './App';
"""
        imports = resolver._extract_imports(content, '.ts')
        
        assert len(imports) == 2
        assert imports[0].default_import == 'React'
        assert imports[1].default_import == 'App'
        assert imports[1].is_relative is True

    def test_extract_imports_typescript_star(self, resolver):
        """Test extracting namespace import from TypeScript."""
        content = """
import * as utils from './utils';
"""
        imports = resolver._extract_imports(content, '.ts')
        
        assert len(imports) == 1
        assert imports[0].namespace_import == '* as utils'
        assert imports[0].is_relative is True

    def test_extract_imports_typescript_type(self, resolver):
        """Test extracting type imports from TypeScript."""
        content = """
import type { User } from './types';
import { fetchData } from './api';
"""
        imports = resolver._extract_imports(content, '.ts')
        
        assert len(imports) == 2
        assert imports[0].is_type_import is True
        assert imports[1].is_type_import is False

    def test_extract_imports_python_from(self, resolver):
        """Test extracting from imports from Python."""
        content = """
from typing import List, Dict, Optional
from .utils import helper_func
from ..models import User
"""
        imports = resolver._extract_imports(content, '.py')
        
        assert len(imports) == 3
        assert imports[0].source == 'typing'
        assert 'List' in imports[0].names
        assert imports[1].source == '.utils'
        assert imports[1].is_relative is True
        assert imports[2].source == '..models'
        assert imports[2].is_relative is True

    def test_extract_imports_python_import(self, resolver):
        """Test extracting import statements from Python."""
        content = """
import os
import sys
import requests
"""
        imports = resolver._extract_imports(content, '.py')
        
        assert len(imports) == 3
        assert imports[0].source == 'os'
        assert imports[1].source == 'sys'

    def test_extract_imports_rust(self, resolver):
        """Test extracting use statements from Rust."""
        content = """
use std::collections::HashMap;
use crate::models::User;
use super::traits::Serializable;
"""
        imports = resolver._extract_imports(content, '.rs')
        
        assert len(imports) == 3
        assert imports[0].source == 'std::collections::HashMap'
        assert imports[1].source == 'crate::models::User'

    def test_register_file(self, resolver, temp_dir):
        """Test registering a file."""
        content = """
export const VALUE = 42;
export function getValue() { return VALUE; }
"""
        file_path = temp_dir / 'src' / 'utils.ts'
        file_path.parent.mkdir(parents=True)
        file_path.write_text(content)
        
        resolver.register_file(file_path, content)
        
        assert 'src/utils.ts' in resolver.file_registry
        assert 'VALUE' in resolver.file_registry['src/utils.ts']
        assert 'getValue' in resolver.file_registry['src/utils.ts']

    def test_resolve_relative_import_same_dir(self, resolver, temp_dir):
        """Test resolving relative import in same directory."""
        # Register both files
        resolver.register_file(
            temp_dir / 'src' / 'utils.ts',
            'export const util = 1;'
        )
        resolver.register_file(
            temp_dir / 'src' / 'main.ts',
            'import { util } from "./utils";'
        )
        
        result = resolver.resolve_imports(temp_dir / 'src' / 'main.ts')
        
        assert result.valid is True
        assert len(result.errors) == 0
        assert ('src/main.ts', 'src/utils.ts') in result.resolved_imports

    def test_resolve_relative_import_subdir(self, resolver, temp_dir):
        """Test resolving relative import from subdirectory."""
        # Register files
        resolver.register_file(
            temp_dir / 'src' / 'components' / 'Button.tsx',
            'export const Button = () => {};'
        )
        resolver.register_file(
            temp_dir / 'src' / 'App.tsx',
            'import { Button } from "./components/Button";'
        )
        
        result = resolver.resolve_imports(temp_dir / 'src' / 'App.tsx')
        
        assert result.valid is True
        assert len(result.errors) == 0

    def test_resolve_relative_import_parent_dir(self, resolver, temp_dir):
        """Test resolving relative import to parent directory."""
        # Register files
        resolver.register_file(
            temp_dir / 'src' / 'utils.ts',
            'export const util = 1;'
        )
        resolver.register_file(
            temp_dir / 'src' / 'components' / 'Button.tsx',
            'import { util } from "../utils";'
        )
        
        result = resolver.resolve_imports(temp_dir / 'src' / 'components' / 'Button.tsx')
        
        assert result.valid is True
        assert len(result.errors) == 0

    def test_resolve_unresolved_import(self, resolver, temp_dir):
        """Test detecting unresolved imports."""
        # Register file with non-existent import
        resolver.register_file(
            temp_dir / 'src' / 'main.ts',
            'import { missing } from "./nonexistent";'
        )
        
        result = resolver.resolve_imports(temp_dir / 'src' / 'main.ts')
        
        assert result.valid is False
        assert len(result.errors) == 1
        assert 'Cannot resolve import' in result.errors[0]

    def test_resolve_external_import_skipped(self, resolver, temp_dir):
        """Test that external package imports are skipped."""
        # Register file with external import
        resolver.register_file(
            temp_dir / 'src' / 'main.ts',
            'import React from "react";'
        )
        
        result = resolver.resolve_imports(temp_dir / 'src' / 'main.ts')
        
        # External imports don't cause errors
        assert result.valid is True
        assert len(result.resolved_imports) == 0

    def test_validate_all_imports(self, resolver, temp_dir):
        """Test validating all imports across files."""
        # Register multiple files
        resolver.register_file(
            temp_dir / 'src' / 'utils.ts',
            'export const util = 1;'
        )
        resolver.register_file(
            temp_dir / 'src' / 'main.ts',
            '''
import { util } from "./utils";
import React from "react";
'''
        )
        resolver.register_file(
            temp_dir / 'src' / 'app.ts',
            'import { main } from "./main";'
        )
        
        result = resolver.validate_all_imports()
        
        assert result.valid is True
        assert len(result.resolved_imports) >= 1

    def test_get_import_graph(self, resolver, temp_dir):
        """Test building import dependency graph."""
        # Register files
        resolver.register_file(
            temp_dir / 'src' / 'a.ts',
            'export const a = 1;'
        )
        resolver.register_file(
            temp_dir / 'src' / 'b.ts',
            '''
import { a } from "./a";
export const b = 2;
'''
        )
        resolver.register_file(
            temp_dir / 'src' / 'c.ts',
            '''
import { b } from "./b";
export const c = 3;
'''
        )
        
        graph = resolver.get_import_graph()
        
        assert 'src/a.ts' in graph
        assert 'src/b.ts' in graph
        assert 'src/c.ts' in graph
        assert 'src/a.ts' in graph['src/b.ts']
        assert 'src/b.ts' in graph['src/c.ts']

    def test_get_reverse_imports(self, resolver, temp_dir):
        """Test building reverse import graph."""
        # Register files
        resolver.register_file(
            temp_dir / 'src' / 'utils.ts',
            'export const util = 1;'
        )
        resolver.register_file(
            temp_dir / 'src' / 'main.ts',
            'import { util } from "./utils";'
        )
        
        reverse = resolver.get_reverse_imports()
        
        assert 'src/utils.ts' in reverse
        assert 'src/main.ts' in reverse['src/utils.ts']

    def test_find_unused_exports(self, resolver, temp_dir):
        """Test finding unused exports."""
        # Register files
        resolver.register_file(
            temp_dir / 'src' / 'utils.ts',
            '''
export const used = 1;
export const unused = 2;
'''
        )
        resolver.register_file(
            temp_dir / 'src' / 'main.ts',
            'import { used } from "./utils";'
        )
        
        unused = resolver.find_unused_exports()
        
        assert 'src/utils.ts' in unused
        assert 'unused' in unused['src/utils.ts']

    def test_import_with_extension_resolution(self, resolver, temp_dir):
        """Test import resolution with different extensions."""
        # Register TypeScript file
        resolver.register_file(
            temp_dir / 'src' / 'utils.ts',
            'export const util = 1;'
        )
        # Register import without extension
        resolver.register_file(
            temp_dir / 'src' / 'main.ts',
            'import { util } from "./utils";'
        )
        
        result = resolver.resolve_imports(temp_dir / 'src' / 'main.ts')
        
        assert result.valid is True
        assert ('src/main.ts', 'src/utils.ts') in result.resolved_imports

    def test_import_with_tsx_extension(self, resolver, temp_dir):
        """Test import resolution with TSX files."""
        # Register TSX file
        resolver.register_file(
            temp_dir / 'src' / 'Component.tsx',
            'export const Component = () => null;'
        )
        resolver.register_file(
            temp_dir / 'src' / 'App.tsx',
            'import { Component } from "./Component";'
        )
        
        result = resolver.resolve_imports(temp_dir / 'src' / 'App.tsx')
        
        assert result.valid is True

    def test_import_warning_for_missing_export(self, resolver, temp_dir):
        """Test warning when imported name doesn't exist."""
        # Register file with limited exports
        resolver.register_file(
            temp_dir / 'src' / 'utils.ts',
            'export const existing = 1;'
        )
        # Register import with non-existent export
        resolver.register_file(
            temp_dir / 'src' / 'main.ts',
            'import { existing, nonexistent } from "./utils";'
        )
        
        result = resolver.resolve_imports(temp_dir / 'src' / 'main.ts')
        
        assert result.valid is True  # Import resolves, but warning
        assert len(result.warnings) >= 1
        assert 'nonexistent' in ' '.join(result.warnings)

    def test_index_file_resolution(self, resolver, temp_dir):
        """Test resolving imports to index files."""
        # Register index file
        resolver.register_file(
            temp_dir / 'src' / 'components' / 'index.ts',
            'export const Button = 1;'
        )
        resolver.register_file(
            temp_dir / 'src' / 'App.tsx',
            'import { Button } from "./components";'
        )
        
        result = resolver.resolve_imports(temp_dir / 'src' / 'App.tsx')
        
        # Should resolve to index.ts
        assert result.valid is True


class TestImportInfo:
    """Test ImportInfo dataclass."""

    def test_import_info_defaults(self):
        """Test ImportInfo default values."""
        info = ImportInfo(
            statement='import x from "y"',
            source='y'
        )
        
        assert info.names == []
        assert info.default_import == ''
        assert info.namespace_import == ''
        assert info.line_number == 0
        assert info.is_relative is False
        assert info.is_type_import is False

    def test_import_info_with_values(self):
        """Test ImportInfo with all values set."""
        info = ImportInfo(
            statement='import { a, b } from "./module"',
            source='./module',
            names=['a', 'b'],
            default_import='default',
            line_number=5,
            is_relative=True,
            is_type_import=False
        )
        
        assert info.names == ['a', 'b']
        assert info.default_import == 'default'
        assert info.line_number == 5
        assert info.is_relative is True


class TestExportInfo:
    """Test ExportInfo dataclass."""

    def test_export_info_defaults(self):
        """Test ExportInfo default values."""
        info = ExportInfo()
        
        assert info.names == []
        assert info.default_export is False
        assert info.named_exports == {}

    def test_export_info_with_values(self):
        """Test ExportInfo with values."""
        info = ExportInfo(
            names=['a', 'b'],
            default_export=True,
            named_exports={'a': 'named', 'b': 'listed'}
        )
        
        assert info.names == ['a', 'b']
        assert info.default_export is True
        assert len(info.named_exports) == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

#!/usr/bin/env python3
"""
Test: Imports are valid for generated code.
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agent.template_coder import TemplateCoder, IMPORT_TEMPLATES


class TestImportGeneration(unittest.TestCase):
    """Test import statement generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.coder = TemplateCoder()

    def test_generate_rust_imports(self):
        """Test generating Rust imports."""
        modules = ['serde', 'json', 'tokio']
        imports = self.coder.generate_imports('rust', modules)

        self.assertIn('use serde::{Deserialize, Serialize};', imports)
        self.assertIn('use serde_json::{json, Value};', imports)
        self.assertIn('use tokio;', imports)

    def test_generate_typescript_imports(self):
        """Test generating TypeScript imports."""
        modules = ['http', 'url', 'events']
        imports = self.coder.generate_imports('typescript', modules)

        self.assertIn("import http from 'http';", imports)
        self.assertIn("import url from 'url';", imports)
        self.assertIn("import { EventEmitter } from 'events';", imports)

    def test_generate_python_imports(self):
        """Test generating Python imports."""
        modules = ['requests', 'json', 'pathlib']
        imports = self.coder.generate_imports('python', modules)

        self.assertIn('import requests', imports)
        self.assertIn('import json', imports)
        self.assertIn('from pathlib import Path', imports)

    def test_generate_unknown_module_import(self):
        """Test generating import for unknown module."""
        # Rust unknown module
        rust_import = self.coder.generate_imports('rust', ['unknown_module'])
        self.assertIn('use unknown_module;', rust_import)

        # TypeScript unknown module
        ts_import = self.coder.generate_imports('typescript', ['unknown_module'])
        self.assertIn("import { } from 'unknown_module';", ts_import)

        # Python unknown module
        py_import = self.coder.generate_imports('python', ['unknown_module'])
        self.assertIn('import unknown_module', py_import)

    def test_get_import_for_module(self):
        """Test getting single import for module."""
        rust_import = self.coder.get_import_for_module('rust', 'serde')
        self.assertEqual(rust_import, 'use serde::{Deserialize, Serialize};')

        ts_import = self.coder.get_import_for_module('typescript', 'react')
        self.assertEqual(ts_import, "import React, { useState, useEffect } from 'react';")

        py_import = self.coder.get_import_for_module('python', 'hashlib')
        self.assertEqual(py_import, 'import hashlib')

    def test_get_unknown_module_returns_none(self):
        """Test getting unknown module returns None."""
        result = self.coder.get_import_for_module('rust', 'nonexistent_module')
        self.assertIsNone(result)

    def test_case_insensitive_language(self):
        """Test language matching is case insensitive."""
        imports1 = self.coder.generate_imports('RUST', ['serde'])
        imports2 = self.coder.generate_imports('Rust', ['serde'])
        imports3 = self.coder.generate_imports('rust', ['serde'])

        self.assertEqual(imports1, imports2)
        self.assertEqual(imports2, imports3)

    def test_empty_modules_list(self):
        """Test generating imports with empty list."""
        imports = self.coder.generate_imports('rust', [])
        self.assertEqual(imports, '')

    def test_import_templates_exist_for_all_languages(self):
        """Test import templates exist for all supported languages."""
        languages = ['rust', 'typescript', 'python']

        for lang in languages:
            self.assertIn(lang, IMPORT_TEMPLATES)
            self.assertIsInstance(IMPORT_TEMPLATES[lang], dict)
            self.assertGreater(len(IMPORT_TEMPLATES[lang]), 0)


class TestRustImports(unittest.TestCase):
    """Test Rust-specific import generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.coder = TemplateCoder()

    def test_rust_serde_import(self):
        """Test Rust serde import."""
        imports = self.coder.generate_imports('rust', ['serde'])
        self.assertIn('Deserialize', imports)
        self.assertIn('Serialize', imports)

    def test_rust_base64_import(self):
        """Test Rust base64 import."""
        imports = self.coder.generate_imports('rust', ['base64'])
        self.assertIn('URL_SAFE_NO_PAD', imports)
        self.assertIn('Engine', imports)

    def test_rust_sha2_import(self):
        """Test Rust sha2 import."""
        imports = self.coder.generate_imports('rust', ['sha2'])
        self.assertIn('Digest', imports)
        self.assertIn('Sha256', imports)

    def test_rust_std_imports(self):
        """Test Rust std library imports."""
        imports = self.coder.generate_imports('rust', ['std_collections', 'std_sync'])
        self.assertIn('use std::collections::HashMap;', imports)
        self.assertIn('use std::sync::mpsc::channel;', imports)

    def test_rust_error_handling_imports(self):
        """Test Rust error handling imports."""
        imports = self.coder.generate_imports('rust', ['thiserror', 'anyhow'])
        self.assertIn('use thiserror::Error;', imports)
        self.assertIn('use anyhow::{Result, Context};', imports)


class TestTypeScriptImports(unittest.TestCase):
    """Test TypeScript-specific import generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.coder = TemplateCoder()

    def test_typescript_react_import(self):
        """Test TypeScript React import."""
        imports = self.coder.generate_imports('typescript', ['react'])
        self.assertIn('React', imports)
        self.assertIn('useState', imports)
        self.assertIn('useEffect', imports)

    def test_typescript_node_imports(self):
        """Test TypeScript Node.js imports."""
        imports = self.coder.generate_imports('typescript', ['http', 'url', 'fs'])
        self.assertIn("import http from 'http';", imports)
        self.assertIn("import url from 'url';", imports)
        self.assertIn("import fs from 'fs/promises';", imports)

    def test_typescript_crypto_import(self):
        """Test TypeScript crypto import."""
        imports = self.coder.generate_imports('typescript', ['crypto'])
        self.assertIn("import crypto from 'crypto';", imports)


class TestPythonImports(unittest.TestCase):
    """Test Python-specific import generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.coder = TemplateCoder()

    def test_python_standard_library_imports(self):
        """Test Python standard library imports."""
        imports = self.coder.generate_imports('python', ['json', 'os', 'sys', 'hashlib'])
        self.assertIn('import json', imports)
        self.assertIn('import os', imports)
        self.assertIn('import sys', imports)
        self.assertIn('import hashlib', imports)

    def test_python_typing_imports(self):
        """Test Python typing imports."""
        imports = self.coder.generate_imports('python', ['typing'])
        self.assertIn('from typing import Dict, List, Optional, Any, Tuple', imports)

    def test_python_web_framework_imports(self):
        """Test Python web framework imports."""
        flask_imports = self.coder.generate_imports('python', ['flask'])
        self.assertIn('from flask import Flask, request, jsonify', flask_imports)

        fastapi_imports = self.coder.generate_imports('python', ['fastapi'])
        self.assertIn('from fastapi import FastAPI, Request, HTTPException', fastapi_imports)

    def test_python_async_imports(self):
        """Test Python async imports."""
        imports = self.coder.generate_imports('python', ['asyncio'])
        self.assertIn('import asyncio', imports)


class TestImportValidity(unittest.TestCase):
    """Test that generated imports are valid."""

    def setUp(self):
        """Set up test fixtures."""
        self.coder = TemplateCoder()

    def test_rust_import_syntax(self):
        """Test Rust import syntax is valid."""
        imports = self.coder.generate_imports('rust', ['serde', 'json'])

        # All Rust imports should end with semicolon
        for line in imports.split('\n'):
            if line.strip():
                self.assertTrue(line.strip().endswith(';'), f"Rust import should end with ;: {line}")
                self.assertTrue(line.strip().startswith('use '), f"Rust import should start with 'use': {line}")

    def test_typescript_import_syntax(self):
        """Test TypeScript import syntax is valid."""
        imports = self.coder.generate_imports('typescript', ['http', 'url'])

        # All TypeScript imports should contain 'import' and end with semicolon
        for line in imports.split('\n'):
            if line.strip():
                self.assertIn('import', line.lower())
                self.assertTrue(line.strip().endswith(';'), f"TypeScript import should end with ;: {line}")

    def test_python_import_syntax(self):
        """Test Python import syntax is valid."""
        imports = self.coder.generate_imports('python', ['json', 'os'])

        # All Python imports should contain 'import'
        for line in imports.split('\n'):
            if line.strip():
                self.assertIn('import', line)
                # Should not have semicolons
                self.assertNotIn(';', line)

    def test_no_empty_imports(self):
        """Test that generated imports are not empty."""
        rust_imports = self.coder.generate_imports('rust', ['serde'])
        ts_imports = self.coder.generate_imports('typescript', ['react'])
        py_imports = self.coder.generate_imports('python', ['json'])

        self.assertGreater(len(rust_imports), 0)
        self.assertGreater(len(ts_imports), 0)
        self.assertGreater(len(py_imports), 0)


class TestImportIntegration(unittest.TestCase):
    """Test import generation integration with code generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.coder = TemplateCoder()

    def test_imports_can_prepend_to_code(self):
        """Test imports can be prepended to generated code."""
        imports = self.coder.generate_imports('rust', ['serde'])
        code = 'fn main() {}'

        combined = f"{imports}\n\n{code}"

        self.assertIn('use serde', combined)
        self.assertIn('fn main()', combined)

    def test_multiple_imports_formatting(self):
        """Test multiple imports are properly formatted."""
        imports = self.coder.generate_imports('typescript', ['http', 'url', 'events'])
        lines = imports.split('\n')

        # Should have 3 separate import lines
        self.assertEqual(len(lines), 3)
        for line in lines:
            self.assertIn('import', line)


if __name__ == '__main__':
    unittest.main(verbosity=2)

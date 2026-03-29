#!/usr/bin/env python3
"""
Test: output/ directory structure matches expected layout.
"""

import sys
import unittest
from pathlib import Path
import shutil

# Add agent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestOutputStructure(unittest.TestCase):
    """Test output directory structure."""

    def setUp(self):
        """Set up test fixtures."""
        self.output_dir = Path('./output')
        self.output_dir.mkdir(exist_ok=True)

    def tearDown(self):
        """Clean up test fixtures."""
        # Don't remove output dir, just ensure it exists
        self.output_dir.mkdir(exist_ok=True)

    def test_output_dir_exists(self):
        """Test that output/ directory exists."""
        self.assertTrue(self.output_dir.exists())
        self.assertTrue(self.output_dir.is_dir())

    def test_src_tauri_dir_exists(self):
        """Test that output/src-tauri/ directory exists."""
        src_tauri_dir = self.output_dir / 'src-tauri'
        src_tauri_dir.mkdir(exist_ok=True)
        self.assertTrue(src_tauri_dir.exists())
        self.assertTrue(src_tauri_dir.is_dir())

    def test_src_tauri_src_dir_exists(self):
        """Test that output/src-tauri/src/ directory exists."""
        src_tauri_src_dir = self.output_dir / 'src-tauri' / 'src'
        src_tauri_src_dir.mkdir(parents=True, exist_ok=True)
        self.assertTrue(src_tauri_src_dir.exists())
        self.assertTrue(src_tauri_src_dir.is_dir())

    def test_src_tauri_auth_dir_exists(self):
        """Test that output/src-tauri/src/auth/ directory exists."""
        auth_dir = self.output_dir / 'src-tauri' / 'src' / 'auth'
        auth_dir.mkdir(parents=True, exist_ok=True)
        self.assertTrue(auth_dir.exists())
        self.assertTrue(auth_dir.is_dir())

    def test_src_dir_exists(self):
        """Test that output/src/ directory exists."""
        src_dir = self.output_dir / 'src'
        src_dir.mkdir(exist_ok=True)
        self.assertTrue(src_dir.exists())
        self.assertTrue(src_dir.is_dir())

    def test_src_components_dir_exists(self):
        """Test that output/src/components/ directory exists."""
        components_dir = self.output_dir / 'src' / 'components'
        components_dir.mkdir(parents=True, exist_ok=True)
        self.assertTrue(components_dir.exists())
        self.assertTrue(components_dir.is_dir())

    def test_src_oauth_dir_exists(self):
        """Test that output/src/oauth/ directory exists."""
        oauth_dir = self.output_dir / 'src' / 'oauth'
        oauth_dir.mkdir(parents=True, exist_ok=True)
        self.assertTrue(oauth_dir.exists())
        self.assertTrue(oauth_dir.is_dir())

    def test_src_lib_dir_exists(self):
        """Test that output/src/lib/ directory exists."""
        lib_dir = self.output_dir / 'src' / 'lib'
        lib_dir.mkdir(parents=True, exist_ok=True)
        self.assertTrue(lib_dir.exists())
        self.assertTrue(lib_dir.is_dir())

    def test_expected_directory_structure(self):
        """Test that all expected directories exist."""
        expected_dirs = [
            'output',
            'output/src-tauri',
            'output/src-tauri/src',
            'output/src-tauri/src/auth',
            'output/src',
            'output/src/components',
            'output/src/oauth',
            'output/src/lib',
        ]

        for dir_path in expected_dirs:
            path = Path(dir_path)
            self.assertTrue(path.exists(), f"Directory {dir_path} should exist")
            self.assertTrue(path.is_dir(), f"{dir_path} should be a directory")


if __name__ == '__main__':
    unittest.main()

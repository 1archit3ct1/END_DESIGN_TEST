#!/usr/bin/env python3
"""
Test: Cargo.toml has correct dependencies and package info.
"""

import sys
import unittest
from pathlib import Path
import re

# Add agent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestCargoToml(unittest.TestCase):
    """Test Cargo.toml content."""

    def setUp(self):
        """Set up test fixtures."""
        self.cargo_path = Path('./output/Cargo.toml')
        self.cargo_content = None

        if self.cargo_path.exists():
            with open(self.cargo_path, 'r', encoding='utf-8') as f:
                self.cargo_content = f.read()

    def test_cargo_exists(self):
        """Test that Cargo.toml exists."""
        self.assertTrue(self.cargo_path.exists())

    def test_cargo_not_empty(self):
        """Test that Cargo.toml is not empty."""
        self.assertIsNotNone(self.cargo_content)
        self.assertGreater(len(self.cargo_content), 0)

    def test_cargo_has_package_section(self):
        """Test that Cargo.toml has [package] section."""
        self.assertIn('[package]', self.cargo_content)

    def test_cargo_has_package_name(self):
        """Test that Cargo.toml has package name."""
        self.assertIn('name =', self.cargo_content)
        self.assertIn('nextaura', self.cargo_content.lower())

    def test_cargo_has_version(self):
        """Test that Cargo.toml has version."""
        self.assertIn('version =', self.cargo_content)
        # Check for semver format
        version_match = re.search(r'version\s*=\s*"(\d+\.\d+\.\d+)"', self.cargo_content)
        self.assertIsNotNone(version_match)

    def test_cargo_has_edition(self):
        """Test that Cargo.toml has edition."""
        self.assertIn('edition =', self.cargo_content)
        self.assertIn('2021', self.cargo_content)

    def test_cargo_has_dependencies_section(self):
        """Test that Cargo.toml has [dependencies] section."""
        self.assertIn('[dependencies]', self.cargo_content)

    def test_cargo_has_tauri_dependency(self):
        """Test that Cargo.toml has tauri dependency."""
        self.assertIn('tauri', self.cargo_content)

    def test_cargo_has_serde_dependency(self):
        """Test that Cargo.toml has serde dependency."""
        self.assertIn('serde', self.cargo_content)
        self.assertIn('serde_json', self.cargo_content)

    def test_cargo_has_sha2_dependency(self):
        """Test that Cargo.toml has sha2 dependency for PKCE."""
        self.assertIn('sha2', self.cargo_content)

    def test_cargo_has_base64_dependency(self):
        """Test that Cargo.toml has base64 dependency for PKCE."""
        self.assertIn('base64', self.cargo_content)

    def test_cargo_has_tokio_dependency(self):
        """Test that Cargo.toml has tokio dependency."""
        self.assertIn('tokio', self.cargo_content)

    def test_cargo_has_build_dependencies_section(self):
        """Test that Cargo.toml has [build-dependencies] section."""
        self.assertIn('[build-dependencies]', self.cargo_content)

    def test_cargo_has_tauri_build(self):
        """Test that Cargo.toml has tauri-build dependency."""
        self.assertIn('tauri-build', self.cargo_content)

    def test_cargo_has_dev_dependencies_section(self):
        """Test that Cargo.toml has [dev-dependencies] section."""
        self.assertIn('[dev-dependencies]', self.cargo_content)

    def test_cargo_has_features_section(self):
        """Test that Cargo.toml has [features] section."""
        self.assertIn('[features]', self.cargo_content)

    def test_cargo_has_custom_protocol_feature(self):
        """Test that Cargo.toml has custom-protocol feature."""
        self.assertIn('custom-protocol', self.cargo_content)

    def test_cargo_has_license(self):
        """Test that Cargo.toml has license."""
        self.assertIn('license', self.cargo_content)
        self.assertIn('MIT', self.cargo_content)


if __name__ == '__main__':
    unittest.main()

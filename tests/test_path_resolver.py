#!/usr/bin/env python3
"""
Test: path_resolver.py maps task IDs to correct file paths.
"""

import sys
import unittest
import tempfile
import shutil
from pathlib import Path

# Add agent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.path_resolver import PathResolver, resolve_task_path, get_task_extension


class TestPathResolver(unittest.TestCase):
    """Test PathResolver functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_output_dir = Path(tempfile.mkdtemp())
        self.resolver = PathResolver(output_dir=self.test_output_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_output_dir, ignore_errors=True)

    def test_resolver_initializes(self):
        """Test that PathResolver initializes without errors."""
        resolver = PathResolver()
        self.assertIsNotNone(resolver)
        self.assertEqual(resolver.output_dir, Path('./output'))

    def test_resolver_with_custom_output_dir(self):
        """Test that PathResolver accepts custom output directory."""
        resolver = PathResolver(output_dir=self.test_output_dir)
        self.assertEqual(resolver.output_dir, self.test_output_dir)

    def test_resolve_pkce_task(self):
        """Test resolving PKCE task path."""
        task = {'id': 'rust_backend.pkce_rfc7636'}
        path = self.resolver.resolve_path(task)

        self.assertIsNotNone(path)
        self.assertEqual(path, self.test_output_dir / 'src-tauri' / 'src' / 'auth' / 'pkce.rs')

    def test_resolve_callback_server_task(self):
        """Test resolving callback server task path."""
        task = {'id': 'rust_backend.callback_server'}
        path = self.resolver.resolve_path(task)

        self.assertIsNotNone(path)
        self.assertEqual(path, self.test_output_dir / 'src-tauri' / 'src' / 'auth' / 'callback_server.rs')

    def test_resolve_oauth_callback_task(self):
        """Test resolving OAuth callback task path."""
        task = {'id': 'oauth_integration.callback_server'}
        path = self.resolver.resolve_path(task)

        self.assertIsNotNone(path)
        self.assertEqual(path, self.test_output_dir / 'src' / 'oauth' / 'callback_server.ts')

    def test_resolve_token_keychain_task(self):
        """Test resolving token keychain task path."""
        task = {'id': 'oauth_integration.token_keychain'}
        path = self.resolver.resolve_path(task)

        self.assertIsNotNone(path)
        self.assertEqual(path, self.test_output_dir / 'src' / 'oauth' / 'token_keychain.ts')

    def test_resolve_rust_backend_pattern(self):
        """Test resolving rust_backend pattern task path."""
        task = {'id': 'rust_backend.some_feature'}
        path = self.resolver.resolve_path(task)

        self.assertIsNotNone(path)
        self.assertTrue(str(path).endswith('.rs'))
        self.assertIn('src-tauri', str(path))

    def test_resolve_oauth_integration_pattern(self):
        """Test resolving oauth_integration pattern task path."""
        task = {'id': 'oauth_integration.some_feature'}
        path = self.resolver.resolve_path(task)

        self.assertIsNotNone(path)
        self.assertTrue(str(path).endswith('.ts'))
        self.assertIn('oauth', str(path))

    def test_resolve_step_pattern(self):
        """Test resolving step pattern task path."""
        task = {'id': 'step1_connect_oauth'}
        path = self.resolver.resolve_path(task)

        self.assertIsNotNone(path)
        self.assertTrue(str(path).endswith('.tsx'))
        self.assertIn('step1', str(path))

    def test_resolve_unknown_task_defaults_to_lib(self):
        """Test that unknown tasks default to src/lib."""
        task = {'id': 'unknown_custom_task'}
        path = self.resolver.resolve_path(task)

        self.assertIsNotNone(path)
        self.assertIn('lib', str(path))
        self.assertTrue(str(path).endswith('.ts'))

    def test_resolve_path_str(self):
        """Test resolve_path_str returns string."""
        task = {'id': 'rust_backend.pkce_rfc7636'}
        path_str = self.resolver.resolve_path_str(task)

        self.assertIsNotNone(path_str)
        self.assertIsInstance(path_str, str)
        self.assertIn('pkce.rs', path_str)

    def test_get_relative_path(self):
        """Test get_relative_path returns relative path."""
        task = {'id': 'rust_backend.pkce_rfc7636'}
        relative = self.resolver.get_relative_path(task)

        self.assertIsNotNone(relative)
        self.assertEqual(relative, 'src-tauri/src/auth/pkce.rs')

    def test_get_file_extension_rust(self):
        """Test get_file_extension for Rust tasks."""
        task = {'id': 'rust_backend.pkce_rfc7636'}
        ext = self.resolver.get_file_extension(task)

        self.assertEqual(ext, '.rs')

    def test_get_file_extension_typescript(self):
        """Test get_file_extension for TypeScript tasks."""
        task = {'id': 'oauth_integration.callback_server'}
        ext = self.resolver.get_file_extension(task)

        self.assertEqual(ext, '.ts')

    def test_get_file_extension_tsx(self):
        """Test get_file_extension for TSX tasks."""
        task = {'id': 'step1_connect_oauth'}
        ext = self.resolver.get_file_extension(task)

        self.assertEqual(ext, '.tsx')

    def test_get_directory(self):
        """Test get_directory returns correct directory."""
        task = {'id': 'rust_backend.pkce_rfc7636'}
        directory = self.resolver.get_directory(task)

        # Normalize path separators for cross-platform comparison
        normalized_dir = directory.replace('\\', '/')
        self.assertEqual(normalized_dir, 'src-tauri/src/auth')

    def test_ensure_directory_exists(self):
        """Test ensure_directory_exists creates directories."""
        task = {'id': 'rust_backend.pkce_rfc7636'}
        directory = self.resolver.ensure_directory_exists(task)

        self.assertTrue(directory.exists())
        self.assertTrue(directory.is_dir())

    def test_resolve_task_no_id(self):
        """Test resolving task with no ID returns None."""
        task = {}
        path = self.resolver.resolve_path(task)

        self.assertIsNone(path)

    def test_resolve_path_str_no_id(self):
        """Test resolve_path_str with no ID returns None."""
        task = {}
        path_str = self.resolver.resolve_path_str(task)

        self.assertIsNone(path_str)

    def test_get_relative_path_no_id(self):
        """Test get_relative_path with no ID returns None."""
        task = {}
        relative = self.resolver.get_relative_path(task)

        self.assertIsNone(relative)


class TestPathResolverConvenienceFunctions(unittest.TestCase):
    """Test convenience functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_output_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_output_dir, ignore_errors=True)

    def test_resolve_task_path_function(self):
        """Test resolve_task_path convenience function."""
        task = {'id': 'rust_backend.pkce_rfc7636'}
        path = resolve_task_path(task, self.test_output_dir)

        self.assertIsNotNone(path)
        self.assertIn('pkce.rs', str(path))

    def test_get_task_extension_function(self):
        """Test get_task_extension convenience function."""
        task = {'id': 'rust_backend.pkce_rfc7636'}
        ext = get_task_extension(task)

        self.assertEqual(ext, '.rs')


class TestPathResolverTaskIdToFilename(unittest.TestCase):
    """Test task ID to filename conversion."""

    def setUp(self):
        """Set up test fixtures."""
        self.resolver = PathResolver()

    def test_task_id_with_dots(self):
        """Test task ID with dots converted."""
        filename = self.resolver._task_id_to_filename('rust_backend.pkce', '.rs')
        self.assertEqual(filename, 'rust_backend_pkce.rs')

    def test_task_id_with_slashes(self):
        """Test task ID with slashes converted."""
        filename = self.resolver._task_id_to_filename('some/path', '.ts')
        self.assertEqual(filename, 'some_path.ts')

    def test_task_id_lowercase(self):
        """Test task ID converted to lowercase."""
        filename = self.resolver._task_id_to_filename('MyTask', '.ts')
        self.assertEqual(filename, 'mytask.ts')


if __name__ == '__main__':
    unittest.main()

"""
Path Resolver — Map task IDs to file paths.
"""

from pathlib import Path
from typing import Optional, Dict, Any

from .logger import setup_logger

logger = setup_logger(__name__)


class PathResolver:
    """Map task IDs to output file paths."""

    # Task ID patterns mapped to output directories
    TASK_PATH_MAP = {
        'rust_backend': ('src-tauri/src', '.rs'),
        'oauth_integration': ('src/oauth', '.ts'),
        'step1': ('src/components/step1', '.tsx'),
        'step2': ('src/components/step2', '.tsx'),
        'step3': ('src/components/step3', '.tsx'),
        'step4': ('src/components/step4', '.tsx'),
        'step5': ('src/components/step5', '.tsx'),
        'step6': ('src/components/step6', '.tsx'),
        'ui_components': ('src/components', '.tsx'),
        'ui_hooks': ('src/hooks', '.ts'),
        'ui_utils': ('src/lib', '.ts'),
        'utils': ('src/lib', '.ts'),
        'lib': ('src/lib', '.ts'),
    }

    # Specific task ID overrides
    TASK_OVERRIDES = {
        'rust_backend.pkce_rfc7636': 'src-tauri/src/auth/pkce.rs',
        'rust_backend.callback_server': 'src-tauri/src/auth/callback_server.rs',
        'rust_backend.token_storage': 'src-tauri/src/auth/token_storage.rs',
        'oauth_integration.callback_server': 'src/oauth/callback_server.ts',
        'oauth_integration.token_keychain': 'src/oauth/token_keychain.ts',
        'oauth_integration.provider_catalog': 'src/oauth/provider_catalog.ts',
    }

    def __init__(self, output_dir: Optional[Path] = None):
        """Initialize path resolver.

        Args:
            output_dir: Base output directory (default: ./output)
        """
        self.output_dir = output_dir or Path('./output')

    def resolve_path(self, task: Dict[str, Any]) -> Optional[Path]:
        """Resolve file path for a task.

        Args:
            task: Task dictionary with 'id' field

        Returns:
            Full file path or None if unable to resolve
        """
        task_id = task.get('id', '')
        if not task_id:
            logger.warning("Task has no ID")
            return None

        # Check for specific override first
        if task_id in self.TASK_OVERRIDES:
            relative_path = self.TASK_OVERRIDES[task_id]
            return self.output_dir / relative_path

        # Try pattern matching
        for pattern, (directory, extension) in self.TASK_PATH_MAP.items():
            if pattern in task_id:
                filename = self._task_id_to_filename(task_id, extension)
                return self.output_dir / directory / filename

        # Default to src/lib for unknown tasks
        logger.warning(f"Unknown task pattern: {task_id}, defaulting to src/lib")
        filename = self._task_id_to_filename(task_id, '.ts')
        return self.output_dir / 'src' / 'lib' / filename

    def resolve_path_str(self, task: Dict[str, Any]) -> Optional[str]:
        """Resolve file path for a task as string.

        Args:
            task: Task dictionary with 'id' field

        Returns:
            Full file path as string or None
        """
        path = self.resolve_path(task)
        if path:
            return str(path)
        return None

    def get_relative_path(self, task: Dict[str, Any]) -> Optional[str]:
        """Get relative path for a task (relative to output dir).

        Args:
            task: Task dictionary with 'id' field

        Returns:
            Relative path as string or None
        """
        task_id = task.get('id', '')
        if not task_id:
            return None

        # Check for specific override first
        if task_id in self.TASK_OVERRIDES:
            return self.TASK_OVERRIDES[task_id]

        # Try pattern matching
        for pattern, (directory, extension) in self.TASK_PATH_MAP.items():
            if pattern in task_id:
                filename = self._task_id_to_filename(task_id, extension)
                return f"{directory}/{filename}"

        # Default
        filename = self._task_id_to_filename(task_id, '.ts')
        return f"src/lib/{filename}"

    def get_file_extension(self, task: Dict[str, Any]) -> str:
        """Get file extension for a task.

        Args:
            task: Task dictionary with 'id' field

        Returns:
            File extension (e.g., '.rs', '.ts', '.tsx')
        """
        task_id = task.get('id', '')

        # Check overrides first
        if task_id in self.TASK_OVERRIDES:
            return Path(self.TASK_OVERRIDES[task_id]).suffix

        # Pattern matching
        for pattern, (_, extension) in self.TASK_PATH_MAP.items():
            if pattern in task_id:
                return extension

        # Default
        return '.ts'

    def get_directory(self, task: Dict[str, Any]) -> str:
        """Get directory for a task.

        Args:
            task: Task dictionary with 'id' field

        Returns:
            Directory path relative to output
        """
        task_id = task.get('id', '')

        # Check overrides first
        if task_id in self.TASK_OVERRIDES:
            return str(Path(self.TASK_OVERRIDES[task_id]).parent)

        # Pattern matching
        for pattern, (directory, _) in self.TASK_PATH_MAP.items():
            if pattern in task_id:
                return directory

        # Default
        return 'src/lib'

    def _task_id_to_filename(self, task_id: str, extension: str) -> str:
        """Convert task ID to safe filename.

        Args:
            task_id: Task ID string
            extension: File extension

        Returns:
            Safe filename with extension
        """
        # Replace dots and slashes with underscores
        filename = task_id.replace('.', '_').replace('/', '_').lower()
        return f"{filename}{extension}"

    def ensure_directory_exists(self, task: Dict[str, Any]) -> Path:
        """Ensure the directory for a task exists.

        Args:
            task: Task dictionary with 'id' field

        Returns:
            Directory path (created if needed)
        """
        path = self.resolve_path(task)
        if path:
            directory = path.parent
            directory.mkdir(parents=True, exist_ok=True)
            return directory
        raise ValueError(f"Could not resolve path for task: {task.get('id')}")


def resolve_task_path(task: Dict[str, Any], output_dir: Optional[Path] = None) -> Optional[Path]:
    """Convenience function to resolve task path.

    Args:
        task: Task dictionary with 'id' field
        output_dir: Base output directory

    Returns:
        Full file path or None
    """
    resolver = PathResolver(output_dir)
    return resolver.resolve_path(task)


def get_task_extension(task: Dict[str, Any]) -> str:
    """Convenience function to get task file extension.

    Args:
        task: Task dictionary with 'id' field

    Returns:
        File extension
    """
    resolver = PathResolver()
    return resolver.get_file_extension(task)

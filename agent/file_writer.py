"""
File Writer — Deterministic file I/O to ./output/.

Adds auto-generated header comments to all generated files.
Supports single-file and multi-file task outputs.
"""

from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime

from .logger import setup_logger
from .multi_file_handler import MultiFileHandler

logger = setup_logger(__name__)


# Auto-generated header templates per language
HEADER_TEMPLATES = {
    '.py': '''# ============================================================================
# Auto-generated file - DO NOT EDIT MANUALLY
# ============================================================================
# Task: {task_id}
# Name: {task_name}
# Generated: {timestamp}
# Description: {task_desc}
# ============================================================================

''',
    '.rs': '''// ============================================================================
// Auto-generated file - DO NOT EDIT MANUALLY
// ============================================================================
// Task: {task_id}
// Name: {task_name}
// Generated: {timestamp}
// Description: {task_desc}
// ============================================================================

''',
    '.ts': '''// ============================================================================
// Auto-generated file - DO NOT EDIT MANUALLY
// ============================================================================
// Task: {task_id}
// Name: {task_name}
// Generated: {timestamp}
// Description: {task_desc}
// ============================================================================

''',
    '.tsx': '''// ============================================================================
// Auto-generated file - DO NOT EDIT MANUALLY
// ============================================================================
// Task: {task_id}
// Name: {task_name}
// Generated: {timestamp}
// Description: {task_desc}
// ============================================================================

''',
    '.jsx': '''// ============================================================================
// Auto-generated file - DO NOT EDIT MANUALLY
// ============================================================================
// Task: {task_id}
// Name: {task_name}
// Generated: {timestamp}
// Description: {task_desc}
// ============================================================================

''',
    '.js': '''// ============================================================================
// Auto-generated file - DO NOT EDIT MANUALLY
// ============================================================================
// Task: {task_id}
// Name: {task_name}
// Generated: {timestamp}
// Description: {task_desc}
// ============================================================================

''',
    '.json': '''// ============================================================================
// Auto-generated file - DO NOT EDIT MANUALLY
// Task: {task_id} | Generated: {timestamp}
// ============================================================================
''',
    '.css': '''/* ============================================================================
 * Auto-generated file - DO NOT EDIT MANUALLY
 * ============================================================================
 * Task: {task_id}
 * Name: {task_name}
 * Generated: {timestamp}
 * Description: {task_desc}
 * ============================================================================ */

''',
    '.html': '''<!--
  ============================================================================
  Auto-generated file - DO NOT EDIT MANUALLY
  ============================================================================
  Task: {task_id}
  Name: {task_name}
  Generated: {timestamp}
  Description: {task_desc}
  ============================================================================
-->
''',
    '.md': '''<!--
  ============================================================================
  Auto-generated file - DO NOT EDIT MANUALLY
  Task: {task_id} | Generated: {timestamp}
  ============================================================================
-->

''',
}


class FileWriter:
    """Write generated code to output directory."""

    def __init__(self, output_dir: Path):
        """Initialize file writer.

        Args:
            output_dir: Output directory path
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.multi_file_handler = MultiFileHandler(output_dir)

    def write_file(self, task: Dict[str, Any], code: str) -> Optional[Path]:
        """Write code to file with auto-generated header.

        Args:
            task: Task dictionary
            code: Generated code string

        Returns:
            Path to written file or None
        """
        # Check if this is a multi-file task
        if self.multi_file_handler.detect_multi_file_task(task):
            results = self.multi_file_handler.write_multi_files(task, code, self)
            # Return primary file path (first successful write)
            for path, success in results:
                if success:
                    return path
            return None
        
        # Single file task - use original logic
        file_path = self._get_file_path(task)
        if not file_path:
            return None

        try:
            # Create parent directories
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Add auto-generated header
            header = self._generate_header(task, file_path.suffix)
            full_code = f"{header}{code}"

            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(full_code)

            logger.info(f"Wrote file: {file_path}")
            return file_path

        except Exception as e:
            logger.error(f"Failed to write file {file_path}: {e}")
            return None

    def write_files(self, task: Dict[str, Any], code: str) -> List[Tuple[Path, bool]]:
        """Write code to one or more files with auto-generated header.

        Args:
            task: Task dictionary
            code: Generated code string

        Returns:
            List of (path, success) tuples
        """
        # Check if this is a multi-file task
        if self.multi_file_handler.detect_multi_file_task(task):
            return self.multi_file_handler.write_multi_files(task, code, self)
        
        # Single file task
        path = self.write_file(task, code)
        return [(path, path is not None)] if path else []

    def _generate_header(self, task: Dict[str, Any], extension: str) -> str:
        """Generate auto-generated header for file.

        Args:
            task: Task dictionary
            extension: File extension

        Returns:
            Header string
        """
        template = HEADER_TEMPLATES.get(extension, HEADER_TEMPLATES['.ts'])

        header = template.format(
            task_id=task.get('id', 'unknown'),
            task_name=task.get('name', ''),
            timestamp=datetime.now().isoformat(),
            task_desc=task.get('desc', '')
        )

        return header

    def _get_file_path(self, task: Dict[str, Any]) -> Optional[Path]:
        """Get file path for task Using PathResolver.
        
        Args:
            task: Task dictionary
            
        Returns:
            File path or None
        """
        from .path_resolver import PathResolver
        resolver = PathResolver(self.output_dir)
        return resolver.resolve_path(task)

    def _slugify(self, text: str) -> str:
        """Convert text to safe filename.
        
        Args:
            text: Text to slugify
            
        Returns:
            Safe filename string
        """
        return text.replace('.', '_').replace('/', '_').lower()

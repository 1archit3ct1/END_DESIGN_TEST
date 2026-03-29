"""
File Writer — Deterministic file I/O to ./output/.

Adds auto-generated header comments to all generated files.
"""

from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from .logger import setup_logger

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

    def write_file(self, task: Dict[str, Any], code: str) -> Optional[Path]:
        """Write code to file with auto-generated header.

        Args:
            task: Task dictionary
            code: Generated code string

        Returns:
            Path to written file or None
        """
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
        """Get file path for task.
        
        Args:
            task: Task dictionary
            
        Returns:
            File path or None
        """
        task_id = task.get('id', '')
        layer = task.get('layer', 'general')

        # Map task ID to file path
        if 'rust_backend' in task_id:
            return self.output_dir / 'src-tauri' / 'src' / f"{self._slugify(task_id)}.rs"
        elif 'oauth_integration' in task_id:
            return self.output_dir / 'src' / 'oauth' / f"{self._slugify(task_id)}.ts"
        elif 'step1' in task_id:
            return self.output_dir / 'src' / 'components' / 'step1' / f"{self._slugify(task_id)}.tsx"
        elif 'step2' in task_id:
            return self.output_dir / 'src' / 'components' / 'step2' / f"{self._slugify(task_id)}.tsx"
        elif 'step3' in task_id:
            return self.output_dir / 'src' / 'components' / 'step3' / f"{self._slugify(task_id)}.tsx"
        elif 'step4' in task_id:
            return self.output_dir / 'src' / 'components' / 'step4' / f"{self._slugify(task_id)}.tsx"
        elif 'step5' in task_id:
            return self.output_dir / 'src' / 'components' / 'step5' / f"{self._slugify(task_id)}.tsx"
        elif 'step6' in task_id:
            return self.output_dir / 'src' / 'components' / 'step6' / f"{self._slugify(task_id)}.tsx"
        else:
            return self.output_dir / 'src' / 'lib' / f"{self._slugify(task_id)}.ts"

    def _slugify(self, text: str) -> str:
        """Convert text to safe filename.
        
        Args:
            text: Text to slugify
            
        Returns:
            Safe filename string
        """
        return text.replace('.', '_').replace('/', '_').lower()

"""
File Writer — Deterministic file I/O to ./output/.
"""

from pathlib import Path
from typing import Optional, Dict, Any

from .logger import setup_logger

logger = setup_logger(__name__)


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
        """Write code to file.
        
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

            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)

            logger.info(f"Wrote file: {file_path}")
            return file_path

        except Exception as e:
            logger.error(f"Failed to write file {file_path}: {e}")
            return None

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

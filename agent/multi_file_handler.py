"""
Multi-File Handler — Support for tasks that generate multiple files.
"""

from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass

from .logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class FileSpec:
    """Specification for a single file in a multi-file task."""
    path: str
    code: str
    description: str = ""
    is_primary: bool = False


class MultiFileHandler:
    """Handle tasks that generate multiple files."""

    # Task patterns that generate multiple files
    MULTI_FILE_PATTERNS = {
        'component': lambda task: [
            f"src/components/{_slugify(task['id'])}.tsx",
            f"src/components/{_slugify(task['id'])}.test.tsx",
            f"src/components/{_slugify(task['id'])}.styles.css"
        ],
        'rust_backend': lambda task: [
            f"src-tauri/src/{_slugify(task['id'])}.rs",
            f"src-tauri/tests/{_slugify(task['id'])}_tests.rs"
        ],
        'api': lambda task: [
            f"src/api/{_slugify(task['id'])}.ts",
            f"src/api/{_slugify(task['id'])}.types.ts",
            f"tests/api/test_{_slugify(task['id'])}.test.ts"
        ],
        'hook': lambda task: [
            f"src/hooks/{_slugify(task['id'])}.ts",
            f"tests/hooks/test_{_slugify(task['id'])}.test.ts"
        ],
    }

    def __init__(self, output_dir: Path):
        """Initialize multi-file handler.

        Args:
            output_dir: Output directory path
        """
        self.output_dir = output_dir

    def detect_multi_file_task(self, task: Dict[str, Any]) -> bool:
        """Detect if a task should generate multiple files.

        Args:
            task: Task dictionary

        Returns:
            True if task generates multiple files
        """
        task_id = task.get('id', '')
        
        # Check for explicit multi-file flag
        if task.get('multiFile', False):
            return True
        
        # Check for files array in task
        if 'files' in task and isinstance(task['files'], list) and len(task['files']) > 1:
            return True
        
        # Check against known patterns
        for pattern, _ in self.MULTI_FILE_PATTERNS.items():
            if pattern in task_id:
                return True
        
        return False

    def get_file_specs(self, task: Dict[str, Any], code: str) -> List[FileSpec]:
        """Get file specifications for a multi-file task.

        Args:
            task: Task dictionary
            code: Generated code (may contain multiple file markers)

        Returns:
            List of file specifications
        """
        task_id = task.get('id', '')
        
        # Check for explicit files array in task
        if 'files' in task and isinstance(task['files'], list):
            return self._build_specs_from_files_array(task, code)
        
        # Check for embedded file markers in code
        if '/// FILE:' in code or '// FILE:' in code or '# FILE:' in code:
            return self._parse_embedded_files(task, code)
        
        # Generate default multi-file structure based on pattern
        return self._generate_default_multi_file(task, code)

    def _build_specs_from_files_array(self, task: Dict[str, Any], code: str) -> List[FileSpec]:
        """Build file specs from explicit files array in task.

        Args:
            task: Task dictionary
            code: Generated code

        Returns:
            List of file specifications
        """
        specs = []
        files = task.get('files', [])
        
        # Handle empty files array - fall back to single file
        if not files:
            return [FileSpec(path=f"src/{_slugify(task['id'])}.ts", code=code, is_primary=True)]
        
        for i, file_info in enumerate(files):
            if isinstance(file_info, dict):
                path = file_info.get('path', f'file_{i}.txt')
                desc = file_info.get('description', '')
                is_primary = file_info.get('primary', i == 0)
            else:
                path = str(file_info)
                desc = ''
                is_primary = (i == 0)
            
            # For now, split code evenly or use full code for primary file
            file_code = code if is_primary else ''
            
            specs.append(FileSpec(
                path=path,
                code=file_code,
                description=desc,
                is_primary=is_primary
            ))
        
        return specs

    def _parse_embedded_files(self, task: Dict[str, Any], code: str) -> List[FileSpec]:
        """Parse embedded file markers from generated code.

        Args:
            task: Task dictionary
            code: Code with embedded file markers

        Returns:
            List of file specifications
        """
        specs = []
        lines = code.split('\n')
        
        current_file = None
        current_code = []
        
        for line in lines:
            # Check for file marker
            marker = None
            if line.startswith('/// FILE:'):
                marker = line.replace('/// FILE:', '').strip()
            elif line.startswith('// FILE:'):
                marker = line.replace('// FILE:', '').strip()
            elif line.startswith('# FILE:'):
                marker = line.replace('# FILE:', '').strip()
            
            if marker:
                # Save previous file
                if current_file:
                    specs.append(FileSpec(
                        path=current_file,
                        code='\n'.join(current_code),
                        is_primary=(len(specs) == 0)
                    ))
                
                current_file = marker
                current_code = []
            elif current_file:
                current_code.append(line)
        
        # Save last file
        if current_file:
            specs.append(FileSpec(
                path=current_file,
                code='\n'.join(current_code),
                is_primary=(len(specs) == 0)
            ))
        
        return specs if specs else [FileSpec(path=f"{_slugify(task['id'])}.ts", code=code, is_primary=True)]

    def _generate_default_multi_file(self, task: Dict[str, Any], code: str) -> List[FileSpec]:
        """Generate default multi-file structure based on task pattern.

        Args:
            task: Task dictionary
            code: Generated code

        Returns:
            List of file specifications
        """
        task_id = task.get('id', '')
        specs = []
        
        # Find matching pattern
        for pattern, path_generator in self.MULTI_FILE_PATTERNS.items():
            if pattern in task_id:
                paths = path_generator(task)
                for i, path in enumerate(paths):
                    specs.append(FileSpec(
                        path=path,
                        code=code if i == 0 else self._generate_stub(task, path),
                        description=f"Generated file {i + 1} of {len(paths)}",
                        is_primary=(i == 0)
                    ))
                break
        
        # Fallback: single file
        if not specs:
            specs.append(FileSpec(
                path=f"src/{_slugify(task_id)}.ts",
                code=code,
                is_primary=True
            ))
        
        return specs

    def _generate_stub(self, task: Dict[str, Any], path: str) -> str:
        """Generate stub code for secondary file.

        Args:
            task: Task dictionary
            path: File path

        Returns:
            Stub code string
        """
        task_id = task.get('id', 'unknown')
        task_name = task.get('name', '')
        
        if path.endswith('.test.ts') or path.endswith('.test.tsx'):
            return f"""// Test stub for {task_id}
// TODO: Implement tests for {task_name}

import {{ describe, it, expect }} from 'vitest';

describe('{task_name}', () => {{
  it('should be tested', () => {{
    // TODO: Add test
  }});
}});
"""
        elif path.endswith('.styles.css'):
            return f"""/* Styles for {task_id} */
/* TODO: Add styles */
"""
        elif path.endswith('.types.ts'):
            return f"""// Type definitions for {task_id}
// TODO: Add type definitions

export interface {task_id.replace('.', '_').title().replace('_', '')}Props {{
  // TODO: Define props
}}
"""
        elif path.endswith('_tests.rs'):
            return f"""// Tests for {task_id}
// TODO: Implement tests

#[cfg(test)]
mod tests {{
    use super::*;

    #[test]
    fn test_stub() {{
        // TODO: Add test
    }}
}}
"""
        elif path.endswith('.ts') or path.endswith('.tsx'):
            return f"""// TypeScript stub for {task_id}
// TODO: Implement
"""
        else:
            return f"""// Stub for {task_id}
// TODO: Implement
"""

    def write_multi_files(self, task: Dict[str, Any], code: str, file_writer) -> List[Tuple[Path, bool]]:
        """Write multiple files for a task.

        Args:
            task: Task dictionary
            code: Generated code
            file_writer: FileWriter instance

        Returns:
            List of (path, success) tuples
        """
        specs = self.get_file_specs(task, code)
        results = []
        
        for spec in specs:
            full_path = self.output_dir / spec.path
            
            # Create parent directories
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Add header
            header = file_writer._generate_header(task, full_path.suffix)
            full_code = f"{header}{spec.code}"
            
            try:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(full_code)
                logger.info(f"Wrote multi-file: {full_path}")
                results.append((full_path, True))
            except Exception as e:
                logger.error(f"Failed to write multi-file {full_path}: {e}")
                results.append((full_path, False))
        
        return results


def _slugify(text: str) -> str:
    """Convert text to safe filename.

    Args:
        text: Text to slugify

    Returns:
        Safe filename string
    """
    return text.replace('.', '_').replace('/', '_').lower()

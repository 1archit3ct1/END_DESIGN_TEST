"""
Build Export — Export partial or complete builds.

Provides functionality to export generated files even if build is incomplete.
"""

import os
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

from .logger import setup_logger, log_task_progress
from .state_manager import StateManager

logger = setup_logger(__name__)


class BuildExporter:
    """Export build output (partial or complete)."""

    def __init__(self, output_dir: Path = None):
        """Initialize build exporter.

        Args:
            output_dir: Path to output directory (default: ./output/)
        """
        self.output_dir = output_dir or Path('./output')
        self.export_dir = Path('./exports')
        self.export_dir.mkdir(exist_ok=True)

    def export_build(self, export_format: str = 'zip',
                     include_incomplete: bool = True,
                     state_manager: StateManager = None) -> Optional[Path]:
        """Export build output.

        Args:
            export_format: Export format ('zip' or 'directory')
            include_incomplete: Include incomplete tasks
            state_manager: StateManager instance for task status

        Returns:
            Path to exported file/directory or None
        """
        if not self.output_dir.exists():
            logger.error(f"Output directory does not exist: {self.output_dir}")
            return None

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_name = f"build_export_{timestamp}"

        if export_format == 'zip':
            return self._export_as_zip(export_name, include_incomplete, state_manager)
        elif export_format == 'directory':
            return self._export_as_directory(export_name, include_incomplete, state_manager)
        else:
            logger.error(f"Unknown export format: {export_format}")
            return None

    def _export_as_zip(self, export_name: str, include_incomplete: bool,
                       state_manager: StateManager = None) -> Optional[Path]:
        """Export build as ZIP file.

        Args:
            export_name: Name for export file
            include_incomplete: Include incomplete tasks
            state_manager: StateManager instance

        Returns:
            Path to ZIP file or None
        """
        zip_path = self.export_dir / f"{export_name}.zip"

        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add all files from output directory
                files_added = 0
                for file_path in self.output_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(self.output_dir.parent)
                        zipf.write(file_path, arcname)
                        files_added += 1

                # Add build manifest if state_manager provided
                if state_manager:
                    manifest = self._create_build_manifest(state_manager, include_incomplete)
                    manifest_path = self.export_dir / 'manifest.json'
                    with open(manifest_path, 'w') as f:
                        json.dump(manifest, f, indent=2)
                    zipf.write(manifest_path, 'manifest.json')
                    manifest_path.unlink()  # Clean up temp file

                # Add README for export
                readme_content = self._create_export_readme(state_manager, files_added)
                readme_path = self.export_dir / 'EXPORT_README.md'
                with open(readme_path, 'w') as f:
                    f.write(readme_content)
                zipf.write(readme_path, 'EXPORT_README.md')
                readme_path.unlink()  # Clean up temp file

            logger.info(f"Exported build to {zip_path} ({files_added} files)")
            log_task_progress(
                task_id='export',
                status='done',
                message=f"Build exported to {zip_path.name}"
            )

            return zip_path

        except Exception as e:
            logger.error(f"Failed to export build as ZIP: {e}")
            return None

    def _export_as_directory(self, export_name: str, include_incomplete: bool,
                             state_manager: StateManager = None) -> Optional[Path]:
        """Export build as directory.

        Args:
            export_name: Name for export directory
            include_incomplete: Include incomplete tasks
            state_manager: StateManager instance

        Returns:
            Path to export directory or None
        """
        export_path = self.export_dir / export_name

        try:
            # Copy output directory
            if export_path.exists():
                shutil.rmtree(export_path)
            shutil.copytree(self.output_dir, export_path)

            # Add build manifest if state_manager provided
            if state_manager:
                manifest = self._create_build_manifest(state_manager, include_incomplete)
                manifest_path = export_path / 'manifest.json'
                with open(manifest_path, 'w') as f:
                    json.dump(manifest, f, indent=2)

            # Add README for export
            readme_content = self._create_export_readme(state_manager)
            readme_path = export_path / 'EXPORT_README.md'
            with open(readme_path, 'w') as f:
                f.write(readme_content)

            logger.info(f"Exported build to {export_path}")
            log_task_progress(
                task_id='export',
                status='done',
                message=f"Build exported to {export_path.name}"
            )

            return export_path

        except Exception as e:
            logger.error(f"Failed to export build as directory: {e}")
            return None

    def _create_build_manifest(self, state_manager: StateManager,
                               include_incomplete: bool) -> Dict[str, Any]:
        """Create build manifest.

        Args:
            state_manager: StateManager instance
            include_incomplete: Include incomplete tasks

        Returns:
            Manifest dictionary
        """
        tasks = state_manager.load_tasks()

        if not include_incomplete:
            tasks = [t for t in tasks if t.get('status') == 'done']

        completed = sum(1 for t in tasks if t.get('status') == 'done')
        skipped = sum(1 for t in tasks if t.get('status') == 'skipped')
        failed = sum(1 for t in tasks if t.get('status') in ('failed', 'blocked'))
        pending = sum(1 for t in tasks if t.get('status') == 'pending')

        return {
            'version': '1.0',
            'exported_at': datetime.now().isoformat(),
            'build_status': 'complete' if failed == 0 and pending == 0 else 'partial',
            'statistics': {
                'total_tasks': len(tasks),
                'completed': completed,
                'skipped': skipped,
                'failed': failed,
                'pending': pending,
                'completion_rate': round(completed / len(tasks) * 100, 2) if tasks else 0
            },
            'tasks': tasks,
            'output_directory': str(self.output_dir)
        }

    def _create_export_readme(self, state_manager: StateManager,
                              files_added: int = 0) -> str:
        """Create README for export.

        Args:
            state_manager: StateManager instance
            files_added: Number of files in export

        Returns:
            README content
        """
        tasks = state_manager.load_tasks() if state_manager else []
        completed = sum(1 for t in tasks if t.get('status') == 'done')
        failed = sum(1 for t in tasks if t.get('status') in ('failed', 'blocked'))
        pending = sum(1 for t in tasks if t.get('status') == 'pending')

        build_status = 'Complete' if failed == 0 and pending == 0 else 'Partial'

        return f"""# Build Export

**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status:** {build_status}

## Build Statistics

| Metric | Value |
|--------|-------|
| Total Tasks | {len(tasks)} |
| Completed | {completed} |
| Failed | {failed} |
| Pending | {pending} |
| Files Generated | {files_added} |
| Completion Rate | {round(completed / len(tasks) * 100, 2) if tasks else 0}% |

## Contents

- `output/` - Generated code files
- `manifest.json` - Build manifest with task details
- `EXPORT_README.md` - This file

## Notes

This is a {'complete' if build_status == 'Complete' else 'partial'} build export.
{'Some tasks may not have completed successfully. Check the manifest for details.' if build_status == 'Partial' else 'All tasks completed successfully.'}

## Next Steps

1. Review generated files in the `output/` directory
2. Check `manifest.json` for task-level details
3. Implement any missing functionality for incomplete tasks
4. Run tests to verify generated code
"""

    def export_partial_build(self, state_manager: StateManager) -> Optional[Path]:
        """Export partial build (convenience method).

        Args:
            state_manager: StateManager instance

        Returns:
            Path to exported ZIP file or None
        """
        return self.export_build(
            export_format='zip',
            include_incomplete=True,
            state_manager=state_manager
        )

    def get_export_history(self) -> List[Dict[str, Any]]:
        """Get history of exports.

        Returns:
            List of export metadata
        """
        history = []

        for export_file in self.export_dir.glob('build_export_*.zip'):
            stat = export_file.stat()
            history.append({
                'filename': export_file.name,
                'path': str(export_file),
                'size': stat.st_size,
                'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat()
            })

        return sorted(history, key=lambda x: x['created_at'], reverse=True)

    def cleanup_old_exports(self, keep_days: int = 7) -> int:
        """Clean up old exports.

        Args:
            keep_days: Number of days to keep exports

        Returns:
            Number of files deleted
        """
        deleted = 0
        cutoff = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)

        for export_file in self.export_dir.glob('build_export_*'):
            if export_file.stat().st_ctime < cutoff:
                export_file.unlink()
                deleted += 1

        logger.info(f"Cleaned up {deleted} old exports")
        return deleted


# Convenience function for direct usage
def export_build(output_dir: Path = None, export_format: str = 'zip',
                 state_manager: StateManager = None) -> Optional[Path]:
    """Export build output.

    Args:
        output_dir: Path to output directory
        export_format: Export format ('zip' or 'directory')
        state_manager: StateManager instance

    Returns:
        Path to exported file/directory or None
    """
    exporter = BuildExporter(output_dir)
    return exporter.export_build(export_format, include_incomplete=True, state_manager=state_manager)

"""
Template Loader — Load project templates from disk.
"""

from pathlib import Path
from typing import Dict, Optional, Any
import json

from .logger import setup_logger

logger = setup_logger(__name__)

TEMPLATES_DIR = Path(__file__).parent / 'templates'
OUTPUT_TEMPLATES_DIR = Path(__file__).parent.parent / 'output'


class TemplateLoader:
    """Load project templates from disk."""

    def __init__(self, templates_dir: Optional[Path] = None):
        """Initialize template loader.

        Args:
            templates_dir: Path to templates directory (default: agent/templates/)
        """
        self.templates_dir = templates_dir or TEMPLATES_DIR
        self._template_cache: Dict[str, Any] = {}

    def load_template(self, template_name: str) -> Optional[str]:
        """Load a template file by name.

        Args:
            template_name: Name of template file (e.g., 'pkce.py')

        Returns:
            Template content as string or None if not found
        """
        # Check cache first
        if template_name in self._template_cache:
            logger.debug(f"Template {template_name} loaded from cache")
            return self._template_cache[template_name]

        template_path = self.templates_dir / template_name

        if not template_path.exists():
            logger.warning(f"Template not found: {template_path}")
            return None

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self._template_cache[template_name] = content
            logger.debug(f"Loaded template: {template_path}")
            return content
        except Exception as e:
            logger.error(f"Failed to load template {template_path}: {e}")
            return None

    def load_json_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Load a JSON template file by name.

        Args:
            template_name: Name of template file (e.g., 'package.json')

        Returns:
            Parsed JSON as dict or None if not found
        """
        content = self.load_template(template_name)
        if content is None:
            return None

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON template {template_name}: {e}")
            return None

    def load_output_template(self, template_name: str) -> Optional[str]:
        """Load a template from the output directory.

        Args:
            template_name: Name of template file (e.g., 'package.json')

        Returns:
            Template content as string or None if not found
        """
        template_path = OUTPUT_TEMPLATES_DIR / template_name

        if not template_path.exists():
            logger.warning(f"Output template not found: {template_path}")
            return None

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.debug(f"Loaded output template: {template_path}")
            return content
        except Exception as e:
            logger.error(f"Failed to load output template {template_path}: {e}")
            return None

    def list_templates(self) -> list:
        """List all available templates.

        Returns:
            List of template file names
        """
        if not self.templates_dir.exists():
            return []

        return [f.name for f in self.templates_dir.iterdir() if f.is_file()]

    def list_output_templates(self) -> list:
        """List all available output templates.

        Returns:
            List of output template file names
        """
        if not OUTPUT_TEMPLATES_DIR.exists():
            return []

        return [f.name for f in OUTPUT_TEMPLATES_DIR.iterdir() if f.is_file()]

    def clear_cache(self) -> None:
        """Clear the template cache."""
        self._template_cache.clear()
        logger.debug("Template cache cleared")

    def get_template_path(self, template_name: str) -> Optional[Path]:
        """Get the path to a template file.

        Args:
            template_name: Name of template file

        Returns:
            Path to template file or None if not found
        """
        template_path = self.templates_dir / template_name
        if template_path.exists():
            return template_path
        return None


def load_project_template(template_name: str) -> Optional[str]:
    """Convenience function to load a project template.

    Args:
        template_name: Name of template file

    Returns:
        Template content as string or None if not found
    """
    loader = TemplateLoader()
    return loader.load_template(template_name)


def load_output_template(template_name: str) -> Optional[str]:
    """Convenience function to load an output template.

    Args:
        template_name: Name of template file

    Returns:
        Template content as string or None if not found
    """
    loader = TemplateLoader()
    return loader.load_output_template(template_name)

"""
Hybrid Router — Route task to template or LLM coder.
"""

from typing import Optional, Dict, Any

from .logger import setup_logger

logger = setup_logger(__name__)


class HybridRouter:
    """Route tasks to template or LLM-based code generation."""

    # Task IDs that have templates
    TEMPLATE_TASKS = {
        'rust_backend.pkce_rfc7636',
        'rust_backend.callback_server',
        'oauth_integration.callback_server',
        'oauth_integration.token_keychain',
    }

    def __init__(self):
        """Initialize hybrid router."""
        self.template_coder = None
        self.llm_coder = None

    def generate_code(self, task: Dict[str, Any]) -> Optional[str]:
        """Generate code for task using template or LLM.
        
        Args:
            task: Task dictionary
            
        Returns:
            Generated code string or None
        """
        task_id = task.get('id', '')

        # Route to template if available
        if task_id in self.TEMPLATE_TASKS:
            logger.info(f"Using template for task: {task_id}")
            return self._generate_from_template(task)

        # Otherwise use LLM
        logger.info(f"Using LLM for task: {task_id}")
        return self._generate_from_llm(task)

    def _generate_from_template(self, task: Dict[str, Any]) -> Optional[str]:
        """Generate code from template.
        
        Args:
            task: Task dictionary
            
        Returns:
            Generated code string or None
        """
        # TODO: Implement template-based generation
        task_id = task.get('id', '')
        desc = task.get('desc', '')

        # Placeholder template
        code = f"""
// Auto-generated code for: {task_id}
// Description: {desc}

// TODO: Implement {task_id}
"""
        return code

    def _generate_from_llm(self, task: Dict[str, Any]) -> Optional[str]:
        """Generate code from LLM (codellama:7b).
        
        Args:
            task: Task dictionary
            
        Returns:
            Generated code string or None
        """
        # TODO: Implement LLM-based generation
        task_id = task.get('id', '')
        desc = task.get('desc', '')

        # Placeholder - will be replaced with actual LLM call
        code = f"""
// Auto-generated code for: {task_id}
// Description: {desc}

// TODO: Implement {task_id} using codellama:7b
"""
        return code

#!/usr/bin/env python3
"""
Prompt Templates — Pre-built prompts for different task types.

Provides specialized prompt templates for:
- Backend tasks (Rust/Python APIs)
- Integration tasks (OAuth, callbacks, data sync)
- UI tasks (React components, styles)
"""

from typing import Dict, Any, Optional
from enum import Enum


class TaskType(Enum):
    """Task type enumeration."""
    BACKEND = "backend"
    INTEGRATION = "integration"
    UI = "ui"
    GENERAL = "general"


# ============================================================================
# Backend Task Templates
# ============================================================================

BACKEND_SYSTEM_PROMPT = """You are an expert backend engineer specializing in {language} development.
Write clean, production-ready, well-documented code following industry best practices."""

BACKEND_TEMPLATE = """Task ID: {task_id}
Task Name: {task_name}
Layer: {layer}
Description: {task_desc}

## Requirements:
1. Write complete, working {language} code (no placeholders or TODOs)
2. Include proper error handling with try/catch or Result types
3. Follow {language} naming conventions and style guides
4. Include comprehensive docstrings/comments
5. Implement input validation
6. Use appropriate data structures and design patterns
7. Do not include markdown code fences (```language ... ```)
8. Include unit test stubs if applicable

## Code Structure:
- Use clear function/method names
- Separate concerns (business logic, data access, API layer)
- Include type hints/annotations
- Add error handling for edge cases

Generate the complete {language} code now:"""

# Rust-specific backend template
RUST_BACKEND_TEMPLATE = """Task ID: {task_id}
Task Name: {task_name}
Layer: {layer}
Description: {task_desc}

## Requirements:
1. Write complete, working Rust code (no placeholders or TODOs)
2. Use Result<T, E> for error handling (no unwrap() in production code)
3. Follow Rust naming conventions (snake_case for functions/variables, PascalCase for types)
4. Include comprehensive Rust doc comments (/// for public, // for private)
5. Implement proper ownership and borrowing
6. Use appropriate Rust patterns (Builder, RAII, etc.)
7. Do not include markdown code fences
8. Include #[cfg(test)] module with unit tests

## Code Structure:
- Use clear module organization
- Implement traits for abstraction where appropriate
- Add lifetime annotations where needed
- Use Option<T> for nullable values

Generate the complete Rust code now:"""

# ============================================================================
# Integration Task Templates
# ============================================================================

INTEGRATION_SYSTEM_PROMPT = """You are an expert integration engineer specializing in API integrations, OAuth flows, and data synchronization.
Write secure, reliable, and well-tested integration code."""

INTEGRATION_TEMPLATE = """Task ID: {task_id}
Task Name: {task_name}
Layer: {layer}
Description: {task_desc}

## Requirements:
1. Write complete, working integration code (no placeholders or TODOs)
2. Include proper authentication handling (OAuth tokens, API keys)
3. Implement retry logic with exponential backoff
4. Handle rate limiting appropriately
5. Include comprehensive error handling
6. Log all integration events for debugging
7. Validate all incoming/outgoing data
8. Do not include markdown code fences
9. Include connection timeout handling
10. Implement graceful degradation/fallback

## Security Considerations:
- Never log sensitive data (tokens, passwords, PII)
- Use environment variables for secrets
- Implement token refresh logic
- Validate webhook signatures if applicable

## Data Handling:
- Transform data to match expected schema
- Handle missing/null fields gracefully
- Include data validation before storage

Generate the complete integration code now:"""

# OAuth-specific integration template
OAUTH_INTEGRATION_TEMPLATE = """Task ID: {task_id}
Task Name: {task_name}
Layer: {layer}
Description: {task_desc}

## Requirements:
1. Implement OAuth 2.0 flow correctly (authorization code, PKCE if applicable)
2. Handle token exchange securely
3. Store tokens securely (encrypted at rest)
4. Implement automatic token refresh before expiration
5. Handle token revocation
6. Support multiple scopes
7. Include callback URL handling
8. Do not include markdown code fences

## OAuth Flow Steps:
1. Generate authorization URL with correct scopes
2. Handle redirect callback with authorization code
3. Exchange code for access/refresh tokens
4. Store tokens securely
5. Use access token for API calls
6. Refresh token before expiration
7. Handle token errors (401, 403)

## Security:
- Use PKCE for public clients (RFC 7636)
- Validate state parameter to prevent CSRF
- Never expose client secrets in frontend code
- Use HTTPS for all OAuth endpoints

Generate the complete OAuth integration code now:"""

# ============================================================================
# UI Task Templates
# ============================================================================

UI_SYSTEM_PROMPT = """You are an expert frontend engineer specializing in React and modern JavaScript/TypeScript.
Write clean, accessible, and performant UI components following React best practices."""

UI_TEMPLATE = """Task ID: {task_id}
Task Name: {task_name}
Layer: {layer}
Description: {task_desc}

## Requirements:
1. Write complete, working React component (no placeholders or TODOs)
2. Use functional components with hooks (no class components)
3. Include proper PropTypes or TypeScript types
4. Implement accessible markup (ARIA attributes, semantic HTML)
5. Handle loading, error, and empty states
6. Include responsive design considerations
7. Do not include markdown code fences
8. Include CSS module or styled-components styles

## Component Structure:
- Use clear, descriptive component names
- Separate concerns (presentational vs container components)
- Implement proper prop validation
- Include error boundaries where appropriate
- Use React.memo for performance optimization if needed

## State Management:
- Use useState for local state
- Use useEffect for side effects
- Implement proper cleanup in useEffect
- Use custom hooks for reusable logic

## Styling:
- Use CSS modules or styled-components
- Follow BEM or similar naming convention
- Include dark/light theme support if applicable
- Ensure mobile-responsive design

Generate the complete React component code now:"""

# Component-specific UI template
COMPONENT_TEMPLATE = """Task ID: {task_id}
Task Name: {task_name}
Layer: {layer}
Description: {task_desc}

## Requirements:
1. Create a reusable React component with clear API
2. Accept props for customization
3. Include proper TypeScript interfaces or PropTypes
4. Handle all edge cases (empty, loading, error)
5. Include user interaction handlers (onClick, onChange, etc.)
6. Add animation/transitions where appropriate
7. Do not include markdown code fences

## Props Interface:
```typescript
interface ComponentProps {{
  // Define all required and optional props
  // Include proper types and default values
}}
```

## Component Features:
- Responsive design (mobile-first)
- Accessible (keyboard navigation, screen reader support)
- Performant (memoization, lazy loading if needed)
- Themable (support for custom styles/themes)

Generate the complete component code now:"""


# ============================================================================
# Template Selection Logic
# ============================================================================

def get_task_type(task: Dict[str, Any]) -> TaskType:
    """Determine task type from task dictionary.

    Args:
        task: Task dictionary with id, name, desc, layer

    Returns:
        TaskType enum value
    """
    task_id = task.get('id', '').lower()
    layer = task.get('layer', '').lower()

    # Check layer first
    if layer == 'backend' or 'rust' in task_id or 'python' in task_id:
        return TaskType.BACKEND
    elif layer == 'integration' or 'oauth' in task_id or 'callback' in task_id:
        return TaskType.INTEGRATION
    elif layer == 'ui' or 'component' in task_id or 'jsx' in task_id:
        return TaskType.UI

    # Fallback to keyword matching
    backend_keywords = ['rust', 'python', 'backend', 'api', 'service', 'repository']
    integration_keywords = ['oauth', 'callback', 'sync', 'integration', 'webhook', 'provider']
    ui_keywords = ['component', 'ui', 'jsx', 'react', 'style', 'css', 'view']

    for keyword in backend_keywords:
        if keyword in task_id:
            return TaskType.BACKEND

    for keyword in integration_keywords:
        if keyword in task_id:
            return TaskType.INTEGRATION

    for keyword in ui_keywords:
        if keyword in task_id:
            return TaskType.UI

    return TaskType.GENERAL


def get_prompt_template(task: Dict[str, Any]) -> str:
    """Get appropriate prompt template for task type.

    Args:
        task: Task dictionary

    Returns:
        Prompt template string
    """
    task_type = get_task_type(task)
    task_id = task.get('id', '').lower()

    # Check for specific sub-types
    if task_type == TaskType.BACKEND:
        if 'rust' in task_id or task.get('language') == 'rust':
            return RUST_BACKEND_TEMPLATE
        return BACKEND_TEMPLATE

    elif task_type == TaskType.INTEGRATION:
        if 'oauth' in task_id:
            return OAUTH_INTEGRATION_TEMPLATE
        return INTEGRATION_TEMPLATE

    elif task_type == TaskType.UI:
        if 'component' in task_id:
            return COMPONENT_TEMPLATE
        return UI_TEMPLATE

    else:
        return BACKEND_TEMPLATE  # Default to backend template


def build_prompt(task: Dict[str, Any], custom_context: Optional[str] = None) -> str:
    """Build complete prompt for task using appropriate template.

    Args:
        task: Task dictionary with id, name, desc, layer
        custom_context: Optional additional context to include

    Returns:
        Complete prompt string
    """
    template = get_prompt_template(task)

    prompt = template.format(
        task_id=task.get('id', 'unknown'),
        task_name=task.get('name', ''),
        layer=task.get('layer', 'general'),
        task_desc=task.get('desc', ''),
        language=task.get('language', 'TypeScript')
    )

    if custom_context:
        prompt += f"\n\n## Additional Context:\n{custom_context}"

    return prompt


def get_system_prompt(task: Dict[str, Any]) -> str:
    """Get system prompt for task type.

    Args:
        task: Task dictionary

    Returns:
        System prompt string
    """
    task_type = get_task_type(task)

    if task_type == TaskType.BACKEND:
        language = task.get('language', 'TypeScript')
        return BACKEND_SYSTEM_PROMPT.format(language=language)
    elif task_type == TaskType.INTEGRATION:
        return INTEGRATION_SYSTEM_PROMPT
    elif task_type == TaskType.UI:
        return UI_SYSTEM_PROMPT
    else:
        return BACKEND_SYSTEM_PROMPT.format(language='TypeScript')

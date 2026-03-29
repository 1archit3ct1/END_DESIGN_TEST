#!/usr/bin/env python3
"""
Docstring Generator — Generate docstrings for Python/TypeScript code.

Supports:
- Python: Google-style, NumPy-style, reStructuredText
- TypeScript: JSDoc comments
"""

from typing import Dict, Any, List, Optional
from enum import Enum

from .logger import setup_logger

logger = setup_logger(__name__)


class DocstringStyle(Enum):
    """Docstring style enumeration."""
    GOOGLE = "google"
    NUMPY = "numpy"
    RST = "rst"
    JSDOC = "jsdoc"


class DocstringGenerator:
    """Generate docstrings for functions and classes."""

    def __init__(self, style: DocstringStyle = DocstringStyle.GOOGLE):
        """Initialize docstring generator.

        Args:
            style: Docstring style to use
        """
        self.style = style

    def generate_function_docstring(self, func_name: str, params: List[Dict[str, Any]],
                                    return_type: Optional[str] = None,
                                    description: str = "",
                                    raises: Optional[List[str]] = None) -> str:
        """Generate docstring for a function.

        Args:
            func_name: Function name
            params: List of param dicts with 'name', 'type', 'description'
            return_type: Return type name
            description: Function description
            raises: List of exceptions that may be raised

        Returns:
            Formatted docstring
        """
        if self.style == DocstringStyle.JSDOC:
            return self._generate_jsdoc(func_name, params, return_type, description, raises)
        elif self.style == DocstringStyle.NUMPY:
            return self._generate_numpy_docstring(func_name, params, return_type, description, raises)
        elif self.style == DocstringStyle.RST:
            return self._generate_rst_docstring(func_name, params, return_type, description, raises)
        else:  # GOOGLE
            return self._generate_google_docstring(func_name, params, return_type, description, raises)

    def generate_class_docstring(self, class_name: str, description: str,
                                 attributes: Optional[List[Dict[str, Any]]] = None) -> str:
        """Generate docstring for a class.

        Args:
            class_name: Class name
            description: Class description
            attributes: List of attribute dicts

        Returns:
            Formatted docstring
        """
        if self.style == DocstringStyle.JSDOC:
            return self._generate_jsdoc_class(class_name, description, attributes)
        elif self.style == DocstringStyle.NUMPY:
            return self._generate_numpy_class_docstring(class_name, description, attributes)
        elif self.style == DocstringStyle.RST:
            return self._generate_rst_class_docstring(class_name, description, attributes)
        else:  # GOOGLE
            return self._generate_google_class_docstring(class_name, description, attributes)

    def _generate_google_docstring(self, func_name: str, params: List[Dict[str, Any]],
                                   return_type: Optional[str], description: str,
                                   raises: Optional[List[str]]) -> str:
        """Generate Google-style docstring."""
        lines = ['"""']

        if description:
            lines.append(description)
            lines.append('')

        if params:
            lines.append('Args:')
            for param in params:
                param_type = param.get('type', 'Any')
                param_desc = param.get('description', '')
                param_name = param.get('name', 'unknown')
                lines.append(f'    {param_name} ({param_type}): {param_desc}')

        if return_type:
            lines.append('')
            lines.append('Returns:')
            lines.append(f'    {return_type}: Result value')

        if raises:
            lines.append('')
            lines.append('Raises:')
            for exc in raises:
                lines.append(f'    {exc}: When something goes wrong')

        lines.append('"""')
        return '\n'.join(lines)

    def _generate_numpy_docstring(self, func_name: str, params: List[Dict[str, Any]],
                                  return_type: Optional[str], description: str,
                                  raises: Optional[List[str]]) -> str:
        """Generate NumPy-style docstring."""
        lines = ['"""']

        if description:
            lines.append(description)
            lines.append('')

        if params:
            lines.append('Parameters')
            lines.append('----------')
            for param in params:
                param_type = param.get('type', 'Any')
                param_desc = param.get('description', '')
                param_name = param.get('name', 'unknown')
                lines.append(f'{param_name} : {param_type}')
                lines.append(f'    {param_desc}')

        if return_type:
            lines.append('')
            lines.append('Returns')
            lines.append('-------')
            lines.append(f'{return_type}')
            lines.append('    Result value')

        if raises:
            lines.append('')
            lines.append('Raises')
            lines.append('------')
            for exc in raises:
                lines.append(f'{exc}')
                lines.append('    When something goes wrong')

        lines.append('"""')
        return '\n'.join(lines)

    def _generate_rst_docstring(self, func_name: str, params: List[Dict[str, Any]],
                                return_type: Optional[str], description: str,
                                raises: Optional[List[str]]) -> str:
        """Generate reStructuredText docstring."""
        lines = ['"""']

        if description:
            lines.append(description)
            lines.append('')

        if params:
            lines.append(':param ' + ': '.join(f"{p.get('name', 'unknown')}: {p.get('description', '')}" for p in params))
            for param in params:
                param_type = param.get('type', 'Any')
                param_name = param.get('name', 'unknown')
                lines.append(f':type {param_name}: {param_type}')

        if return_type:
            lines.append(f':return: Result value')
            lines.append(f':rtype: {return_type}')

        if raises:
            for exc in raises:
                lines.append(f':raises {exc}: When something goes wrong')

        lines.append('"""')
        return '\n'.join(lines)

    def _generate_jsdoc(self, func_name: str, params: List[Dict[str, Any]],
                        return_type: Optional[str], description: str,
                        raises: Optional[List[str]]) -> str:
        """Generate JSDoc comment."""
        lines = ['/**']

        if description:
            lines.append(f' * {description}')
            lines.append(' *')

        for param in params:
            param_type = param.get('type', 'any')
            param_name = param.get('name', 'unknown')
            param_desc = param.get('description', '')
            optional = param.get('optional', False)
            optional_marker = '=' if optional else ''
            lines.append(f' * @param {{{param_type}}} {param_name}{optional_marker} {param_desc}')

        if return_type:
            lines.append(f' * @returns {{{return_type}}} Result value')

        if raises:
            for exc in raises:
                lines.append(f' * @throws {{{exc}}} When something goes wrong')

        lines.append(' */')
        return '\n'.join(lines)

    def _generate_google_class_docstring(self, class_name: str, description: str,
                                         attributes: Optional[List[Dict[str, Any]]]) -> str:
        """Generate Google-style class docstring."""
        lines = ['"""']

        if description:
            lines.append(description)
            lines.append('')

        lines.append(f'Attributes:')

        if attributes:
            for attr in attributes:
                attr_type = attr.get('type', 'Any')
                attr_desc = attr.get('description', '')
                attr_name = attr.get('name', 'unknown')
                lines.append(f'    {attr_name} ({attr_type}): {attr_desc}')
        else:
            lines.append('    None')

        lines.append('"""')
        return '\n'.join(lines)

    def _generate_numpy_class_docstring(self, class_name: str, description: str,
                                        attributes: Optional[List[Dict[str, Any]]]) -> str:
        """Generate NumPy-style class docstring."""
        lines = ['"""']

        if description:
            lines.append(description)
            lines.append('')

        lines.append('Attributes')
        lines.append('----------')

        if attributes:
            for attr in attributes:
                attr_type = attr.get('type', 'Any')
                attr_desc = attr.get('description', '')
                attr_name = attr.get('name', 'unknown')
                lines.append(f'{attr_name} : {attr_type}')
                lines.append(f'    {attr_desc}')
        else:
            lines.append('None')

        lines.append('"""')
        return '\n'.join(lines)

    def _generate_rst_class_docstring(self, class_name: str, description: str,
                                      attributes: Optional[List[Dict[str, Any]]]) -> str:
        """Generate RST-style class docstring."""
        lines = ['"""']

        if description:
            lines.append(description)
            lines.append('')

        if attributes:
            for attr in attributes:
                attr_type = attr.get('type', 'Any')
                attr_name = attr.get('name', 'unknown')
                lines.append(f':ivar {attr_name}: {attr.get("description", "")}')
                lines.append(f':vartype {attr_name}: {attr_type}')
        else:
            lines.append(':ivar None: No attributes')

        lines.append('"""')
        return '\n'.join(lines)

    def _generate_jsdoc_class(self, class_name: str, description: str,
                              attributes: Optional[List[Dict[str, Any]]]) -> str:
        """Generate JSDoc class comment."""
        lines = ['/**']
        lines.append(f' * {class_name} class')

        if description:
            lines.append(f' * {description}')
            lines.append(' *')

        if attributes:
            for attr in attributes:
                attr_type = attr.get('type', 'any')
                attr_name = attr.get('name', 'unknown')
                lines.append(f' * @property {{{attr_type}}} {attr_name} - {attr.get("description", "")}')

        lines.append(' */')
        return '\n'.join(lines)


# Convenience functions
def generate_docstring(func_name: str, params: List[Dict[str, Any]],
                       return_type: Optional[str] = None,
                       description: str = "") -> str:
    """Generate Google-style docstring."""
    generator = DocstringGenerator(DocstringStyle.GOOGLE)
    return generator.generate_function_docstring(func_name, params, return_type, description)


def generate_jsdoc(func_name: str, params: List[Dict[str, Any]],
                   return_type: Optional[str] = None,
                   description: str = "") -> str:
    """Generate JSDoc comment."""
    generator = DocstringGenerator(DocstringStyle.JSDOC)
    return generator.generate_function_docstring(func_name, params, return_type, description)

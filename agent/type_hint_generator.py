#!/usr/bin/env python3
"""
Type Hint Generator — Generate type hints for TypeScript/Python.

Supports:
- Python: Type annotations (PEP 484)
- TypeScript: Type annotations and interfaces
"""

from typing import Dict, Any, List, Optional, Tuple
import re

from .logger import setup_logger

logger = setup_logger(__name__)


# Python type mappings
PYTHON_TYPE_MAP = {
    'string': 'str',
    'number': 'int',
    'float': 'float',
    'boolean': 'bool',
    'list': 'List',
    'array': 'List',
    'dict': 'Dict',
    'object': 'Dict[str, Any]',
    'any': 'Any',
    'optional': 'Optional',
    'union': 'Union',
    'tuple': 'Tuple',
    'none': 'None',
    'callable': 'Callable',
}

# TypeScript type mappings
TYPESCRIPT_TYPE_MAP = {
    'string': 'string',
    'number': 'number',
    'float': 'number',
    'integer': 'number',
    'boolean': 'boolean',
    'array': 'Array',
    'list': 'Array',
    'object': 'Record<string, any>',
    'dict': 'Record<string, any>',
    'any': 'any',
    'void': 'void',
    'null': 'null',
    'undefined': 'undefined',
    'promise': 'Promise',
    'function': 'Function',
}


class TypeHintGenerator:
    """Generate type hints for Python and TypeScript."""

    def __init__(self):
        """Initialize type hint generator."""
        self.python_type_map = PYTHON_TYPE_MAP
        self.ts_type_map = TYPESCRIPT_TYPE_MAP

    def generate_python_type_hint(self, param_name: str, param_type: str, is_optional: bool = False) -> str:
        """Generate Python type hint for a parameter.

        Args:
            param_name: Parameter name
            param_type: Type name (e.g., 'string', 'number')
            is_optional: Whether parameter is optional

        Returns:
            Type hint string (e.g., 'name: str')
        """
        python_type = self._convert_to_python_type(param_type)

        if is_optional:
            python_type = f'Optional[{python_type}]'

        return f'{param_name}: {python_type}'

    def generate_python_return_hint(self, return_type: str, is_optional: bool = False) -> str:
        """Generate Python return type hint.

        Args:
            return_type: Return type name
            is_optional: Whether return is optional

        Returns:
            Return type hint (e.g., '-> str')
        """
        python_type = self._convert_to_python_type(return_type)

        if is_optional:
            python_type = f'Optional[{python_type}]'

        return f' -> {python_type}'

    def generate_typescript_type_hint(self, param_name: str, param_type: str, is_optional: bool = False) -> str:
        """Generate TypeScript type hint for a parameter.

        Args:
            param_name: Parameter name
            param_type: Type name
            is_optional: Whether parameter is optional

        Returns:
            Type hint string (e.g., 'name: string')
        """
        ts_type = self._convert_to_ts_type(param_type)

        optional_marker = '?' if is_optional else ''
        return f'{param_name}{optional_marker}: {ts_type}'

    def generate_typescript_return_hint(self, return_type: str) -> str:
        """Generate TypeScript return type hint.

        Args:
            return_type: Return type name

        Returns:
            Return type hint (e.g., ': string')
        """
        ts_type = self._convert_to_ts_type(return_type)
        return f': {ts_type}'

    def _convert_to_python_type(self, type_name: str) -> str:
        """Convert generic type name to Python type.

        Args:
            type_name: Type name to convert

        Returns:
            Python type string
        """
        type_name_lower = type_name.lower()

        # Check direct mapping
        if type_name_lower in self.python_type_map:
            return self.python_type_map[type_name_lower]

        # Handle generic types like List[str], Dict[str, int]
        list_match = re.match(r'(list|array)<(\w+)>', type_name_lower)
        if list_match:
            inner_type = self._convert_to_python_type(list_match.group(2))
            return f'List[{inner_type}]'

        dict_match = re.match(r'(dict|object)<(\w+),\s*(\w+)>', type_name_lower)
        if dict_match:
            key_type = self._convert_to_python_type(dict_match.group(2))
            value_type = self._convert_to_python_type(dict_match.group(3))
            return f'Dict[{key_type}, {value_type}]'

        # Handle union types
        union_match = re.match(r'union<([\w,\s]+)>', type_name_lower)
        if union_match:
            types = [self._convert_to_python_type(t.strip()) for t in union_match.group(1).split(',')]
            return f'Union[{", ".join(types)}]'

        # Handle tuple types
        tuple_match = re.match(r'(tuple|Tuple)<([\w,\s]+)>', type_name_lower)
        if tuple_match:
            types = [self._convert_to_python_type(t.strip()) for t in tuple_match.group(2).split(',')]
            return f'Tuple[{", ".join(types)}]'

        # Default: return as-is (could be custom type)
        return type_name

    def _convert_to_ts_type(self, type_name: str) -> str:
        """Convert generic type name to TypeScript type.

        Args:
            type_name: Type name to convert

        Returns:
            TypeScript type string
        """
        type_name_lower = type_name.lower()

        # Check direct mapping
        if type_name_lower in self.ts_type_map:
            return self.ts_type_map[type_name_lower]

        # Handle generic types like Array<string>, Record<string, any>
        array_match = re.match(r'(array|list)<(\w+)>', type_name_lower)
        if array_match:
            inner_type = self._convert_to_ts_type(array_match.group(2))
            return f'Array<{inner_type}>'

        dict_match = re.match(r'(dict|object)<([\w,\s]+)>', type_name_lower)
        if dict_match:
            inner = dict_match.group(2)
            return f'Record<{inner}>'

        # Handle union types
        union_match = re.match(r'union<([\w|,\s]+)>', type_name_lower)
        if union_match:
            types = [self._convert_to_ts_type(t.strip()) for t in union_match.group(1).split(',')]
            return ' | '.join(types)

        # Handle tuple types
        tuple_match = re.match(r'tuple<([\w,\s]+)>', type_name_lower)
        if tuple_match:
            types = [self._convert_to_ts_type(t.strip()) for t in tuple_match.group(1).split(',')]
            return f'[{", ".join(types)}]'

        # Handle promise types
        promise_match = re.match(r'promise<(\w+)>', type_name_lower)
        if promise_match:
            inner_type = self._convert_to_ts_type(promise_match.group(1))
            return f'Promise<{inner_type}>'

        # Default: return as-is (could be custom type)
        return type_name

    def generate_python_function_signature(self, func_name: str, params: List[Dict[str, str]], return_type: str = 'None') -> str:
        """Generate complete Python function signature with type hints.

        Args:
            func_name: Function name
            params: List of param dicts with 'name' and 'type' keys
            return_type: Return type

        Returns:
            Complete function signature
        """
        param_hints = []
        for param in params:
            hint = self.generate_python_type_hint(
                param['name'],
                param['type'],
                param.get('optional', False)
            )
            param_hints.append(hint)

        return_hint = self.generate_python_return_hint(return_type)

        return f'def {func_name}({", ".join(param_hints)}){return_hint}:'

    def generate_typescript_function_signature(self, func_name: str, params: List[Dict[str, str]], return_type: str = 'void') -> str:
        """Generate complete TypeScript function signature with type hints.

        Args:
            func_name: Function name
            params: List of param dicts with 'name' and 'type' keys
            return_type: Return type

        Returns:
            Complete function signature
        """
        param_hints = []
        for param in params:
            hint = self.generate_typescript_type_hint(
                param['name'],
                param['type'],
                param.get('optional', False)
            )
            param_hints.append(hint)

        return_hint = self.generate_typescript_return_hint(return_type)

        return f'function {func_name}({", ".join(param_hints)}){return_hint}'

    def generate_python_interface(self, name: str, fields: List[Dict[str, str]]) -> str:
        """Generate Python class with type hints (interface-like).

        Args:
            name: Class name
            fields: List of field dicts with 'name' and 'type' keys

        Returns:
            Python class definition
        """
        lines = [f'class {name}:']
        lines.append('    """Auto-generated class with type hints."""')
        lines.append('')
        lines.append('    def __init__(self,')

        # Build __init__ parameters
        init_params = ['self']
        for field in fields:
            hint = self.generate_python_type_hint(field['name'], field['type'])
            init_params.append(f'        {hint}')

        lines.append(',\n'.join(init_params))
        lines.append('    ) -> None:')

        # Build assignments
        for field in fields:
            lines.append(f'        self.{field["name"]}: {self._convert_to_python_type(field["type"])} = {field["name"]}')

        return '\n'.join(lines)

    def generate_typescript_interface(self, name: str, fields: List[Dict[str, str]]) -> str:
        """Generate TypeScript interface with type hints.

        Args:
            name: Interface name
            fields: List of field dicts with 'name' and 'type' keys

        Returns:
            TypeScript interface definition
        """
        lines = [f'export interface {name} {{']

        for field in fields:
            hint = self.generate_typescript_type_hint(
                field['name'],
                field['type'],
                field.get('optional', False)
            )
            lines.append(f'    {hint};')

        lines.append('}')

        return '\n'.join(lines)


# Convenience functions
def generate_python_type_hint(param_name: str, param_type: str) -> str:
    """Generate Python type hint."""
    generator = TypeHintGenerator()
    return generator.generate_python_type_hint(param_name, param_type)


def generate_typescript_type_hint(param_name: str, param_type: str) -> str:
    """Generate TypeScript type hint."""
    generator = TypeHintGenerator()
    return generator.generate_typescript_type_hint(param_name, param_type)

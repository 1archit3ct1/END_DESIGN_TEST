"""
Import Resolver — Cross-file import resolution.

Validates and resolves imports between generated files.
"""

import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field

from .logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class CircularDependencyInfo:
    """Information about a circular dependency."""
    cycle: List[str]  # Files in the cycle
    description: str


@dataclass
class ImportInfo:
    """Information about a single import statement."""
    statement: str
    source: str  # The module being imported from
    names: List[str] = field(default_factory=list)  # Named imports
    default_import: str = ""  # Default import name
    namespace_import: str = ""  # * import or namespace
    line_number: int = 0
    is_relative: bool = False
    is_type_import: bool = False


@dataclass
class ExportInfo:
    """Information about exports from a file."""
    names: List[str] = field(default_factory=list)
    default_export: bool = False
    named_exports: Dict[str, str] = field(default_factory=dict)  # name -> type


@dataclass
class ImportResolutionResult:
    """Result of import resolution."""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    resolved_imports: List[Tuple[str, str]] = field(default_factory=list)  # (from, to)


class ImportResolver:
    """Resolve and validate cross-file imports."""

    # Regex patterns for different import styles
    PATTERNS = {
        'typescript_es6': re.compile(
            r'^\s*import\s+(?:type\s+)?(?:'
            r'(?P<default>\w+)(?:\s*,\s*)?'
            r'(?:(?P<braced>\{[^}]*\})\s*(?:from\s*)?|'
            r'(?P<star>\*\s*as\s+\w+)\s*from\s*)?'
            r'["\'](?P<source>[^"\']+)["\']'
            r'|import\s+(?P<side_effect_side>[^"\']+)["\']([^"\']*)["\']'
            r')',
            re.MULTILINE
        ),
        'python': re.compile(
            r'^\s*(?:from\s+(?P<from>\S+)\s+)?import\s+(?P<import>\S+)',
            re.MULTILINE
        ),
        'rust': re.compile(
            r'^\s*use\s+(?P<use>\S+);',
            re.MULTILINE
        ),
    }

    # File extension mappings
    EXTENSION_MAP = {
        '.ts': ['.ts', '.tsx', '.d.ts'],
        '.tsx': ['.ts', '.tsx', '.d.ts'],
        '.js': ['.js', '.jsx', '.mjs'],
        '.jsx': ['.js', '.jsx'],
        '.py': ['.py'],
        '.rs': ['.rs'],
    }

    def __init__(self, output_dir: Path):
        """Initialize import resolver.

        Args:
            output_dir: Output directory path
        """
        self.output_dir = output_dir
        self.file_registry: Dict[str, Set[str]] = {}  # file -> exports
        self.import_map: Dict[str, List[ImportInfo]] = {}  # file -> imports

    def register_file(self, file_path: Path, content: str) -> None:
        """Register a file and its exports.

        Args:
            file_path: Path to the file
            content: File content
        """
        rel_path = self._normalize_path(file_path)
        
        # Extract exports
        exports = self._extract_exports(content, file_path.suffix)
        self.file_registry[rel_path] = exports.names
        
        # Extract imports
        imports = self._extract_imports(content, file_path.suffix)
        self.import_map[rel_path] = imports
        
        logger.debug(f"Registered file: {rel_path} ({len(exports.names)} exports, {len(imports)} imports)")

    def _normalize_path(self, file_path: Path) -> str:
        """Normalize path to use forward slashes.

        Args:
            file_path: Path to normalize

        Returns:
            Normalized path string
        """
        try:
            rel_path = str(file_path.relative_to(self.output_dir))
        except ValueError:
            rel_path = str(file_path)
        return rel_path.replace('\\', '/')

    def _extract_exports(self, content: str, extension: str) -> ExportInfo:
        """Extract exports from file content.

        Args:
            content: File content
            extension: File extension

        Returns:
            ExportInfo with extracted exports
        """
        exports = ExportInfo()
        
        if extension in ['.ts', '.tsx', '.js', '.jsx']:
            # Named exports: export const/function/class name
            named_pattern = re.compile(r'export\s+(?:const|let|var|function|class|interface|type|enum)\s+(\w+)', re.MULTILINE)
            for match in named_pattern.finditer(content):
                name = match.group(1)
                exports.names.append(name)
                exports.named_exports[name] = 'named'
            
            # Export list: export { name1, name2 }
            list_pattern = re.compile(r'export\s+\{([^}]+)\}', re.MULTILINE)
            for match in list_pattern.finditer(content):
                names = [n.strip().split(' as ')[0].strip() for n in match.group(1).split(',')]
                for name in names:
                    if name and name not in exports.names:
                        exports.names.append(name)
                        exports.named_exports[name] = 'listed'
            
            # Default export
            if re.search(r'export\s+default\s+', content):
                exports.default_export = True
                
        elif extension == '.py':
            # Python: check __all__ or public names
            all_pattern = re.compile(r'__all__\s*=\s*\[([^\]]+)\]')
            match = all_pattern.search(content)
            if match:
                names = [n.strip().strip('"\'') for n in match.group(1).split(',')]
                exports.names = names
            else:
                # Extract public functions/classes (not starting with _)
                for pattern in [r'def\s+(\w+)\s*\(', r'class\s+(\w+)']:
                    for m in re.finditer(pattern, content):
                        name = m.group(1)
                        if not name.startswith('_'):
                            exports.names.append(name)
                            
        elif extension == '.rs':
            # Rust: pub functions/structs
            for pattern in [r'pub\s+fn\s+(\w+)', r'pub\s+struct\s+(\w+)', r'pub\s+mod\s+(\w+)']:
                for m in re.finditer(pattern, content):
                    name = m.group(1)
                    exports.names.append(name)
        
        return exports

    def _extract_imports(self, content: str, extension: str) -> List[ImportInfo]:
        """Extract imports from file content.

        Args:
            content: File content
            extension: File extension

        Returns:
            List of ImportInfo objects
        """
        imports = []
        lines = content.split('\n')
        
        if extension in ['.ts', '.tsx', '.js', '.jsx']:
            # ES6 imports - improved pattern for default imports
            import_pattern = re.compile(
                r'import\s+(?:type\s+)?'
                r'(?:(\w+)(?:\s*,\s*)?)?'
                r'(?:(\{[^}]*\})\s*(?:from\s*)?'
                r'|(\*\s*as\s+\w+)\s*from\s*)?'
                r'["\']([^"\']+)["\']'
            )
            # Simpler pattern for default imports: import Name from "source"
            default_import_pattern = re.compile(
                r'import\s+(\w+)\s+from\s+["\']([^"\']+)["\']'
            )
            
            for line_num, line in enumerate(lines, 1):
                # Try default import pattern first
                default_match = default_import_pattern.search(line)
                if default_match and '{' not in line and '*' not in line:
                    imports.append(ImportInfo(
                        statement=line.strip(),
                        source=default_match.group(2),
                        default_import=default_match.group(1),
                        line_number=line_num,
                        is_relative=default_match.group(2).startswith('.')
                    ))
                    continue
                
                # Try full pattern
                match = import_pattern.search(line)
                if match:
                    default_import = match.group(1) or ""
                    braced = match.group(2) or ""
                    star = match.group(3) or ""
                    source = match.group(4)
                    
                    names = []
                    if braced:
                        names = [n.strip().split(' as ')[0].strip() 
                                for n in braced.strip('{}').split(',')]
                        names = [n for n in names if n]
                    
                    is_type_import = 'import type' in line
                    
                    imports.append(ImportInfo(
                        statement=line.strip(),
                        source=source,
                        names=names,
                        default_import=default_import,
                        namespace_import=star,
                        line_number=line_num,
                        is_relative=source.startswith('.'),
                        is_type_import=is_type_import
                    ))
                    
        elif extension == '.py':
            # Python imports
            for line_num, line in enumerate(lines, 1):
                # from X import Y
                from_match = re.match(r'^\s*from\s+(\S+)\s+import\s+(.+)', line)
                if from_match:
                    source = from_match.group(1)
                    imported = from_match.group(2).strip()
                    names = [n.strip().split(' as ')[0].strip() for n in imported.split(',')]
                    imports.append(ImportInfo(
                        statement=line.strip(),
                        source=source,
                        names=names,
                        line_number=line_num,
                        is_relative=source.startswith('.')
                    ))
                    continue
                
                # import X
                import_match = re.match(r'^\s*import\s+(\S+)', line)
                if import_match:
                    source = import_match.group(1)
                    imports.append(ImportInfo(
                        statement=line.strip(),
                        source=source,
                        names=[source.split('.')[0]],
                        line_number=line_num
                    ))
                    
        elif extension == '.rs':
            # Rust use statements
            for line_num, line in enumerate(lines, 1):
                use_match = re.match(r'^\s*use\s+(.+);', line)
                if use_match:
                    source = use_match.group(1)
                    imports.append(ImportInfo(
                        statement=line.strip(),
                        source=source,
                        line_number=line_num
                    ))
        
        return imports

    def resolve_imports(self, file_path: Path) -> ImportResolutionResult:
        """Resolve all imports for a file.

        Args:
            file_path: Path to the file

        Returns:
            ImportResolutionResult with validation results
        """
        rel_path = self._normalize_path(file_path)
        result = ImportResolutionResult(valid=True)
        
        if rel_path not in self.import_map:
            result.errors.append(f"File not registered: {rel_path}")
            result.valid = False
            return result
        
        imports = self.import_map[rel_path]
        
        for imp in imports:
            if not imp.is_relative:
                # External package import - skip resolution
                continue
            
            # Resolve relative import
            resolved_path = self._resolve_relative_import(
                rel_path, imp.source, file_path.suffix
            )
            
            if resolved_path is None:
                result.errors.append(
                    f"Line {imp.line_number}: Cannot resolve import '{imp.source}' in {rel_path}"
                )
                result.valid = False
            else:
                result.resolved_imports.append((rel_path, resolved_path))
                
                # Check if imported names exist
                if imp.names and resolved_path in self.file_registry:
                    exports = self.file_registry[resolved_path]
                    for name in imp.names:
                        if name not in exports and not name.startswith('_'):
                            result.warnings.append(
                                f"Line {imp.line_number}: '{name}' not exported from {resolved_path}"
                            )
        
        return result

    def _resolve_relative_import(self, from_file: str, import_path: str, extension: str) -> Optional[str]:
        """Resolve a relative import path.

        Args:
            from_file: Source file path (normalized with forward slashes)
            import_path: Import statement path
            extension: File extension

        Returns:
            Resolved file path (normalized) or None
        """
        from_dir = Path(from_file).parent
        
        # Handle relative path - manually resolve .. and .
        if import_path.startswith('.'):
            # Combine paths and normalize
            combined = from_dir / import_path
            parts = combined.as_posix().split('/')
            normalized = []
            for part in parts:
                if part == '..':
                    if normalized:
                        normalized.pop()
                elif part and part != '.':
                    normalized.append(part)
            resolved_path = '/'.join(normalized)
        else:
            resolved_path = (from_dir / import_path).as_posix()
        
        # Clean up the path (remove double slashes, etc.)
        resolved_path = resolved_path.replace('//', '/')
        
        # Try with original extension
        possible_paths = [resolved_path]
        
        # Try with alternative extensions
        possible_extensions = self.EXTENSION_MAP.get(extension, [extension])
        for ext in possible_extensions:
            if not resolved_path.endswith(ext):
                possible_paths.append(resolved_path + ext)
        
        # Try with index files
        for ext in possible_extensions:
            possible_paths.append(f"{resolved_path}/index{ext}")
        
        # Check which file exists in registry (normalize all paths)
        for path in possible_paths:
            # Normalize path to forward slashes
            normalized = path.replace('\\', '/')
            if normalized in self.file_registry:
                return normalized
            
            # Try without leading ./
            if normalized.startswith('./') and normalized[2:] in self.file_registry:
                return normalized[2:]
        
        return None

    def validate_all_imports(self) -> ImportResolutionResult:
        """Validate all imports across all registered files.

        Returns:
            ImportResolutionResult with combined validation results
        """
        combined = ImportResolutionResult(valid=True)
        
        for file_path_str in self.import_map.keys():
            file_path = self.output_dir / file_path_str
            result = self.resolve_imports(file_path)
            
            combined.errors.extend(result.errors)
            combined.warnings.extend(result.warnings)
            combined.resolved_imports.extend(result.resolved_imports)
            
            if not result.valid:
                combined.valid = False
        
        logger.info(f"Validated imports: {len(combined.resolved_imports)} resolved, {len(combined.errors)} errors")
        return combined

    def get_import_graph(self) -> Dict[str, Set[str]]:
        """Build import dependency graph.

        Returns:
            Dictionary mapping files to their dependencies
        """
        graph = {}
        
        for file_path, imports in self.import_map.items():
            deps = set()
            for imp in imports:
                if imp.is_relative:
                    from_path = self.output_dir / file_path
                    resolved = self._resolve_relative_import(
                        file_path, imp.source, from_path.suffix
                    )
                    if resolved:
                        deps.add(resolved)
            graph[file_path] = deps
        
        return graph

    def get_reverse_imports(self) -> Dict[str, Set[str]]:
        """Build reverse import graph (who imports me).

        Returns:
            Dictionary mapping files to their dependents
        """
        forward = self.get_import_graph()
        reverse = {f: set() for f in forward}
        
        for file_path, deps in forward.items():
            for dep in deps:
                if dep in reverse:
                    reverse[dep].add(file_path)
        
        return reverse

    def find_unused_exports(self) -> Dict[str, List[str]]:
        """Find exports that are never imported.

        Returns:
            Dictionary mapping files to their unused exports
        """
        unused = {}
        reverse = self.get_reverse_imports()
        
        for file_path, exports in self.file_registry.items():
            importers = reverse.get(file_path, set())
            
            # If file has no importers, all exports are potentially unused
            # (except if it's an entry point)
            if not importers and not self._is_entry_point(file_path):
                unused[file_path] = exports
            else:
                # Check individual exports
                used_exports = set()
                for importer in importers:
                    if importer in self.import_map:
                        for imp in self.import_map[importer]:
                            if imp.source in file_path or imp.source.endswith(file_path):
                                used_exports.update(imp.names)
                
                unused_exports = [e for e in exports if e not in used_exports]
                if unused_exports:
                    unused[file_path] = unused_exports
        
        return unused

    def _is_entry_point(self, file_path: str) -> bool:
        """Check if file is an entry point.

        Args:
            file_path: File path to check

        Returns:
            True if file is an entry point
        """
        entry_points = [
            'index.ts', 'index.tsx', 'index.js', 'index.jsx',
            'main.py', 'app.py', '__init__.py',
            'main.rs', 'lib.rs',
        ]
        return Path(file_path).name in entry_points

    def detect_circular_dependencies(self) -> List[CircularDependencyInfo]:
        """Detect circular dependencies in the import graph.

        Returns:
            List of CircularDependencyInfo objects describing each cycle
        """
        graph = self.get_import_graph()
        cycles = []
        visited = set()
        rec_stack = set()
        path = []

        def dfs(node: str) -> None:
            """DFS to detect cycles."""
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, set()):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(CircularDependencyInfo(
                        cycle=cycle,
                        description=f"Circular dependency: {' -> '.join(cycle)}"
                    ))

            path.pop()
            rec_stack.remove(node)

        for node in graph:
            if node not in visited:
                dfs(node)

        if cycles:
            logger.warning(f"Detected {len(cycles)} circular dependencies")
        else:
            logger.debug("No circular dependencies detected")

        return cycles

    def validate_imports_with_cycles(self) -> Tuple[ImportResolutionResult, List[CircularDependencyInfo]]:
        """Validate imports and detect circular dependencies.

        Returns:
            Tuple of (ImportResolutionResult, list of CircularDependencyInfo)
        """
        result = self.validate_all_imports()
        cycles = self.detect_circular_dependencies()

        # Add circular dependency errors to result
        for cycle_info in cycles:
            result.errors.append(f"Circular dependency: {cycle_info.description}")
            result.valid = False

        return result, cycles

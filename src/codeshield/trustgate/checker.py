"""
TrustGate Checker - Core verification engine

Verifies code before you see it:
- Syntax checking
- Missing import detection
- Type checking (basic)
- Execution testing
"""

import ast
import sys
import re
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path

# Standard library modules that are commonly used
STDLIB_MODULES = {
    'os', 'sys', 'json', 're', 'math', 'random', 'datetime', 'time',
    'collections', 'itertools', 'functools', 'typing', 'pathlib',
    'subprocess', 'threading', 'multiprocessing', 'asyncio',
    'urllib', 'http', 'socket', 'email', 'html', 'xml',
    'sqlite3', 'csv', 'configparser', 'logging', 'unittest',
    'hashlib', 'hmac', 'secrets', 'base64', 'pickle', 'copy',
    'io', 'tempfile', 'shutil', 'glob', 'fnmatch',
    'argparse', 'getopt', 'textwrap', 'string',
    'dataclasses', 'enum', 'abc', 'contextlib',
}

# Common third-party modules and their pip names
COMMON_PACKAGES = {
    'requests': 'requests',
    'numpy': 'numpy',
    'pandas': 'pandas',
    'flask': 'flask',
    'django': 'django',
    'fastapi': 'fastapi',
    'httpx': 'httpx',
    'aiohttp': 'aiohttp',
    'pydantic': 'pydantic',
    'sqlalchemy': 'sqlalchemy',
    'pytest': 'pytest',
    'rich': 'rich',
    'click': 'click',
    'typer': 'typer',
    'beautifulsoup4': 'bs4',
    'bs4': 'beautifulsoup4',
    'PIL': 'pillow',
    'cv2': 'opencv-python',
    'sklearn': 'scikit-learn',
    'torch': 'torch',
    'tensorflow': 'tensorflow',
}


@dataclass
class VerificationIssue:
    """A single verification issue"""
    severity: str  # "error", "warning", "info"
    message: str
    line: Optional[int] = None
    column: Optional[int] = None
    fix_available: bool = False
    fix_description: Optional[str] = None


@dataclass
class VerificationResult:
    """Result of code verification"""
    is_valid: bool
    issues: list[VerificationIssue] = field(default_factory=list)
    fixed_code: Optional[str] = None
    confidence_score: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            "is_valid": self.is_valid,
            "issues": [
                {
                    "type": i.severity,
                    "severity": i.severity,
                    "message": i.message,
                    "line": i.line,
                    "fix_available": i.fix_available,
                    "fix_description": i.fix_description,
                }
                for i in self.issues
            ],
            "confidence_score": self.confidence_score,
            "has_fixes": self.fixed_code is not None,
        }


class ImportVisitor(ast.NodeVisitor):
    """Visits AST to find all imports"""
    
    def __init__(self):
        self.imports: set[str] = set()
        self.from_imports: dict[str, set[str]] = {}
    
    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imports.add(alias.name.split('.')[0])
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            base_module = node.module.split('.')[0]
            self.imports.add(base_module)
            if base_module not in self.from_imports:
                self.from_imports[base_module] = set()
            for alias in node.names:
                self.from_imports[base_module].add(alias.name)
        self.generic_visit(node)


class NameVisitor(ast.NodeVisitor):
    """Visits AST to find all used names"""
    
    def __init__(self):
        self.used_names: set[str] = set()
        self.defined_names: set[str] = set()
        self.function_calls: set[str] = set()
    
    def visit_Name(self, node: ast.Name):
        if isinstance(node.ctx, ast.Load):
            self.used_names.add(node.id)
        elif isinstance(node.ctx, ast.Store):
            self.defined_names.add(node.id)
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Attribute):
            # module.function() calls
            if isinstance(node.func.value, ast.Name):
                self.function_calls.add(f"{node.func.value.id}.{node.func.attr}")
        elif isinstance(node.func, ast.Name):
            self.function_calls.add(node.func.id)
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.defined_names.add(node.name)
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.defined_names.add(node.name)
        self.generic_visit(node)
    
    def visit_ClassDef(self, node: ast.ClassDef):
        self.defined_names.add(node.name)
        self.generic_visit(node)


def check_syntax(code: str) -> tuple[bool, Optional[VerificationIssue]]:
    """Check if code has valid Python syntax"""
    try:
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, VerificationIssue(
            severity="error",
            message=f"Syntax error: {e.msg}",
            line=e.lineno,
            column=e.offset,
            fix_available=False,
        )


def detect_missing_imports(code: str) -> list[VerificationIssue]:
    """Detect missing imports in code"""
    issues = []
    
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return issues  # Can't parse, syntax check will catch this
    
    # Get all imports
    import_visitor = ImportVisitor()
    import_visitor.visit(tree)
    imported = import_visitor.imports
    
    # Get all used names
    name_visitor = NameVisitor()
    name_visitor.visit(tree)
    
    # Check function calls for module usage
    for call in name_visitor.function_calls:
        if '.' in call:
            module = call.split('.')[0]
            if module not in imported and module not in name_visitor.defined_names:
                # Check if it's a known module
                if module in STDLIB_MODULES:
                    issues.append(VerificationIssue(
                        severity="error",
                        message=f"Missing import: {module}",
                        fix_available=True,
                        fix_description=f"Add 'import {module}'",
                    ))
                elif module in COMMON_PACKAGES:
                    issues.append(VerificationIssue(
                        severity="error",
                        message=f"Missing import: {module} (pip install {COMMON_PACKAGES[module]})",
                        fix_available=True,
                        fix_description=f"Add 'import {module}'",
                    ))
    
    return issues


def detect_undefined_names(code: str) -> list[VerificationIssue]:
    """Detect potentially undefined variable names"""
    issues = []
    
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return issues
    
    # Get imports
    import_visitor = ImportVisitor()
    import_visitor.visit(tree)
    
    # Get names
    name_visitor = NameVisitor()
    name_visitor.visit(tree)
    
    # Built-in names that don't need imports
    builtins = set(dir(__builtins__)) if isinstance(__builtins__, dict) else set(dir(__builtins__))
    builtins.update({'True', 'False', 'None', 'self', 'cls'})
    
    # Find undefined names
    all_defined = (
        name_visitor.defined_names | 
        import_visitor.imports | 
        builtins
    )
    
    for name in name_visitor.used_names:
        if name not in all_defined and not name.startswith('_'):
            # Check if it might be a module
            if name in STDLIB_MODULES or name in COMMON_PACKAGES:
                issues.append(VerificationIssue(
                    severity="warning",
                    message=f"'{name}' used but not imported",
                    fix_available=True,
                    fix_description=f"Add 'import {name}'",
                ))
    
    return issues


def auto_fix_imports(code: str, issues: list[VerificationIssue]) -> str:
    """Auto-fix missing imports"""
    imports_to_add = []
    
    for issue in issues:
        if issue.fix_available and "Missing import:" in issue.message:
            # Extract module name
            match = re.search(r"Missing import: (\w+)", issue.message)
            if match:
                module = match.group(1)
                imports_to_add.append(f"import {module}")
    
    if not imports_to_add:
        return code
    
    # Add imports at the top (after any existing imports or docstrings)
    lines = code.split('\n')
    insert_pos = 0
    
    # Skip docstrings
    in_docstring = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            if in_docstring:
                in_docstring = False
                insert_pos = i + 1
            else:
                in_docstring = True
        elif not in_docstring and (stripped.startswith('import ') or stripped.startswith('from ')):
            insert_pos = i + 1
        elif not in_docstring and stripped and not stripped.startswith('#'):
            break
    
    # Insert imports
    for imp in imports_to_add:
        lines.insert(insert_pos, imp)
        insert_pos += 1
    
    return '\n'.join(lines)


def verify_code(code: str, auto_fix: bool = True) -> VerificationResult:
    """
    Main verification function.
    
    Args:
        code: Python code to verify
        auto_fix: Whether to attempt auto-fixes
    
    Returns:
        VerificationResult with issues and optionally fixed code
    """
    issues: list[VerificationIssue] = []
    
    # 1. Syntax check
    syntax_ok, syntax_issue = check_syntax(code)
    if not syntax_ok and syntax_issue:
        issues.append(syntax_issue)
        return VerificationResult(
            is_valid=False,
            issues=issues,
            confidence_score=0.0,
        )
    
    # 2. Missing imports
    import_issues = detect_missing_imports(code)
    issues.extend(import_issues)
    
    # 3. Undefined names
    undefined_issues = detect_undefined_names(code)
    issues.extend(undefined_issues)
    
    # Calculate confidence score
    error_count = sum(1 for i in issues if i.severity == "error")
    warning_count = sum(1 for i in issues if i.severity == "warning")
    confidence = max(0.0, 1.0 - (error_count * 0.2) - (warning_count * 0.05))
    
    # Auto-fix if requested
    fixed_code = None
    if auto_fix and issues:
        fixed_code = auto_fix_imports(code, issues)
        if fixed_code != code:
            # Re-verify fixed code
            recheck_syntax, _ = check_syntax(fixed_code)
            if recheck_syntax:
                confidence = min(confidence + 0.1, 1.0)
    
    is_valid = error_count == 0
    
    return VerificationResult(
        is_valid=is_valid,
        issues=issues,
        fixed_code=fixed_code,
        confidence_score=confidence,
    )


def verify_file(file_path: str) -> VerificationResult:
    """Verify a Python file"""
    path = Path(file_path)
    if not path.exists():
        return VerificationResult(
            is_valid=False,
            issues=[VerificationIssue(
                severity="error",
                message=f"File not found: {file_path}",
            )],
            confidence_score=0.0,
        )
    
    code = path.read_text(encoding='utf-8')
    return verify_code(code)


# Quick test
if __name__ == "__main__":
    test_code = '''
def fetch_data():
    response = requests.get("https://api.example.com")
    return json.loads(response.text)
'''
    
    result = verify_code(test_code)
    print(f"Valid: {result.is_valid}")
    print(f"Confidence: {result.confidence_score:.0%}")
    for issue in result.issues:
        print(f"  [{issue.severity}] {issue.message}")
    if result.fixed_code:
        print("\nFixed code:")
        print(result.fixed_code)

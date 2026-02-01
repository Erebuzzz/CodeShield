"""
StyleForge Corrector - Convention enforcement

Enforces YOUR codebase conventions:
- Naming pattern detection
- Variable name correction
- Function name matching
"""

import ast
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from collections import Counter


@dataclass
class NamingConvention:
    """Detected naming convention"""
    pattern: str  # "snake_case", "camelCase", "PascalCase", "SCREAMING_SNAKE"
    confidence: float
    examples: list[str] = field(default_factory=list)


@dataclass
class StyleIssue:
    """A style issue found in code"""
    message: str
    original: str
    suggested: str
    line: Optional[int] = None


@dataclass
class StyleCheckResult:
    """Result of style checking"""
    matches_convention: bool
    issues: list[StyleIssue] = field(default_factory=list)
    conventions_detected: dict = field(default_factory=dict)
    corrected_code: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "matches_convention": self.matches_convention,
            "issues": [
                {
                    "message": i.message,
                    "original": i.original,
                    "suggested": i.suggested,
                    "line": i.line,
                }
                for i in self.issues
            ],
            "conventions_detected": self.conventions_detected,
            "has_corrections": self.corrected_code is not None,
        }


def detect_naming_pattern(name: str) -> str:
    """Detect the naming pattern of a single name"""
    if name.isupper() and '_' in name:
        return "SCREAMING_SNAKE"
    elif '_' in name and name.islower():
        return "snake_case"
    elif name[0].isupper() and not '_' in name:
        return "PascalCase"
    elif name[0].islower() and any(c.isupper() for c in name):
        return "camelCase"
    elif name.islower():
        return "snake_case"
    else:
        return "mixed"


def convert_to_snake_case(name: str) -> str:
    """Convert name to snake_case"""
    # Handle camelCase and PascalCase
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def convert_to_camel_case(name: str) -> str:
    """Convert name to camelCase"""
    if '_' in name:
        components = name.split('_')
        return components[0].lower() + ''.join(x.title() for x in components[1:])
    return name


class CodebaseAnalyzer(ast.NodeVisitor):
    """Analyzes codebase to extract naming conventions"""
    
    def __init__(self):
        self.variable_names: list[str] = []
        self.function_names: list[str] = []
        self.class_names: list[str] = []
        self.constant_names: list[str] = []
    
    def visit_Name(self, node: ast.Name):
        if isinstance(node.ctx, ast.Store):
            if node.id.isupper():
                self.constant_names.append(node.id)
            else:
                self.variable_names.append(node.id)
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.function_names.append(node.name)
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.function_names.append(node.name)
        self.generic_visit(node)
    
    def visit_ClassDef(self, node: ast.ClassDef):
        self.class_names.append(node.name)
        self.generic_visit(node)


def analyze_codebase(path: str) -> dict[str, NamingConvention]:
    """Analyze codebase and extract naming conventions"""
    path = Path(path)
    
    if not path.exists():
        return {}
    
    analyzer = CodebaseAnalyzer()
    
    # Find all Python files
    py_files = list(path.rglob("*.py")) if path.is_dir() else [path]
    
    for py_file in py_files[:50]:  # Limit for performance
        try:
            code = py_file.read_text(encoding='utf-8')
            tree = ast.parse(code)
            analyzer.visit(tree)
        except (SyntaxError, UnicodeDecodeError):
            continue
    
    # Detect patterns
    conventions = {}
    
    # Variable naming
    if analyzer.variable_names:
        patterns = [detect_naming_pattern(n) for n in analyzer.variable_names if len(n) > 1]
        pattern_counts = Counter(patterns)
        if pattern_counts:
            most_common = pattern_counts.most_common(1)[0]
            conventions["variables"] = NamingConvention(
                pattern=most_common[0],
                confidence=most_common[1] / len(patterns),
                examples=analyzer.variable_names[:5]
            )
    
    # Function naming
    if analyzer.function_names:
        patterns = [detect_naming_pattern(n) for n in analyzer.function_names if not n.startswith('_')]
        pattern_counts = Counter(patterns)
        if pattern_counts:
            most_common = pattern_counts.most_common(1)[0]
            conventions["functions"] = NamingConvention(
                pattern=most_common[0],
                confidence=most_common[1] / len(patterns),
                examples=analyzer.function_names[:5]
            )
    
    return conventions


def build_name_registry(path: str) -> dict[str, set[str]]:
    """Build registry of all names in codebase"""
    path = Path(path)
    
    if not path.exists():
        return {}
    
    analyzer = CodebaseAnalyzer()
    
    py_files = list(path.rglob("*.py")) if path.is_dir() else [path]
    
    for py_file in py_files[:50]:
        try:
            code = py_file.read_text(encoding='utf-8')
            tree = ast.parse(code)
            analyzer.visit(tree)
        except (SyntaxError, UnicodeDecodeError):
            continue
    
    return {
        "variables": set(analyzer.variable_names),
        "functions": set(analyzer.function_names),
        "classes": set(analyzer.class_names),
    }


def check_style(code: str, codebase_path: str = ".") -> StyleCheckResult:
    """
    Check code against codebase conventions.
    
    Args:
        code: Code to check
        codebase_path: Path to codebase for convention extraction
    
    Returns:
        StyleCheckResult with issues and suggestions
    """
    issues: list[StyleIssue] = []
    
    # Analyze codebase conventions
    conventions = analyze_codebase(codebase_path)
    registry = build_name_registry(codebase_path)
    
    # Parse code
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return StyleCheckResult(
            matches_convention=False,
            issues=[StyleIssue(
                message="Cannot parse code",
                original="",
                suggested="",
            )],
        )
    
    # Analyze code names
    code_analyzer = CodebaseAnalyzer()
    code_analyzer.visit(tree)
    
    # Check variable naming
    var_convention = conventions.get("variables")
    if var_convention and var_convention.pattern == "snake_case":
        for var in code_analyzer.variable_names:
            pattern = detect_naming_pattern(var)
            if pattern == "camelCase":
                suggested = convert_to_snake_case(var)
                issues.append(StyleIssue(
                    message=f"Variable '{var}' uses camelCase, codebase uses snake_case",
                    original=var,
                    suggested=suggested,
                ))
    
    # Check function naming
    func_convention = conventions.get("functions")
    if func_convention and func_convention.pattern == "snake_case":
        for func in code_analyzer.function_names:
            pattern = detect_naming_pattern(func)
            if pattern == "camelCase":
                suggested = convert_to_snake_case(func)
                issues.append(StyleIssue(
                    message=f"Function '{func}' uses camelCase, codebase uses snake_case",
                    original=func,
                    suggested=suggested,
                ))
    
    # Check for similar existing names (typo detection)
    all_existing_names = set()
    for names in registry.values():
        all_existing_names.update(names)
    
    for var in code_analyzer.variable_names:
        normalized = var.lower().replace('_', '')
        for existing in all_existing_names:
            existing_normalized = existing.lower().replace('_', '')
            # Check for slight variations
            if normalized != existing_normalized and len(normalized) > 3:
                if normalized[:-1] == existing_normalized or normalized == existing_normalized[:-1]:
                    issues.append(StyleIssue(
                        message=f"'{var}' might be a typo of existing '{existing}'",
                        original=var,
                        suggested=existing,
                    ))
    
    # Apply corrections
    corrected_code = code
    if issues:
        for issue in issues:
            if issue.original and issue.suggested:
                # Simple replacement (word boundary aware)
                pattern = r'\b' + re.escape(issue.original) + r'\b'
                corrected_code = re.sub(pattern, issue.suggested, corrected_code)
    
    # Build conventions dict for response
    conv_dict = {}
    for name, conv in conventions.items():
        conv_dict[name] = {
            "pattern": conv.pattern,
            "confidence": conv.confidence,
            "examples": conv.examples[:3],
        }
    
    return StyleCheckResult(
        matches_convention=len(issues) == 0,
        issues=issues,
        conventions_detected=conv_dict,
        corrected_code=corrected_code if corrected_code != code else None,
    )

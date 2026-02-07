"""
Parsing Layer — tree-sitter multi-language parser

Wraps tree-sitter to provide a uniform parse interface for
Python, JavaScript, and TypeScript.  Returns the raw tree-sitter
tree which the normalisation layer then converts to a MetaAST.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

import tree_sitter_python as ts_python
import tree_sitter_javascript as ts_javascript
from tree_sitter import Language, Parser, Tree, Node


# ---------------------------------------------------------------------------
# Language registry
# ---------------------------------------------------------------------------

class Lang(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"


_LANGUAGES: dict[Lang, Language] = {}


def _get_language(lang: Lang) -> Language:
    """Lazily initialise and cache tree-sitter Language objects."""
    if lang not in _LANGUAGES:
        if lang == Lang.PYTHON:
            ptr = ts_python.language()
        elif lang == Lang.JAVASCRIPT:
            ptr = ts_javascript.language()
        else:
            raise ValueError(f"Unsupported language: {lang}")

        # Handle both old (Language(ptr, name)) and new (Language(ptr)) APIs
        _LANGUAGES[lang] = Language(ptr)
    return _LANGUAGES[lang]


def get_supported_languages() -> list[str]:
    """Return the list of languages the engine can parse."""
    return [l.value for l in Lang]


# ---------------------------------------------------------------------------
# File-extension → language mapping
# ---------------------------------------------------------------------------

_EXT_MAP: dict[str, Lang] = {
    ".py": Lang.PYTHON,
    ".pyw": Lang.PYTHON,
    ".pyi": Lang.PYTHON,
    ".js": Lang.JAVASCRIPT,
    ".mjs": Lang.JAVASCRIPT,
    ".cjs": Lang.JAVASCRIPT,
    ".jsx": Lang.JAVASCRIPT,
}


def detect_language(filename: str) -> Optional[Lang]:
    """Guess language from file extension."""
    for ext, lang in _EXT_MAP.items():
        if filename.endswith(ext):
            return lang
    return None


# ---------------------------------------------------------------------------
# Parse result wrapper
# ---------------------------------------------------------------------------

@dataclass
class ParseResult:
    """Wraps a tree-sitter parse tree with metadata."""
    tree: Tree
    source: bytes
    language: Lang
    has_errors: bool

    @property
    def root(self) -> Node:
        return self.tree.root_node

    def text_of(self, node: Node) -> str:
        """Extract source text for a given node."""
        return self.source[node.start_byte:node.end_byte].decode("utf-8", errors="replace")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_source(
    code: str,
    language: str | Lang = Lang.PYTHON,
) -> ParseResult:
    """
    Parse source code with tree-sitter.

    Args:
        code: Source code string.
        language: Language identifier (e.g. "python", "javascript").

    Returns:
        ParseResult with the tree-sitter tree and metadata.
    """
    if isinstance(language, str):
        language = Lang(language.lower())

    ts_lang = _get_language(language)
    parser = Parser(ts_lang)

    source_bytes = code.encode("utf-8")
    tree = parser.parse(source_bytes)

    has_errors = _tree_has_errors(tree.root_node)

    return ParseResult(
        tree=tree,
        source=source_bytes,
        language=language,
        has_errors=has_errors,
    )


def _tree_has_errors(node: Node) -> bool:
    """Walk tree looking for ERROR or MISSING nodes."""
    if node.type == "ERROR" or node.is_missing:
        return True
    for child in node.children:
        if _tree_has_errors(child):
            return True
    return False

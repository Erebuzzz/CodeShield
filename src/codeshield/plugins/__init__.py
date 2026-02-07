"""
CodeShield Plugin Architecture

Provides a registry-based plugin system supporting:
  - Language plugins   (parser + normalizer + taint defs)
  - Rule plugins       (custom verification rules)
  - Analysis plugins   (hooks into the verification pipeline)
  - Dashboard plugins  (custom UI panels — metadata only)
  - Policy plugins     (organizational enforcement policies)

Plugins are discovered via:
  1. Entry-points (``codeshield.plugins`` group)
  2. Explicit registration via ``register_plugin()``
  3. Directory scanning (``~/.codeshield/plugins/``)
"""

from __future__ import annotations

import importlib
import importlib.metadata
import json
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

from codeshield.trustgate.engine.rules import Rule, RuleSet, Severity
from codeshield.trustgate.engine.parser import Lang


# ===================================================================
# Plugin types
# ===================================================================

class PluginType(str, Enum):
    LANGUAGE = "language"
    RULE = "rule"
    ANALYSIS = "analysis"
    DASHBOARD = "dashboard"
    POLICY = "policy"


# ===================================================================
# Hook events for analysis plugins
# ===================================================================

class HookEvent(str, Enum):
    ON_PARSE = "on_parse"
    ON_NORMALIZE = "on_normalize"
    ON_GRAPH_BUILD = "on_graph_build"
    ON_RULE_EXECUTE = "on_rule_execute"
    ON_VIOLATION = "on_violation"


# ===================================================================
# Plugin descriptors
# ===================================================================

@dataclass
class PluginMeta:
    """Metadata every plugin must provide."""
    name: str
    version: str
    plugin_type: PluginType
    author: str = ""
    description: str = ""
    languages: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    signed: bool = False


@dataclass
class LanguagePlugin:
    """
    Adds a new language to the engine.

    Must provide:
      - ``lang_id``: unique language slug
      - ``extensions``: file extensions this language handles
      - ``get_tree_sitter_language``: callable returning a tree-sitter Language ptr
      - ``node_kind_map``: mapping of tree-sitter node types → NodeKind
      - ``taint_sources/sinks``: language-specific known-dangerous APIs
    """
    meta: PluginMeta
    lang_id: str
    extensions: list[str] = field(default_factory=list)
    get_tree_sitter_language: Optional[Callable] = None
    node_kind_map: dict[str, str] = field(default_factory=dict)
    taint_sources: set[str] = field(default_factory=set)
    taint_sinks: set[str] = field(default_factory=set)


@dataclass
class RulePlugin:
    """
    Provides one or more custom verification rules.
    """
    meta: PluginMeta
    rules: list[Rule] = field(default_factory=list)


@dataclass
class AnalysisPlugin:
    """
    Hooks into the verification pipeline at specific points.
    """
    meta: PluginMeta
    hooks: dict[HookEvent, Callable] = field(default_factory=dict)


@dataclass
class DashboardPlugin:
    """
    Registers a custom dashboard panel (metadata-only on backend).
    The frontend reads panel descriptors from the API.
    """
    meta: PluginMeta
    panel_id: str = ""
    panel_title: str = ""
    component_url: str = ""  # URL of the panel's JS bundle


@dataclass
class PolicyPlugin:
    """
    Organizational policy enforcement.

    Defines which rules are mandatory, minimum confidence thresholds,
    and blocked patterns for a team / project.
    """
    meta: PluginMeta
    required_rules: list[str] = field(default_factory=list)
    min_confidence: float = 0.0
    blocked_patterns: list[str] = field(default_factory=list)
    severity_overrides: dict[str, str] = field(default_factory=dict)


# ===================================================================
# Plugin Registry (singleton)
# ===================================================================

class PluginRegistry:
    """Central registry for all plugins."""

    _instance: Optional["PluginRegistry"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self.language_plugins: dict[str, LanguagePlugin] = {}
        self.rule_plugins: dict[str, RulePlugin] = {}
        self.analysis_plugins: dict[str, AnalysisPlugin] = {}
        self.dashboard_plugins: dict[str, DashboardPlugin] = {}
        self.policy_plugins: dict[str, PolicyPlugin] = {}
        self._hooks: dict[HookEvent, list[Callable]] = {e: [] for e in HookEvent}

    # ----- registration -----

    def register(self, plugin: Any) -> None:
        """Register a plugin by type."""
        if isinstance(plugin, LanguagePlugin):
            self.language_plugins[plugin.lang_id] = plugin
        elif isinstance(plugin, RulePlugin):
            self.rule_plugins[plugin.meta.name] = plugin
        elif isinstance(plugin, AnalysisPlugin):
            self.analysis_plugins[plugin.meta.name] = plugin
            for event, fn in plugin.hooks.items():
                self._hooks[event].append(fn)
        elif isinstance(plugin, DashboardPlugin):
            self.dashboard_plugins[plugin.panel_id] = plugin
        elif isinstance(plugin, PolicyPlugin):
            self.policy_plugins[plugin.meta.name] = plugin
        else:
            raise TypeError(f"Unknown plugin type: {type(plugin)}")

    def unregister(self, name: str) -> bool:
        """Remove a plugin by name from all registries."""
        for registry in (
            self.language_plugins,
            self.rule_plugins,
            self.analysis_plugins,
            self.dashboard_plugins,
            self.policy_plugins,
        ):
            if name in registry:
                del registry[name]
                return True
        return False

    # ----- queries -----

    def get_all_rules(self) -> RuleSet:
        """Merge built-in rules with all rule-plugin rules."""
        from codeshield.trustgate.engine.rules import load_builtin_rules
        rs = load_builtin_rules()
        for rp in self.rule_plugins.values():
            for rule in rp.rules:
                rs.add(rule)
        return rs

    def get_hooks(self, event: HookEvent) -> list[Callable]:
        return self._hooks.get(event, [])

    def fire_hook(self, event: HookEvent, **kwargs) -> None:
        for fn in self.get_hooks(event):
            try:
                fn(**kwargs)
            except Exception:
                pass

    def get_active_policy(self) -> Optional[PolicyPlugin]:
        """Return the first registered policy (team policy)."""
        if self.policy_plugins:
            return next(iter(self.policy_plugins.values()))
        return None

    def list_plugins(self) -> list[dict]:
        """Return metadata for all registered plugins."""
        out = []
        for registry in (
            self.language_plugins,
            self.rule_plugins,
            self.analysis_plugins,
            self.dashboard_plugins,
            self.policy_plugins,
        ):
            for name, p in registry.items():
                meta = p.meta
                out.append({
                    "name": meta.name,
                    "version": meta.version,
                    "type": meta.plugin_type.value,
                    "author": meta.author,
                    "description": meta.description,
                    "languages": meta.languages,
                    "tags": meta.tags,
                })
        return out

    # ----- discovery -----

    def discover_entrypoints(self) -> int:
        """Load plugins registered via ``codeshield.plugins`` entry-point group."""
        loaded = 0
        try:
            eps = importlib.metadata.entry_points()
            group = eps.get("codeshield.plugins", []) if isinstance(eps, dict) else [
                ep for ep in eps if ep.group == "codeshield.plugins"
            ]
            for ep in group:
                try:
                    plugin_factory = ep.load()
                    plugin = plugin_factory()
                    self.register(plugin)
                    loaded += 1
                except Exception:
                    pass
        except Exception:
            pass
        return loaded

    def discover_directory(self, path: str | Path | None = None) -> int:
        """Scan a directory for ``plugin.json`` descriptors."""
        if path is None:
            path = Path.home() / ".codeshield" / "plugins"
        path = Path(path)
        if not path.exists():
            return 0

        loaded = 0
        for manifest in path.rglob("plugin.json"):
            try:
                data = json.loads(manifest.read_text())
                entry = data.get("entry_module")
                if entry:
                    mod = importlib.import_module(entry)
                    plugin = mod.create_plugin()
                    self.register(plugin)
                    loaded += 1
            except Exception:
                pass
        return loaded


def get_registry() -> PluginRegistry:
    """Return the singleton registry."""
    return PluginRegistry()

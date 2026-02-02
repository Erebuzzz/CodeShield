"""
Token Efficiency Module - Optimize LLM token usage

Implements:
- Response caching (avoid duplicate API calls)
- Prompt compression (reduce input tokens)
- Smart truncation (limit context size)
- Token budgeting (track and limit usage)
- Semantic similarity caching (fuzzy matching)
- Model tiering (cheap models for simple tasks)
- Local-first processing (skip LLM when possible)
"""

import hashlib
import json
import re
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from threading import Lock
from difflib import SequenceMatcher


CACHE_DB_PATH = Path.home() / ".codeshield" / "token_cache.sqlite"
_cache_lock = Lock()


@dataclass
class CachedResponse:
    """A cached LLM response"""
    content: str
    provider: str
    model: str
    tokens_saved: int
    cached_at: str
    hits: int = 0


class TokenOptimizer:
    """
    Optimizes token usage through caching and compression.
    
    Features:
    - LRU cache for identical prompts
    - Prompt compression for common patterns
    - Smart context truncation
    - Token budget enforcement
    """
    
    _instance = None
    
    # Token budget settings
    DEFAULT_BUDGET = 100000  # 100K tokens per session
    
    # Cache settings
    CACHE_TTL_HOURS = 24
    MAX_CACHE_ENTRIES = 1000
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._session_tokens = 0
        self._token_budget = self.DEFAULT_BUDGET
        self._cache_hits = 0
        self._cache_misses = 0
        self._tokens_saved = 0
        self._ensure_db()
        self._initialized = True
    
    def _ensure_db(self):
        """Initialize cache database"""
        CACHE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(CACHE_DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS response_cache (
                prompt_hash TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                provider TEXT NOT NULL,
                model TEXT NOT NULL,
                tokens_used INTEGER NOT NULL,
                cached_at TEXT NOT NULL,
                hits INTEGER DEFAULT 0,
                last_hit TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _hash_prompt(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate cache key from prompt"""
        combined = f"{system_prompt or ''}||{prompt}"
        return hashlib.sha256(combined.encode()).hexdigest()[:32]
    
    def get_cached(self, prompt: str, system_prompt: Optional[str] = None) -> Optional[CachedResponse]:
        """Check cache for existing response"""
        prompt_hash = self._hash_prompt(prompt, system_prompt)
        
        with _cache_lock:
            conn = sqlite3.connect(str(CACHE_DB_PATH))
            cursor = conn.cursor()
            
            # Check for valid cache entry
            cursor.execute("""
                SELECT content, provider, model, tokens_used, cached_at, hits
                FROM response_cache 
                WHERE prompt_hash = ?
            """, (prompt_hash,))
            
            row = cursor.fetchone()
            
            if row:
                # Update hit count
                cursor.execute("""
                    UPDATE response_cache 
                    SET hits = hits + 1, last_hit = ?
                    WHERE prompt_hash = ?
                """, (datetime.now().isoformat(), prompt_hash))
                conn.commit()
                
                self._cache_hits += 1
                self._tokens_saved += row[3]  # tokens_used
                
                conn.close()
                return CachedResponse(
                    content=row[0],
                    provider=row[1],
                    model=row[2],
                    tokens_saved=row[3],
                    cached_at=row[4],
                    hits=row[5] + 1
                )
            
            conn.close()
            self._cache_misses += 1
            return None
    
    def cache_response(self, prompt: str, response: Any, 
                      system_prompt: Optional[str] = None):
        """Cache an LLM response"""
        prompt_hash = self._hash_prompt(prompt, system_prompt)
        
        with _cache_lock:
            conn = sqlite3.connect(str(CACHE_DB_PATH))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO response_cache 
                (prompt_hash, content, provider, model, tokens_used, cached_at, hits)
                VALUES (?, ?, ?, ?, ?, ?, 0)
            """, (
                prompt_hash,
                response.content,
                response.provider,
                response.model,
                response.tokens_used,
                datetime.now().isoformat()
            ))
            
            # Cleanup old entries if over limit
            cursor.execute("""
                DELETE FROM response_cache 
                WHERE prompt_hash NOT IN (
                    SELECT prompt_hash FROM response_cache 
                    ORDER BY last_hit DESC, cached_at DESC 
                    LIMIT ?
                )
            """, (self.MAX_CACHE_ENTRIES,))
            
            conn.commit()
            conn.close()
    
    def compress_prompt(self, prompt: str) -> str:
        """
        Compress prompt to reduce tokens.
        
        Techniques:
        - Remove excessive whitespace
        - Shorten common phrases
        - Remove redundant instructions
        """
        # Remove multiple spaces/newlines
        import re
        prompt = re.sub(r'\n{3,}', '\n\n', prompt)
        prompt = re.sub(r' {2,}', ' ', prompt)
        prompt = prompt.strip()
        
        # Common compression patterns
        compressions = [
            ("Please ", ""),
            ("Could you please ", ""),
            ("I would like you to ", ""),
            ("Make sure to ", ""),
            ("Be sure to ", ""),
            ("Don't forget to ", ""),
            ("Remember to ", ""),
            ("Note that ", ""),
            ("Please note that ", ""),
            ("It's important that ", ""),
            ("As a reminder, ", ""),
        ]
        
        for old, new in compressions:
            prompt = prompt.replace(old, new)
        
        return prompt
    
    def truncate_code(self, code: str, max_lines: int = 100) -> str:
        """
        Smart truncation of code to reduce tokens.
        
        Preserves:
        - Function signatures
        - Class definitions
        - Import statements
        - First/last lines of functions
        """
        lines = code.split('\n')
        
        if len(lines) <= max_lines:
            return code
        
        # Keep important lines
        important_patterns = [
            'import ', 'from ', 'class ', 'def ', 'async def ',
            'return ', 'raise ', '@', 'if __name__'
        ]
        
        result = []
        skipped = 0
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Always keep important lines
            is_important = any(stripped.startswith(p) for p in important_patterns)
            
            # Keep first and last 20 lines always
            is_boundary = i < 20 or i >= len(lines) - 20
            
            if is_important or is_boundary:
                if skipped > 0:
                    result.append(f"    # ... ({skipped} lines omitted)")
                    skipped = 0
                result.append(line)
            else:
                skipped += 1
        
        if skipped > 0:
            result.append(f"    # ... ({skipped} lines omitted)")
        
        return '\n'.join(result)
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count (rough approximation).
        
        Rule of thumb: ~4 chars per token for English
        Code tends to be ~3 chars per token due to symbols
        """
        # Rough estimate: 1 token ≈ 4 characters
        return len(text) // 4
    
    def check_budget(self, estimated_tokens: int) -> bool:
        """Check if request is within budget"""
        return (self._session_tokens + estimated_tokens) <= self._token_budget
    
    def record_usage(self, tokens: int):
        """Record token usage"""
        self._session_tokens += tokens
    
    def get_stats(self) -> dict:
        """Get optimization statistics"""
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "cache_hit_rate": round(hit_rate, 2),
            "tokens_saved_by_cache": self._tokens_saved,
            "tokens_saved_by_local": getattr(self, '_local_saves', 0),
            "tokens_saved_by_compression": getattr(self, '_compression_saves', 0),
            "session_tokens_used": self._session_tokens,
            "token_budget": self._token_budget,
            "budget_remaining": self._token_budget - self._session_tokens,
            "budget_used_percent": round(self._session_tokens / self._token_budget * 100, 2),
            "llm_calls_avoided": self._cache_hits + getattr(self, '_local_saves', 0),
        }
    
    def set_budget(self, tokens: int):
        """Set token budget for session"""
        self._token_budget = tokens
    
    def reset_session(self):
        """Reset session token counter"""
        self._session_tokens = 0
        self._cache_hits = 0
        self._cache_misses = 0
        self._tokens_saved = 0
        self._local_saves = 0
        self._compression_saves = 0


# Singleton accessor
def get_token_optimizer() -> TokenOptimizer:
    """Get the global token optimizer instance"""
    return TokenOptimizer()


# =============================================================================
# LOCAL-FIRST PROCESSING - Skip LLM entirely when possible
# =============================================================================

class LocalProcessor:
    """
    Handle simple tasks locally without LLM calls.
    
    HUGE token savings - 100% reduction for supported tasks.
    """
    
    # Common import fixes (no LLM needed)
    IMPORT_FIXES = {
        'json': 'import json',
        'os': 'import os',
        'sys': 'import sys',
        're': 'import re',
        'math': 'import math',
        'random': 'import random',
        'datetime': 'from datetime import datetime',
        'time': 'import time',
        'pathlib': 'from pathlib import Path',
        'typing': 'from typing import Optional, List, Dict, Any',
        'dataclasses': 'from dataclasses import dataclass',
        'collections': 'from collections import defaultdict, Counter',
        'itertools': 'import itertools',
        'functools': 'import functools',
        'requests': 'import requests',
        'httpx': 'import httpx',
        'asyncio': 'import asyncio',
        'logging': 'import logging',
        'subprocess': 'import subprocess',
        'tempfile': 'import tempfile',
        'shutil': 'import shutil',
        'glob': 'import glob',
        'csv': 'import csv',
        'sqlite3': 'import sqlite3',
        'hashlib': 'import hashlib',
        'base64': 'import base64',
        'copy': 'import copy',
        'io': 'import io',
        'threading': 'import threading',
        'uuid': 'import uuid',
        'enum': 'from enum import Enum',
        'abc': 'from abc import ABC, abstractmethod',
        'contextlib': 'from contextlib import contextmanager',
        'pydantic': 'from pydantic import BaseModel',
        'fastapi': 'from fastapi import FastAPI, HTTPException',
        'flask': 'from flask import Flask, request, jsonify',
        'numpy': 'import numpy as np',
        'pandas': 'import pandas as pd',
        'pytest': 'import pytest',
    }
    
    @classmethod
    def can_fix_locally(cls, code: str, issues: List[str]) -> bool:
        """Check if issues can be fixed without LLM"""
        for issue in issues:
            issue_lower = issue.lower()
            # Only handle simple missing imports locally
            if 'missing import' in issue_lower:
                module = cls._extract_module(issue)
                if module and module in cls.IMPORT_FIXES:
                    continue
                return False
            else:
                return False  # Other issues need LLM
        return len(issues) > 0
    
    @classmethod
    def fix_locally(cls, code: str, issues: List[str]) -> Optional[str]:
        """
        Fix code locally without LLM.
        
        Returns fixed code or None if can't fix locally.
        """
        if not cls.can_fix_locally(code, issues):
            return None
        
        imports_to_add = []
        for issue in issues:
            if 'missing import' in issue.lower():
                module = cls._extract_module(issue)
                if module and module in cls.IMPORT_FIXES:
                    imports_to_add.append(cls.IMPORT_FIXES[module])
        
        if not imports_to_add:
            return None
        
        # Add imports at the top
        lines = code.split('\n')
        insert_pos = 0
        
        # Skip docstrings and existing imports
        in_docstring = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('"""') or stripped.startswith("'''"):
                if in_docstring or stripped.count('"""') >= 2 or stripped.count("'''") >= 2:
                    in_docstring = not in_docstring if stripped.count('"""') == 1 or stripped.count("'''") == 1 else in_docstring
                else:
                    in_docstring = not in_docstring
                insert_pos = i + 1
            elif not in_docstring and (stripped.startswith('import ') or stripped.startswith('from ')):
                insert_pos = i + 1
            elif not in_docstring and stripped and not stripped.startswith('#'):
                break
        
        # Deduplicate imports
        existing_imports = set()
        for line in lines:
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                existing_imports.add(line.strip())
        
        new_imports = [imp for imp in imports_to_add if imp not in existing_imports]
        
        if not new_imports:
            return code  # Nothing to add
        
        for imp in reversed(new_imports):
            lines.insert(insert_pos, imp)
        
        return '\n'.join(lines)
    
    @classmethod
    def _extract_module(cls, issue: str) -> Optional[str]:
        """Extract module name from issue message"""
        # "Missing import: json" -> "json"
        # "Missing import: json (pip install json)" -> "json"
        match = re.search(r'missing import[:\s]+(\w+)', issue.lower())
        if match:
            return match.group(1)
        return None


# =============================================================================
# SEMANTIC CACHING - Match similar prompts
# =============================================================================

def normalize_code(code: str) -> str:
    """Normalize code for semantic comparison"""
    # Remove comments
    code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
    # Normalize whitespace
    code = re.sub(r'\s+', ' ', code)
    # Remove string contents (keep structure)
    code = re.sub(r'"[^"]*"', '""', code)
    code = re.sub(r"'[^']*'", "''", code)
    return code.strip().lower()


def code_similarity(code1: str, code2: str) -> float:
    """Calculate similarity between two code snippets"""
    norm1 = normalize_code(code1)
    norm2 = normalize_code(code2)
    return SequenceMatcher(None, norm1, norm2).ratio()


# =============================================================================
# MODEL TIERING - Use cheaper models for simple tasks
# =============================================================================

class ModelTier:
    """Select optimal model based on task complexity"""
    
    # Task complexity thresholds
    SIMPLE_MAX_LINES = 20
    SIMPLE_MAX_ISSUES = 3
    
    # Model recommendations per provider
    MODELS = {
        "cometapi": {
            "simple": "deepseek-chat",      # Free, fast
            "complex": "gpt-4o-mini",       # Smarter but costs more
        },
        "novita": {
            "simple": "meta-llama/llama-3-8b-instruct",  # Fast, cheap
            "complex": "deepseek/deepseek-r1",           # Better reasoning
        },
        "aiml": {
            "simple": "gpt-4o-mini",
            "complex": "gpt-4o",
        }
    }
    
    @classmethod
    def select_model(cls, code: str, issues: List[str], provider: str) -> str:
        """Select optimal model based on task complexity"""
        complexity = cls._assess_complexity(code, issues)
        
        default_model = "deepseek-chat"
        models = cls.MODELS.get(provider, {"simple": default_model, "complex": default_model})
        
        if complexity == "simple":
            return models.get("simple", default_model)
        return models.get("complex", default_model)
    
    @classmethod
    def _assess_complexity(cls, code: str, issues: List[str]) -> str:
        """Assess task complexity"""
        lines = code.count('\n') + 1
        
        # Simple: short code, few issues, only import/syntax issues
        if lines <= cls.SIMPLE_MAX_LINES and len(issues) <= cls.SIMPLE_MAX_ISSUES:
            simple_issues = all(
                'import' in i.lower() or 'syntax' in i.lower() or 'indent' in i.lower()
                for i in issues
            )
            if simple_issues:
                return "simple"
        
        return "complex"


# =============================================================================
# OPTIMIZED PROMPTS - Maximum compression
# =============================================================================

OPTIMIZED_PROMPTS = {
    # Ultra-short fix prompt (~60% smaller than verbose)
    "fix_code": "Fix:\n{issues}\n\nCode:\n```\n{code}\n```\nReturn fixed code only.",
    
    # Minimal context briefing
    "context_briefing": "Summarize work state (2 sentences):\nFiles: {files}\nLast: {last_edited}\nTime: {time_ago}",
    
    # Style suggestion
    "style_suggest": "Suggest {convention} names for:\n{names}",
    
    # Ultra minimal for simple fixes (when we must use LLM)
    "simple_fix": "Add imports and fix:\n```\n{code}\n```",
}


def optimize_fix_prompt(code: str, issues: List[str]) -> str:
    """Optimized prompt for code fixing - uses ~60% fewer tokens"""
    optimizer = get_token_optimizer()
    
    # Try local fix first (0 tokens!)
    local_fix = LocalProcessor.fix_locally(code, issues)
    if local_fix is not None:
        if not hasattr(optimizer, '_local_saves'):
            optimizer._local_saves = 0
        optimizer._local_saves += 1
        return "__LOCAL_FIX__"  # Signal to skip LLM
    
    # Use ultra-minimal prompt for simple issues
    if all('import' in i.lower() for i in issues) and code.count('\n') < 30:
        code = optimizer.truncate_code(code, max_lines=30)
        return OPTIMIZED_PROMPTS["simple_fix"].format(code=code)
    
    # Standard optimized prompt
    issues_text = "; ".join(issues)  # Semicolons instead of bullets
    code = optimizer.truncate_code(code, max_lines=50)  # Reduced from 80
    
    return OPTIMIZED_PROMPTS["fix_code"].format(
        issues=issues_text,
        code=code
    )


def optimize_context_prompt(context: dict) -> str:
    """Optimized prompt for context briefing"""
    return OPTIMIZED_PROMPTS["context_briefing"].format(
        files=", ".join(context.get("files", [])[:3]),  # Limit to 3 files (was 5)
        last_edited=context.get("last_edited", "?"),
        time_ago=context.get("time_ago", "?")
    )


# =============================================================================
# RESPONSE OPTIMIZATION
# =============================================================================

def get_optimal_max_tokens(task: str, code_length: int) -> int:
    """Calculate minimum max_tokens needed for task"""
    if task == "fix":
        # Output is usually similar size to input
        return min(500, max(100, code_length // 3))
    elif task == "briefing":
        return 50  # Just 2 sentences
    elif task == "style":
        return 100  # Short suggestions
    return 500  # Default

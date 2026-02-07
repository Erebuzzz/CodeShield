"""
ContextVault Auto-Save — Failsafe for force-close / crash

Registers atexit hooks and signal handlers to automatically
persist the current coding context before the process exits.
Also provides a periodic auto-save daemon thread.
"""

from __future__ import annotations

import atexit
import os
import signal
import sys
import threading
import time
from datetime import datetime
from typing import Optional

from codeshield.contextvault.capture import save_context, list_contexts, get_context


# ===================================================================
# Configuration
# ===================================================================

_AUTOSAVE_INTERVAL_SEC = int(os.getenv("CODESHIELD_AUTOSAVE_INTERVAL", "300"))  # 5 min
_AUTOSAVE_NAME_PREFIX = "__autosave__"
_MAX_AUTOSAVES = int(os.getenv("CODESHIELD_MAX_AUTOSAVES", "5"))

_autosave_thread: Optional[threading.Thread] = None
_autosave_stop = threading.Event()
_last_context: dict = {}


# ===================================================================
# Context state tracking
# ===================================================================

def update_tracked_state(
    files: list[str] | None = None,
    cursor: dict | None = None,
    notes: str | None = None,
    last_edited_file: str | None = None,
) -> None:
    """
    Update the in-memory tracked state.

    Call this whenever the user opens/closes files, moves cursor,
    or edits a file, so the auto-save captures the latest state.
    """
    if files is not None:
        _last_context["files"] = files
    if cursor is not None:
        _last_context["cursor"] = cursor
    if notes is not None:
        _last_context["notes"] = notes
    if last_edited_file is not None:
        _last_context["last_edited_file"] = last_edited_file


# ===================================================================
# Auto-save logic
# ===================================================================

def _autosave_name() -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{_AUTOSAVE_NAME_PREFIX}{ts}"


def perform_autosave(reason: str = "periodic") -> dict | None:
    """
    Persist the current tracked context.

    Returns the save result dict, or None if nothing to save.
    """
    if not _last_context.get("files") and not _last_context.get("notes"):
        return None

    try:
        name = _autosave_name()
        result = save_context(
            name=name,
            files=_last_context.get("files", []),
            cursor=_last_context.get("cursor", {}),
            notes=f"[auto-save: {reason}] {_last_context.get('notes', '')}".strip(),
            last_edited_file=_last_context.get("last_edited_file", ""),
        )
        _prune_old_autosaves()
        return result
    except Exception:
        # Auto-save must never crash the host process
        return None


def _prune_old_autosaves() -> None:
    """Keep only the N most recent auto-saves."""
    try:
        all_ctxs = list_contexts()
        autosaves = [c for c in all_ctxs if c["name"].startswith(_AUTOSAVE_NAME_PREFIX)]
        # Already sorted desc by created_at from list_contexts
        if len(autosaves) > _MAX_AUTOSAVES:
            from codeshield.contextvault.capture import delete_context
            for old in autosaves[_MAX_AUTOSAVES:]:
                delete_context(old["name"])
    except Exception:
        pass


def get_latest_autosave() -> dict | None:
    """Return the most recent auto-saved context, if any."""
    try:
        all_ctxs = list_contexts()
        for ctx in all_ctxs:
            if ctx["name"].startswith(_AUTOSAVE_NAME_PREFIX):
                full = get_context(ctx["name"])
                return full.to_dict() if full else None
    except Exception:
        pass
    return None


# ===================================================================
# Periodic auto-save daemon
# ===================================================================

def _autosave_loop() -> None:
    """Background thread: saves context every N seconds."""
    while not _autosave_stop.wait(timeout=_AUTOSAVE_INTERVAL_SEC):
        perform_autosave(reason="periodic")


def start_autosave_daemon() -> None:
    """Start the periodic auto-save background thread."""
    global _autosave_thread
    if _autosave_thread is not None and _autosave_thread.is_alive():
        return
    _autosave_stop.clear()
    _autosave_thread = threading.Thread(
        target=_autosave_loop, daemon=True, name="codeshield-autosave"
    )
    _autosave_thread.start()


def stop_autosave_daemon() -> None:
    """Stop the background auto-save thread."""
    _autosave_stop.set()
    if _autosave_thread is not None:
        _autosave_thread.join(timeout=2)


# ===================================================================
# atexit + signal handlers (failsafe)
# ===================================================================

def _on_exit() -> None:
    """atexit callback — save before interpreter shuts down."""
    perform_autosave(reason="exit")
    stop_autosave_daemon()


def _on_signal(signum: int, frame) -> None:
    """Signal handler — save before forced termination."""
    perform_autosave(reason=f"signal_{signum}")
    stop_autosave_daemon()
    sys.exit(128 + signum)


def install_failsafe_hooks() -> None:
    """
    Register atexit and signal hooks so context is saved on:
      - Normal exit
      - Ctrl+C (SIGINT)
      - SIGTERM (container stop, kill -15)
    """
    atexit.register(_on_exit)

    # SIGINT — Ctrl+C
    try:
        signal.signal(signal.SIGINT, _on_signal)
    except (OSError, ValueError):
        pass  # can fail if not main thread

    # SIGTERM — graceful kill
    try:
        signal.signal(signal.SIGTERM, _on_signal)
    except (OSError, ValueError, AttributeError):
        pass  # SIGTERM may not exist on Windows


# ===================================================================
# Convenience: one-call bootstrap
# ===================================================================

def enable_autosave(
    interval_sec: int | None = None,
    max_saves: int | None = None,
) -> None:
    """
    Enable auto-save with failsafe hooks.

    Call once at app startup (api_server, mcp server, or CLI).
    """
    global _AUTOSAVE_INTERVAL_SEC, _MAX_AUTOSAVES

    if interval_sec is not None:
        _AUTOSAVE_INTERVAL_SEC = interval_sec
    if max_saves is not None:
        _MAX_AUTOSAVES = max_saves

    install_failsafe_hooks()
    start_autosave_daemon()

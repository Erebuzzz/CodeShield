"""
ContextVault Capture - Save coding context

Saves your mental state like a game save file:
- Open files
- Cursor position
- Recent changes
- Timestamps
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional


DB_PATH = Path.home() / ".codeshield" / "context_vault.sqlite"


@dataclass
class CodingContext:
    """A saved coding context"""
    name: str
    created_at: str
    files: list[str]
    cursor: Optional[dict] = None
    notes: Optional[str] = None
    last_edited_file: Optional[str] = None
    
    def to_dict(self) -> dict:
        return asdict(self)


def _ensure_db():
    """Ensure database exists and has schema"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contexts (
            name TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            files TEXT NOT NULL,
            cursor TEXT,
            notes TEXT,
            last_edited_file TEXT
        )
    """)
    
    conn.commit()
    conn.close()


def save_context(
    name: str,
    files: list[str] = None,
    cursor: dict = None,
    notes: str = None,
    last_edited_file: str = None,
) -> dict:
    """
    Save coding context.
    
    Args:
        name: Unique name for this context
        files: List of open file paths
        cursor: Cursor position {file, line, column}
        notes: Optional notes about current work
        last_edited_file: Last file that was edited
    
    Returns:
        Dict with save confirmation
    """
    _ensure_db()
    
    context = CodingContext(
        name=name,
        created_at=datetime.now().isoformat(),
        files=files or [],
        cursor=cursor,
        notes=notes,
        last_edited_file=last_edited_file,
    )
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor_db = conn.cursor()
    
    cursor_db.execute("""
        INSERT OR REPLACE INTO contexts 
        (name, created_at, files, cursor, notes, last_edited_file)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        context.name,
        context.created_at,
        json.dumps(context.files),
        json.dumps(context.cursor) if context.cursor else None,
        context.notes,
        context.last_edited_file,
    ))
    
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "message": f"Context '{name}' saved at {context.created_at}",
        "context": context.to_dict(),
    }


def list_contexts() -> list[dict]:
    """List all saved contexts"""
    _ensure_db()
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    cursor.execute("SELECT name, created_at, notes FROM contexts ORDER BY created_at DESC")
    rows = cursor.fetchall()
    
    conn.close()
    
    return [
        {"name": row[0], "created_at": row[1], "notes": row[2]}
        for row in rows
    ]


def get_context(name: str) -> Optional[CodingContext]:
    """Get a specific context by name"""
    _ensure_db()
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT name, created_at, files, cursor, notes, last_edited_file
        FROM contexts WHERE name = ?
    """, (name,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return CodingContext(
        name=row[0],
        created_at=row[1],
        files=json.loads(row[2]),
        cursor=json.loads(row[3]) if row[3] else None,
        notes=row[4],
        last_edited_file=row[5],
    )


def delete_context(name: str) -> bool:
    """Delete a context by name"""
    _ensure_db()
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM contexts WHERE name = ?", (name,))
    deleted = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    
    return deleted

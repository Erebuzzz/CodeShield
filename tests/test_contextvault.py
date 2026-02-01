"""Tests for ContextVault context management"""

import pytest
import tempfile
import sqlite3
from pathlib import Path
from unittest.mock import patch

from codeshield.contextvault.capture import (
    save_context,
    list_contexts,
    get_context,
    delete_context,
    CodingContext,
)
from codeshield.contextvault.restore import (
    restore_context,
    generate_briefing,
    quick_restore,
)


@pytest.fixture
def temp_db(monkeypatch):
    """Use temporary database for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_vault.sqlite"
        monkeypatch.setattr("codeshield.contextvault.capture.DB_PATH", db_path)
        monkeypatch.setattr("codeshield.contextvault.restore.get_context", 
                          lambda name: get_context(name))
        yield db_path


class TestSaveContext:
    """Test context saving functionality"""
    
    def test_save_basic_context(self, temp_db):
        """Test saving a basic context"""
        result = save_context(
            name="test-context",
            files=["src/main.py", "tests/test_main.py"],
            notes="Working on feature X"
        )
        
        assert result["success"] is True
        assert "test-context" in result["message"]
        assert result["context"]["name"] == "test-context"
        assert len(result["context"]["files"]) == 2
    
    def test_save_context_with_cursor(self, temp_db):
        """Test saving context with cursor position"""
        result = save_context(
            name="cursor-test",
            files=["src/app.py"],
            cursor={"file": "src/app.py", "line": 42, "column": 10}
        )
        
        assert result["success"] is True
        assert result["context"]["cursor"]["line"] == 42
        assert result["context"]["cursor"]["column"] == 10
    
    def test_save_context_overwrites_existing(self, temp_db):
        """Test that saving with same name overwrites"""
        save_context(name="duplicate", files=["file1.py"])
        result = save_context(name="duplicate", files=["file2.py"])
        
        assert result["success"] is True
        assert result["context"]["files"] == ["file2.py"]
    
    def test_save_minimal_context(self, temp_db):
        """Test saving with minimal information"""
        result = save_context(name="minimal")
        
        assert result["success"] is True
        assert result["context"]["files"] == []
        assert result["context"]["cursor"] is None


class TestListContexts:
    """Test listing saved contexts"""
    
    def test_list_empty(self, temp_db):
        """Test listing when no contexts saved"""
        contexts = list_contexts()
        assert contexts == []
    
    def test_list_multiple_contexts(self, temp_db):
        """Test listing multiple saved contexts"""
        save_context(name="context1", notes="First")
        save_context(name="context2", notes="Second")
        save_context(name="context3", notes="Third")
        
        contexts = list_contexts()
        
        assert len(contexts) == 3
        assert all("name" in ctx for ctx in contexts)
        assert all("created_at" in ctx for ctx in contexts)
    
    def test_list_ordered_by_date(self, temp_db):
        """Test that contexts are ordered by creation date (newest first)"""
        save_context(name="old", notes="Old context")
        save_context(name="new", notes="New context")
        
        contexts = list_contexts()
        
        # Most recent should be first
        assert contexts[0]["name"] == "new"
        assert contexts[1]["name"] == "old"


class TestGetContext:
    """Test retrieving specific context"""
    
    def test_get_existing_context(self, temp_db):
        """Test getting an existing context"""
        save_context(
            name="test-get",
            files=["main.py"],
            cursor={"line": 10},
            notes="Test notes"
        )
        
        context = get_context("test-get")
        
        assert context is not None
        assert context.name == "test-get"
        assert context.files == ["main.py"]
        assert context.cursor == {"line": 10}
        assert context.notes == "Test notes"
    
    def test_get_nonexistent_context(self, temp_db):
        """Test getting a context that doesn't exist"""
        context = get_context("nonexistent")
        assert context is None
    
    def test_get_context_with_full_data(self, temp_db):
        """Test getting context with all fields populated"""
        save_context(
            name="full-context",
            files=["a.py", "b.py", "c.py"],
            cursor={"file": "a.py", "line": 100, "column": 5},
            notes="Complex feature implementation",
            last_edited_file="a.py"
        )
        
        context = get_context("full-context")
        
        assert len(context.files) == 3
        assert context.cursor["line"] == 100
        assert context.last_edited_file == "a.py"


class TestDeleteContext:
    """Test deleting contexts"""
    
    def test_delete_existing_context(self, temp_db):
        """Test deleting an existing context"""
        save_context(name="to-delete", files=["file.py"])
        
        deleted = delete_context("to-delete")
        
        assert deleted is True
        assert get_context("to-delete") is None
    
    def test_delete_nonexistent_context(self, temp_db):
        """Test deleting a context that doesn't exist"""
        deleted = delete_context("nonexistent")
        assert deleted is False
    
    def test_delete_doesnt_affect_others(self, temp_db):
        """Test that deleting one context doesn't affect others"""
        save_context(name="keep1", files=["a.py"])
        save_context(name="delete", files=["b.py"])
        save_context(name="keep2", files=["c.py"])
        
        delete_context("delete")
        
        assert get_context("keep1") is not None
        assert get_context("keep2") is not None
        assert get_context("delete") is None


class TestRestoreContext:
    """Test context restoration"""
    
    def test_restore_existing_context(self, temp_db):
        """Test restoring an existing context"""
        save_context(
            name="restore-test",
            files=["main.py", "utils.py"],
            cursor={"line": 42},
            notes="Working on authentication"
        )
        
        result = restore_context("restore-test")
        
        assert result["success"] is True
        assert result["context"]["name"] == "restore-test"
        assert len(result["files_to_open"]) == 2
        assert result["cursor_position"]["line"] == 42
        assert "briefing" in result
    
    def test_restore_nonexistent_context(self, temp_db):
        """Test restoring a context that doesn't exist"""
        result = restore_context("nonexistent")
        
        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"]
    
    def test_restore_provides_briefing(self, temp_db):
        """Test that restore includes a briefing"""
        save_context(
            name="brief-test",
            files=["app.py"],
            notes="Bug fix in progress"
        )
        
        result = restore_context("brief-test")
        
        assert result["briefing"] != ""
        assert isinstance(result["briefing"], str)


class TestGenerateBriefing:
    """Test briefing generation"""
    
    def test_briefing_includes_file_count(self, temp_db):
        """Test that briefing mentions file count"""
        context = CodingContext(
            name="test",
            created_at="2024-01-01T10:00:00",
            files=["a.py", "b.py", "c.py"],
            notes="Test"
        )
        
        briefing = generate_briefing(context)
        
        assert "3 files" in briefing or "3" in briefing
    
    def test_briefing_includes_notes(self, temp_db):
        """Test that briefing includes user notes"""
        context = CodingContext(
            name="test",
            created_at="2024-01-01T10:00:00",
            files=["main.py"],
            notes="Implementing login feature"
        )
        
        briefing = generate_briefing(context)
        
        assert "Implementing login feature" in briefing
    
    def test_briefing_handles_cursor_info(self, temp_db):
        """Test that briefing mentions cursor position"""
        context = CodingContext(
            name="test",
            created_at="2024-01-01T10:00:00",
            files=["code.py"],
            cursor={"line": 150}
        )
        
        briefing = generate_briefing(context)
        
        assert "150" in briefing or "line" in briefing.lower()


class TestQuickRestore:
    """Test quick restore functionality"""
    
    def test_quick_restore_gets_most_recent(self, temp_db):
        """Test that quick restore gets the most recent context"""
        save_context(name="old", files=["old.py"])
        save_context(name="recent", files=["recent.py"])
        
        result = quick_restore()
        
        assert result is not None
        assert result["success"] is True
        assert result["context"]["name"] == "recent"
    
    def test_quick_restore_with_no_contexts(self, temp_db):
        """Test quick restore when no contexts exist"""
        result = quick_restore()
        assert result is None


class TestCodingContext:
    """Test CodingContext dataclass"""
    
    def test_context_to_dict(self):
        """Test converting context to dictionary"""
        context = CodingContext(
            name="test",
            created_at="2024-01-01T10:00:00",
            files=["a.py", "b.py"],
            cursor={"line": 10},
            notes="Test notes"
        )
        
        context_dict = context.to_dict()
        
        assert context_dict["name"] == "test"
        assert len(context_dict["files"]) == 2
        assert context_dict["cursor"]["line"] == 10
        assert context_dict["notes"] == "Test notes"


# Run with: pytest tests/test_contextvault.py -v

"""
ContextVault Restore - Restore coding context

Restores your mental state with AI briefing:
- Reopens files
- Returns AI summary of where you left off
"""

from typing import Optional
from datetime import datetime

from codeshield.contextvault.capture import get_context, CodingContext


def restore_context(name: str) -> dict:
    """
    Restore a previously saved coding context.
    
    Args:
        name: Name of context to restore
    
    Returns:
        Dict with context info and AI briefing
    """
    context = get_context(name)
    
    if not context:
        return {
            "success": False,
            "error": f"Context '{name}' not found",
            "available_contexts": [],  # Could list available ones
        }
    
    # Generate AI briefing
    briefing = generate_briefing(context)
    
    return {
        "success": True,
        "context": context.to_dict(),
        "briefing": briefing,
        "files_to_open": context.files,
        "cursor_position": context.cursor,
    }


def generate_briefing(context: CodingContext) -> str:
    """
    Generate a natural language briefing about the context.
    
    Uses LLM if available, otherwise generates basic briefing.
    """
    # Calculate time since context was saved
    try:
        saved_time = datetime.fromisoformat(context.created_at)
        time_diff = datetime.now() - saved_time
        
        if time_diff.days > 0:
            time_str = f"{time_diff.days} days ago"
        elif time_diff.seconds > 3600:
            hours = time_diff.seconds // 3600
            time_str = f"{hours} hours ago"
        else:
            minutes = time_diff.seconds // 60
            time_str = f"{minutes} minutes ago"
    except:
        time_str = "unknown time ago"
    
    # Try to use LLM for briefing
    try:
        from codeshield.utils.llm import get_llm_client
        
        client = get_llm_client()
        llm_briefing = client.generate_context_briefing({
            "files": context.files,
            "last_edited": context.last_edited_file,
            "cursor": context.cursor,
            "notes": context.notes,
            "time_ago": time_str,
        })
        
        if llm_briefing:
            return llm_briefing
    except:
        pass
    
    # Fallback to basic briefing
    briefing_parts = []
    
    if context.files:
        file_count = len(context.files)
        last_file = context.files[-1].split('/')[-1].split('\\')[-1] if context.files else "unknown"
        briefing_parts.append(f"You had {file_count} files open. Last working on '{last_file}'.")
    
    if context.cursor:
        line = context.cursor.get('line', '?')
        briefing_parts.append(f"Cursor was at line {line}.")
    
    if context.notes:
        briefing_parts.append(f"Your notes: {context.notes}")
    
    briefing_parts.append(f"This was saved {time_str}.")
    
    return " ".join(briefing_parts)


def quick_restore() -> Optional[dict]:
    """Quick restore the most recent context"""
    from codeshield.contextvault.capture import list_contexts
    
    contexts = list_contexts()
    if not contexts:
        return None
    
    most_recent = contexts[0]["name"]
    return restore_context(most_recent)

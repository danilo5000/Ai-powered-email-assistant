from typing import Dict, Any, List
from collections import deque

class MemoryStore:
    """
    Lightweight in-memory storage for inbox and drafts.
    Uses deque with a max length to avoid unbounded growth.
    """

    def __init__(self, max_items: int = 200):
        self.inbox = deque(maxlen=max_items)
        self.drafts = deque(maxlen=max_items)

    def add_inbox(self, item: Dict[str, Any]) -> None:
        """Add an email item to the inbox cache."""
        self.inbox.appendleft(item)

    def list_inbox(self) -> List[Dict[str, Any]]:
        """Return all cached inbox items as a list."""
        return list(self.inbox)

    def add_draft(self, item: Dict[str, Any]) -> None:
        """Add a draft email to the drafts cache."""
        self.drafts.appendleft(item)

    def list_drafts(self) -> List[Dict[str, Any]]:
        """Return all cached drafts as a list."""
        return list(self.drafts)

# Global store instance
store = MemoryStore()

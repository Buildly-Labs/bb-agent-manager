"""
Abstract memory service interface.

The default implementation is MarkdownMemory (file-based, Git-tracked).
Future implementations could wrap Mem0, Graphiti, or a vector store —
plug them in by replacing MarkdownMemory without touching MCP tool code.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class MemoryService(ABC):
    """Base interface for the Buildly memory system."""

    # ------------------------------------------------------------------ #
    # Read
    # ------------------------------------------------------------------ #

    @abstractmethod
    def read_file(self, relative_path: str) -> str:
        """Read a memory file and return its text content, or '' if missing."""

    @abstractmethod
    def get_project_summary(self) -> dict[str, Any]:
        """Return a structured summary of the current project."""

    @abstractmethod
    def search(self, query: str, scope: str = "current") -> list[dict[str, Any]]:
        """
        Full-text search across memory files.

        Args:
            query: Search term.
            scope: 'current' (this project only) or 'org' (~/.buildly/memory/).

        Returns:
            List of matches with 'file', 'snippet', and 'score' keys.
        """

    @abstractmethod
    def get_recent_work(self, limit: int = 10) -> list[dict[str, Any]]:
        """Return the most recent session notes, newest first."""

    # ------------------------------------------------------------------ #
    # Write
    # ------------------------------------------------------------------ #

    @abstractmethod
    def write_session_note(self, title: str, content: str) -> str:
        """Persist a session note. Returns the file path written."""

    @abstractmethod
    def capture_decision(
        self,
        title: str,
        decision: str,
        rationale: str,
        alternatives: str = "",
    ) -> str:
        """Record an architectural decision. Returns the file path written."""

    @abstractmethod
    def capture_pattern(
        self,
        name: str,
        description: str,
        usage_example: str = "",
    ) -> str:
        """Append a reusable pattern to conventions.md. Returns the file path."""

    @abstractmethod
    def update_current_focus(self, content: str) -> str:
        """Overwrite current_focus.md. Returns the file path."""

    # ------------------------------------------------------------------ #
    # Index
    # ------------------------------------------------------------------ #

    @abstractmethod
    def rebuild_index(self) -> dict[str, Any]:
        """Scan all memory files and regenerate the index. Returns a summary."""

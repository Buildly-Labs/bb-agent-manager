"""
Markdown-based memory implementation.

Reads and writes structured Markdown files in buildly_memory/.
Everything is human-readable and Git-tracked. No external services required.

File layout:
    buildly_memory/
        project_overview.md
        architecture.md
        environments.md
        conventions.md
        current_focus.md
        project_links.md
        release_notes.md
        decisions/       ← one file per architectural decision
        features/        ← one file per feature/epic
        issues/          ← one file per tracked issue
        sessions/        ← one file per work session
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any

from bb_agent_manager.memory.memory_service import MemoryService

# Cross-project (org-level) memory lives here
_ORG_MEMORY_ROOT = Path.home() / ".buildly" / "memory"


class MarkdownMemory(MemoryService):
    """Default memory backend — plain Markdown files on disk."""

    def __init__(self, memory_path: str) -> None:
        self.root = Path(memory_path)
        self._ensure_structure()

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    def _ensure_structure(self) -> None:
        """Create missing directories and stub files."""
        for sub in ("decisions", "features", "issues", "sessions"):
            (self.root / sub).mkdir(parents=True, exist_ok=True)

        stubs: dict[str, str] = {
            "project_overview.md": _STUB_OVERVIEW,
            "architecture.md": _STUB_ARCH,
            "environments.md": _STUB_ENVS,
            "conventions.md": _STUB_CONVENTIONS,
            "current_focus.md": _STUB_FOCUS,
            "project_links.md": _STUB_PROJECT_LINKS,
            "release_notes.md": _STUB_RELEASE_NOTES,
        }
        for filename, stub in stubs.items():
            path = self.root / filename
            if not path.exists():
                path.write_text(stub, encoding="utf-8")

    def _path(self, relative: str) -> Path:
        return self.root / relative

    # ------------------------------------------------------------------ #
    # Read
    # ------------------------------------------------------------------ #

    def read_file(self, relative_path: str) -> str:
        p = self._path(relative_path)
        if p.exists():
            return p.read_text(encoding="utf-8")
        return ""

    def get_project_summary(self) -> dict[str, Any]:
        overview = self.read_file("project_overview.md")
        focus = self.read_file("current_focus.md")
        arch = self.read_file("architecture.md")
        return {
            "overview": overview[:3000],
            "current_focus": focus[:2000],
            "architecture": arch[:2000],
        }

    def search(self, query: str, scope: str = "current") -> list[dict[str, Any]]:
        root = self.root if scope == "current" else _ORG_MEMORY_ROOT
        if not root.exists():
            return []

        results: list[dict[str, Any]] = []
        q_lower = query.lower()

        for md_file in root.rglob("*.md"):
            try:
                text = md_file.read_text(encoding="utf-8")
            except OSError:
                continue

            lines = text.splitlines()
            for i, line in enumerate(lines):
                if q_lower in line.lower():
                    snippet_lines = lines[max(0, i - 1) : i + 3]
                    results.append({
                        "file": str(md_file.relative_to(root)),
                        "line": i + 1,
                        "snippet": "\n".join(snippet_lines),
                    })
                    break  # one hit per file is enough for now

        return results[:20]  # cap results

    def get_recent_work(self, limit: int = 10) -> list[dict[str, Any]]:
        sessions_dir = self.root / "sessions"
        files = sorted(sessions_dir.glob("*.md"), reverse=True)[:limit]
        results = []
        for f in files:
            text = f.read_text(encoding="utf-8")
            results.append({
                "file": f.name,
                "preview": text[:500],
            })
        return results

    # ------------------------------------------------------------------ #
    # Write
    # ------------------------------------------------------------------ #

    def write_session_note(self, title: str, content: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = re.sub(r"[^a-z0-9]+", "_", title.lower())[:40]
        filename = f"{timestamp}_{slug}.md"
        path = self.root / "sessions" / filename
        path.write_text(
            f"# {title}\n\n_Session: {datetime.now().strftime('%Y-%m-%d %H:%M')}_\n\n{content}",
            encoding="utf-8",
        )
        return str(path)

    def capture_decision(
        self,
        title: str,
        decision: str,
        rationale: str,
        alternatives: str = "",
    ) -> str:
        timestamp = datetime.now().strftime("%Y%m%d")
        slug = re.sub(r"[^a-z0-9]+", "_", title.lower())[:40]
        filename = f"{timestamp}_{slug}.md"
        path = self.root / "decisions" / filename
        content = f"""# Decision: {title}

_Date: {datetime.now().strftime('%Y-%m-%d')}_

## Decision

{decision}

## Rationale

{rationale}
"""
        if alternatives:
            content += f"\n## Alternatives Considered\n\n{alternatives}\n"
        path.write_text(content, encoding="utf-8")
        return str(path)

    def capture_pattern(self, name: str, description: str, usage_example: str = "") -> str:
        path = self.root / "conventions.md"
        entry = f"\n\n## Pattern: {name}\n\n{description}\n"
        if usage_example:
            entry += f"\n**Example:**\n\n```\n{usage_example}\n```\n"
        with path.open("a", encoding="utf-8") as f:
            f.write(entry)
        return str(path)

    def update_current_focus(self, content: str) -> str:
        path = self.root / "current_focus.md"
        path.write_text(content, encoding="utf-8")
        return str(path)

    # ------------------------------------------------------------------ #
    # Index
    # ------------------------------------------------------------------ #

    def rebuild_index(self) -> dict[str, Any]:
        index: dict[str, list[str]] = {}
        for sub in ("decisions", "features", "issues", "sessions"):
            index[sub] = sorted(p.name for p in (self.root / sub).glob("*.md"))

        root_files = sorted(p.name for p in self.root.glob("*.md"))

        index_content = "# Buildly Memory Index\n\n"
        index_content += f"_Rebuilt: {datetime.now().strftime('%Y-%m-%d %H:%M')}_\n\n"
        index_content += "## Root files\n\n"
        for f in root_files:
            index_content += f"- {f}\n"
        for sub, files in index.items():
            index_content += f"\n## {sub}/\n\n"
            for f in files:
                index_content += f"- {f}\n"

        index_path = self.root / "INDEX.md"
        index_path.write_text(index_content, encoding="utf-8")

        total = sum(len(v) for v in index.values()) + len(root_files)
        return {
            "status": "ok",
            "index_file": str(index_path),
            "total_files": total,
            "breakdown": {k: len(v) for k, v in index.items()},
        }


# ---------------------------------------------------------------------------
# Stub content for initial memory files
# ---------------------------------------------------------------------------

_STUB_OVERVIEW = """\
# Project Overview

> Edit this file to describe your project. The Buildly MCP Server uses it to
> give AI assistants context at the start of every session.

## What this project does

(describe here)

## Key stakeholders

(list here)

## Current status

(describe here)
"""

_STUB_ARCH = """\
# Architecture

> Document the technical architecture of this project.

## Stack

(list technologies)

## Key components

(describe major modules/services)

## Data flow

(describe how data moves through the system)
"""

_STUB_ENVS = """\
# Environments

## Local development

- URL:
- Notes:

## Staging

- URL:
- Notes:

## Production

- URL:
- Notes:
"""

_STUB_CONVENTIONS = """\
# Conventions

> Coding standards, naming conventions, and team patterns for this project.

## Code style

(describe formatting rules, linting, etc.)

## Naming conventions

(describe how to name things)

## Workflow rules

- Always update devdocs after meaningful changes
- Create draft PRs for human review
- Update Buildly Labs issue status when work starts/completes
"""

_STUB_FOCUS = """\
# Current Focus

> What is being actively worked on right now?
> Update this file when starting a new piece of work.

## Active work

(describe current task)

## Blocked by

(anything blocking progress)

## Next up

(what comes after current task)
"""

_STUB_RELEASE_NOTES = """\
# Release Notes

> One entry per release, newest first.

## Unreleased

- Initial setup
"""

_STUB_PROJECT_LINKS = """\
# Project Links

> Buildly project-to-repository connections live here.

<!-- buildly-project-links:begin -->
{
    "entries": []
}
<!-- buildly-project-links:end -->
"""

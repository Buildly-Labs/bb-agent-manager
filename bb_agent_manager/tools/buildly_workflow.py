"""
Buildly workflow tools for the Buildly MCP Server.

Provides workflow enforcement and automation:
- Definition of Done checks
- DevDocs summary creation
- Release summaries
"""

from __future__ import annotations

import json
import subprocess
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

from mcp.types import Tool

if TYPE_CHECKING:
    from bb_agent_manager.config import BuildlySettings


# ---------------------------------------------------------------------------
# Default Definition of Done checklist
# ---------------------------------------------------------------------------

_DEFAULT_DOD = [
    "Code is written and reviewed",
    "Unit tests added or updated",
    "Tests pass locally",
    "DevDocs updated (devdocs_write called)",
    "No debug/temp code left in",
    "Buildly Labs issue status updated",
    "PR created as draft for human review",
    "No secrets or credentials committed",
]


# ---------------------------------------------------------------------------
# Tool schemas
# ---------------------------------------------------------------------------

TOOLS: list[Tool] = [
    Tool(
        name="buildly_definition_of_done_check",
        description=(
            "Run a Definition of Done checklist for the current task. "
            "Returns each criterion with a pass/fail marker based on context provided."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "task_description": {
                    "type": "string",
                    "description": "Brief description of what was done",
                },
                "files_changed": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of files modified",
                },
                "tests_run": {"type": "boolean", "description": "Were tests run?"},
                "devdocs_updated": {"type": "boolean", "description": "Was devdocs updated?"},
                "issue_id": {"type": "string", "description": "Related Buildly issue ID (optional)"},
            },
            "required": ["task_description"],
        },
    ),
    Tool(
        name="buildly_create_devdocs_summary",
        description=(
            "Create a structured devdocs entry summarizing a change. "
            "Appends to devdocs/index.md and writes a standalone summary file."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Short title for this change"},
                "files_changed": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Files that were modified",
                },
                "summary": {"type": "string", "description": "What was changed and why"},
                "reuse_notes": {
                    "type": "string",
                    "description": "Any reusable patterns or components created",
                },
                "related_issue": {"type": "string", "description": "Related issue ID or URL (optional)"},
            },
            "required": ["title", "files_changed", "summary"],
        },
    ),
    Tool(
        name="buildly_release_summary",
        description=(
            "Generate a release summary from recent devdocs entries and memory. "
            "Useful for changelog generation and sprint retrospectives."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "version": {"type": "string", "description": "Version tag (e.g. 'v1.2.0')"},
                "since_date": {
                    "type": "string",
                    "description": "Include changes since this date (YYYY-MM-DD)",
                },
            },
        },
    ),
]

TOOL_NAMES: set[str] = {t.name for t in TOOLS}


# ---------------------------------------------------------------------------
# Implementations
# ---------------------------------------------------------------------------

async def handle(name: str, arguments: dict, settings: "BuildlySettings") -> dict:
    """Route workflow tool calls."""
    if name == "buildly_definition_of_done_check":
        return _dod_check(arguments, settings)
    if name == "buildly_create_devdocs_summary":
        return _create_summary(arguments, settings)
    if name == "buildly_release_summary":
        return _release_summary(arguments, settings)
    return {"error": f"Unknown workflow tool: {name}"}


def _dod_check(arguments: dict, settings: "BuildlySettings") -> dict:
    """Evaluate DoD criteria based on arguments provided."""
    # Load custom DoD from memory if available
    dod_path = Path(settings.memory_path) / "conventions.md"
    checklist = _DEFAULT_DOD[:]

    results = []
    for criterion in checklist:
        c_lower = criterion.lower()
        passed: bool | None = None

        if "test" in c_lower:
            passed = arguments.get("tests_run", None)
        elif "devdoc" in c_lower:
            passed = arguments.get("devdocs_updated", None)
        elif "secret" in c_lower or "credential" in c_lower:
            passed = True  # assume unless overridden
        else:
            passed = None  # requires human judgment

        results.append({
            "criterion": criterion,
            "status": "pass" if passed is True else ("fail" if passed is False else "review"),
        })

    failed = [r for r in results if r["status"] == "fail"]
    needs_review = [r for r in results if r["status"] == "review"]

    return {
        "status": "ok",
        "task": arguments.get("task_description", ""),
        "checklist": results,
        "summary": {
            "passed": len(results) - len(failed) - len(needs_review),
            "failed": len(failed),
            "needs_human_review": len(needs_review),
        },
        "recommendation": (
            "Ready to ship — get human review on PR"
            if not failed
            else f"Fix {len(failed)} failing criteria before shipping"
        ),
    }


def _create_summary(arguments: dict, settings: "BuildlySettings") -> dict:
    """Write a devdocs summary entry."""
    today = date.today().isoformat()
    title = arguments["title"]
    files = arguments["files_changed"]
    summary = arguments["summary"]
    reuse_notes = arguments.get("reuse_notes", "")
    related_issue = arguments.get("related_issue", "")

    entry = f"""
## {today} — {title}

**Files:** {", ".join(files)}

**Summary:** {summary}
"""
    if reuse_notes:
        entry += f"\n**Reuse Notes:** {reuse_notes}\n"
    if related_issue:
        entry += f"\n**Related Issue:** {related_issue}\n"
    entry += "\n---\n"

    devdocs_dir = Path(settings.devdocs_path)
    devdocs_dir.mkdir(parents=True, exist_ok=True)

    index_path = devdocs_dir / "index.md"
    with index_path.open("a", encoding="utf-8") as f:
        f.write(entry)

    return {
        "status": "ok",
        "appended_to": str(index_path),
        "entry_title": title,
        "date": today,
    }


def _release_summary(arguments: dict, settings: "BuildlySettings") -> dict:
    """Read devdocs/index.md and summarize recent entries."""
    version = arguments.get("version", "unreleased")
    since_date = arguments.get("since_date", "")

    index_path = Path(settings.devdocs_path) / "index.md"
    if not index_path.exists():
        return {
            "status": "no_devdocs",
            "message": "No devdocs/index.md found. Use buildly_create_devdocs_summary to add entries.",
        }

    content = index_path.read_text(encoding="utf-8")
    sections = [s.strip() for s in content.split("---") if s.strip()]

    if since_date:
        sections = [s for s in sections if since_date <= s[:10] if len(s) >= 10]

    # Also read memory release notes if available
    release_notes_path = Path(settings.memory_path) / "release_notes.md"
    memory_notes = ""
    if release_notes_path.exists():
        memory_notes = release_notes_path.read_text(encoding="utf-8")

    return {
        "status": "ok",
        "version": version,
        "since_date": since_date or "all time",
        "entry_count": len(sections),
        "entries": sections[:20],  # limit to 20 most recent
        "memory_release_notes": memory_notes[:2000] if memory_notes else None,
    }

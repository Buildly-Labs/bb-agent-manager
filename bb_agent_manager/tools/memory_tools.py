"""
Memory MCP tools for the Buildly MCP Server.

Provides read/write access to the two-layer Buildly memory system:
  Layer 1: Markdown/wiki memory (buildly_memory/ — human-readable, Git-tracked)
  Layer 2: Semantic memory (stub — pluggable via memory_service.py interface)

Resources exposed:
  memory://current-project/overview
  memory://current-project/architecture
  memory://current-project/current-focus
  memory://buildly/standards
  memory://related-projects/{name}
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from mcp.types import Resource, Tool

from bb_agent_manager.memory.markdown_memory import MarkdownMemory

if TYPE_CHECKING:
    from bb_agent_manager.config import BuildlySettings

_ORG_MEMORY_ROOT = Path.home() / ".buildly" / "memory"


# ---------------------------------------------------------------------------
# Tool schemas
# ---------------------------------------------------------------------------

TOOLS: list[Tool] = [
    Tool(
        name="memory_get_project_summary",
        description=(
            "Get a structured summary of the current project from Buildly Memory. "
            "Returns project overview, current focus, and architecture notes."
        ),
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="memory_search_current_project",
        description="Full-text search across all memory files in buildly_memory/.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search term"},
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="memory_search_related_projects",
        description=(
            "Search across org-level memory at ~/.buildly/memory/ for related projects "
            "and cross-project patterns."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search term"},
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="memory_write_session_note",
        description=(
            "Persist a session note to buildly_memory/sessions/. "
            "Use this to capture what was done in a work session."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Short title for this session"},
                "content": {"type": "string", "description": "Session notes in Markdown"},
            },
            "required": ["title", "content"],
        },
    ),
    Tool(
        name="memory_capture_decision",
        description=(
            "Record an architectural decision to buildly_memory/decisions/. "
            "Captures the decision, rationale, and alternatives considered."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Short decision title"},
                "decision": {"type": "string", "description": "What was decided"},
                "rationale": {"type": "string", "description": "Why this was chosen"},
                "alternatives": {"type": "string", "description": "Alternatives that were considered"},
            },
            "required": ["title", "decision", "rationale"],
        },
    ),
    Tool(
        name="memory_capture_pattern",
        description=(
            "Append a reusable pattern or convention to buildly_memory/conventions.md. "
            "Use this to document patterns worth reusing across projects."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Pattern name"},
                "description": {"type": "string", "description": "What the pattern does and when to use it"},
                "usage_example": {"type": "string", "description": "Code or config example"},
            },
            "required": ["name", "description"],
        },
    ),
    Tool(
        name="memory_get_recent_work",
        description="Return the most recent session notes from buildly_memory/sessions/.",
        inputSchema={
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Max sessions to return (default 5)"},
            },
        },
    ),
    Tool(
        name="memory_get_environment_context",
        description="Read environment notes from buildly_memory/environments.md.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="memory_promote_to_org_memory",
        description=(
            "Copy a memory file or content to org-level memory at ~/.buildly/memory/{project}/. "
            "Use this to share patterns or decisions across projects."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "project_name": {
                    "type": "string",
                    "description": "Project name to file it under in org memory",
                },
                "memory_type": {
                    "type": "string",
                    "description": "Type: 'decision', 'pattern', or 'overview'",
                    "enum": ["decision", "pattern", "overview"],
                },
                "content": {"type": "string", "description": "Content to promote"},
                "filename": {"type": "string", "description": "File name in org memory"},
            },
            "required": ["project_name", "memory_type", "content", "filename"],
        },
    ),
    Tool(
        name="memory_rebuild_index",
        description=(
            "Scan all buildly_memory/ files and regenerate INDEX.md. "
            "Run this after bulk changes to keep the index current."
        ),
        inputSchema={"type": "object", "properties": {}},
    ),
]

TOOL_NAMES: set[str] = {t.name for t in TOOLS}


# ---------------------------------------------------------------------------
# Implementations
# ---------------------------------------------------------------------------

async def handle(name: str, arguments: dict, settings: "BuildlySettings") -> dict:
    """Route memory tool calls."""
    mem = MarkdownMemory(settings.memory_path)

    if name == "memory_get_project_summary":
        return {"status": "ok", **mem.get_project_summary()}

    if name == "memory_search_current_project":
        results = mem.search(arguments["query"], scope="current")
        return {"status": "ok", "query": arguments["query"], "results": results}

    if name == "memory_search_related_projects":
        if not _ORG_MEMORY_ROOT.exists():
            return {
                "status": "ok",
                "message": "No org-level memory found at ~/.buildly/memory/. "
                           "Use memory_promote_to_org_memory to add entries.",
                "results": [],
            }
        results = mem.search(arguments["query"], scope="org")
        return {"status": "ok", "query": arguments["query"], "results": results}

    if name == "memory_write_session_note":
        path = mem.write_session_note(arguments["title"], arguments["content"])
        return {"status": "ok", "file": path}

    if name == "memory_capture_decision":
        path = mem.capture_decision(
            arguments["title"],
            arguments["decision"],
            arguments["rationale"],
            arguments.get("alternatives", ""),
        )
        return {"status": "ok", "file": path}

    if name == "memory_capture_pattern":
        path = mem.capture_pattern(
            arguments["name"],
            arguments["description"],
            arguments.get("usage_example", ""),
        )
        return {"status": "ok", "file": path}

    if name == "memory_get_recent_work":
        sessions = mem.get_recent_work(limit=arguments.get("limit", 5))
        return {"status": "ok", "sessions": sessions}

    if name == "memory_get_environment_context":
        content = mem.read_file("environments.md")
        return {"status": "ok", "content": content}

    if name == "memory_promote_to_org_memory":
        project = arguments["project_name"]
        target_dir = _ORG_MEMORY_ROOT / project / arguments["memory_type"]
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / arguments["filename"]
        target_file.write_text(arguments["content"], encoding="utf-8")
        return {"status": "ok", "file": str(target_file)}

    if name == "memory_rebuild_index":
        return mem.rebuild_index()

    return {"error": f"Unknown memory tool: {name}"}


# ---------------------------------------------------------------------------
# MCP Resources
# ---------------------------------------------------------------------------

_RESOURCE_MAP: dict[str, str] = {
    "memory://current-project/overview": "project_overview.md",
    "memory://current-project/architecture": "architecture.md",
    "memory://current-project/current-focus": "current_focus.md",
    "memory://buildly/standards": "conventions.md",
}


def list_resources(settings: "BuildlySettings") -> list[Resource]:
    """Return available Buildly memory resources."""
    base = [
        Resource(
            uri="memory://current-project/overview",  # type: ignore[arg-type]
            name="Project Overview",
            description="Current project overview from buildly_memory/",
            mimeType="text/markdown",
        ),
        Resource(
            uri="memory://current-project/architecture",  # type: ignore[arg-type]
            name="Architecture",
            description="Architecture notes from buildly_memory/",
            mimeType="text/markdown",
        ),
        Resource(
            uri="memory://current-project/current-focus",  # type: ignore[arg-type]
            name="Current Focus",
            description="What is being worked on right now",
            mimeType="text/markdown",
        ),
        Resource(
            uri="memory://buildly/standards",  # type: ignore[arg-type]
            name="Buildly Standards",
            description="Conventions and patterns from buildly_memory/conventions.md",
            mimeType="text/markdown",
        ),
    ]

    # Add cross-project resources if org memory exists
    if _ORG_MEMORY_ROOT.exists():
        for project_dir in sorted(_ORG_MEMORY_ROOT.iterdir()):
            if project_dir.is_dir():
                base.append(
                    Resource(
                        uri=f"memory://related-projects/{project_dir.name}",  # type: ignore[arg-type]
                        name=f"Related: {project_dir.name}",
                        description=f"Org memory for {project_dir.name}",
                        mimeType="text/markdown",
                    )
                )

    return base


async def read_resource(uri: str, settings: "BuildlySettings") -> str:
    """Read a memory resource by URI."""
    mem = MarkdownMemory(settings.memory_path)

    if uri in _RESOURCE_MAP:
        return mem.read_file(_RESOURCE_MAP[uri])

    if uri.startswith("memory://related-projects/"):
        project = uri.removeprefix("memory://related-projects/")
        project_dir = _ORG_MEMORY_ROOT / project
        if project_dir.exists():
            # Return concatenated overview files
            parts = []
            for md_file in sorted(project_dir.rglob("*.md"))[:5]:
                parts.append(f"## {md_file.name}\n\n{md_file.read_text(encoding='utf-8')}")
            return "\n\n---\n\n".join(parts) if parts else f"No memory files found for {project}"
        return f"Project '{project}' not found in org memory (~/.buildly/memory/)"

    return f"Unknown resource URI: {uri}"

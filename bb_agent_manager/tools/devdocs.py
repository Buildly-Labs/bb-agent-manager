"""
DevDocs tools for the Buildly MCP Server.

Provides read/write/list access to the local devdocs/ folder.
This is the primary documentation layer — all meaningful code changes
should be reflected here.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING

from mcp.types import Tool

if TYPE_CHECKING:
    from bb_agent_manager.config import BuildlySettings


# ---------------------------------------------------------------------------
# Tool schemas
# ---------------------------------------------------------------------------

TOOLS: list[Tool] = [
    Tool(
        name="devdocs_write",
        description=(
            "Write or update a documentation file in the devdocs/ folder. "
            "Call this after any meaningful code change to keep docs current."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "File name (e.g. 'api.md' or 'guides/setup.md')",
                },
                "content": {
                    "type": "string",
                    "description": "Markdown content to write",
                },
            },
            "required": ["filename", "content"],
        },
    ),
    Tool(
        name="devdocs_read",
        description="Read a documentation file from the devdocs/ folder.",
        inputSchema={
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "File name relative to devdocs/ folder",
                },
            },
            "required": ["filename"],
        },
    ),
    Tool(
        name="devdocs_list",
        description="List all documentation files in the devdocs/ folder.",
        inputSchema={"type": "object", "properties": {}},
    ),
]

TOOL_NAMES: set[str] = {t.name for t in TOOLS}


# ---------------------------------------------------------------------------
# Implementations
# ---------------------------------------------------------------------------

async def handle(name: str, arguments: dict, settings: "BuildlySettings") -> dict:
    """Route devdocs tool calls."""
    devdocs_dir = Path(settings.devdocs_path)

    if name == "devdocs_write":
        return _write(arguments["filename"], arguments["content"], devdocs_dir)
    if name == "devdocs_read":
        return _read(arguments["filename"], devdocs_dir)
    if name == "devdocs_list":
        return _list(devdocs_dir)
    return {"error": f"Unknown devdocs tool: {name}"}


def _write(filename: str, content: str, devdocs_dir: Path) -> dict:
    filepath = devdocs_dir / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content, encoding="utf-8")
    return {
        "status": "ok",
        "filename": filename,
        "bytes_written": len(content.encode()),
    }


def _read(filename: str, devdocs_dir: Path) -> dict:
    filepath = devdocs_dir / filename
    if not filepath.exists():
        return {"error": f"File not found: {filename}", "devdocs_path": str(devdocs_dir)}
    return {
        "status": "ok",
        "filename": filename,
        "content": filepath.read_text(encoding="utf-8"),
    }


def _list(devdocs_dir: Path) -> dict:
    devdocs_dir.mkdir(parents=True, exist_ok=True)
    files = sorted(
        str(p.relative_to(devdocs_dir))
        for p in devdocs_dir.rglob("*")
        if p.is_file()
    )
    return {"status": "ok", "count": len(files), "files": files}


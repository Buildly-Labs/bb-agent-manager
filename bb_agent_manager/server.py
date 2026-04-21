"""
Core Buildly MCP Server.

Registers all tools and resources. Run via:
    python mcp_server_stdio.py
    buildly-mcp   (after pip install -e .)

This server is model-agnostic — it provides context, memory, and workflow tools.
Model selection remains with the external MCP client (GitHub Copilot, Claude, etc.).
"""

import asyncio
import json
import logging
import sys

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, TextContent, Tool

from bb_agent_manager.config import BuildlySettings
import bb_agent_manager.tools.devdocs as devdocs_tools
import bb_agent_manager.tools.buildly_labs as labs_tools
import bb_agent_manager.tools.buildly_workflow as workflow_tools
import bb_agent_manager.tools.buildly_env as env_tools
import bb_agent_manager.tools.memory_tools as memory_tools

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Server instance
# ---------------------------------------------------------------------------

server = Server("buildly-mcp")

# ---------------------------------------------------------------------------
# Tool registry — merge all tool lists from each module
# ---------------------------------------------------------------------------

ALL_TOOLS: list[Tool] = (
    devdocs_tools.TOOLS
    + labs_tools.TOOLS
    + workflow_tools.TOOLS
    + env_tools.TOOLS
    + memory_tools.TOOLS
)

_TOOL_ROUTERS = {
    **{n: devdocs_tools.handle for n in devdocs_tools.TOOL_NAMES},
    **{n: labs_tools.handle for n in labs_tools.TOOL_NAMES},
    **{n: workflow_tools.handle for n in workflow_tools.TOOL_NAMES},
    **{n: env_tools.handle for n in env_tools.TOOL_NAMES},
    **{n: memory_tools.handle for n in memory_tools.TOOL_NAMES},
}


@server.list_tools()
async def list_tools() -> list[Tool]:
    """Return all available Buildly MCP tools."""
    return ALL_TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Route an MCP tool call to the appropriate handler."""
    settings = BuildlySettings()
    handler = _TOOL_ROUTERS.get(name)

    if handler is None:
        result = {"error": f"Unknown tool: {name}", "available_tools": [t.name for t in ALL_TOOLS]}
    else:
        try:
            result = await handler(name, arguments, settings)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Tool %s raised an exception", name)
            result = {"error": str(exc), "tool": name}

    return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]


# ---------------------------------------------------------------------------
# Resource registry
# ---------------------------------------------------------------------------

@server.list_resources()
async def list_resources() -> list[Resource]:
    """Return all Buildly memory resources."""
    settings = BuildlySettings()
    return memory_tools.list_resources(settings)


@server.read_resource()
async def read_resource(uri) -> str:
    """Read a Buildly memory resource by URI."""
    settings = BuildlySettings()
    return await memory_tools.read_resource(str(uri), settings)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

async def _run() -> None:
    async with stdio_server() as (read_stream, write_stream):
        logger.info("Buildly MCP Server starting — stdio transport")
        logger.info("Tools available: %s", [t.name for t in ALL_TOOLS])
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main() -> None:
    """Main entry point — used by 'buildly-mcp' console script."""
    logging.basicConfig(
        stream=sys.stderr,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    asyncio.run(_run())

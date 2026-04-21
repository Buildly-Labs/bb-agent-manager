"""
Buildly environment and repo context tools.

Provides awareness of the current environment, project, and git state
without requiring model knowledge.
"""

from __future__ import annotations

import subprocess
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
        name="buildly_get_environment_context",
        description=(
            "Get the current Buildly environment context: env name, product UUID, org UUID, "
            "and configuration summary. Use this to confirm which environment is active."
        ),
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="buildly_get_repo_context",
        description=(
            "Get the current git repository context: remote URL, current branch, "
            "recent commits, and dirty status. Helps ground the AI in current code state."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "commit_count": {
                    "type": "integer",
                    "description": "Number of recent commits to include (default 5)",
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
    """Route environment/repo tool calls."""
    if name == "buildly_get_environment_context":
        return _env_context(settings)
    if name == "buildly_get_repo_context":
        return _repo_context(arguments.get("commit_count", 5), settings)
    return {"error": f"Unknown env tool: {name}"}


def _env_context(settings: "BuildlySettings") -> dict:
    # Also read environments.md from memory for richer context
    env_memory_path = Path(settings.memory_path) / "environments.md"
    env_memory = ""
    if env_memory_path.exists():
        env_memory = env_memory_path.read_text(encoding="utf-8")

    return {
        "status": "ok",
        "env_name": settings.buildly_env_name or "(not set — configure BUILDLY_ENV_NAME)",
        "product_uuid": settings.buildly_product_uuid or "(not set — configure BUILDLY_PRODUCT_UUID)",
        "org_uuid": settings.buildly_org_uuid or "(not set — configure BUILDLY_ORG_UUID)",
        "labs_base_url": settings.labs_base_url,
        "devdocs_path": settings.devdocs_path,
        "memory_path": settings.memory_path,
        "token_configured": bool(settings.labs_api_token),
        "github_repo": settings.github_repo or "(not set)",
        "env_notes": env_memory[:2000] if env_memory else None,
    }


def _repo_context(commit_count: int, settings: "BuildlySettings") -> dict:
    result: dict = {}

    def _git(*args: str) -> str:
        try:
            return subprocess.check_output(
                ["git", *args],
                stderr=subprocess.DEVNULL,
                text=True,
            ).strip()
        except Exception:  # noqa: BLE001
            return ""

    result["remote_url"] = _git("remote", "get-url", "origin")
    result["current_branch"] = _git("rev-parse", "--abbrev-ref", "HEAD")
    result["latest_commit"] = _git("log", "-1", "--oneline")
    result["status_summary"] = _git("status", "--short")
    result["is_dirty"] = bool(result["status_summary"])

    log = _git("log", f"-{commit_count}", "--oneline")
    result["recent_commits"] = log.splitlines() if log else []

    if settings.github_repo:
        result["github_repo"] = settings.github_repo

    result["status"] = "ok"
    return result

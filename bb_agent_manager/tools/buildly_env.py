"""
Buildly environment and repo context tools.

Provides awareness of the current environment, project, and git state
without requiring model knowledge.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urlparse

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
    Tool(
        name="buildly_remember_project_link",
        description=(
            "Persist a link between the current repository and a Buildly project so future "
            "sessions can reuse the same project context."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "product_uuid": {"type": "string", "description": "Buildly product UUID (uses BUILDLY_PRODUCT_UUID if omitted)"},
                "product_name": {"type": "string", "description": "Human-readable Buildly product name"},
                "repo_url": {"type": "string", "description": "Repository remote URL (uses git origin if omitted)"},
                "github_repo": {"type": "string", "description": "GitHub repo in owner/repo format"},
                "org_uuid": {"type": "string", "description": "Buildly organization UUID (uses BUILDLY_ORG_UUID if omitted)"},
                "notes": {"type": "string", "description": "Optional notes about the mapping"},
            },
        },
    ),
    Tool(
        name="buildly_get_project_link",
        description=(
            "Read the remembered Buildly project-to-repo link for the current repository or a "
            "provided repo/product identifier."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "repo_url": {"type": "string", "description": "Repository remote URL to look up"},
                "github_repo": {"type": "string", "description": "GitHub repo in owner/repo format"},
                "product_uuid": {"type": "string", "description": "Buildly product UUID"},
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
    if name == "buildly_remember_project_link":
        return _remember_project_link(arguments, settings)
    if name == "buildly_get_project_link":
        return _get_project_link(arguments, settings)
    return {"error": f"Unknown env tool: {name}"}


def _links_file(settings: "BuildlySettings") -> Path:
    return Path(settings.memory_path) / "project_links.md"


def _read_links(settings: "BuildlySettings") -> dict:
    path = _links_file(settings)
    if not path.exists():
        return {"entries": []}

    text = path.read_text(encoding="utf-8")
    match = re.search(r"<!-- buildly-project-links:begin -->(.*?)<!-- buildly-project-links:end -->", text, re.S)
    if not match:
        return {"entries": []}

    try:
        data = json.loads(match.group(1).strip())
    except json.JSONDecodeError:
        return {"entries": []}

    if isinstance(data, dict) and isinstance(data.get("entries"), list):
        return data
    return {"entries": []}


def _write_links(settings: "BuildlySettings", data: dict) -> str:
    path = _links_file(settings)
    path.parent.mkdir(parents=True, exist_ok=True)
    content = (
        "# Project Links\n\n"
        "Persistent links between Buildly projects and repositories.\n\n"
        "<!-- buildly-project-links:begin -->\n"
        f"{json.dumps(data, indent=2, sort_keys=True)}\n"
        "<!-- buildly-project-links:end -->\n"
    )
    path.write_text(content, encoding="utf-8")
    return str(path)


def _current_repo_identifiers(settings: "BuildlySettings") -> tuple[str, str]:
    remote_url = _repo_context(1, settings).get("remote_url", "")
    github_repo = settings.github_repo or _github_repo_from_url(remote_url)
    return remote_url, github_repo


def _github_repo_from_url(repo_url: str) -> str:
    if not repo_url:
        return ""

    if repo_url.endswith(".git"):
        repo_url = repo_url[:-4]

    if repo_url.startswith("git@"):
        _, _, tail = repo_url.partition(":")
        return tail if tail else ""

    parsed = urlparse(repo_url)
    if parsed.scheme in {"http", "https"}:
        return parsed.path.strip("/")

    return ""


def _match_link(entry: dict, arguments: dict, settings: "BuildlySettings") -> bool:
    repo_url = arguments.get("repo_url")
    github_repo = arguments.get("github_repo")
    product_uuid = arguments.get("product_uuid") or settings.buildly_product_uuid

    if repo_url and entry.get("repo_url") == repo_url:
        return True
    if github_repo and entry.get("github_repo") == github_repo:
        return True
    if product_uuid and entry.get("product_uuid") == product_uuid:
        return True
    return False


def _remember_project_link(arguments: dict, settings: "BuildlySettings") -> dict:
    product_uuid = arguments.get("product_uuid") or settings.buildly_product_uuid
    repo_url = arguments.get("repo_url")
    github_repo = arguments.get("github_repo")

    if not repo_url or not github_repo:
        current_repo_url, current_github_repo = _current_repo_identifiers(settings)
        repo_url = repo_url or current_repo_url
        github_repo = github_repo or current_github_repo

    if not product_uuid:
        return {"status": "error", "error": "product_uuid is required. Set BUILDLY_PRODUCT_UUID or pass product_uuid explicitly."}

    if not github_repo:
        return {"status": "error", "error": "github_repo could not be determined from the current remote. Set GITHUB_REPO or pass github_repo explicitly."}

    entries = _read_links(settings).get("entries", [])
    updated_entry = {
        "product_uuid": product_uuid,
        "product_name": arguments.get("product_name", ""),
        "repo_url": repo_url or "",
        "github_repo": github_repo,
        "org_uuid": arguments.get("org_uuid") or settings.buildly_org_uuid,
        "env_name": settings.buildly_env_name,
        "notes": arguments.get("notes", ""),
        "updated_at": _now_iso(),
    }

    replaced = False
    for index, entry in enumerate(entries):
        if _match_link(entry, arguments, settings):
            entries[index] = {**entry, **updated_entry, "created_at": entry.get("created_at", _now_iso())}
            replaced = True
            break

    if not replaced:
        updated_entry["created_at"] = _now_iso()
        entries.append(updated_entry)

    file_path = _write_links(settings, {"entries": entries})
    return {
        "status": "ok",
        "file": file_path,
        "entry": updated_entry,
        "message": f"Saved project link for {github_repo} -> {product_uuid}",
    }


def _get_project_link(arguments: dict, settings: "BuildlySettings") -> dict:
    repo_url = arguments.get("repo_url")
    github_repo = arguments.get("github_repo")
    product_uuid = arguments.get("product_uuid")

    if not repo_url and not github_repo and not product_uuid:
        repo_url, github_repo = _current_repo_identifiers(settings)
        product_uuid = settings.buildly_product_uuid or None

    entries = _read_links(settings).get("entries", [])
    for entry in entries:
        if repo_url and entry.get("repo_url") == repo_url:
            return {"status": "ok", "entry": entry}
        if github_repo and entry.get("github_repo") == github_repo:
            return {"status": "ok", "entry": entry}
        if product_uuid and entry.get("product_uuid") == product_uuid:
            return {"status": "ok", "entry": entry}

    return {"status": "ok", "entry": None, "message": "No saved project link found."}


def _now_iso() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _env_context(settings: "BuildlySettings") -> dict:
    # Also read environments.md from memory for richer context
    env_memory_path = Path(settings.memory_path) / "environments.md"
    env_memory = ""
    if env_memory_path.exists():
        env_memory = env_memory_path.read_text(encoding="utf-8")

    project_link = _get_project_link({}, settings)

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
        "project_link": project_link.get("entry"),
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

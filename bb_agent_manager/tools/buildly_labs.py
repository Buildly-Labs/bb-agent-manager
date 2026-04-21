"""
Buildly Labs tools for the Buildly MCP Server.

Provides authentication and data access for the Buildly Labs platform.
Token is read from (in priority order):
  1. The 'access_token' tool argument
  2. LABS_API_TOKEN environment variable
  3. ~/.buildly/token file (written by buildly_login)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

import httpx
from mcp.types import Tool

if TYPE_CHECKING:
    from bb_agent_manager.config import BuildlySettings

_TOKEN_FILE = Path.home() / ".buildly" / "token"


# ---------------------------------------------------------------------------
# Token helpers
# ---------------------------------------------------------------------------

def _get_token(settings: "BuildlySettings", arguments: dict) -> str | None:
    """Resolve auth token from argument → env var → token file."""
    if arguments.get("access_token"):
        return arguments["access_token"]
    if settings.labs_api_token:
        return settings.labs_api_token
    if _TOKEN_FILE.exists():
        return _TOKEN_FILE.read_text(encoding="utf-8").strip()
    return None


def _auth_headers(token: str | None) -> dict[str, str]:
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


async def _get(url: str, token: str | None, params: dict | None = None) -> dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(url, headers=_auth_headers(token), params=params)
            r.raise_for_status()
            return {"status": "ok", "data": r.json()}
    except httpx.HTTPStatusError as exc:
        return {"error": f"HTTP {exc.response.status_code}", "detail": exc.response.text[:500]}
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}


async def _post(url: str, payload: dict, token: str | None = None) -> dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(url, json=payload, headers=_auth_headers(token))
            r.raise_for_status()
            return {"status": "ok", "data": r.json()}
    except httpx.HTTPStatusError as exc:
        return {"error": f"HTTP {exc.response.status_code}", "detail": exc.response.text[:500]}
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}


# ---------------------------------------------------------------------------
# Tool schemas
# ---------------------------------------------------------------------------

TOOLS: list[Tool] = [
    Tool(
        name="buildly_test_connection",
        description="Test connectivity to the Buildly Labs API.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="buildly_login",
        description=(
            "Authenticate with Buildly Labs. Stores the token locally at "
            "~/.buildly/token so you don't need to pass it on every call."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "username": {"type": "string", "description": "Buildly Labs username or email"},
                "password": {"type": "string", "description": "Buildly Labs password"},
            },
            "required": ["username", "password"],
        },
    ),
    Tool(
        name="buildly_get_products",
        description="List all products in your Buildly Labs organization.",
        inputSchema={
            "type": "object",
            "properties": {
                "access_token": {"type": "string", "description": "JWT token (optional if stored)"},
                "limit": {"type": "integer", "description": "Max results (default 50)"},
                "offset": {"type": "integer", "description": "Pagination offset"},
            },
        },
    ),
    Tool(
        name="buildly_get_issues",
        description="Fetch backlog issues from Buildly Labs, optionally filtered by product.",
        inputSchema={
            "type": "object",
            "properties": {
                "access_token": {"type": "string", "description": "JWT token (optional if stored)"},
                "product_uuid": {"type": "string", "description": "Filter by product UUID"},
                "status": {"type": "string", "description": "Filter by status (e.g. 'in_progress')"},
                "limit": {"type": "integer", "description": "Max results (default 50)"},
                "offset": {"type": "integer", "description": "Pagination offset"},
            },
        },
    ),
    Tool(
        name="buildly_get_features",
        description="Fetch features/epics from Buildly Labs for a product.",
        inputSchema={
            "type": "object",
            "properties": {
                "access_token": {"type": "string", "description": "JWT token (optional if stored)"},
                "product_uuid": {"type": "string", "description": "Product UUID (uses env BUILDLY_PRODUCT_UUID if omitted)"},
                "limit": {"type": "integer", "description": "Max results (default 50)"},
            },
        },
    ),
    Tool(
        name="buildly_get_current_work_context",
        description=(
            "Get a combined snapshot of current work: active issues, current sprint/milestone, "
            "and product context. Use this at the start of a session to orient the AI."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "access_token": {"type": "string", "description": "JWT token (optional if stored)"},
                "product_uuid": {"type": "string", "description": "Product UUID (uses env BUILDLY_PRODUCT_UUID if omitted)"},
            },
        },
    ),
    Tool(
        name="buildly_update_issue_status",
        description="Update the status of a Buildly Labs issue.",
        inputSchema={
            "type": "object",
            "properties": {
                "issue_id": {"type": "string", "description": "Issue ID to update"},
                "status": {
                    "type": "string",
                    "description": "New status (e.g. 'in_progress', 'done', 'blocked')",
                },
                "access_token": {"type": "string", "description": "JWT token (optional if stored)"},
            },
            "required": ["issue_id", "status"],
        },
    ),
]

TOOL_NAMES: set[str] = {t.name for t in TOOLS}


# ---------------------------------------------------------------------------
# Implementations
# ---------------------------------------------------------------------------

async def handle(name: str, arguments: dict, settings: "BuildlySettings") -> dict:
    """Route Buildly Labs tool calls."""
    base = settings.labs_base_url.rstrip("/")

    if name == "buildly_test_connection":
        return await _test_connection(base)

    if name == "buildly_login":
        return await _login(base, arguments["username"], arguments["password"])

    token = _get_token(settings, arguments)
    if token is None and name != "buildly_test_connection":
        return {
            "error": "Not authenticated. Run buildly_login first or set LABS_API_TOKEN.",
        }

    if name == "buildly_get_products":
        return await _get(f"{base}/products", token, {
            "limit": arguments.get("limit", 50),
            "offset": arguments.get("offset", 0),
        })

    if name == "buildly_get_issues":
        params: dict = {
            "limit": arguments.get("limit", 50),
            "offset": arguments.get("offset", 0),
        }
        product_uuid = arguments.get("product_uuid") or settings.buildly_product_uuid
        if product_uuid:
            params["product_uuid"] = product_uuid
        if arguments.get("status"):
            params["status"] = arguments["status"]
        return await _get(f"{base}/issues", token, params)

    if name == "buildly_get_features":
        product_uuid = arguments.get("product_uuid") or settings.buildly_product_uuid
        params = {"limit": arguments.get("limit", 50)}
        if product_uuid:
            params["product_uuid"] = product_uuid
        return await _get(f"{base}/features", token, params)

    if name == "buildly_get_current_work_context":
        product_uuid = arguments.get("product_uuid") or settings.buildly_product_uuid
        params: dict = {"status": "in_progress", "limit": 20}
        if product_uuid:
            params["product_uuid"] = product_uuid
        issues = await _get(f"{base}/issues", token, params)
        milestones = await _get(f"{base}/milestones", token, {"product_uuid": product_uuid} if product_uuid else {})
        return {
            "status": "ok",
            "env_name": settings.buildly_env_name,
            "product_uuid": product_uuid,
            "org_uuid": settings.buildly_org_uuid,
            "active_issues": issues.get("data", issues.get("error")),
            "milestones": milestones.get("data", milestones.get("error")),
        }

    if name == "buildly_update_issue_status":
        issue_id = arguments["issue_id"]
        return await _post(
            f"{base}/issues/{issue_id}",
            {"status": arguments["status"]},
            token,
        )

    return {"error": f"Unknown labs tool: {name}"}


async def _test_connection(base: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(base, follow_redirects=True)
            return {"status": "ok", "http_status": r.status_code, "url": base}
    except Exception as exc:  # noqa: BLE001
        return {"status": "unreachable", "error": str(exc), "url": base}


async def _login(base: str, username: str, password: str) -> dict:
    result = await _post(f"{base}/auth/jwt/create/", {"username": username, "password": password})
    if "error" in result:
        return result
    data = result.get("data", {})
    token = data.get("access") or data.get("token")
    if token:
        _TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        _TOKEN_FILE.write_text(token, encoding="utf-8")
        return {
            "status": "ok",
            "message": "Logged in. Token saved to ~/.buildly/token",
            "token_preview": token[:12] + "...",
        }
    return {"error": "Login response did not contain a token", "response": data}

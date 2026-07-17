"""
Buildly Labs tools for the Buildly MCP Server.

Targets the labs.buildly.io API (new HTMX frontend, /api/v1/*).

Auth: the /api/v1 data endpoints accept an API token via the `X-API-Token`
header (or `Authorization: Bearer <token>`). Create a token at
https://labs.buildly.io/settings/api-keys and provide it via (priority order):
  1. The 'access_token' tool argument
  2. LABS_API_TOKEN environment variable
  3. ~/.buildly/token file
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
    """Resolve API token from argument -> env var -> token file."""
    if arguments.get("access_token"):
        return arguments["access_token"]
    if settings.labs_api_token:
        return settings.labs_api_token
    if _TOKEN_FILE.exists():
        return _TOKEN_FILE.read_text(encoding="utf-8").strip()
    return None


def _auth_headers(token: str | None) -> dict[str, str]:
    """New API takes X-API-Token; also send Bearer for OAuth access tokens."""
    headers = {"Accept": "application/json"}
    if token:
        headers["X-API-Token"] = token
        headers["Authorization"] = f"Bearer {token}"
    return headers


async def _get(url: str, token: str | None, params: dict | None = None) -> dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            r = await client.get(url, headers=_auth_headers(token), params=params)
            r.raise_for_status()
            return {"status": "ok", "data": r.json()}
    except httpx.HTTPStatusError as exc:
        return {"error": f"HTTP {exc.response.status_code}", "detail": exc.response.text[:500]}
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}


async def _send(url: str, method: str, token: str | None, payload: dict | None = None) -> dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            r = await client.request(method, url, json=payload, headers=_auth_headers(token))
            r.raise_for_status()
            ct = r.headers.get("content-type", "")
            return {"status": "ok", "data": r.json() if "json" in ct else r.text[:500]}
    except httpx.HTTPStatusError as exc:
        return {"error": f"HTTP {exc.response.status_code}", "detail": exc.response.text[:500]}
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}


def _extract_items(payload: Any) -> list[dict[str, Any]]:
    """Normalize an API payload into a list of mapping items."""
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        for key in ("results", "items", "data", "products", "backlog", "tasks"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


# ---------------------------------------------------------------------------
# Tool schemas
# ---------------------------------------------------------------------------

TOOLS: list[Tool] = [
    Tool(
        name="buildly_test_connection",
        description="Test connectivity to the Buildly Labs API (labs.buildly.io).",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="buildly_login",
        description=(
            "Store a Buildly Labs API token locally (~/.buildly/token) for later calls. "
            "Create the token at https://labs.buildly.io/settings/api-keys and pass it as 'api_token'. "
            "(The new labs.buildly.io API uses API tokens / OAuth2, not username+password.)"
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "api_token": {"type": "string", "description": "API token from labs.buildly.io/settings/api-keys"},
            },
            "required": ["api_token"],
        },
    ),
    Tool(
        name="buildly_get_products",
        description="List products in your Buildly Labs organization.",
        inputSchema={
            "type": "object",
            "properties": {
                "access_token": {"type": "string", "description": "API token (optional if stored)"},
                "limit": {"type": "integer", "description": "Max results (default 50)"},
                "offset": {"type": "integer", "description": "Pagination offset"},
            },
        },
    ),
    Tool(
        name="buildly_get_issues",
        description="Fetch backlog items (issues) from Buildly Labs, optionally filtered by product/status.",
        inputSchema={
            "type": "object",
            "properties": {
                "access_token": {"type": "string", "description": "API token (optional if stored)"},
                "product_id": {"type": "string", "description": "Filter by product id"},
                "status": {"type": "string", "description": "Filter by status (e.g. 'in_progress')"},
                "limit": {"type": "integer", "description": "Max results (default 50)"},
                "offset": {"type": "integer", "description": "Pagination offset"},
            },
        },
    ),
    Tool(
        name="buildly_get_features",
        description="Fetch backlog features/epics from Buildly Labs for a product.",
        inputSchema={
            "type": "object",
            "properties": {
                "access_token": {"type": "string", "description": "API token (optional if stored)"},
                "product_id": {"type": "string", "description": "Product id (uses env BUILDLY_PRODUCT_UUID if omitted)"},
                "limit": {"type": "integer", "description": "Max results (default 50)"},
            },
        },
    ),
    Tool(
        name="buildly_get_tasks",
        description="Fetch backlog items for a product, organized by type (features, issues, tasks).",
        inputSchema={
            "type": "object",
            "properties": {
                "access_token": {"type": "string", "description": "API token (optional if stored)"},
                "product_id": {"type": "string", "description": "Product id (optional if BUILDLY_PRODUCT_UUID set)"},
            },
        },
    ),
    Tool(
        name="buildly_get_current_work_context",
        description=(
            "Combined snapshot of current work: in-progress backlog items and milestones "
            "for a product. Use at session start to orient the AI."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "access_token": {"type": "string", "description": "API token (optional if stored)"},
                "product_id": {"type": "string", "description": "Product id (uses env BUILDLY_PRODUCT_UUID if omitted)"},
            },
        },
    ),
    Tool(
        name="buildly_update_issue_status",
        description="Update the status of a Buildly Labs backlog issue.",
        inputSchema={
            "type": "object",
            "properties": {
                "issue_uuid": {"type": "string", "description": "Issue UUID to update"},
                "status": {"type": "string", "description": "New status (e.g. 'in_progress', 'done')"},
                "access_token": {"type": "string", "description": "API token (optional if stored)"},
            },
            "required": ["issue_uuid", "status"],
        },
    ),
]

TOOL_NAMES: set[str] = {t.name for t in TOOLS}


# ---------------------------------------------------------------------------
# Implementations
# ---------------------------------------------------------------------------

def _api(base: str) -> str:
    """Return the /api/v1 root, tolerating base URLs with or without it."""
    base = base.rstrip("/")
    if base.endswith("/api/v1"):
        return base
    if base.endswith("/api"):
        return base + "/v1"
    return base + "/api/v1"


def _product_filter(arguments: dict, settings: "BuildlySettings") -> dict:
    pid = arguments.get("product_id") or settings.buildly_product_uuid
    return {"product_id": pid} if pid else {}


async def handle(name: str, arguments: dict, settings: "BuildlySettings") -> dict:
    """Route Buildly Labs tool calls."""
    base = settings.labs_base_url
    api = _api(base)

    if name == "buildly_test_connection":
        return await _test_connection(base.rstrip("/"))

    if name == "buildly_login":
        return _save_token(arguments["api_token"])

    token = _get_token(settings, arguments)
    if token is None:
        return {"error": "No API token. Run buildly_login with a token from "
                         "labs.buildly.io/settings/api-keys, or set LABS_API_TOKEN."}

    if name == "buildly_get_products":
        return await _get(f"{api}/products", token, {
            "limit": arguments.get("limit", 50),
            "offset": arguments.get("offset", 0),
        })

    if name == "buildly_get_issues":
        params = {"limit": arguments.get("limit", 50), "offset": arguments.get("offset", 0)}
        params.update(_product_filter(arguments, settings))
        if arguments.get("status"):
            params["status"] = arguments["status"]
        return await _get(f"{api}/backlog", token, params)

    if name == "buildly_get_features":
        params = {"limit": arguments.get("limit", 50)}
        params.update(_product_filter(arguments, settings))
        result = await _get(f"{api}/backlog", token, params)
        if "error" in result:
            return result
        items = [i for i in _extract_items(result.get("data"))
                 if str(i.get("type", i.get("item_type", ""))).lower() in ("feature", "epic")]
        return {"status": "ok", "count": len(items), "features": items}

    if name == "buildly_get_tasks":
        params = _product_filter(arguments, settings)
        result = await _get(f"{api}/backlog", token, params | {"limit": 200})
        if "error" in result:
            return result
        items = _extract_items(result.get("data"))
        organized: dict[str, list] = {"features": [], "issues": [], "tasks": []}
        for it in items:
            t = str(it.get("type", it.get("item_type", ""))).lower()
            if t in ("feature", "epic"):
                organized["features"].append(it)
            elif t in ("issue", "bug"):
                organized["issues"].append(it)
            else:
                organized["tasks"].append(it)
        return {"status": "ok", "total": len(items), "tasks": organized,
                "product_id": arguments.get("product_id") or settings.buildly_product_uuid}

    if name == "buildly_get_current_work_context":
        params = _product_filter(arguments, settings)
        issues = await _get(f"{api}/backlog", token, params | {"status": "in_progress", "limit": 20})
        milestones = await _get(f"{api}/milestones", token, params)
        return {
            "status": "ok",
            "env_name": settings.buildly_env_name,
            "product_id": arguments.get("product_id") or settings.buildly_product_uuid,
            "org_uuid": settings.buildly_org_uuid,
            "active_issues": issues.get("data", issues.get("error")),
            "milestones": milestones.get("data", milestones.get("error")),
        }

    if name == "buildly_update_issue_status":
        uuid = arguments["issue_uuid"]
        return await _send(
            f"{base.rstrip('/')}/backlog/issue/{uuid}/status",
            "PATCH", token, {"status": arguments["status"]},
        )

    return {"error": f"Unknown labs tool: {name}"}


async def _test_connection(base: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(base, follow_redirects=True)
            return {"status": "ok", "http_status": r.status_code, "url": base}
    except Exception as exc:  # noqa: BLE001
        return {"status": "unreachable", "error": str(exc), "url": base}


def _save_token(token: str) -> dict:
    _TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    _TOKEN_FILE.write_text(token.strip(), encoding="utf-8")
    return {
        "status": "ok",
        "message": "API token saved to ~/.buildly/token",
        "token_preview": token[:8] + "...",
    }

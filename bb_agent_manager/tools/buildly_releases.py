"""
Release & build management tools for the Buildly MCP Server.

Wires up the release/build/repository/design-system surface that already exists
in the Labs API (labs.buildly.io) but was not previously exposed to MCP clients.

Model (see devdocs/RELEASE_BUILD_MANAGEMENT.md):
  * A **release** is a primary version (e.g. v1.4.0)      -> /api/v1/releases
  * A **build** is a micro-release related to a release    -> /rad/api/micro-releases
    (a change set that reached production quickly; RAD = Rapid Application Dev)
  * Resolved issues/features/tasks are associated with a release (native
    `release_uuid`) and a build (micro-release), so reports can show exactly
    what shipped in a given build or release.

Auth and HTTP handling reuse the helpers in buildly_labs so token resolution
(arg -> per-session OAuth -> env -> ~/.buildly/token) stays identical.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from mcp.types import Tool

from bb_agent_manager.tools.buildly_labs import (
    _api,
    _extract_items,
    _get,
    _get_token,
    _send,
)

if TYPE_CHECKING:
    from bb_agent_manager.config import BuildlySettings


# ---------------------------------------------------------------------------
# Tool schemas
# ---------------------------------------------------------------------------

_ACCESS_TOKEN = {"type": "string", "description": "API token (optional if stored)"}
_PRODUCT_ID = {
    "type": "string",
    "description": "Product id/UUID (uses env BUILDLY_PRODUCT_UUID if omitted)",
}

TOOLS: list[Tool] = [
    Tool(
        name="buildly_get_releases",
        description=(
            "List releases (primary versions) for a product, newest first. "
            "Each release groups one or more builds (micro-releases)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "access_token": _ACCESS_TOKEN,
                "product_id": _PRODUCT_ID,
                "limit": {"type": "integer", "description": "Max results (default 50)"},
                "offset": {"type": "integer", "description": "Pagination offset"},
            },
        },
    ),
    Tool(
        name="buildly_get_release",
        description=(
            "Get one release with its cycle summary (scope, dates, rollup). "
            "Use buildly_get_builds to list the builds inside it."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "access_token": _ACCESS_TOKEN,
                "release_uuid": {"type": "string", "description": "Release UUID"},
            },
            "required": ["release_uuid"],
        },
    ),
    Tool(
        name="buildly_get_builds",
        description=(
            "List builds (micro-releases) for a product, newest first. A build is a "
            "change set that shipped; each is related to a parent release. The most "
            "recent one is flagged is_latest_build=true."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "access_token": _ACCESS_TOKEN,
                "product_id": _PRODUCT_ID,
                "release_uuid": {
                    "type": "string",
                    "description": "Optional: only builds belonging to this release",
                },
                "limit": {"type": "integer", "description": "Max results (default 50)"},
            },
        },
    ),
    Tool(
        name="buildly_get_build",
        description=(
            "Get one build (micro-release) with its GitHub-linked changes: the "
            "commits/PRs and the issues/features/tasks resolved in it."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "access_token": _ACCESS_TOKEN,
                "micro_uuid": {"type": "string", "description": "Micro-release (build) UUID"},
            },
            "required": ["micro_uuid"],
        },
    ),
    Tool(
        name="buildly_next_build_number",
        description=(
            "Return the next build number for a product (current max + 1). Use this "
            "when resolving or shipping work so the build number always increases. "
            "Also reports the current latest build."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "access_token": _ACCESS_TOKEN,
                "product_id": _PRODUCT_ID,
            },
        },
    ),
    Tool(
        name="buildly_assign_release",
        description=(
            "Bulk-assign backlog items (issues/features/tasks) to a release. Use when "
            "resolving work so each resolved item records which release it shipped in."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "access_token": _ACCESS_TOKEN,
                "product_id": _PRODUCT_ID,
                "release_uuid": {"type": "string", "description": "Target release UUID"},
                "item_uuids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "UUIDs of the items to assign to the release",
                },
            },
            "required": ["release_uuid", "item_uuids"],
        },
    ),
    Tool(
        name="buildly_build_report",
        description=(
            "Report what shipped: the issues/features/tasks resolved in a given build "
            "or release, plus how many builds are in the release and which is latest. "
            "Feeds changelogs, boards, and 'what's in the latest build' views."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "access_token": _ACCESS_TOKEN,
                "product_id": _PRODUCT_ID,
                "release_uuid": {"type": "string", "description": "Report on this release"},
                "micro_uuid": {"type": "string", "description": "Report on this build (micro-release)"},
            },
        },
    ),
    Tool(
        name="buildly_sync_github_releases",
        description=(
            "Trigger a GitHub sync so recent commits/PRs are turned into builds "
            "(micro-releases) in Labs. Run after merges to keep build history current."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "access_token": _ACCESS_TOKEN,
                "product_id": _PRODUCT_ID,
            },
        },
    ),
    Tool(
        name="buildly_get_product_repositories",
        description="List the repositories linked to a product in Buildly Labs.",
        inputSchema={
            "type": "object",
            "properties": {
                "access_token": _ACCESS_TOKEN,
                "product_id": _PRODUCT_ID,
            },
        },
    ),
    Tool(
        name="buildly_link_repository",
        description=(
            "Link a repository to a product in Buildly Labs (authoritative binding, "
            "visible in the web UI). Complements the local buildly_remember_project_link."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "access_token": _ACCESS_TOKEN,
                "product_id": _PRODUCT_ID,
                "repo_url": {"type": "string", "description": "Repository URL to link"},
                "name": {"type": "string", "description": "Optional display name for the repo"},
            },
            "required": ["repo_url"],
        },
    ),
    Tool(
        name="buildly_get_design_system",
        description=(
            "Read a product's design system / coding standards from Buildly Labs so "
            "generated code follows the product's conventions."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "access_token": _ACCESS_TOKEN,
                "product_id": _PRODUCT_ID,
            },
        },
    ),
]

TOOL_NAMES: set[str] = {t.name for t in TOOLS}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _product(arguments: dict, settings: "BuildlySettings") -> str | None:
    return arguments.get("product_id") or settings.buildly_product_uuid or None


def _build_release_uuid(build: dict) -> str | None:
    """Extract the parent release UUID from a micro-release, tolerating shapes."""
    rel = build.get("release_uuid") or build.get("release")
    if isinstance(rel, dict):
        return rel.get("uuid") or rel.get("id")
    return rel if isinstance(rel, str) else None


def _build_seq(item: dict) -> int | None:
    """Best-effort extraction of a numeric build sequence from a micro-release."""
    for key in ("build_number", "number", "sequence", "seq", "index", "micro_release_number"):
        val = item.get(key)
        if isinstance(val, int):
            return val
        if isinstance(val, str) and val.isdigit():
            return int(val)
    return None


async def _list_builds(
    api_root: str, token: str | None, product: str | None, release_uuid: str | None, limit: int
) -> tuple[list[dict], dict | None]:
    """Fetch micro-releases (builds), filtered/annotated. Returns (builds, error)."""
    params: dict[str, Any] = {"limit": limit}
    if product:
        params["product_uuid"] = product
    # /rad lives at the site root, not under /api/v1
    site_root = api_root[: -len("/api/v1")] if api_root.endswith("/api/v1") else api_root
    result = await _get(f"{site_root}/rad/api/micro-releases", token, params)
    if "error" in result:
        return [], result
    builds = _extract_items(result.get("data"))
    if release_uuid:
        builds = [b for b in builds if _build_release_uuid(b) == release_uuid]
    # newest first, flag latest
    for i, b in enumerate(builds):
        b["is_latest_build"] = i == 0
    return builds, None


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

async def handle(name: str, arguments: dict, settings: "BuildlySettings") -> dict:
    """Route release/build/repo/standards tool calls."""
    token = _get_token(settings, arguments)
    if token is None:
        return {
            "error": "Not authenticated. Call buildly_login to log in with your "
                     "Buildly account (OAuth), or set LABS_API_TOKEN."
        }

    api = _api(settings.labs_base_url)
    site_root = settings.labs_base_url.rstrip("/")
    product = _product(arguments, settings)

    if name == "buildly_get_releases":
        params: dict[str, Any] = {
            "limit": arguments.get("limit", 50),
            "offset": arguments.get("offset", 0),
        }
        if product:
            params["product_uuid"] = product
        return await _get(f"{api}/releases", token, params)

    if name == "buildly_get_release":
        uuid = arguments["release_uuid"]
        detail = await _get(f"{site_root}/releases/{uuid}", token)
        summary = await _get(f"{site_root}/releases/{uuid}/cycle-summary", token)
        return {
            "status": "ok",
            "release_uuid": uuid,
            "release": detail.get("data", detail.get("error")),
            "cycle_summary": summary.get("data", summary.get("error")),
        }

    if name == "buildly_get_builds":
        builds, err = await _list_builds(
            api, token, product, arguments.get("release_uuid"), arguments.get("limit", 50)
        )
        if err:
            return err
        return {
            "status": "ok",
            "product_id": product,
            "count": len(builds),
            "builds": builds,
        }

    if name == "buildly_get_build":
        uuid = arguments["micro_uuid"]
        return await _get(f"{site_root}/rad/github/{uuid}", token)

    if name == "buildly_next_build_number":
        builds, err = await _list_builds(api, token, product, None, 50)
        if err:
            return err
        seqs = [s for s in (_build_seq(b) for b in builds) if s is not None]
        current = max(seqs) if seqs else 0
        return {
            "status": "ok",
            "product_id": product,
            "current_build_number": current if seqs else None,
            "next_build_number": current + 1,
            "latest_build": builds[0] if builds else None,
            "note": None if seqs else (
                "No numeric build sequence found on micro-releases; next_build_number "
                "starts at 1. Verify the field name once a valid token is available."
            ),
        }

    if name == "buildly_assign_release":
        if not product:
            return {"error": "product_id is required (set BUILDLY_PRODUCT_UUID or pass product_id)."}
        # Labs bulk-assign takes form-encoded finding_uuids + release_uuid.
        payload = {
            "finding_uuids": arguments["item_uuids"],
            "release_uuid": arguments["release_uuid"],
        }
        return await _send(
            f"{site_root}/audit/{product}/bulk/assign-release", "POST", token, payload
        )

    if name == "buildly_build_report":
        return await _build_report(api, site_root, token, product, arguments)

    if name == "buildly_sync_github_releases":
        payload = {"product_uuid": product} if product else {}
        return await _send(f"{site_root}/rad/github/sync", "POST", token, payload)

    if name == "buildly_get_product_repositories":
        if not product:
            return {"error": "product_id is required (set BUILDLY_PRODUCT_UUID or pass product_id)."}
        return await _get(f"{site_root}/products/{product}/repositories", token)

    if name == "buildly_link_repository":
        if not product:
            return {"error": "product_id is required (set BUILDLY_PRODUCT_UUID or pass product_id)."}
        payload = {"repo_url": arguments["repo_url"]}
        if arguments.get("name"):
            payload["name"] = arguments["name"]
        return await _send(
            f"{site_root}/products/{product}/repositories/link", "POST", token, payload
        )

    if name == "buildly_get_design_system":
        if not product:
            return {"error": "product_id is required (set BUILDLY_PRODUCT_UUID or pass product_id)."}
        return await _get(f"{api}/design-system/{product}", token)

    return {"error": f"Unknown release/build tool: {name}"}


async def _build_report(
    api: str, site_root: str, token: str | None, product: str | None, arguments: dict
) -> dict:
    """Compose 'what shipped' for a build or a release."""
    release_uuid = arguments.get("release_uuid")
    micro_uuid = arguments.get("micro_uuid")

    if not release_uuid and not micro_uuid:
        return {"error": "Provide release_uuid or micro_uuid to report on."}

    # Single build report
    if micro_uuid:
        build = await _get(f"{site_root}/rad/github/{micro_uuid}", token)
        if "error" in build:
            return build
        data = build.get("data", {})
        items = _extract_items(data) or (data.get("items") if isinstance(data, dict) else []) or []
        return {
            "status": "ok",
            "scope": "build",
            "micro_uuid": micro_uuid,
            "resolved_items": items,
            "resolved_count": len(items),
            "build": data,
        }

    # Release report: all builds in the release + rollup of resolved items
    builds, err = await _list_builds(api, token, product, release_uuid, 200)
    if err:
        return err
    summary = await _get(f"{site_root}/releases/{release_uuid}/cycle-summary", token)
    return {
        "status": "ok",
        "scope": "release",
        "release_uuid": release_uuid,
        "build_count": len(builds),
        "latest_build": builds[0] if builds else None,
        "builds": builds,
        "cycle_summary": summary.get("data", summary.get("error")),
    }

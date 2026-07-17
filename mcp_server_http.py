#!/usr/bin/env python3
"""
Network (SSE/HTTP) transport for the Buildly MCP Server.

The upstream server (bb_agent_manager.server) speaks stdio, which only works for
a locally-spawned subprocess. This wrapper exposes the SAME server object over
HTTP using the MCP SSE transport so any machine on the LAN (Claude, VS Code,
Codex, etc.) can connect to it as a remote MCP server.

Endpoints:
    GET  /sse        -> SSE stream (MCP client connects here)
    POST /messages/  -> client -> server messages
    GET  /health     -> liveness probe

Run:
    python mcp_server_http.py            # 0.0.0.0:8000
    HOST=0.0.0.0 PORT=8000 python ...    # override
"""
import logging
import os
import sys

import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

from mcp.server.sse import SseServerTransport

from bb_agent_manager.server import server, ALL_TOOLS
from bb_agent_manager.oauth import manager as oauth_manager

logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("buildly-mcp-http")

sse = SseServerTransport("/messages/")


async def handle_sse(request):
    async with sse.connect_sse(request.scope, request.receive, request._send) as (r, w):
        await server.run(r, w, server.create_initialization_options())


async def health(request):
    return JSONResponse({
        "status": "ok",
        "server": "buildly-mcp",
        "transport": "sse",
        "oauth_enabled": oauth_manager.enabled,
        "tools": [t.name for t in ALL_TOOLS],
    })


async def oauth_callback(request):
    """OAuth2 redirect target: exchange the code and bind token to the session."""
    params = request.query_params
    error = params.get("error")
    if error:
        return _html(f"Login failed: {error}", ok=False)
    code, state = params.get("code"), params.get("state")
    if not code or not state:
        return _html("Missing code/state in callback.", ok=False)
    ok, msg = await oauth_manager.exchange_code(code, state)
    if ok:
        return _html("You're logged in to Buildly Labs. You can close this tab "
                     "and return to your editor.")
    return _html(f"Login could not be completed: {msg}", ok=False)


def _html(message: str, ok: bool = True):
    from starlette.responses import HTMLResponse
    color = "#16a34a" if ok else "#dc2626"
    icon = "✓" if ok else "✗"
    return HTMLResponse(
        f"""<!doctype html><html><head><meta charset=utf-8><title>Buildly MCP</title>
        <style>body{{font-family:system-ui;background:#0b1120;color:#e2e8f0;display:grid;
        place-items:center;height:100vh;margin:0}}.c{{text-align:center;padding:2rem}}
        .i{{font-size:3rem;color:{color}}}</style></head>
        <body><div class=c><div class=i>{icon}</div><h2>{message}</h2></div></body></html>""",
        status_code=200 if ok else 400,
    )


app = Starlette(
    debug=False,
    routes=[
        Route("/sse", endpoint=handle_sse),
        Route("/health", endpoint=health),
        Route("/oauth/callback", endpoint=oauth_callback),
        Mount("/messages/", app=sse.handle_post_message),
    ],
)


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    logger.info("Buildly MCP Server (SSE) on http://%s:%d/sse", host, port)
    logger.info("Tools: %s", [t.name for t in ALL_TOOLS])
    uvicorn.run(app, host=host, port=port, log_level="info")

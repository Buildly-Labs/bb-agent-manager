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
        "tools": [t.name for t in ALL_TOOLS],
    })


app = Starlette(
    debug=False,
    routes=[
        Route("/sse", endpoint=handle_sse),
        Route("/health", endpoint=health),
        Mount("/messages/", app=sse.handle_post_message),
    ],
)


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    logger.info("Buildly MCP Server (SSE) on http://%s:%d/sse", host, port)
    logger.info("Tools: %s", [t.name for t in ALL_TOOLS])
    uvicorn.run(app, host=host, port=port, log_level="info")

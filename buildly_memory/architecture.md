# Architecture

## Design principles

1. **Model-agnostic** — MCP server provides tools/context; model lives outside
2. **Markdown-first memory** — human-readable, Git-tracked, no hidden state
3. **stdio primary** — runs cleanly as `python mcp_server_stdio.py`
4. **Graceful degradation** — tools return structured errors if backend unavailable
5. **Simple over clever** — no unnecessary abstractions

## MCP Server layers

```
External MCP Client (Copilot / Claude / Cursor)
        │
        │ stdio (JSON-RPC)
        ▼
mcp_server_stdio.py  ←  thin launcher
        │
        ▼
bb_agent_manager/server.py  ←  tool + resource registry
        │
    ┌───┴────────────────────────────┐
    │                                │
    ▼                                ▼
tools/                          memory/
  devdocs.py                      markdown_memory.py  (default)
  buildly_labs.py                 memory_service.py   (interface)
  buildly_workflow.py             (vector_memory.py)  (future stub)
  buildly_env.py
  memory_tools.py
        │
        ▼
Buildly Labs API  /  local filesystem  /  git
```

## Memory architecture

Two layers:

| Layer | Location | Purpose |
|-------|----------|---------|
| Project memory | `buildly_memory/` | Current project context, decisions, patterns |
| Org memory | `~/.buildly/memory/` | Cross-project patterns, promoted decisions |

Session notes → `buildly_memory/sessions/`  
Decisions → `buildly_memory/decisions/`  
Patterns → appended to `buildly_memory/conventions.md`

## Auth flow

Token resolution (highest priority first):
1. `access_token` argument in tool call
2. `LABS_API_TOKEN` environment variable
3. `~/.buildly/token` file (written by `buildly_login`)

## Deployment modes

| Mode | How | When |
|------|-----|------|
| stdio MCP | `python mcp_server_stdio.py` | Primary — Copilot, Claude, Cursor |
| Console script | `buildly-mcp` | After `pip install -e .` |
| Docker microservice | `docker-compose up` | CI / shared team server (legacy) |

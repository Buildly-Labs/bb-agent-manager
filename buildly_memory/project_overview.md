# Project Overview

## What this project does

**Buildly MCP Server** (`bb-agent-manager`) is a model-agnostic context, memory, and workflow
layer for AI coding agents. It connects AI assistants to the Buildly Labs platform and keeps
project memory persistent across sessions.

It does **not** host or select AI models. Model choice belongs to the external MCP client
(GitHub Copilot, Claude Desktop, Copilot CLI + Ollama, etc.).

## Key capabilities

- **Buildly Labs integration** — issues, products, features, milestones, sprints
- **Persistent memory** — Markdown-based, Git-tracked, cross-session
- **DevDocs automation** — structured documentation for every meaningful change
- **Workflow tools** — Definition of Done checks, release summaries
- **Environment context** — git state, env config, active product

## Tech stack

- Python 3.11+
- MCP Python SDK (`mcp>=1.0.0`)
- FastAPI (legacy microservice mode — not the primary mode)
- httpx for Buildly Labs API calls
- Markdown files for memory persistence

## Repository structure

```
mcp_server_stdio.py          ← thin launcher (run this)
bb_agent_manager/
  server.py                  ← MCP server core (tools + resources)
  config.py                  ← BuildlySettings from env vars
  mcp_server_stdio.py        ← console script entry point
  tools/
    devdocs.py               ← devdocs_* tools
    buildly_labs.py          ← buildly_* API tools
    buildly_workflow.py      ← DoD, summaries, releases
    buildly_env.py           ← environment + git context
    memory_tools.py          ← memory_* tools + MCP resources
  memory/
    memory_service.py        ← abstract interface
    markdown_memory.py       ← default file-based implementation
buildly_memory/              ← THIS folder (persistent project memory)
devdocs/                     ← developer documentation
```

## Current status

Active development. MCP stdio mode is the primary mode.

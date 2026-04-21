# Current Focus

## Active work

**Buildly MCP Server refactor** — transforming bb-agent-manager into a clean,
model-agnostic MCP server with persistent memory and Buildly workflow tools.

### What's done

- [x] Simplified config (removed LLM settings)
- [x] Core MCP server (`bb_agent_manager/server.py`)
- [x] DevDocs tools (refactored)
- [x] Buildly Labs tools (login, products, issues, features, work context)
- [x] Workflow tools (DoD check, devdocs summary, release summary)
- [x] Environment tools (env context, repo context)
- [x] Memory system (MarkdownMemory + abstract interface)
- [x] Memory MCP tools (10 tools)
- [x] MCP Resources (memory:// URIs)
- [x] buildly_memory/ populated with project starter content
- [x] Console script (`buildly-mcp`)

### What's next

- [ ] Tests for new tool modules
- [ ] Vector memory stub (`bb_agent_manager/memory/vector_memory.py`)
- [ ] GitHub PR tool update (use BuildlySettings not legacy AgentSettings)
- [ ] CI workflow update

## Blocked by

Nothing currently.

## Next up

Tests and documentation polish.

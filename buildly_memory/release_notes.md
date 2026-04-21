# Release Notes

## Unreleased — Buildly MCP Server v0.2.0

### Added

- `bb_agent_manager/server.py` — clean MCP server core
- `bb_agent_manager/mcp_server_stdio.py` — console script entry point
- `bb_agent_manager/tools/buildly_labs.py` — unified Buildly Labs tools
- `bb_agent_manager/tools/buildly_workflow.py` — workflow automation tools
- `bb_agent_manager/tools/buildly_env.py` — environment + repo context tools
- `bb_agent_manager/tools/memory_tools.py` — 10 memory management tools
- `bb_agent_manager/memory/` — memory service abstraction + MarkdownMemory
- `buildly_memory/` — persistent project memory folder
- `buildly-mcp` console script via `pip install -e .`
- MCP Resources: `memory://current-project/*`, `memory://buildly/standards`

### Changed

- `bb_agent_manager/config.py` — removed LLM provider settings; added Buildly context fields
- `bb_agent_manager/tools/devdocs.py` — clean rewrite, structured JSON returns
- `mcp_server_stdio.py` — now a thin launcher (logic in `bb_agent_manager/server.py`)
- `.env.example` — removed model settings; added `BUILDLY_*` variables
- `pyproject.toml` — added `buildly-mcp` console script; trimmed dependencies

### Architecture change

This release formalises the model-agnostic architecture.
The MCP server no longer selects or routes LLM providers — that is entirely
the responsibility of the external MCP client.

---

## v0.1.0 — Initial release

Initial bb-agent-manager with FastAPI microservice, LLM routing (Gemini/Claude/OpenAI/Ollama),
and basic devdocs/Labs tools.

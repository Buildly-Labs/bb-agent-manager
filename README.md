# Buildly MCP Server

**A model-agnostic context, memory, and workflow layer for AI coding agents.**

Connect GitHub Copilot, Claude, Cursor, or any MCP-compatible client to Buildly Labs —
with persistent project memory, devdocs automation, and workflow enforcement.

---

## What it does

| Capability | Description |
|-----------|-------------|
| **Buildly Labs** | Issues, products, features, milestones, work context |
| **Persistent Memory** | Markdown-based project memory across sessions |
| **DevDocs** | Automated developer documentation management |
| **Workflow** | Definition of Done checks, release summaries |
| **Environment** | Git state, env config, active product context |

## What it does NOT do

- Does **not** host or serve AI models
- Does **not** select Claude vs DeepSeek vs GPT — that is the client's job
- Does **not** auto-merge PRs or close issues without human approval

Model selection is entirely the responsibility of the external MCP client.

---

## Architecture

```
External MCP Client
  ├── GitHub Copilot (Claude / GPT-4o / etc.)
  ├── Copilot CLI + Ollama (DeepSeek, Llama, etc.)
  └── Claude Desktop / Cursor / any MCP client
          │
          │ stdio (MCP JSON-RPC)
          ▼
  mcp_server_stdio.py  ←── thin launcher
          │
          ▼
  bb_agent_manager/server.py
          │
    ┌─────┴──────────────────────────────┐
    │                                     │
    ▼                                     ▼
  Tools (20+)                        Memory (buildly_memory/)
    devdocs_*                            project_overview.md
    buildly_labs_*                       architecture.md
    buildly_workflow_*                   current_focus.md
    buildly_env_*                        conventions.md
    memory_*                             decisions/
                                         sessions/
```

---

## Buildly Memory

The memory system is the primary feature that makes this server valuable across sessions.

### Layer 1 — Markdown memory (default)

```
buildly_memory/
  project_overview.md    ← what this project is
  architecture.md        ← how it's built
  environments.md        ← environment config
  conventions.md         ← coding standards + patterns
  current_focus.md       ← what's being worked on now
  release_notes.md       ← version history
  decisions/             ← one file per architecture decision
  features/              ← one file per feature/epic
  issues/                ← tracked issues
  sessions/              ← session notes
```

Everything is human-readable and Git-tracked. No hidden state.

### Layer 2 — Org memory (cross-project)

Promoted patterns and decisions live at `~/.buildly/memory/{project}/`.
Use `memory_promote_to_org_memory` to share across projects.

### Why this matters

Without memory, every AI session starts from zero. With Buildly Memory:
- The AI knows the project architecture without re-reading the codebase
- Decisions are captured and searchable
- Sessions build on each other
- Patterns propagate across projects

---

## Quick start

### 1. Install

```bash
git clone https://github.com/buildly-release/bb-agent-manager.git
cd bb-agent-manager
pip install -e .
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env — set LABS_BASE_URL, LABS_API_TOKEN, BUILDLY_PRODUCT_UUID
```

### 3. Run

```bash
python mcp_server_stdio.py
# or
buildly-mcp
```

### 4. Connect your client

See usage modes below.

---

## Usage modes

### Mode 1 — GitHub Copilot + MCP

Add to `.vscode/mcp.json` (or global MCP config):

```json
{
  "servers": {
    "buildly": {
      "type": "stdio",
      "command": "python",
      "args": ["${workspaceFolder}/mcp_server_stdio.py"],
      "env": {
        "LABS_BASE_URL": "https://labs-api.buildly.io",
        "BUILDLY_PRODUCT_UUID": "your-product-uuid"
      }
    }
  }
}
```

Or using the installed script:

```json
{
  "servers": {
    "buildly": {
      "type": "stdio",
      "command": "buildly-mcp"
    }
  }
}
```

### Mode 2 — Copilot CLI + Ollama (local DeepSeek)

Ollama runs local models at `http://localhost:11434` with an OpenAI-compatible endpoint.

```bash
# Start Ollama with DeepSeek
ollama run deepseek-coder-v2:16b

# Connect Copilot CLI (BYOK mode)
gh copilot config set model ollama/deepseek-coder-v2:16b
gh copilot config set endpoint http://localhost:11434/v1
```

The MCP server stays the same — only the model changes in the client.

### Mode 3 — Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "buildly": {
      "command": "python",
      "args": ["/absolute/path/to/mcp_server_stdio.py"],
      "env": {
        "LABS_BASE_URL": "https://labs-api.buildly.io",
        "LABS_API_TOKEN": "your-token"
      }
    }
  }
}
```

---

## Tool reference

### DevDocs tools

| Tool | Description |
|------|-------------|
| `devdocs_write` | Write or update a documentation file |
| `devdocs_read` | Read a documentation file |
| `devdocs_list` | List all documentation files |

### Buildly Labs tools

| Tool | Description |
|------|-------------|
| `buildly_login` | Authenticate with Buildly Labs |
| `buildly_test_connection` | Test API connectivity |
| `buildly_get_products` | List products |
| `buildly_get_issues` | Fetch issues (filterable by product/status) |
| `buildly_get_features` | Fetch features/epics |
| `buildly_get_current_work_context` | Combined snapshot: active issues + milestones |
| `buildly_update_issue_status` | Update an issue's status |

### Workflow tools

| Tool | Description |
|------|-------------|
| `buildly_definition_of_done_check` | Run a DoD checklist |
| `buildly_create_devdocs_summary` | Write a structured devdocs entry |
| `buildly_release_summary` | Summarise recent changes |

### Environment tools

| Tool | Description |
|------|-------------|
| `buildly_get_environment_context` | Current env name, product, org config |
| `buildly_get_repo_context` | Git branch, recent commits, dirty state |

### Memory tools

| Tool | Description |
|------|-------------|
| `memory_get_project_summary` | Overview + focus + architecture from memory |
| `memory_search_current_project` | Full-text search in `buildly_memory/` |
| `memory_search_related_projects` | Search org-level memory (`~/.buildly/memory/`) |
| `memory_write_session_note` | Persist a session note |
| `memory_capture_decision` | Record an architectural decision |
| `memory_capture_pattern` | Append a reusable pattern to conventions |
| `memory_get_recent_work` | Recent session notes |
| `memory_get_environment_context` | Read `buildly_memory/environments.md` |
| `memory_promote_to_org_memory` | Share memory to `~/.buildly/memory/` |
| `memory_rebuild_index` | Regenerate `buildly_memory/INDEX.md` |

### MCP Resources

| URI | Content |
|-----|---------|
| `memory://current-project/overview` | `buildly_memory/project_overview.md` |
| `memory://current-project/architecture` | `buildly_memory/architecture.md` |
| `memory://current-project/current-focus` | `buildly_memory/current_focus.md` |
| `memory://buildly/standards` | `buildly_memory/conventions.md` |
| `memory://related-projects/{name}` | Org memory for a related project |

---

## The Buildly Way

1. **Check context before coding** — always start with `buildly_get_current_work_context`
2. **Document as you go** — call `buildly_create_devdocs_summary` after meaningful changes
3. **Capture decisions** — use `memory_capture_decision` for architecture choices
4. **Small changes** — one concern per PR, release-sized increments
5. **Human in the loop** — draft PRs, no auto-merges
6. **Never commit secrets** — credentials stay in env vars

---

## Development

```bash
# Install with dev dependencies
pip install -e .
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v

# Start the MCP server
python mcp_server_stdio.py
```

## Project structure

```
mcp_server_stdio.py              ← thin launcher (use this)
bb_agent_manager/
  server.py                      ← MCP server core
  config.py                      ← BuildlySettings
  mcp_server_stdio.py            ← console script entry point
  tools/
    devdocs.py                   ← devdocs_* tools
    buildly_labs.py              ← Buildly Labs API tools
    buildly_workflow.py          ← workflow tools
    buildly_env.py               ← environment + repo tools
    memory_tools.py              ← memory_* tools + resources
  memory/
    memory_service.py            ← abstract interface
    markdown_memory.py           ← file-based implementation
buildly_memory/                  ← persistent project memory (Git-tracked)
devdocs/                         ← developer documentation
.env.example                     ← environment config template
.vscode/mcp.json                 ← VS Code MCP config example
```

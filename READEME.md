# BB Agent Manager

## Overview

**bb-agent-manager** is an AI-powered development assistant designed as a pluggable module for the BabbleBeaver platform. It provides intelligent automation for Buildly Labs development workflows, integrating LLM capabilities with project management and documentation tools.

## What It Does

The agent serves as an intelligent bridge between code changes, project management, and documentation by:

1. **AI Chat Interface** - Provides conversational AI powered by Gemini or Ollama
2. **Development Automation** - Executes specialized tools for common dev tasks
3. **Buildly Labs Integration** - Automatically syncs tasks and project management
4. **Smart Documentation** - Auto-updates `/devdocs` with change summaries and reuse notes
5. **Git Operations** - Handles PR creation and repository management

## Key Features

### Multi-LLM Support
- **Gemini Integration** - Google's AI models for production use
- **Ollama Support** - Local/self-hosted models for development
- **Provider Switching** - Runtime selection between AI providers

### Development Tools
- **DevDocs Tool** - Maintains developer documentation with automated summaries
- **Labs Sync Tool** - Creates/updates tasks in Buildly Labs linked to repos/PRs  
- **Git Operations** - Automated pull request creation and management

### API Endpoints
- `POST /agent/chat` - Conversational AI interface
- `GET /agent/mcp/tools` - Discover available development tools
- `POST /agent/mcp/invoke` - Direct tool execution

## Typical Workflow

A developer can interact with the agent naturally:

```
User: "Refactor the user service, update devdocs, and create a Labs task"

Agent: 
1. Analyzes the refactoring request using LLM reasoning
2. Calls update_devdocs tool to document changes  
3. Calls labs_upsert_task to create/update task in Buildly Labs
4. Creates PR via create_pr tool
5. Returns summary of actions taken
```

## Project Structure

```
bb-agent-manager/
├─ pyproject.toml
├─ README.md
├─ devdocs/                # Developer documentation
├─ .github/
│  └─ prompts/            # AI assistant prompts
├─ bb_agent_manager/
│  ├─ __init__.py
│  ├─ config.py           # Environment configuration
│  ├─ plugin.py           # BabbleBeaver registration
│  ├─ router.py           # FastAPI routes for /agent
│  ├─ orchestrator.py     # Agent orchestration & tool dispatch
│  ├─ llm/
│  │  ├─ __init__.py
│  │  ├─ base.py          # LLM provider abstraction
│  │  ├─ gemini.py        # Google Gemini integration
│  │  ├─ ollama.py        # Ollama local model support
│  │  └─ router.py        # Provider selection logic
│  ├─ tools/
│  │  ├─ __init__.py
│  │  ├─ devdocs.py       # Documentation automation
│  │  ├─ labs_sync.py     # Buildly Labs integration
│  │  ├─ git_ops.py       # Git/GitHub operations
│  │  └─ test_ops.py      # Test automation tools
│  └─ mcp/
│     ├─ __init__.py
│     └─ server.py        # MCP-compatible tool server
└─ tests/
   └─ test_smoke.py
```


## Option A — entry-point auto-load (preferred)

Add your private index/credentials to BabbleBeaver’s environment (so pip can read your private repo).

Install in BabbleBeaver’s runtime image:

pip install bb-agent-manager @ git+ssh://git@github.com/your-org/bb-agent-manager.git


In BabbleBeaver startup (where the FastAPI app is created), add this generic loader:

# in babblebeaver/main.py (or wherever app is constructed)
import pkg_resources

for ep in pkg_resources.iter_entry_points(group="babblebeaver.modules"):
    try:
        register_fn = ep.load()
        register_fn(app, {})  # can pass merged settings dict if you keep a central config
    except Exception as e:
        print(f"[BB] Failed to load module {ep.name}: {e}")


No changes to the agent module are required—register mounts /agent and /agent/mcp.

## Option B — explicit import

If you don’t want dynamic entry-points:

# babblebeaver/main.py
from bb_agent_manager import register as register_bb_agent
register_bb_agent(app, {})

## 💻 IDE Integration (VS Code Chat Assistant)

Use bb-agent-manager as a chat assistant in VS Code, similar to GitHub Copilot Chat:

### Quick Start
```bash
# Install chat client dependencies
pip install -r requirements-dev.txt

# Start the agent service
python test_server.py

# Start interactive chat (like Copilot Chat)
python chat_client.py --provider ollama
```

### Chat Features
- 🔍 **Code Review**: Analyze code quality and suggest improvements
- 📝 **Documentation**: Auto-generate docs using devdocs tools
- 🧪 **Test Generation**: Create comprehensive test suites
- 🔧 **Debugging**: Help identify and fix issues
- 📋 **Git Workflow**: Manage version control with best practices

### VS Code Integration Options

1. **REST Client Extension** (Recommended)
   ```bash
   # Install REST Client extension in VS Code
   # Use examples/api_requests.http for quick testing
   ```

2. **Thunder Client Extension**
   ```bash
   # Install Thunder Client extension
   # Import provided collection for BB Agent APIs
   ```

3. **Interactive Chat Client**
   ```bash
   # Full-featured chat interface with syntax highlighting
   python chat_client.py --provider ollama --model deepseek-coder:6.7b
   ```

### Example Usage
```http
POST http://localhost:8001/agent/chat
Content-Type: application/json

{
  "provider": "ollama",
  "messages": [
    {
      "role": "system",
      "content": "You are a Buildly development assistant."
    },
    {
      "role": "user", 
      "content": "Review this function and suggest improvements: def process(data): return [x*2 for x in data if x > 0]"
    }
  ]
}
```

📖 **See [IDE_INTEGRATION_GUIDE.md](IDE_INTEGRATION_GUIDE.md) for complete setup instructions**

11) Env & Docker compose (example)

Add to BabbleBeaver’s .env (or secrets):

LABS_BASE_URL=https://labs.buildly.io/api
LABS_API_TOKEN=...
BB_AM_DEFAULT_PROVIDER=gemini
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-1.5-pro
OLLAMA_BASE_URL=http://ollama:11434/v1
OLLAMA_MODEL=llama3.1:8b
BB_AM_MOUNT_PATH=/agent
GITHUB_TOKEN=ghp_...


Compose snippet (add Ollama if you want local models):

services:
  babblebeaver:
    build: .
    env_file: .env
    volumes:
      - ./:/app
    ports:
      - "8000:8000"
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama:/root/.ollama
volumes:
  ollama: {}

12) How an IDE/Agent would call it

Chat (from any UI) POST to /agent/chat:

{
  "provider": "gemini",
  "messages": [
    {"role":"system","content":"You are the Buildly Agent. Use tools to update devdocs & Labs."},
    {"role":"user","content":"Refactor user service; update devdocs and create a Labs task."}
  ]
}


MCP-like tooling:

GET /agent/mcp/tools → discover available tools

POST /agent/mcp/invoke { "name": "update_devdocs", "arguments": {...} }

13) Where to wire Buildly-specific behavior

Replace the stubs in tools/ with:

git_ops.py using GitHub App (least-privilege) to branch/commit/PR,

devdocs.py writing to /devdocs/* and maintaining an index with timestamps,

labs_sync.py pointing at your real Labs endpoints for tasks, PR linkage, release notes, etc.

If BabbleBeaver already has a module registry or DI container, you can have register() receive shared services (e.g., repo access) via settings_dict.

14) Security notes (quick wins)

Enforce a repo allow-list and path allow-list inside tools (e.g., only devdocs/, src/, tests/).

Keep model provider choice behind env vars per deployment.

Use a GitHub App instead of a PAT where possible; restrict to needed repos.

That’s it. This slots into BabbleBeaver as a clean, private module with:

a single register(app, settings) entrypoint,

FastAPI routes for chat and tool invocation,

a provider router to flip between Gemini and Ollama, and

Buildly-opinionated tools for /devdocs + Labs sync you can harden over time.


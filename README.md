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

## Installation & Setup

### Option A: Entry-point Auto-load (Recommended)

Add your private repository credentials to BabbleBeaver's environment:

```bash
pip install bb-agent-manager @ git+ssh://git@github.com/Buildly-Labs/bb-agent-manager.git
```

In BabbleBeaver startup, add the generic module loader:

```python
# in babblebeaver/main.py
import pkg_resources

for ep in pkg_resources.iter_entry_points(group="babblebeaver.modules"):
    try:
        register_fn = ep.load()
        register_fn(app, {})
    except Exception as e:
        print(f"[BB] Failed to load module {ep.name}: {e}")
```

### Option B: Explicit Import

```python
# babblebeaver/main.py  
from bb_agent_manager import register as register_bb_agent
register_bb_agent(app, {})
```

## Configuration

Required environment variables:

```bash
# Buildly Labs Integration
LABS_BASE_URL=https://labs.buildly.io/api
LABS_API_TOKEN=your_labs_token

# AI Provider Settings
BB_AM_DEFAULT_PROVIDER=gemini  # or "ollama"
GEMINI_API_KEY=your_gemini_key
GEMINI_MODEL=gemini-1.5-pro

# Ollama (for local models)
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama3.1:8b

# GitHub Integration
GITHUB_TOKEN=ghp_your_github_token

# Plugin Configuration
BB_AM_MOUNT_PATH=/agent
```

## Docker Compose Example

```yaml
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
```

## API Usage

### Chat Interface
```bash
POST /agent/chat
{
  "provider": "gemini",
  "messages": [
    {"role":"system","content":"You are the Buildly Agent. Use tools to update devdocs & Labs."},
    {"role":"user","content":"Refactor user service; update devdocs and create a Labs task."}
  ]
}
```

### Tool Discovery & Invocation
```bash
# Discover available tools
GET /agent/mcp/tools

# Invoke specific tool
POST /agent/mcp/invoke 
{
  "name": "update_devdocs", 
  "arguments": {
    "files": ["src/user_service.py"],
    "summary": "Refactored user authentication logic",
    "component_reuse_notes": "Extract auth middleware for reuse"
  }
}
```

## Development Standards

This project follows Buildly's development practices:

- **Documentation**: All changes documented in `/devdocs` with summaries and reuse notes
- **API Documentation**: OpenAPI/Swagger specs for all endpoints  
- **Code Standards**: Python type hints, async/await patterns, Pydantic models
- **Testing**: Comprehensive test coverage with pytest
- **Architecture**: Clean separation of concerns, dependency injection via FastAPI
- **Security**: Repository allow-lists, environment-based configuration, GitHub App authentication

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes following Buildly coding standards
4. Update `/devdocs` with change summary and component reuse notes
5. Add/update tests as needed
6. Submit pull request with clear description

## License

Private - Buildly Labs Internal Use

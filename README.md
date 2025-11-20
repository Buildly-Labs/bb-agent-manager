# Buildly Labs MCP Server

## Overview

**buildly-agent** is a Model Context Protocol (MCP) server that enables AI assistants (like Claude Desktop, Claude Code, Cursor) to interact with the Buildly Labs platform. It provides tools for documentation management and Buildly Labs API integration.

## Quick Start - AI Integration

### Claude Desktop (Recommended)

1. **Start the Docker container:**
   ```bash
   docker-compose up -d
   ```

2. **Add the MCP server:**
   ```bash
   claude mcp add --transport http buildly-agent http://localhost:8001/agent
   ```

3. **Restart Claude Desktop** and run `/mcp` to verify connection

4. **Use in chat:**
   - "Login to Buildly Labs"
   - "Show me my issues"
   - "List my products"
   - "Write API docs to devdocs/api.md"

### Cursor IDE

1. **Start the Docker container:**
   ```bash
   docker-compose up -d
   ```

2. **Create MCP config** at `~/.cursor/mcp.json`:
   ```json
   {
     "mcpServers": {
       "buildly-agent": {
         "command": "node",
         "args": ["-e", "const http = require('http'); process.stdin.pipe(http.request({host:'localhost',port:8001,path:'/agent/mcp/invoke',method:'POST',headers:{'Content-Type':'application/json'}}, res => res.pipe(process.stdout)))"]
       }
     }
   }
   ```

3. **Restart Cursor** and use AI chat to invoke tools

### VS Code with GitHub Copilot

1. **Start the Docker container:**
   ```bash
   docker-compose up -d
   ```

2. **Create MCP config** at `~/.config/Code/User/globalStorage/github.copilot-chat/mcp.json`:
   ```json
   {
     "mcpServers": {
       "buildly-agent": {
         "command": "node",
         "args": ["-e", "const http = require('http'); process.stdin.pipe(http.request({host:'localhost',port:8001,path:'/agent/mcp/invoke',method:'POST',headers:{'Content-Type':'application/json'}}, res => res.pipe(process.stdout)))"]
       }
     }
   }
   ```

3. **Reload VS Code window** (Cmd/Ctrl+Shift+P → "Reload Window")

4. **Use in Copilot Chat:** Type `@buildly-agent` to invoke tools

**Note:** VS Code Copilot has limited MCP support. For best experience, use Claude Desktop or Cursor.

## Available Tools

- **devdocs_write** - Write documentation to devdocs folder
- **devdocs_read** - Read documentation files
- **devdocs_list** - List all documentation files
- **buildly_login** - Authenticate with Buildly Labs
- **buildly_test_connection** - Test Buildly Labs API connection
- **buildly_get_issues** - Fetch your Buildly issues
- **buildly_get_products** - Fetch your Buildly products ## Development

### Testing Standalone
```bash
# Run test server
python test_server.py

# Run test suite
python test_client.py

# Test with Docker
docker-compose -f docker-compose.test.yml up
```

### Integration Testing
```bash
# Test plugin mode
pip install -e .
# Add to BabbleBeaver and test

# Test microservice mode
docker-compose -f docker-compose.prod.yml up -d
curl http://localhost:8001/agent/mcp/tools
```

This project follows Buildly's development standards:

- **Documentation**: All changes documented in `/devdocs` with summaries and reuse notes
- **API Documentation**: OpenAPI/Swagger specs for all endpoints  
- **Code Standards**: Python type hints, async/await patterns, Pydantic models
- **Testing**: Comprehensive test coverage with pytest
- **Architecture**: Clean separation of concerns, dependency injection via FastAPI
- **Security**: Repository allow-lists, environment-based configuration, GitHub App authentication
- **Deployment**: Both plugin and microservice patterns supportednagement and documentation tools.

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

BB Agent Manager supports two deployment modes:

### 🔌 Plugin Mode (Embedded)
**Best for**: Development, simple deployments, single-node setups

#### Option A: Entry-point Auto-load (Recommended)

```bash
# Install in BabbleBeaver's environment
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

#### Option B: Explicit Import

```python
# babblebeaver/main.py  
from bb_agent_manager import register as register_bb_agent
register_bb_agent(app, {})
```

### 🚀 Microservice Mode (Independent)
**Best for**: Production, scaling, cloud deployments, isolation

#### Quick Start with Docker Compose

```bash
# Clone and setup
git clone https://github.com/Buildly-Labs/bb-agent-manager.git
cd bb-agent-manager
cp .env.example .env
# Edit .env with your API keys

# Deploy as microservices
docker-compose -f docker-compose.prod.yml up -d
```

**Access Points:**
- BabbleBeaver: `http://localhost:8000`
- BB Agent Manager: `http://localhost:8001`
- Combined via Nginx: `http://localhost` (optional)

#### Production Deployment

```bash
# Build production image
docker build -f Dockerfile.prod -t bb-agent-manager:prod .

# Run independently
docker run -d \
  --name bb-agent-manager \
  -p 8001:8000 \
  -e GEMINI_API_KEY=your_key \
  -e LABS_API_TOKEN=your_token \
  --restart unless-stopped \
  bb-agent-manager:prod
```

> 📖 **See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for comprehensive deployment options including Kubernetes, monitoring, and BabbleBeaver integration patterns.**

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

### Development/Testing
```yaml
# docker-compose.test.yml
services:
  bb-agent-test:
    build: .
    ports:
      - "8001:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - LABS_API_TOKEN=${LABS_API_TOKEN}
    volumes:
      - ./test_server.py:/app/main.py

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
```

### Production Microservices
```yaml
# docker-compose.prod.yml - Full setup with BabbleBeaver
services:
  babblebeaver:
    build: ./babblebeaver
    ports:
      - "8000:8000"
    depends_on:
      - bb-agent-manager

  bb-agent-manager:
    build:
      dockerfile: Dockerfile.prod
    ports:
      - "8001:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - LABS_API_TOKEN=${LABS_API_TOKEN}
    restart: unless-stopped

  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama_data:/root/.ollama
```

Run with: `docker-compose -f docker-compose.prod.yml up -d`

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
6. Test in both plugin and microservice modes
7. Submit pull request with clear description

### Development Resources
- **Integration Guide**: [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) - Detailed setup and testing
- **Deployment Guide**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Production deployment patterns
- **AI Guidelines**: [.github/prompts/buildly-guidelines.md](.github/prompts/buildly-guidelines.md) - Buildly development practices

## License

Private - Buildly Labs Internal Use

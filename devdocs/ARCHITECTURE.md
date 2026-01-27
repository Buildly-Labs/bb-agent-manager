# BB Agent Manager - Architecture Review

**Date:** January 27, 2026  
**Project:** Buildly Agent Manager (bb-agent-manager)  
**Version:** 0.1.0  

---

## Executive Summary

The **Buildly Agent Manager** is an AI-powered microservice that integrates AI assistants (Claude Desktop, Cursor, VS Code Copilot) with the Buildly Labs platform using the Model Context Protocol (MCP). It provides:

- **Multi-LLM Support**: Claude, OpenAI, Google Gemini, and local Ollama models
- **MCP Server**: Standard-compliant MCP implementation for IDE integration
- **Development Tools**: Documentation management, Git operations, and task synchronization
- **Modular Architecture**: Plugin-based system for easy extensibility

---

## 1. Architecture Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    IDE / AI Assistant                        │
│          (Claude Desktop, Cursor, VS Code Copilot)          │
└──────────────────────┬──────────────────────────────────────┘
                       │ MCP Protocol (JSON-RPC)
┌──────────────────────▼──────────────────────────────────────┐
│              BB Agent Manager (FastAPI)                      │
├──────────┬──────────┬──────────┬──────────┬──────────────────┤
│  Router  │   Chat   │  MCP     │ Config   │   Orchestrator   │
│  Endpoint│  Endpoint│  Server  │ Manager  │                  │
└──────────┴──────────┴──────────┴──────────┴──────────────────┘
                       │
        ┌──────────────┼──────────────┬──────────────┐
        │              │              │              │
   ┌────▼────┐   ┌────▼────┐  ┌────▼────┐  ┌────▼────┐
   │  LLM    │   │  Tools  │  │External │  │  Local  │
   │ Router  │   │ Handler │  │  APIs   │  │ Storage │
   └────┬────┘   └────┬────┘  └────┬────┘  └────┬────┘
        │             │            │             │
  ┌─────┴──────┬──────┴──────┬─────┴──────┬─────┴──────┐
  │             │              │            │            │
┌─▼──┐  ┌─────▼───┐  ┌──────▼──┐  ┌──────▼──┐  ┌────▼─┐
│GPT │  │ Gemini  │  │ Claude  │  │ Ollama  │  │ Docs │
└────┘  └─────────┘  └─────────┘  └─────────┘  └──────┘

    Git Ops, DevDocs, Labs Sync, Test Ops
```

### 1.2 Core Components

| Component | Purpose | Language | Status |
|-----------|---------|----------|--------|
| **FastAPI Server** | HTTP API & request routing | Python | Production |
| **MCP Server** | Model Context Protocol implementation | Python | Production |
| **LLM Router** | Multi-provider LLM abstraction | Python | Production |
| **Tools Handler** | Document, Git, API sync tools | Python | Active |
| **Plugin System** | Integration with BabbleBeaver | Python | Active |

---

## 2. Directory Structure & Components

### 2.1 Root Level Files

```
bb-agent/
├── pyproject.toml              # Package metadata & dependencies
├── requirements.txt            # Runtime dependencies
├── requirements-dev.txt        # Development dependencies
├── Dockerfile / docker-compose # Container orchestration
├── ops/
│   └── startup.sh             # Application startup/control script
├── scripts/
│   ├── test_server.py         # Standalone development server
│   ├── chat_client.py         # CLI chat client
│   ├── test_client.py         # HTTP test client
│   ├── simple_test_server.py  # Simple test server
│   └── test_mcp_docker.sh     # MCP Docker tests
├── buildly_mcp_server.py      # MCP stdio server (official SDK)
├── buildly_workflow.py        # Workflow definitions
└── .env.example               # Configuration template
```

### 2.2 BB Agent Manager Module Structure

```
bb_agent_manager/
├── __init__.py
├── config.py                  # Settings management (Pydantic)
├── main.py                    # FastAPI application
├── plugin.py                  # BabbleBeaver plugin registration
├── router.py                  # Chat endpoint routing
├── orchestrator.py            # Agent execution orchestrator
│
├── llm/                       # LLM Provider Abstraction
│   ├── base.py               # LLMProvider base class
│   ├── claude.py             # Anthropic Claude provider
│   ├── gemini.py             # Google Gemini provider
│   ├── openai_provider.py    # OpenAI GPT provider
│   ├── ollama.py             # Local Ollama provider
│   └── router.py             # Provider selection logic
│
├── mcp/                       # Model Context Protocol
│   ├── __init__.py
│   └── server.py             # MCP JSON-RPC endpoint
│
└── tools/                     # Tool implementations
    ├── __init__.py
    ├── devdocs.py            # Documentation management
    ├── git_ops.py            # GitHub PR/issue management
    ├── buildly_auth.py       # Buildly Labs authentication
    ├── labs_sync.py          # Task synchronization
    └── test_ops.py           # Testing operations
```

### 2.3 Supporting Directories

```
.github/
├── prompts/
│   ├── buildly-guidelines.md  # AI guidelines for development
│   └── TODO.md                # Prompt engineering tasks
│
└── workflows/
    ├── auto-close-issues.yml  # GitHub Actions workflow
    └── code-review.yml        # Automated code quality checks

devdocs/                        # Developer documentation
├── ARCHITECTURE.md            # This document
├── TODO.md                    # Development tasks & roadmap
├── index.md                   # Change log
├── INTEGRATION_GUIDE.md
├── DEPLOYMENT_GUIDE.md
└── [other docs...]

tests/                          # Test files
├── test_tools.py
├── test_providers.py
└── test_integration.py

examples/                       # Example requests
└── api_requests.http
```

---

## 3. Core Functionality

### 3.1 Configuration Management (`config.py`)

Uses **Pydantic BaseModel** for type-safe configuration:

```python
class AgentSettings(BaseModel):
    # Buildly Labs
    labs_base_url: str = "https://labs.buildly.io/api"
    labs_api_token: str = os.getenv("LABS_API_TOKEN", "")
    
    # LLM Providers
    default_provider: str = "gemini"  # Can be: gemini, claude, openai, ollama
    
    # Provider-specific configs
    gemini_api_key: str
    anthropic_api_key: str
    openai_api_key: str
    ollama_base_url: str = "http://localhost:11434/v1"
    
    # GitHub & Git Operations
    github_token: str
    github_repo: str
    
    # Feature Flags
    require_human_review: bool = True
    auto_close_issues: bool = True
    create_draft_prs: bool = True
```

**Key Features:**
- Environment variable support (12-factor app)
- Validation via Pydantic
- Provider-agnostic design
- Feature toggles for safety

### 3.2 LLM Provider Abstraction (`llm/`)

**Base Interface:**
```python
class LLMProvider(ABC):
    async def chat(self, messages: List[Dict[str, str]], 
                   tools: List[Dict], tool_callback: Callable) -> Dict[str, Any]
```

**Supported Providers:**

1. **Claude** (`claude.py`)
   - Models: Claude 3.5 Sonnet, 3 Opus, 3 Sonnet, 3 Haiku
   - Tools: Native tool_use
   - SDK: `anthropic>=0.34.0`

2. **OpenAI** (`openai_provider.py`)
   - Models: GPT-4, GPT-4o, GPT-3.5, o1
   - Tools: function_call
   - SDK: `openai>=1.0.0`

3. **Google Gemini** (`gemini.py`)
   - Models: Gemini 1.5 Pro, 1.5 Flash
   - Tools: function_calling
   - SDK: `google-generativeai>=0.3.0`

4. **Ollama** (`ollama.py`)
   - Local models via Ollama
   - OpenAI-compatible API
   - SDK: `httpx` (HTTP-only)

**Router Logic:**
```python
def get_provider(settings: AgentSettings, hint: Optional[str]) -> LLMProvider:
    # Returns appropriate provider based on hint or settings.default_provider
```

### 3.3 MCP Server Implementation (`mcp/server.py`)

**Entry Points:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/message` | POST | Main MCP JSON-RPC endpoint |
| `/tools` | GET | List available tools |
| `/invoke` | POST | Execute a tool |

**Tools Exposed:**

1. **devdocs_write** - Create/update documentation
2. **devdocs_read** - Read documentation
3. **devdocs_list** - List all docs
4. **buildly_login** - Authenticate with Labs
5. **buildly_test_connection** - Test API connection
6. **buildly_get_issues** - Fetch issues
7. **buildly_get_products** - Fetch products

**MCP Protocol:** JSON-RPC 2.0 over HTTP

---

## 4. Strengths

✅ **Multi-LLM Support**
- Provider abstraction allows easy swapping
- Supports Claude, OpenAI, Gemini, Ollama
- Can route based on availability/cost

✅ **MCP Compliance**
- Uses official MCP Python SDK
- JSON-RPC 2.0 protocol
- Works with Claude Desktop, Cursor, VS Code

✅ **Modular Tools**
- Clear tool definitions with JSON schemas
- Extensible tool system
- Documentation, Git, API, Testing operations

✅ **Development Workflow Integration**
- GitHub automation (auto-close issues)
- Code quality checks (Black, Pylint, MyPy)
- DevDocs for tracking changes

✅ **Plugin Architecture**
- BabbleBeaver integration ready
- Easy mounting in FastAPI apps
- Configuration-driven

✅ **Type Safety**
- Pydantic models for all inputs
- Type hints throughout
- MyPy checking in CI/CD

---

## 5. Areas for Improvement

⚠️ **Testing**
- No comprehensive unit tests
- No integration tests
- Recommendation: Implement pytest suite with >80% coverage

⚠️ **Error Handling**
- Limited error recovery
- No retry logic for API calls
- No circuit breaker pattern

⚠️ **Logging & Monitoring**
- Basic logging only
- No distributed tracing
- No metrics/observability

⚠️ **Tool Implementation Status**
- `labs_sync.py` and `test_ops.py` are incomplete
- Git operations need GitHub App support
- Buildly API integration incomplete

⚠️ **Security**
- No rate limiting
- No input validation on tool parameters
- No audit logging for sensitive operations

---

## 6. Operational Scripts

### `ops/startup.sh`

The startup script provides unified application control:

```bash
# Start application on port 8000
./ops/startup.sh start

# Stop running application
./ops/startup.sh stop

# Restart application
./ops/startup.sh restart

# Check status
./ops/startup.sh status
```

**Features:**
- Automatic venv setup and activation
- Requirements installation with caching
- FastAPI server launch on port 8000
- Process management (start/stop/restart)
- Works in both Docker and local environments

---

## 7. Configuration Quick Reference

### Environment Variables

```bash
# Buildly Labs
LABS_BASE_URL=https://labs.buildly.io/api
LABS_API_TOKEN=<your-token>

# LLM Providers
BB_AM_DEFAULT_PROVIDER=claude  # claude, openai, gemini, ollama

# Claude
ANTHROPIC_API_KEY=<your-key>
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# OpenAI
OPENAI_API_KEY=<your-key>
OPENAI_MODEL=gpt-4o

# Gemini
GEMINI_API_KEY=<your-key>
GEMINI_MODEL=gemini-1.5-pro

# Ollama (local)
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama3.1:8b

# GitHub
GITHUB_TOKEN=<your-token>
GITHUB_REPO=owner/repo

# Features
BB_AM_REQUIRE_HUMAN_REVIEW=true
BB_AM_AUTO_CLOSE_ISSUES=true
BB_AM_CREATE_DRAFT_PRS=true

# Service
BB_AM_MOUNT_PATH=/agent
```

---

## 8. Conclusion

The **Buildly Agent Manager** is a well-designed, modular microservice that effectively bridges AI assistants with the Buildly platform. Key strengths include clean architecture, provider abstraction, MCP compliance, and comprehensive automation.

The primary areas for development are completing the test suite, finishing tool implementations, and adding robustness features (retry logic, error handling, monitoring).

---

**Document Version:** 1.0  
**Last Updated:** January 27, 2026  
**Next Review:** February 27, 2026

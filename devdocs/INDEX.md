# BB Agent Manager - Complete Documentation Index

**Last Updated:** January 27, 2026  
**Project:** Buildly Agent Manager (bb-agent-manager)  
**Version:** 0.1.0  

---

## 📚 Documentation Structure

This project follows a organized documentation approach with clear separation of concerns:

### Main Documentation (`devdocs/`)
- [**ARCHITECTURE.md**](ARCHITECTURE.md) - Complete system architecture and design
- [**TODO.md**](TODO.md) - Development roadmap and task tracking
- [**index.md**](index.md) - Change log and updates
- [**INTEGRATION_GUIDE.md**](INTEGRATION_GUIDE.md) - IDE integration setup (Claude, Cursor, VS Code)
- [**DEPLOYMENT_GUIDE.md**](DEPLOYMENT_GUIDE.md) - Production deployment instructions
- [**ENVIRONMENT_SETUP.md**](ENVIRONMENT_SETUP.md) - Development environment configuration
- [**IDE_INTEGRATION_GUIDE.md**](IDE_INTEGRATION_GUIDE.md) - IDE-specific setup
- [**QUICK_START.md**](QUICK_START.md) - Quick start guide
- [**TEST_RESULTS.md**](TEST_RESULTS.md) - Test execution results

### Operations & Scripts
- [**ops/README.md**](../ops/README.md) - Application management and lifecycle (`startup.sh`)
- [**scripts/README.md**](../scripts/README.md) - Development and testing utilities

### Tests & Quality
- [**tests/README.md**](../tests/README.md) - Test structure and running tests
- [**tests/conftest.py**](../tests/conftest.py) - Pytest fixtures and configuration

### Development Standards
- [**.github/prompts/buildly-guidelines.md**](../.github/prompts/buildly-guidelines.md) - AI development guidelines
- [**pyproject.toml**](../pyproject.toml) - Project metadata and dependencies
- [**requirements.txt**](../requirements.txt) - Runtime dependencies

---

## 🚀 Quick Navigation

### For Getting Started
1. Read [QUICK_START.md](QUICK_START.md)
2. Set up environment with [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md)
3. Run `./ops/startup.sh start`
4. Check [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) to connect your IDE

### For Architecture Understanding
1. Start with [ARCHITECTURE.md](ARCHITECTURE.md) overview
2. Review component descriptions
3. Study design patterns and data flows
4. Check [TODO.md](TODO.md) for development areas

### For Running Tests
1. See [tests/README.md](../tests/README.md)
2. Run `pytest tests/`
3. Check coverage with `pytest --cov`

### For Deployment
1. Follow [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
2. Configure environment variables
3. Use Docker Compose files
4. Monitor health checks

### For IDE Integration
1. Choose your IDE in [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
2. Configure MCP connection
3. Test with provided examples

---

## 📁 Directory Structure Reference

```
bb-agent/
├── 📄 README.md                    # Project overview
├── 📄 pyproject.toml               # Package metadata
├── 📄 requirements.txt             # Dependencies
│
├── 📂 devdocs/                     # Developer documentation
│   ├── ARCHITECTURE.md             # System design (START HERE)
│   ├── TODO.md                     # Development roadmap
│   ├── QUICK_START.md              # Quick start guide
│   ├── ENVIRONMENT_SETUP.md        # Environment config
│   ├── INTEGRATION_GUIDE.md        # IDE integration
│   ├── DEPLOYMENT_GUIDE.md         # Production deployment
│   ├── IDE_INTEGRATION_GUIDE.md    # IDE-specific guides
│   ├── TEST_RESULTS.md             # Test outcomes
│   ├── index.md                    # Change log
│   └── 📋 Documentation Index.md   # THIS FILE
│
├── 📂 ops/                         # Operations & Management
│   ├── README.md                   # Operations guide
│   └── startup.sh                  # App lifecycle (start/stop/restart)
│
├── 📂 scripts/                     # Development & Test Scripts
│   ├── README.md                   # Scripts guide
│   ├── test_server.py              # FastAPI test server
│   ├── chat_client.py              # CLI chat client
│   ├── test_client.py              # HTTP test client
│   └── [other utilities]
│
├── 📂 tests/                       # Unit & Integration Tests
│   ├── README.md                   # Testing guide
│   ├── conftest.py                 # Pytest configuration
│   ├── test_tools.py               # Tools tests
│   ├── test_providers.py           # Provider tests
│   └── test_integration.py         # Integration tests
│
├── 📂 bb_agent_manager/            # Main Application
│   ├── config.py                   # Configuration
│   ├── main.py                     # FastAPI app
│   ├── router.py                   # Chat endpoints
│   ├── orchestrator.py             # Agent orchestration
│   ├── llm/                        # LLM providers (Claude, GPT, Gemini, Ollama)
│   ├── mcp/                        # MCP server implementation
│   └── tools/                      # Tool implementations
│
├── 📂 .github/                     # GitHub configuration
│   ├── prompts/
│   │   ├── buildly-guidelines.md   # Development standards
│   │   └── TODO.md                 # Prompt engineering tasks
│   └── workflows/
│       ├── auto-close-issues.yml   # GitHub automation
│       └── code-review.yml         # Code quality checks
│
├── 📂 examples/                    # Example usage
│   └── api_requests.http           # Example API calls
│
├── 📂 devdocs/                     # (generated) Docs folder
│
├── Dockerfile                      # Development image
├── Dockerfile.prod                 # Production image
├── docker-compose.yml              # Development deployment
├── docker-compose.test.yml         # Test deployment
├── docker-compose.prod.yml         # Production deployment
│
└── .env.example                    # Environment template
```

---

## 🎯 Common Tasks

### Start Development
```bash
# Option 1: Using startup script
./ops/startup.sh start

# Option 2: Manual
source .venv/bin/activate
pip install -r requirements.txt
python scripts/test_server.py
```

### Run Tests
```bash
pytest tests/                              # All tests
pytest tests/test_tools.py -v              # Specific file
pytest tests/ --cov=bb_agent_manager       # With coverage
```

### Connect IDE
See [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
- **Claude Desktop**: Recommended
- **Cursor IDE**: Fully supported
- **VS Code + Copilot**: Limited support

### Deploy to Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```
See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

### View Application Logs
```bash
./ops/startup.sh logs        # Last 50 lines
tail -f logs/app.log         # Follow logs
```

### Check Application Status
```bash
./ops/startup.sh status
curl http://localhost:8000/health
```

---

## 📊 Project Status

| Component | Status | Coverage | Notes |
|-----------|--------|----------|-------|
| **Architecture** | ✅ Complete | 100% | Well-designed, production-ready |
| **Core Features** | ✅ Complete | ~80% | Multi-LLM, MCP, tools functional |
| **Testing** | ⚠️ Partial | ~20% | Needs comprehensive test suite |
| **Documentation** | ✅ Complete | 95% | Comprehensive coverage |
| **Operations** | ✅ Complete | 100% | startup.sh handles all scenarios |
| **Deployment** | ✅ Complete | 100% | Docker & docker-compose ready |

---

## 🔧 Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Framework** | FastAPI | >=0.104.0 |
| **Server** | Uvicorn | >=0.24.0 |
| **Data Validation** | Pydantic | >=2.4.0 |
| **HTTP Client** | httpx | >=0.25.0 |
| **LLM: Claude** | anthropic | >=0.34.0 |
| **LLM: OpenAI** | openai | >=1.0.0 |
| **LLM: Gemini** | google-generativeai | >=0.3.0 |
| **Testing** | pytest | >=7.4.0 |
| **Python** | 3.11+ | Recommended 3.12 |

---

## 🚨 Important Links

- **Repository**: [buildly/bb-agent](https://github.com/buildly/bb-agent)
- **Issues**: [GitHub Issues](https://github.com/buildly/bb-agent/issues)
- **MCP Spec**: [Model Context Protocol](https://spec.modelcontextprotocol.io/)
- **FastAPI Docs**: [FastAPI Documentation](https://fastapi.tiangolo.com/)
- **Buildly Labs**: [labs.buildly.io](https://labs.buildly.io)

---

## 📝 Document Versions

| Document | Version | Last Updated |
|----------|---------|--------------|
| ARCHITECTURE.md | 1.0 | Jan 27, 2026 |
| TODO.md | 1.0 | Jan 27, 2026 |
| Documentation Index.md | 1.0 | Jan 27, 2026 |
| QUICK_START.md | 1.0 | Jan 27, 2026 |
| INTEGRATION_GUIDE.md | 1.0 | Jan 27, 2026 |
| DEPLOYMENT_GUIDE.md | 1.0 | Jan 27, 2026 |

---

## 🤝 Contributing

Before contributing, please:
1. Read [.github/prompts/buildly-guidelines.md](../.github/prompts/buildly-guidelines.md)
2. Check [TODO.md](TODO.md) for priority items
3. Write tests for new features
4. Update documentation
5. Run code quality checks: `black`, `isort`, `pylint`, `mypy`

---

## 📞 Support & Questions

- **For architecture questions**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **For setup issues**: See [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md)
- **For deployment questions**: See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **For IDE integration**: See [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
- **For development roadmap**: See [TODO.md](TODO.md)

---

**Project Owner**: Buildly Labs  
**Last Review**: January 27, 2026  
**Next Review**: February 27, 2026

**Quick Start**: Begin with [QUICK_START.md](QUICK_START.md) or [ARCHITECTURE.md](ARCHITECTURE.md)

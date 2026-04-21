# Scripts Directory

This directory contains development and testing scripts for the BB Agent Manager.

## Test & Development Servers

- **test_server.py** - FastAPI test server with plugin registration (port 8001)
- **simple_test_server.py** - Simplified test server for quick testing
- **mcp_server_stdio.py** - MCP stdio bridge for testing MCP protocol

## Chat & Client Tools

- **chat_client.py** - CLI chat client for testing agent responses
- **test_client.py** - HTTP client for testing API endpoints

## Testing & Workflows

- **test_issues.py** - Test script for issue handling
- **start_agent.py** - Agent startup script for orchestration

## Utility Scripts

- **test_mcp_docker.sh** - Docker MCP protocol testing script
- **mcp_bridge.sh** - MCP bridge for stdio communication
- **claude_bridge.sh** - Claude-specific MCP bridge
- **mcp_stdio_bridge.sh** - Stdio bridge for MCP communication

## Usage

### Running the Test Server
```bash
python scripts/test_server.py
# Server runs on http://localhost:8001
# Docs available at http://localhost:8001/docs
```

### Testing with CLI Chat Client
```bash
python scripts/chat_client.py --provider claude
# Interactive chat interface with agent
```

### Running HTTP Tests
```bash
python scripts/test_client.py
# Tests various endpoints
```

### Testing MCP Protocol
```bash
bash scripts/test_mcp_docker.sh
# Tests MCP protocol in Docker environment
```

## Configuration

All scripts respect environment variables from `.env` file:
- `ANTHROPIC_API_KEY` - Claude API key
- `OPENAI_API_KEY` - OpenAI API key  
- `GEMINI_API_KEY` - Google Gemini API key
- `OLLAMA_BASE_URL` - Ollama local server

## See Also

- [Architecture Documentation](../devdocs/ARCHITECTURE.md)
- [Development Roadmap](../devdocs/TODO.md)
- [Main README](../README.md)

# Installation Guide

## Quick Start

### 1. Install Dependencies

```bash
# Install the MCP SDK and dependencies
pip install -e .
```

Or manually:
```bash
pip install mcp httpx
```

### 2. Configure Your AI Client

#### For Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%/Claude/claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "buildly-agent": {
      "command": "python3",
      "args": ["/absolute/path/to/buildly_mcp_server.py"],
      "env": {
        "LABS_BASE_URL": "https://labs-api.buildly.io"
      }
    }
  }
}
```

#### For Claude Code (VS Code Extension)

Edit `~/.claude.json` in your project directory:

```json
{
  "mcpServers": {
    "buildly-agent": {
      "command": "python3",
      "args": ["/absolute/path/to/buildly_mcp_server.py"],
      "env": {
        "LABS_BASE_URL": "https://labs-api.buildly.io"
      }
    }
  }
}
```

#### For Cursor

Edit `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "buildly-agent": {
      "command": "python3",
      "args": ["/absolute/path/to/buildly_mcp_server.py"],
      "env": {
        "LABS_BASE_URL": "https://labs-api.buildly.io"
      }
    }
  }
}
```

### 3. Restart Your AI Client

After updating the configuration, restart Claude Desktop, VS Code, or Cursor to load the MCP server.

### 4. Test the Connection

In Claude chat, try:
- "List the available tools from buildly-agent"
- "Login to Buildly Labs with my credentials"
- "Show me my issues"

## Available Tools

### Documentation Tools
- `devdocs_write` - Write/update documentation files
- `devdocs_read` - Read documentation files
- `devdocs_list` - List all documentation files

### Buildly Labs Tools
- `buildly_test_connection` - Test API connection
- `buildly_login` - Authenticate with Buildly Labs
- `buildly_get_issues` - Fetch your issues
- `buildly_get_products` - Fetch your products

## How It Works

1. **MCP Protocol**: This server implements the official Model Context Protocol
2. **stdio Transport**: Communication happens via standard input/output
3. **No HTTP/OAuth**: Unlike web services, MCP servers are launched as subprocesses
4. **AI Integration**: Your AI client (Claude, Cursor) launches the server automatically

## Troubleshooting

### Server not appearing in AI client
- Check that the absolute path in config is correct
- Verify Python 3.11+ is available: `python3 --version`
- Check logs in your AI client's developer console

### Import errors
- Run `pip install mcp httpx`
- Ensure you're using Python 3.11 or higher

### Connection to Buildly Labs fails
- Verify `LABS_BASE_URL` is set correctly in config
- Test manually: `curl https://labs-api.buildly.io`

## For Developers

### Running in Docker

You can also run the MCP server in a Docker container:

```bash
# Build and run
docker-compose up -d

# The container runs the MCP server via stdio
# You can connect to it by configuring your AI client to use docker exec:
```

Example config for Claude Desktop (using Docker):
```json
{
  "mcpServers": {
    "buildly-agent": {
      "command": "docker",
      "args": ["exec", "-i", "buildly-agent-manager", "python3", "buildly_mcp_server.py"],
      "env": {
        "LABS_BASE_URL": "https://labs-api.buildly.io"
      }
    }
  }
}
```

### Testing the Server Locally

```bash
# The server expects JSON-RPC messages via stdin
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python3 buildly_mcp_server.py
```

### Development

The server is a single Python file (`buildly_mcp_server.py`) that:
- Uses the official MCP Python SDK
- Implements `list_tools()` and `call_tool()` handlers
- Runs on stdio (not HTTP)

### Why This Approach?

**This is the standard way to build MCP servers.** Previous attempts using HTTP endpoints, OAuth, and SSE were incorrect. MCP clients like Claude Desktop expect:

1. A subprocess they can launch
2. Communication via stdin/stdout
3. JSON-RPC 2.0 messages
4. The official MCP protocol

The MCP SDK handles all the protocol details for us.

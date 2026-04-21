#!/bin/bash
# Test the MCP server running in Docker

# First, send initialize request
echo "Testing MCP server in Docker..."
echo ""

# Initialize
echo "1. Sending initialize request..."
cat <<EOF | docker exec -i buildly-agent-manager python3 buildly_mcp_server.py
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test-client","version":"1.0.0"}}}
{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}
EOF

echo ""
echo "Done! The server is ready to use."
echo ""
echo "To use with Claude Desktop, add this to your config:"
echo ""
echo '{
  "mcpServers": {
    "buildly-agent": {
      "command": "docker",
      "args": ["exec", "-i", "buildly-agent-manager", "python3", "buildly_mcp_server.py"],
      "env": {
        "LABS_BASE_URL": "https://labs-api.buildly.io"
      }
    }
  }
}'

#!/bin/bash
# MCP Bridge for Claude Desktop
# Translates stdio MCP protocol to HTTP API calls

API_BASE="http://localhost:8001/agent/mcp"

# Read JSON-RPC requests from stdin and forward to HTTP API
while IFS= read -r line; do
    # Parse the JSON-RPC request
    method=$(echo "$line" | jq -r '.method // empty')
    
    case "$method" in
        "tools/list")
            # Get tools list
            curl -s "${API_BASE}/tools"
            ;;
        "tools/call")
            # Invoke tool
            params=$(echo "$line" | jq -c '.params')
            curl -s -X POST "${API_BASE}/invoke" \
                -H "Content-Type: application/json" \
                -d "$params"
            ;;
        *)
            # Unknown method
            echo '{"error":{"code":-32601,"message":"Method not found"}}'
            ;;
    esac
done

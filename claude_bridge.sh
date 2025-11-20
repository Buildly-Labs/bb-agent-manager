#!/bin/bash
# Simple MCP bridge for Claude Desktop
# Forwards stdio to HTTP API

API_URL="http://localhost:8001/agent"

# Simple proxy: read from stdin, send to API, output to stdout
while IFS= read -r line; do
    # Forward to health check for now (proof of concept)
    curl -s "${API_URL}/../health"
done

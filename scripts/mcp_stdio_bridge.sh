#!/bin/bash
# MCP stdio bridge - translates stdin/stdout to HTTP

while IFS= read -r line; do
    # Forward JSON-RPC request to HTTP endpoint
    response=$(curl -s -X POST http://localhost:8001/agent/message \
        -H "Content-Type: application/json" \
        -d "$line")
    
    # Output response to stdout
    echo "$response"
done

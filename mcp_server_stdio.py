#!/usr/bin/env python3
"""
Buildly MCP Server — thin launcher.

Run directly:
    python mcp_server_stdio.py

Or use the installed console script:
    buildly-mcp

All logic lives in bb_agent_manager/server.py.
This file exists so MCP clients can point at a single root-level file.
"""
from bb_agent_manager.server import main

if __name__ == "__main__":
    main()

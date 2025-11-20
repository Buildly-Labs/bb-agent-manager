#!/usr/bin/env python3
"""
Proper MCP Server for Buildly Agent using official MCP SDK
This runs as a stdio server that Claude Code can connect to directly
"""

import asyncio
import os
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import httpx

# Initialize MCP server
app = Server("buildly-agent")

# Tool definitions
TOOLS = [
    Tool(
        name="devdocs_write",
        description="Write or update documentation file in devdocs folder",
        inputSchema={
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "Name of the file (e.g., 'api.md')"},
                "content": {"type": "string", "description": "Content to write"}
            },
            "required": ["filename", "content"]
        }
    ),
    Tool(
        name="devdocs_read",
        description="Read a documentation file from devdocs folder",
        inputSchema={
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "Name of the file to read"}
            },
            "required": ["filename"]
        }
    ),
    Tool(
        name="devdocs_list",
        description="List all documentation files in devdocs folder",
        inputSchema={
            "type": "object",
            "properties": {}
        }
    ),
    Tool(
        name="buildly_login",
        description="Login to Buildly Labs platform",
        inputSchema={
            "type": "object",
            "properties": {
                "username": {"type": "string", "description": "Buildly Labs username or email"},
                "password": {"type": "string", "description": "Buildly Labs password"}
            },
            "required": ["username", "password"]
        }
    ),
    Tool(
        name="buildly_test_connection",
        description="Test connection to Buildly Labs API",
        inputSchema={
            "type": "object",
            "properties": {}
        }
    ),
    Tool(
        name="buildly_get_issues",
        description="Get issues from Buildly Labs for your organization",
        inputSchema={
            "type": "object",
            "properties": {
                "access_token": {"type": "string", "description": "Access token from login"}
            },
            "required": ["access_token"]
        }
    ),
    Tool(
        name="buildly_get_products",
        description="Get products from Buildly Labs for your organization",
        inputSchema={
            "type": "object",
            "properties": {
                "access_token": {"type": "string", "description": "Access token from login"}
            },
            "required": ["access_token"]
        }
    )
]

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return TOOLS

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a tool"""
    
    if name == "devdocs_write":
        filename = arguments["filename"]
        content = arguments["content"]
        
        os.makedirs("devdocs", exist_ok=True)
        filepath = os.path.join("devdocs", filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        return [TextContent(
            type="text",
            text=f"Successfully wrote {len(content)} bytes to {filename}"
        )]
    
    elif name == "devdocs_read":
        filename = arguments["filename"]
        filepath = os.path.join("devdocs", filename)
        
        if not os.path.exists(filepath):
            return [TextContent(
                type="text",
                text=f"Error: File not found: {filename}"
            )]
        
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        return [TextContent(type="text", text=content)]
    
    elif name == "devdocs_list":
        os.makedirs("devdocs", exist_ok=True)
        files = [f for f in os.listdir("devdocs") if os.path.isfile(os.path.join("devdocs", f))]
        
        return [TextContent(
            type="text",
            text=f"Found {len(files)} files:\n" + "\n".join(f"- {f}" for f in files)
        )]
    
    elif name == "buildly_test_connection":
        labs_url = os.getenv("LABS_BASE_URL", "https://labs-api.buildly.io")
        async with httpx.AsyncClient() as client:
            response = await client.get(labs_url, timeout=10.0, follow_redirects=True)
            return [TextContent(
                type="text",
                text=f"Connection successful! Status: {response.status_code}"
            )]
    
    elif name == "buildly_login":
        username = arguments["username"]
        password = arguments["password"]
        labs_url = os.getenv("LABS_BASE_URL", "https://labs-api.buildly.io")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{labs_url}/token/",
                json={"username": username, "password": password},
                timeout=10.0
            )
            if response.status_code in [200, 201]:
                data = response.json()
                return [TextContent(
                    type="text",
                    text=f"Login successful!\nAccess Token: {data.get('access')}\nRefresh Token: {data.get('refresh')}"
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"Login failed: {response.status_code} - {response.text}"
                )]
    
    elif name == "buildly_get_issues":
        access_token = arguments["access_token"]
        labs_url = os.getenv("LABS_BASE_URL", "https://labs-api.buildly.io")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{labs_url}/release/issue/",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10.0
            )
            if response.status_code == 200:
                issues = response.json()
                issue_list = "\n".join([f"- [{i.get('id')}] {i.get('title', 'Untitled')}" for i in issues[:10]])
                return [TextContent(
                    type="text",
                    text=f"Found {len(issues)} issues:\n{issue_list}"
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"Failed to fetch issues: {response.status_code}"
                )]
    
    elif name == "buildly_get_products":
        access_token = arguments["access_token"]
        labs_url = os.getenv("LABS_BASE_URL", "https://labs-api.buildly.io")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{labs_url}/product/product/",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10.0
            )
            if response.status_code == 200:
                products = response.json()
                product_list = "\n".join([f"- {p.get('name', 'Unnamed')}" for p in products])
                return [TextContent(
                    type="text",
                    text=f"Found {len(products)} products:\n{product_list}"
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"Failed to fetch products: {response.status_code}"
                )]
    
    return [TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())

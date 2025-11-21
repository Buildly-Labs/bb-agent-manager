#!/usr/bin/env python3
"""
Proper MCP Server for Buildly Agent using the official MCP Python SDK
This is the standard way to build an MCP server that works with Claude Desktop, Claude Code, etc.
"""

import asyncio
import os
import sys
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import httpx

# Initialize MCP server
server = Server("buildly-agent")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
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
            description="Authenticate with Buildly Labs and get access tokens. Use this first before calling other buildly tools. Returns JWT access and refresh tokens.",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {"type": "string", "description": "Buildly Labs username"},
                    "password": {"type": "string", "description": "Buildly Labs password"}
                },
                "required": ["username", "password"]
            }
        ),
        Tool(
            name="buildly_test_connection",
            description="Test connection to Buildly Labs API to verify it's reachable",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="buildly_get_issues",
            description="Fetch all issues from Buildly Labs for the authenticated user. Returns a formatted list of issues with IDs and titles. Use the access_token from buildly_login.",
            inputSchema={
                "type": "object",
                "properties": {
                    "access_token": {"type": "string", "description": "JWT access token from buildly_login"}
                },
                "required": ["access_token"]
            }
        ),
        Tool(
            name="buildly_get_products",
            description="Fetch all products from Buildly Labs for the authenticated user. Returns a formatted list of product names. Use the access_token from buildly_login.",
            inputSchema={
                "type": "object",
                "properties": {
                    "access_token": {"type": "string", "description": "JWT access token from buildly_login"}
                },
                "required": ["access_token"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a tool and return results"""
    
    try:
        if name == "devdocs_write":
            filename = arguments["filename"]
            content = arguments["content"]
            
            os.makedirs("devdocs", exist_ok=True)
            filepath = os.path.join("devdocs", filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            
            return [TextContent(
                type="text",
                text=f"✓ Successfully wrote {len(content)} bytes to {filename}"
            )]
        
        elif name == "devdocs_read":
            filename = arguments["filename"]
            filepath = os.path.join("devdocs", filename)
            
            if not os.path.exists(filepath):
                return [TextContent(
                    type="text",
                    text=f"✗ Error: File not found: {filename}"
                )]
            
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            return [TextContent(type="text", text=content)]
        
        elif name == "devdocs_list":
            os.makedirs("devdocs", exist_ok=True)
            files = [f for f in os.listdir("devdocs") if os.path.isfile(os.path.join("devdocs", f))]
            
            if not files:
                return [TextContent(type="text", text="No documentation files found")]
            
            return [TextContent(
                type="text",
                text=f"📁 Found {len(files)} files:\n" + "\n".join(f"  • {f}" for f in sorted(files))
            )]
        
        elif name == "buildly_test_connection":
            labs_url = os.getenv("LABS_BASE_URL", "https://labs-api.buildly.io")
            async with httpx.AsyncClient() as client:
                response = await client.get(labs_url, timeout=10.0, follow_redirects=True)
                return [TextContent(
                    type="text",
                    text=f"✓ Connected to Buildly Labs API\nStatus: {response.status_code}\nURL: {labs_url}"
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
                    access = data.get('access', '')
                    refresh = data.get('refresh', '')
                    
                    return [TextContent(
                        type="text",
                        text=f"✓ Login successful!\n\n🔑 Access Token:\n{access}\n\n🔄 Refresh Token:\n{refresh}\n\nℹ️ Use the access token for subsequent API calls."
                    )]
                else:
                    return [TextContent(
                        type="text",
                        text=f"✗ Login failed\nStatus: {response.status_code}\nError: {response.text}"
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
                    
                    if not issues:
                        return [TextContent(type="text", text="No issues found")]
                    
                    issue_list = "\n".join([
                        f"  #{i.get('id')} - {i.get('title', 'Untitled')}" 
                        for i in issues[:20]
                    ])
                    
                    return [TextContent(
                        type="text",
                        text=f"📋 Found {len(issues)} issues:\n\n{issue_list}\n\n{f'(Showing first 20 of {len(issues)})' if len(issues) > 20 else ''}"
                    )]
                else:
                    return [TextContent(
                        type="text",
                        text=f"✗ Failed to fetch issues\nStatus: {response.status_code}\nError: {response.text}"
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
                    
                    if not products:
                        return [TextContent(type="text", text="No products found")]
                    
                    product_list = "\n".join([
                        f"  • {p.get('name', 'Unnamed Product')}" 
                        for p in products
                    ])
                    
                    return [TextContent(
                        type="text",
                        text=f"📦 Found {len(products)} products:\n\n{product_list}"
                    )]
                else:
                    return [TextContent(
                        type="text",
                        text=f"✗ Failed to fetch products\nStatus: {response.status_code}\nError: {response.text}"
                    )]
        
        else:
            return [TextContent(
                type="text",
                text=f"✗ Unknown tool: {name}"
            )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"✗ Error executing {name}: {str(e)}"
        )]

async def main():
    """Run the MCP server on stdio"""
    # This is the standard way MCP servers run - via stdio
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    # Run the server
    asyncio.run(main())

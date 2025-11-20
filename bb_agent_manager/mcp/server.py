from fastapi import FastAPI, APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from bb_agent_manager.config import AgentSettings
import os
import json
import asyncio

app = FastAPI(title="Buildly Agent Manager", version="0.1.0")
mcp = APIRouter(prefix="/agent")

# MCP JSON-RPC Models
class JsonRpcRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[int | str] = None
    method: str
    params: Optional[Dict[str, Any]] = None

class JsonRpcResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[int | str] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None

def get_settings() -> AgentSettings:
    return AgentSettings()

# MCP JSON-RPC endpoint (main protocol entry point)
@mcp.post("/message")
async def mcp_message(request: JsonRpcRequest, settings: AgentSettings = Depends(get_settings)):
    """Handle MCP JSON-RPC requests"""
    
    if request.method == "tools/list":
        # Return list of available tools
        tools = [
            {
                "name": "devdocs_write",
                "description": "Write or update documentation file in devdocs folder",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string", "description": "Name of the file (e.g., 'api.md')"},
                        "content": {"type": "string", "description": "Content to write"}
                    },
                    "required": ["filename", "content"]
                }
            },
            {
                "name": "devdocs_read",
                "description": "Read a documentation file from devdocs folder",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string", "description": "Name of the file to read"}
                    },
                    "required": ["filename"]
                }
            },
            {
                "name": "devdocs_list",
                "description": "List all documentation files in devdocs folder",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "buildly_login",
                "description": "Login to Buildly Labs platform",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "username": {"type": "string", "description": "Buildly Labs username or email"},
                        "password": {"type": "string", "description": "Buildly Labs password"}
                    },
                    "required": ["username", "password"]
                }
            },
            {
                "name": "buildly_test_connection",
                "description": "Test connection to Buildly Labs API",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "buildly_get_issues",
                "description": "Get issues from Buildly Labs for your organization",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "access_token": {"type": "string", "description": "Access token from login"}
                    },
                    "required": ["access_token"]
                }
            },
            {
                "name": "buildly_get_products",
                "description": "Get products from Buildly Labs for your organization",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "access_token": {"type": "string", "description": "Access token from login"}
                    },
                    "required": ["access_token"]
                }
            }
        ]
        
        return JsonRpcResponse(
            id=request.id,
            result={"tools": tools}
        )
    
    elif request.method == "tools/call":
        # Execute a tool
        params = request.params or {}
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        result = await execute_tool(tool_name, arguments, settings)
        
        return JsonRpcResponse(
            id=request.id,
            result=result
        )
    
    elif request.method == "initialize":
        # MCP initialization
        return JsonRpcResponse(
            id=request.id,
            result={
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "buildly-agent",
                    "version": "0.1.0"
                }
            }
        )
    
    else:
        return JsonRpcResponse(
            id=request.id,
            error={
                "code": -32601,
                "message": f"Method not found: {request.method}"
            }
        )

async def execute_tool(tool_name: str, arguments: Dict[str, Any], settings: AgentSettings):
    """Execute a tool and return results"""
    try:
        if tool_name == "devdocs_write":
            filename = arguments.get("filename")
            content = arguments.get("content")
            
            os.makedirs("devdocs", exist_ok=True)
            filepath = os.path.join("devdocs", filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            return {
                "content": [{
                    "type": "text",
                    "text": f"Successfully wrote {len(content)} bytes to {filename}"
                }]
            }
        
        elif tool_name == "devdocs_read":
            filename = arguments.get("filename")
            filepath = os.path.join("devdocs", filename)
            
            if not os.path.exists(filepath):
                return {
                    "content": [{
                        "type": "text",
                        "text": f"Error: File not found: {filename}"
                    }],
                    "isError": True
                }
            
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            return {
                "content": [{
                    "type": "text",
                    "text": content
                }]
            }
        
        elif tool_name == "devdocs_list":
            os.makedirs("devdocs", exist_ok=True)
            files = [f for f in os.listdir("devdocs") if os.path.isfile(os.path.join("devdocs", f))]
            return {
                "content": [{
                    "type": "text",
                    "text": f"Found {len(files)} files:\n" + "\n".join(f"- {f}" for f in files)
                }]
            }
        
        elif tool_name == "buildly_test_connection":
            import httpx
            labs_url = settings.labs_base_url or "https://labs-api.buildly.io"
            async with httpx.AsyncClient() as client:
                response = await client.get(labs_url, timeout=10.0, follow_redirects=True)
                return {
                    "content": [{
                        "type": "text",
                        "text": f"Connection successful! Status: {response.status_code}"
                    }]
                }
        
        elif tool_name == "buildly_login":
            import httpx
            username = arguments.get("username")
            password = arguments.get("password")
            labs_url = settings.labs_base_url or "https://labs-api.buildly.io"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{labs_url}/token/",
                    json={"username": username, "password": password},
                    timeout=10.0
                )
                if response.status_code in [200, 201]:
                    data = response.json()
                    return {
                        "content": [{
                            "type": "text",
                            "text": f"Login successful!\nAccess Token: {data.get('access')}\nRefresh Token: {data.get('refresh')}"
                        }]
                    }
                else:
                    return {
                        "content": [{
                            "type": "text",
                            "text": f"Login failed: {response.status_code} - {response.text}"
                        }],
                        "isError": True
                    }
        
        elif tool_name == "buildly_get_issues":
            import httpx
            access_token = arguments.get("access_token")
            labs_url = settings.labs_base_url or "https://labs-api.buildly.io"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{labs_url}/release/issue/",
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10.0
                )
                if response.status_code == 200:
                    issues = response.json()
                    issue_list = "\n".join([f"- [{i.get('id')}] {i.get('title', 'Untitled')}" for i in issues[:10]])
                    return {
                        "content": [{
                            "type": "text",
                            "text": f"Found {len(issues)} issues:\n{issue_list}"
                        }]
                    }
                else:
                    return {
                        "content": [{
                            "type": "text",
                            "text": f"Failed to fetch issues: {response.status_code}"
                        }],
                        "isError": True
                    }
        
        elif tool_name == "buildly_get_products":
            import httpx
            access_token = arguments.get("access_token")
            labs_url = settings.labs_base_url or "https://labs-api.buildly.io"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{labs_url}/product/product/",
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10.0
                )
                if response.status_code == 200:
                    products = response.json()
                    product_list = "\n".join([f"- {p.get('name', 'Unnamed')}" for p in products])
                    return {
                        "content": [{
                            "type": "text",
                            "text": f"Found {len(products)} products:\n{product_list}"
                        }]
                    }
                else:
                    return {
                        "content": [{
                            "type": "text",
                            "text": f"Failed to fetch products: {response.status_code}"
                        }],
                        "isError": True
                    }
        
        else:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Unknown tool: {tool_name}"
                }],
                "isError": True
            }
    
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error executing {tool_name}: {str(e)}"
            }],
            "isError": True
        }

# OAuth endpoints for Claude MCP integration
@mcp.get("/oauth/authorize")
async def oauth_authorize(
    response_type: str,
    client_id: str,
    redirect_uri: str,
    state: str,
    code_challenge: Optional[str] = None,
    code_challenge_method: Optional[str] = None
):
    # Generate authorization code
    auth_code = "buildly-auth-code-123"
    
    # Redirect back to Claude with the code
    from fastapi.responses import RedirectResponse
    redirect_url = f"{redirect_uri}?code={auth_code}&state={state}"
    return RedirectResponse(url=redirect_url)

@mcp.post("/oauth/token")  
async def oauth_token(request: Request):
    # Get content type
    content_type = request.headers.get("content-type", "")
    
    # Parse body based on content type
    if "application/json" in content_type:
        body = await request.json()
    else:
        # Handle form data without python-multipart
        body_bytes = await request.body()
        body_str = body_bytes.decode()
        # Simple form parsing
        body = {}
        for pair in body_str.split("&"):
            if "=" in pair:
                key, value = pair.split("=", 1)
                body[key] = value
    
    # Return access token
    return {
        "access_token": "buildly-agent-token",
        "token_type": "bearer",
        "expires_in": 3600
    }

@mcp.get("/oauth/callback")
async def oauth_callback():
    # OAuth callback endpoint
    return {"status": "authorized"}

# OAuth discovery endpoint (/.well-known/oauth-authorization-server)
@app.get("/.well-known/oauth-authorization-server")
async def oauth_discovery():
    return {
        "issuer": "http://localhost:8001",
        "authorization_endpoint": "http://localhost:8001/agent/oauth/authorize",
        "token_endpoint": "http://localhost:8001/agent/oauth/token",
        "registration_endpoint": "http://localhost:8001/agent/oauth/register",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code"],
        "code_challenge_methods_supported": ["S256"]
    }

@app.get("/agent/.well-known/oauth-authorization-server")
async def oauth_discovery_agent():
    return {
        "issuer": "http://localhost:8001/agent",
        "authorization_endpoint": "http://localhost:8001/agent/oauth/authorize",
        "token_endpoint": "http://localhost:8001/agent/oauth/token",
        "registration_endpoint": "http://localhost:8001/agent/oauth/register",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code"],
        "code_challenge_methods_supported": ["S256"]
    }

# Dynamic client registration
@mcp.post("/oauth/register")
async def oauth_register(request: Request):
    body = await request.json()
    # Return a registered client
    return {
        "client_id": "buildly-agent-client",
        "client_secret": "not-needed",
        "redirect_uris": body.get("redirect_uris", []),
        "grant_types": ["authorization_code"],
        "response_types": ["code"]
    }

# MCP Server Info endpoint (required for Claude HTTP transport)
@app.get("/agent")
async def mcp_info():
    return {
        "name": "buildly-agent",
        "version": "0.1.0",
        "description": "Buildly Labs AI Agent with devdocs and API integration",
        "capabilities": {
            "tools": True
        }
    }

# SSE endpoint for Server-Sent Events transport
@mcp.get("/sse")
async def mcp_sse():
    """SSE endpoint for MCP protocol"""
    async def event_generator():
        # Send initial connection event
        yield f"data: {json.dumps({'type': 'connection', 'status': 'connected'})}\n\n"
        
        # Keep connection alive
        while True:
            await asyncio.sleep(30)
            yield f": keepalive\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

# Health check
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "buildly-agent", "version": "0.1.0"}

# Discovery endpoint to list available tools (MCP-like descriptor)
@mcp.get("/mcp/tools")
async def list_tools():
    tools = [
        {
            "name": "devdocs_write",
            "description": "Write or update documentation file in devdocs folder",
            "parameters": {
                "filename": {"type": "string", "description": "Name of the file (e.g., 'api.md')"},
                "content": {"type": "string", "description": "Content to write"}
            }
        },
        {
            "name": "devdocs_read",
            "description": "Read a documentation file from devdocs folder",
            "parameters": {
                "filename": {"type": "string", "description": "Name of the file to read"}
            }
        },
        {
            "name": "devdocs_list",
            "description": "List all documentation files in devdocs folder",
            "parameters": {}
        },
        {
            "name": "buildly_login",
            "description": "Login to Buildly Labs platform",
            "parameters": {
                "username": {"type": "string", "description": "Buildly Labs username or email"},
                "password": {"type": "string", "description": "Buildly Labs password"}
            }
        },
        {
            "name": "buildly_test_connection",
            "description": "Test connection to Buildly Labs API",
            "parameters": {}
        },
        {
            "name": "buildly_get_issues",
            "description": "Get issues from Buildly Labs for your organization",
            "parameters": {
                "access_token": {"type": "string", "description": "Access token from login"}
            }
        },
        {
            "name": "buildly_get_products",
            "description": "Get products from Buildly Labs for your organization",
            "parameters": {
                "access_token": {"type": "string", "description": "Access token from login"}
            }
        }
    ]
    return {"tools": tools, "count": len(tools)}

class ToolInvoke(BaseModel):
    name: str
    arguments: Dict[str, Any] = {}

# Tool invocation endpoint
@mcp.post("/mcp/invoke")
async def invoke_tool(req: ToolInvoke, settings: AgentSettings = Depends(get_settings)):
    try:
        if req.name == "devdocs_write":
            filename = req.arguments.get("filename")
            content = req.arguments.get("content")
            if not filename or not content:
                return {"error": "Missing filename or content"}
            
            os.makedirs("devdocs", exist_ok=True)
            filepath = os.path.join("devdocs", filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            return {"success": True, "message": f"Wrote {len(content)} bytes to {filename}", "path": filepath}
        
        elif req.name == "devdocs_read":
            filename = req.arguments.get("filename")
            if not filename:
                return {"error": "Missing filename"}
            
            filepath = os.path.join("devdocs", filename)
            if not os.path.exists(filepath):
                return {"error": f"File not found: {filename}"}
            
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            return {"success": True, "filename": filename, "content": content}
        
        elif req.name == "devdocs_list":
            os.makedirs("devdocs", exist_ok=True)
            files = [f for f in os.listdir("devdocs") if os.path.isfile(os.path.join("devdocs", f))]
            return {"success": True, "files": files, "count": len(files)}
        
        elif req.name == "buildly_test_connection":
            import httpx
            labs_url = settings.labs_base_url or "https://labs-api.buildly.io"
            try:
                async with httpx.AsyncClient() as client:
                    # Just check if we can reach the server
                    response = await client.get(labs_url, timeout=10.0, follow_redirects=True)
                    return {
                        "success": response.status_code == 200, 
                        "status_code": response.status_code,
                        "labs_url": labs_url,
                        "message": f"Server reachable (status {response.status_code})"
                    }
            except Exception as e:
                return {"success": False, "error": str(e), "labs_url": labs_url}
        
        elif req.name == "buildly_login":
            import httpx
            username = req.arguments.get("username")
            password = req.arguments.get("password")
            
            if not username or not password:
                return {"error": "Missing username or password"}
            
            labs_url = settings.labs_base_url or "https://labs-api.buildly.io"
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{labs_url}/token/",
                        json={"username": username, "password": password},
                        timeout=10.0
                    )
                    if response.status_code in [200, 201]:
                        data = response.json()
                        return {
                            "success": True,
                            "message": "Login successful",
                            "access_token": data.get("access"),
                            "refresh_token": data.get("refresh"),
                            "response": data
                        }
                    else:
                        return {
                            "success": False,
                            "status_code": response.status_code,
                            "error": response.text
                        }
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        elif req.name == "buildly_get_issues":
            import httpx
            access_token = req.arguments.get("access_token")
            
            if not access_token:
                return {"error": "Missing access_token"}
            
            labs_url = settings.labs_base_url or "https://labs-api.buildly.io"
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{labs_url}/release/issue/",
                        headers={"Authorization": f"Bearer {access_token}"},
                        timeout=10.0
                    )
                    if response.status_code == 200:
                        issues = response.json()
                        return {
                            "success": True,
                            "count": len(issues),
                            "issues": issues
                        }
                    else:
                        return {
                            "success": False,
                            "status_code": response.status_code,
                            "error": response.text
                        }
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        elif req.name == "buildly_get_products":
            import httpx
            access_token = req.arguments.get("access_token")
            
            if not access_token:
                return {"error": "Missing access_token"}
            
            labs_url = settings.labs_base_url or "https://labs-api.buildly.io"
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{labs_url}/product/product/",
                        headers={"Authorization": f"Bearer {access_token}"},
                        timeout=10.0
                    )
                    if response.status_code == 200:
                        products = response.json()
                        return {
                            "success": True,
                            "count": len(products),
                            "products": products
                        }
                    else:
                        return {
                            "success": False,
                            "status_code": response.status_code,
                            "error": response.text
                        }
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        else:
            return {"error": f"Unknown tool: {req.name}"}
    
    except Exception as e:
        return {"error": str(e)}

app.include_router(mcp)

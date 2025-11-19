from fastapi import FastAPI, APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from bb_agent_manager.config import AgentSettings
import os
import json

app = FastAPI(title="BB Agent Manager", version="0.1.0")
mcp = APIRouter(prefix="/agent")

def get_settings() -> AgentSettings:
    return AgentSettings()

# Health check
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "bb-agent-manager", "version": "0.1.0"}

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

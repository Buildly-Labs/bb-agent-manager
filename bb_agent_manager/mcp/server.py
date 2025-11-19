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
        
        else:
            return {"error": f"Unknown tool: {req.name}"}
    
    except Exception as e:
        return {"error": str(e)}

app.include_router(mcp)

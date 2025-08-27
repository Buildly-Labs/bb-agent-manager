from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from bb_agent_manager.tools.devdocs import DEV_DOCS_TOOL, update_devdocs
from bb_agent_manager.tools.labs_sync import LABS_TASK_TOOL, labs_upsert_task
from bb_agent_manager.tools.git_ops import GIT_PR_TOOL, create_pr
from bb_agent_manager.config import AgentSettings

mcp = APIRouter(prefix="/mcp")

def get_settings() -> AgentSettings:
    return AgentSettings()

# Discovery endpoint to list available tools (MCP-like descriptor)
@mcp.get("/tools")
async def list_tools():
    return {"tools": [DEV_DOCS_TOOL, LABS_TASK_TOOL, GIT_PR_TOOL]}

class ToolInvoke(BaseModel):
    name: str
    arguments: Dict[str, Any] = {}

@mcp.post("/invoke")
async def invoke_tool(req: ToolInvoke, settings: AgentSettings = Depends(get_settings)):
    if req.name == "update_devdocs":
        return await update_devdocs(**req.arguments)
    if req.name == "labs_upsert_task":
        return await labs_upsert_task(settings, **req.arguments)
    if req.name == "create_pr":
        return await create_pr(**req.arguments)
    return {"error": f"Unknown tool: {req.name}"}

from fastapi import FastAPI
from bb_agent_manager.config import AgentSettings
from bb_agent_manager.router import router as agent_router
from bb_agent_manager.mcp.server import mcp as mcp_router

def register(app: FastAPI, settings_dict: dict | None = None):
    """
    BabbleBeaver calls this to mount the module.
    settings_dict allows BB to pass aggregated settings; we still read envs via AgentSettings.
    """
    settings = AgentSettings(**(settings_dict or {}))
    mount_path = settings.mount_path.rstrip("/")
    app.include_router(agent_router, prefix=mount_path)
    app.include_router(mcp_router,   prefix=mount_path)
    return {"status": "bb_agent_manager mounted", "mount_path": mount_path}

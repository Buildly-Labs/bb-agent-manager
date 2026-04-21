"""
Configuration for Buildly MCP Server.

All settings are read from environment variables. No model provider settings live here —
model selection is the responsibility of the external MCP client (Copilot, Claude, etc.).
"""
from pydantic import BaseModel
import os


class BuildlySettings(BaseModel):
    """Runtime configuration for Buildly MCP Server."""

    # Buildly Labs
    labs_base_url: str = os.getenv("LABS_BASE_URL", "https://labs-api.buildly.io")
    labs_api_token: str = os.getenv("LABS_API_TOKEN", "")

    # Buildly project context
    buildly_env_name: str = os.getenv("BUILDLY_ENV_NAME", "")
    buildly_product_uuid: str = os.getenv("BUILDLY_PRODUCT_UUID", "")
    buildly_org_uuid: str = os.getenv("BUILDLY_ORG_UUID", "")

    # Local paths (relative to CWD when the MCP server is launched)
    devdocs_path: str = os.getenv("DEVDOCS_PATH", "devdocs")
    memory_path: str = os.getenv("MEMORY_PATH", "buildly_memory")

    # GitHub integration (optional — for PR/repo tools)
    github_token: str = os.getenv("GITHUB_TOKEN", "")
    github_repo: str = os.getenv("GITHUB_REPO", "")  # "owner/repo"

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    debug: bool = os.getenv("DEBUG", "0") == "1"


# Keep backward-compat alias so existing plugin code doesn't break
AgentSettings = BuildlySettings

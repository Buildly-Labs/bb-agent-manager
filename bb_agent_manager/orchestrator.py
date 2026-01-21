from typing import Dict, Any, List, Callable
from bb_agent_manager.config import AgentSettings
from bb_agent_manager.llm.router import get_provider
from bb_agent_manager.tools.devdocs import DEV_DOCS_TOOL, update_devdocs
from bb_agent_manager.tools.labs_sync import (
    LABS_PRODUCTS_TOOL, LABS_BACKLOG_TOOL, LABS_RELEASES_TOOL, LABS_MILESTONES_TOOL, LABS_INSIGHTS_TOOL,
    labs_list_products, labs_list_backlog, labs_list_releases, labs_list_milestones, labs_get_insights
)
from bb_agent_manager.tools.git_ops import GIT_PR_TOOL, create_pr

TOOLS = [
    DEV_DOCS_TOOL,
    LABS_PRODUCTS_TOOL,
    LABS_BACKLOG_TOOL,
    LABS_RELEASES_TOOL,
    LABS_MILESTONES_TOOL,
    LABS_INSIGHTS_TOOL,
    GIT_PR_TOOL
]

def _dispatcher(settings: AgentSettings) -> Callable[[str, Dict[str, Any]], Any]:
    async def _call(name: str, args: Dict[str, Any]):
        if name == "update_devdocs":
            return await update_devdocs(**args)
        if name == "labs_list_products":
            return await labs_list_products(settings, **args)
        if name == "labs_list_backlog":
            return await labs_list_backlog(settings, **args)
        if name == "labs_list_releases":
            return await labs_list_releases(settings, **args)
        if name == "labs_list_milestones":
            return await labs_list_milestones(settings, **args)
        if name == "labs_get_insights":
            return await labs_get_insights(settings, **args)
        if name == "create_pr":
            return await create_pr(**args)
        return f"Unknown tool: {name}"
    return _call

async def run_agent(messages: List[Dict[str, str]], settings: AgentSettings, provider_hint: str | None = None):
    provider = get_provider(settings, provider_hint)
    on_tool = _dispatcher(settings)
    return await provider.chat(messages, tools=TOOLS, tool_callback=lambda n, a: settings.__class__.__mro__ and __import__("asyncio").get_event_loop().run_until_complete(on_tool(n, a)))


from typing import Optional, Dict, Any
import httpx, json
from bb_agent_manager.config import AgentSettings

LABS_PRODUCTS_TOOL = {
  "name": "labs_list_products",
  "description": "List all Buildly Labs products.",
  "parameters": {
    "type": "object",
    "properties": {
      "limit": {"type": "integer", "description": "Number of results (default: 50, max: 100)"},
      "offset": {"type": "integer", "description": "Skip this many results (for pagination)"}
    }
  }
}

LABS_BACKLOG_TOOL = {
  "name": "labs_list_backlog",
  "description": "List backlog items for a product.",
  "parameters": {
    "type": "object",
    "properties": {
      "product_id": {"type": "string", "description": "Product ID to filter by (optional)"},
      "limit": {"type": "integer", "description": "Number of results (default: 50, max: 100)"},
      "offset": {"type": "integer", "description": "Skip this many results (for pagination)"}
    }
  }
}

LABS_RELEASES_TOOL = {
  "name": "labs_list_releases",
  "description": "List releases for a product.",
  "parameters": {
    "type": "object",
    "properties": {
      "product_id": {"type": "string", "description": "Product ID to filter by (optional)"},
      "limit": {"type": "integer", "description": "Number of results (default: 50, max: 100)"},
      "offset": {"type": "integer", "description": "Skip this many results (for pagination)"}
    }
  }
}

LABS_MILESTONES_TOOL = {
  "name": "labs_list_milestones",
  "description": "List milestones for a product.",
  "parameters": {
    "type": "object",
    "properties": {
      "product_id": {"type": "string", "description": "Product ID to filter by (optional)"},
      "limit": {"type": "integer", "description": "Number of results (default: 50, max: 100)"},
      "offset": {"type": "integer", "description": "Skip this many results (for pagination)"}
    }
  }
}

LABS_INSIGHTS_TOOL = {
  "name": "labs_get_insights",
  "description": "Get product insights.",
  "parameters": {
    "type": "object",
    "properties": {
      "product_id": {"type": "string", "description": "Product ID to filter by (optional)"}
    }
  }
}

def _labs_headers(settings: AgentSettings) -> Dict[str, str]:
  headers = {"Accept": "application/json"}
  if settings.labs_api_token:
    headers["Authorization"] = f"Bearer {settings.labs_api_token}"
  return headers

async def labs_list_products(settings: AgentSettings, limit: int = 50, offset: int = 0) -> str:
  url = f"{settings.labs_base_url}/products"
  params = {"limit": limit, "offset": offset}
  headers = _labs_headers(settings)
  async with httpx.AsyncClient(timeout=20) as client:
    r = await client.get(url, params=params, headers=headers)
    r.raise_for_status()
    return json.dumps(r.json())

async def labs_list_backlog(settings: AgentSettings, product_id: Optional[str] = None, limit: int = 50, offset: int = 0) -> str:
  url = f"{settings.labs_base_url}/backlog"
  params = {"limit": limit, "offset": offset}
  if product_id:
    params["product_id"] = product_id
  headers = _labs_headers(settings)
  async with httpx.AsyncClient(timeout=20) as client:
    r = await client.get(url, params=params, headers=headers)
    r.raise_for_status()
    return json.dumps(r.json())

async def labs_list_releases(settings: AgentSettings, product_id: Optional[str] = None, limit: int = 50, offset: int = 0) -> str:
  url = f"{settings.labs_base_url}/releases"
  params = {"limit": limit, "offset": offset}
  if product_id:
    params["product_id"] = product_id
  headers = _labs_headers(settings)
  async with httpx.AsyncClient(timeout=20) as client:
    r = await client.get(url, params=params, headers=headers)
    r.raise_for_status()
    return json.dumps(r.json())

async def labs_list_milestones(settings: AgentSettings, product_id: Optional[str] = None, limit: int = 50, offset: int = 0) -> str:
  url = f"{settings.labs_base_url}/milestones"
  params = {"limit": limit, "offset": offset}
  if product_id:
    params["product_id"] = product_id
  headers = _labs_headers(settings)
  async with httpx.AsyncClient(timeout=20) as client:
    r = await client.get(url, params=params, headers=headers)
    r.raise_for_status()
    return json.dumps(r.json())

async def labs_get_insights(settings: AgentSettings, product_id: Optional[str] = None) -> str:
  url = f"{settings.labs_base_url}/insights"
  params = {}
  if product_id:
    params["product_id"] = product_id
  headers = _labs_headers(settings)
  async with httpx.AsyncClient(timeout=20) as client:
    r = await client.get(url, params=params, headers=headers)
    r.raise_for_status()
    return json.dumps(r.json())

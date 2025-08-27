from typing import List, Optional
import httpx, json
from bb_agent_manager.config import AgentSettings

LABS_TASK_TOOL = {
  "name": "labs_upsert_task",
  "description": "Create/update a Buildly Labs task linked to the current repo/PR.",
  "parameters": {
    "type":"object",
    "properties":{
      "product_uuid":{"type":"string"},
      "title":{"type":"string"},
      "description":{"type":"string"},
      "pr_url":{"type":"string"},
      "labels":{"type":"array","items":{"type":"string"}}
    },
    "required":["product_uuid","title"]
  }
}

async def labs_upsert_task(settings: AgentSettings, product_uuid: str, title: str,
                           description: str = "", pr_url: str = "", labels: Optional[List[str]]=None) -> str:
    payload = {"product_uuid":product_uuid, "title":title, "description":description, "pr_url":pr_url, "labels":labels or []}
    headers = {"Authorization": f"Bearer {settings.labs_api_token}"} if settings.labs_api_token else {}
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(f"{settings.labs_base_url}/tasks/upsert", json=payload, headers=headers)
        r.raise_for_status()
        return json.dumps(r.json())

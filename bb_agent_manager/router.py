from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from bb_agent_manager.config import AgentSettings
from bb_agent_manager.orchestrator import run_agent

router = APIRouter()

class ChatTurn(BaseModel):
    role: str  # "user" | "system" | "assistant" | "tool"
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatTurn]
    provider: Optional[str] = None  # "gemini" | "ollama"

class ChatResponse(BaseModel):
    content: str

def get_settings() -> AgentSettings:
    return AgentSettings()

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, settings: AgentSettings = Depends(get_settings)):
    result = await run_agent([m.model_dump() for m in req.messages], settings, req.provider)
    return ChatResponse(content=result.get("content", ""))

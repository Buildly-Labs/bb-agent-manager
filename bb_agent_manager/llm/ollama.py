from typing import Any, Dict, List, Optional, Callable
from openai import OpenAI
from .base import LLMProvider, ToolSpec
from bb_agent_manager.config import AgentSettings

class OllamaProvider(LLMProvider):
    def __init__(self, settings: AgentSettings):
        self.client = OpenAI(base_url=settings.ollama_base_url, api_key="ollama")
        self.model = settings.ollama_model

    def name(self) -> str: return "ollama"

    async def chat(self, messages: List[Dict[str, str]],
                   tools: Optional[List[ToolSpec]] = None,
                   tool_callback: Optional[Callable[[str, Dict[str, Any]], Any]] = None,
                   **kwargs) -> Dict[str, Any]:
        res = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=[{"type": "function", "function": t} for t in (tools or [])] if tools else None
        )
        msg = res.choices[0].message
        while getattr(msg, "tool_calls", None):
            for call in msg.tool_calls:
                out = tool_callback and tool_callback(call.function.name, call.function.arguments or {})
                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "name": call.function.name,
                    "content": str(out),
                })
            res = self.client.chat.completions.create(model=self.model, messages=messages)
            msg = res.choices[0].message

        return {"content": msg.content or ""}

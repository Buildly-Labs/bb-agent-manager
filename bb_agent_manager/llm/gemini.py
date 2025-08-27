from typing import Any, Dict, List, Optional, Callable
import google.generativeai as genai
from .base import LLMProvider, ToolSpec
from bb_agent_manager.config import AgentSettings

class GeminiProvider(LLMProvider):
    def __init__(self, settings: AgentSettings):
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)

    def name(self) -> str: return "gemini"

    async def chat(self, messages: List[Dict[str, str]],
                   tools: Optional[List[ToolSpec]] = None,
                   tool_callback: Optional[Callable[[str, Dict[str, Any]], Any]] = None,
                   **kwargs) -> Dict[str, Any]:
        # Convert to Gemini's history format
        history = [{"role": m["role"], "parts": [m["content"]]} for m in messages]
        tool_defs = [{"name": t["name"], "description": t["description"], "parameters": t["parameters"]} for t in (tools or [])]
        resp = self.model.generate_content(history, tools=tool_defs)

        # Handle tool calls
        if getattr(resp, "function_calls", None):
            for call in resp.function_calls:
                out = tool_callback and tool_callback(call.name, call.args or {})
                history.append({"role": "tool", "parts": [str(out)]})
            resp = self.model.generate_content(history)

        return {"content": getattr(resp, "text", "") or ""}

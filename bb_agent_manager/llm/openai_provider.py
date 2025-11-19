"""
OpenAI Provider for BB Agent Manager
Supports GPT-4, GPT-4 Turbo, GPT-3.5 Turbo, and o1 models
"""
from typing import Any, Dict, List, Optional, Callable
from openai import OpenAI
from .base import LLMProvider, ToolSpec
from bb_agent_manager.config import AgentSettings

class OpenAIProvider(LLMProvider):
    def __init__(self, settings: AgentSettings):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    def name(self) -> str:
        return "openai"

    async def chat(self, messages: List[Dict[str, str]],
                   tools: Optional[List[ToolSpec]] = None,
                   tool_callback: Optional[Callable[[str, Dict[str, Any]], Any]] = None,
                   **kwargs) -> Dict[str, Any]:
        """
        Chat with OpenAI GPT models
        Supports: gpt-4, gpt-4-turbo, gpt-4o, gpt-3.5-turbo, o1-preview, o1-mini
        """
        # Handle o1 models which don't support system messages or tools
        is_o1_model = self.model.startswith("o1")
        
        if is_o1_model:
            # o1 models: no system messages, no tools, only user/assistant
            filtered_messages = [
                msg for msg in messages 
                if msg["role"] in ["user", "assistant"]
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=filtered_messages
            )
            
            return {"content": response.choices[0].message.content or ""}
        
        # Standard GPT models with tool support
        tool_defs = None
        if tools:
            tool_defs = [
                {
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool.get("description", ""),
                        "parameters": tool.get("parameters", {})
                    }
                }
                for tool in tools
            ]
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tool_defs if tool_defs else None
        )
        
        msg = response.choices[0].message
        
        # Handle tool calls
        while getattr(msg, "tool_calls", None):
            messages.append({
                "role": "assistant",
                "content": msg.content,
                "tool_calls": [
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {
                            "name": call.function.name,
                            "arguments": call.function.arguments
                        }
                    }
                    for call in msg.tool_calls
                ]
            })
            
            for call in msg.tool_calls:
                import json
                tool_args = json.loads(call.function.arguments) if call.function.arguments else {}
                result = tool_callback(call.function.name, tool_args) if tool_callback else {}
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "name": call.function.name,
                    "content": str(result)
                })
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tool_defs if tool_defs else None
            )
            msg = response.choices[0].message
        
        return {"content": msg.content or ""}

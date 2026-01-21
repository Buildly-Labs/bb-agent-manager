"""
Anthropic Claude Provider for BB Agent Manager
Supports Claude 3.5 Sonnet, Claude 3 Opus, and other Claude models
"""
from typing import Any, Dict, List, Optional, Callable
import anthropic
from .base import LLMProvider, ToolSpec
from bb_agent_manager.config import AgentSettings

import httpx

class ClaudeProvider(LLMProvider):
    def __init__(self, settings: AgentSettings):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.anthropic_model
        self.settings = settings

    def name(self) -> str:
        return "claude"

    async def fetch_buildly_context(self, messages: List[Dict[str, str]]) -> str:
        """
        Fetch Buildly context from API and sources for agentic augmentation.
        """
        # Example: fetch product insights and backlog (can be extended)
        headers = {"Authorization": f"Bearer {self.settings.labs_api_token}"} if self.settings.labs_api_token else {}
        context_parts = []
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                # Fetch insights
                r = await client.get(f"{self.settings.labs_base_url}/insights", headers=headers)
                if r.status_code == 200:
                    context_parts.append("Buildly Insights:\n" + str(r.json()))
                # Fetch backlog (first 3 items)
                r2 = await client.get(f"{self.settings.labs_base_url}/backlog", params={"limit": 3}, headers=headers)
                if r2.status_code == 200:
                    context_parts.append("Buildly Backlog (top 3):\n" + str(r2.json()))
            except Exception as e:
                context_parts.append(f"[Buildly context fetch error: {e}]")
        return "\n\n".join(context_parts)

    async def chat(self, messages: List[Dict[str, str]],
                   tools: Optional[List[ToolSpec]] = None,
                   tool_callback: Optional[Callable[[str, Dict[str, Any]], Any]] = None,
                   **kwargs) -> Dict[str, Any]:
        """
        Chat with Claude using Anthropic API, with agentic context injection from Buildly API.
        """
        # Fetch Buildly context and prepend to system/user message
        buildly_context = await self.fetch_buildly_context(messages)
        system_message = None
        claude_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_message = (buildly_context + "\n\n" + msg["content"]) if buildly_context else msg["content"]
            elif msg["role"] == "user" and not system_message:
                # If no system message, prepend to first user message
                claude_messages.append({
                    "role": msg["role"],
                    "content": (buildly_context + "\n\n" + msg["content"]) if buildly_context else msg["content"]
                })
            else:
                claude_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        # Convert tools to Claude format
        claude_tools = None
        if tools:
            claude_tools = [
                {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "input_schema": tool.get("parameters", {})
                }
                for tool in tools
            ]
        # Make API call
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system_message if system_message else anthropic.NOT_GIVEN,
            messages=claude_messages,
            tools=claude_tools if claude_tools else anthropic.NOT_GIVEN
        )
        # Handle tool calls
        while response.stop_reason == "tool_use":
            # Extract tool calls from response
            tool_results = []
            for content_block in response.content:
                if content_block.type == "tool_use":
                    tool_name = content_block.name
                    tool_input = content_block.input
                    tool_id = content_block.id
                    
                    # Execute tool
                    result = tool_callback(tool_name, tool_input) if tool_callback else {}
                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": str(result)
                    })
            
            # Add assistant message with tool use
            claude_messages.append({
                "role": "assistant",
                "content": response.content
            })
            
            # Add tool results
            claude_messages.append({
                "role": "user",
                "content": tool_results
            })
            
            # Continue conversation
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_message if system_message else anthropic.NOT_GIVEN,
                messages=claude_messages,
                tools=claude_tools if claude_tools else anthropic.NOT_GIVEN
            )
        
        # Extract final response
        content = ""
        for block in response.content:
            if hasattr(block, "text"):
                content += block.text
        
        return {"content": content}

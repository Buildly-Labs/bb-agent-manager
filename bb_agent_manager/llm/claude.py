"""
Anthropic Claude Provider for BB Agent Manager
Supports Claude 3.5 Sonnet, Claude 3 Opus, and other Claude models
"""
from typing import Any, Dict, List, Optional, Callable
import anthropic
from .base import LLMProvider, ToolSpec
from bb_agent_manager.config import AgentSettings

class ClaudeProvider(LLMProvider):
    def __init__(self, settings: AgentSettings):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.anthropic_model

    def name(self) -> str:
        return "claude"

    async def chat(self, messages: List[Dict[str, str]],
                   tools: Optional[List[ToolSpec]] = None,
                   tool_callback: Optional[Callable[[str, Dict[str, Any]], Any]] = None,
                   **kwargs) -> Dict[str, Any]:
        """
        Chat with Claude using Anthropic API
        Supports Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Sonnet, Claude 3 Haiku
        """
        # Convert messages format
        system_message = None
        claude_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
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

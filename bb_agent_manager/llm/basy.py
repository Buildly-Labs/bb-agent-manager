from typing import Any, Dict, List, Optional, Callable, TypedDict

class ToolSpec(TypedDict):
    name: str
    description: str
    parameters: Dict[str, Any]  # JSON Schema

class LLMProvider:
    def name(self) -> str: ...
    def supports_tools(self) -> bool: return True

    async def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[ToolSpec]] = None,
        tool_callback: Optional[Callable[[str, Dict[str, Any]], str | Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        raise NotImplementedError

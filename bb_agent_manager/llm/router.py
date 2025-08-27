from typing import Optional
from bb_agent_manager.config import AgentSettings
from .gemini import GeminiProvider
from .ollama import OllamaProvider
from .base import LLMProvider

def get_provider(settings: AgentSettings, hint: Optional[str] = None) -> LLMProvider:
    name = (hint or settings.default_provider).lower()
    if name == "ollama":
        return OllamaProvider(settings)
    return GeminiProvider(settings)

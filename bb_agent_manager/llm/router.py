from typing import Optional
from bb_agent_manager.config import AgentSettings
from .gemini import GeminiProvider
from .ollama import OllamaProvider
from .claude import ClaudeProvider
from .openai_provider import OpenAIProvider
from .base import LLMProvider

def get_provider(settings: AgentSettings, hint: Optional[str] = None) -> LLMProvider:
    """
    Get LLM provider based on settings or hint.
    
    Supported providers:
    - claude: Anthropic Claude (3.5 Sonnet, 3 Opus, 3 Sonnet, 3 Haiku)
    - openai: OpenAI GPT models (GPT-4, GPT-4o, GPT-3.5, o1)
    - gemini: Google Gemini (1.5 Pro, 1.5 Flash)
    - ollama: Local models (via Ollama)
    """
    name = (hint or settings.default_provider).lower()
    
    if name == "claude" or name == "anthropic":
        return ClaudeProvider(settings)
    elif name == "openai" or name == "gpt":
        return OpenAIProvider(settings)
    elif name == "ollama":
        return OllamaProvider(settings)
    else:  # Default to Gemini
        return GeminiProvider(settings)

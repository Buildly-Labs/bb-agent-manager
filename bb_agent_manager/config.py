from pydantic import BaseModel
import os

class AgentSettings(BaseModel):
    labs_base_url: str = os.getenv("LABS_BASE_URL", "https://labs.buildly.io/api")
    labs_api_token: str = os.getenv("LABS_API_TOKEN", "")
    default_provider: str = os.getenv("BB_AM_DEFAULT_PROVIDER", "gemini")  # "gemini" | "ollama"
    # Gemini
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
    # Ollama OpenAI-compatible
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    # Git operations (token or GH App fallback if you have one)
    github_token: str = os.getenv("GITHUB_TOKEN", "")
    # Optional mount path for the plugin
    mount_path: str = os.getenv("BB_AM_MOUNT_PATH", "/agent")

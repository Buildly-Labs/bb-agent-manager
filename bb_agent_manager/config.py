from pydantic import BaseModel
import os

class AgentSettings(BaseModel):
    labs_base_url: str = os.getenv("LABS_BASE_URL", "https://labs.buildly.io/api")
    labs_api_token: str = os.getenv("LABS_API_TOKEN", "")
    default_provider: str = os.getenv("BB_AM_DEFAULT_PROVIDER", "gemini")  # "gemini" | "ollama" | "claude" | "openai"
    
    # Gemini
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
    
    # Anthropic Claude (claude-3-5-sonnet, claude-3-opus, claude-3-sonnet, claude-3-haiku)
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    anthropic_model: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    
    # OpenAI (gpt-4, gpt-4-turbo, gpt-4o, gpt-3.5-turbo, o1-preview, o1-mini)
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    
    # Ollama (local models - OpenAI-compatible)
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    
    # Git operations (token or GH App fallback if you have one)
    github_token: str = os.getenv("GITHUB_TOKEN", "")
    github_repo: str = os.getenv("GITHUB_REPO", "")  # e.g., "owner/repo"
    
    # Optional mount path for the plugin
    mount_path: str = os.getenv("BB_AM_MOUNT_PATH", "/agent")
    
    # Code review and PR settings
    require_human_review: bool = os.getenv("BB_AM_REQUIRE_HUMAN_REVIEW", "true").lower() == "true"
    auto_close_issues: bool = os.getenv("BB_AM_AUTO_CLOSE_ISSUES", "true").lower() == "true"
    create_draft_prs: bool = os.getenv("BB_AM_CREATE_DRAFT_PRS", "true").lower() == "true"

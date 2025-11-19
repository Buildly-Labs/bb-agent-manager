# Environment Variables for BB Agent Manager

## Required Environment Variables

### For Claude Sonnet (Anthropic - Recommended for Production)

```bash
# Set the default provider
export BB_AM_DEFAULT_PROVIDER=claude

# Get API key from: https://console.anthropic.com/
export ANTHROPIC_API_KEY=sk-ant-xxxxx

# Model to use
export ANTHROPIC_MODEL=claude-3-5-sonnet-20241022  # Latest Sonnet
# Other options: claude-3-opus-20240229, claude-3-sonnet-20240229, claude-3-haiku-20240307
```

### For OpenAI GPT (OpenAI - Production)

```bash
# Set the default provider
export BB_AM_DEFAULT_PROVIDER=openai

# Get API key from: https://platform.openai.com/api-keys
export OPENAI_API_KEY=sk-xxxxx

# Model to use
export OPENAI_MODEL=gpt-4o  # Latest GPT-4
# Other options: gpt-4-turbo, gpt-4, gpt-3.5-turbo, o1-preview, o1-mini
```

### For Gemini (Google - Production)

```bash
# Set the default provider  
export BB_AM_DEFAULT_PROVIDER=gemini

# Get API key from: https://makersuite.google.com/app/apikey
export GEMINI_API_KEY=your_gemini_api_key_here

# Model to use
export GEMINI_MODEL=gemini-1.5-pro  # Large context window
# Other options: gemini-1.5-flash
```

### For Ollama (Local AI - Development/Testing)

```bash
# Set the default provider
export BB_AM_DEFAULT_PROVIDER=ollama

# Ollama service URL (default if running locally)
export OLLAMA_BASE_URL=http://localhost:11434/v1

# Model to use (install with: ollama pull deepseek-coder:6.7b)
export OLLAMA_MODEL=deepseek-coder:6.7b
# Other options: llama3.1:8b, codellama:7b, deepseek-coder-v2:latest
```

## GitHub Integration (Required for PR Management)

```bash
# GitHub Personal Access Token (required for PR creation)
export GITHUB_TOKEN=ghp_xxxxx

# Repository in format "owner/repo"
export GITHUB_REPO=Buildly-Labs/bb-agent-manager
```

## Code Review & Safety Settings

```bash
# Require human review for AI-generated PRs (default: true, cannot be disabled)
export BB_AM_REQUIRE_HUMAN_REVIEW=true

# Auto-close issues when PR merges (default: true)
export BB_AM_AUTO_CLOSE_ISSUES=true

# Create PRs as drafts requiring review (default: true)
export BB_AM_CREATE_DRAFT_PRS=true
```

## Optional Environment Variables

```bash
# Enable debug logging
export DEBUG=1
export LOG_LEVEL=DEBUG

# Custom mount path for BabbleBeaver integration
export BB_AM_MOUNT_PATH=/agent

# Labs integration (for production)
export LABS_BASE_URL=https://labs.buildly.io/api
export LABS_API_TOKEN=your_labs_token
```

## Quick Setup Commands

### For Ollama Testing:
```bash
# Install and start Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve

# Pull a code-friendly model
ollama pull deepseek-coder:6.7b

# Set environment
export BB_AM_DEFAULT_PROVIDER=ollama
export OLLAMA_MODEL=deepseek-coder:6.7b

# Start BB Agent
./start_agent.py
```

### For Gemini Testing:
```bash
# Set environment  
export BB_AM_DEFAULT_PROVIDER=gemini
export GEMINI_API_KEY=your_api_key_here

# Start BB Agent
./start_agent.py --provider gemini
```

## .env File Support

You can also create a `.env` file in the project root:

```env
# .env file
BB_AM_DEFAULT_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=deepseek-coder:6.7b
DEBUG=1
```

The application will automatically load these variables.

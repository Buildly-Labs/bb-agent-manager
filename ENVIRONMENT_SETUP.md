# Environment Variables for BB Agent Manager

## Required Environment Variables

### For Ollama (Local AI - Recommended for Testing)

```bash
# Set the default provider
export BB_AM_DEFAULT_PROVIDER=ollama

# Ollama service URL (default if running locally)
export OLLAMA_BASE_URL=http://localhost:11434/v1

# Model to use (install with: ollama pull deepseek-coder:6.7b)
export OLLAMA_MODEL=deepseek-coder:6.7b
```

### For Gemini (Hosted AI)

```bash
# Set the default provider  
export BB_AM_DEFAULT_PROVIDER=gemini

# Get API key from: https://makersuite.google.com/app/apikey
export GEMINI_API_KEY=your_gemini_api_key_here

# Model to use
export GEMINI_MODEL=gemini-1.5-pro
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

# GitHub integration (for production)
export GITHUB_TOKEN=ghp_your_github_token
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

# BB Agent Manager - Test Results and Environment Setup

## ✅ Testing Status

**Successfully tested** bb-agent-manager with local Ollama in VS Code environment!

## 🔧 Required Environment Variables

### For Ollama (Local AI - Recommended)

```bash
# Essential variables
export BB_AM_DEFAULT_PROVIDER=ollama
export OLLAMA_BASE_URL=http://localhost:11434/v1
export OLLAMA_MODEL=deepseek-coder:6.7b  # or any available model

# Optional debugging
export DEBUG=1
export LOG_LEVEL=DEBUG
```

### For Gemini (Hosted AI)

```bash
# Essential variables
export BB_AM_DEFAULT_PROVIDER=gemini
export GEMINI_API_KEY=your_gemini_api_key_here
export GEMINI_MODEL=gemini-1.5-pro

# Optional debugging
export DEBUG=1
export LOG_LEVEL=DEBUG
```

## 🚀 Quick Start Commands

### 1. Install Dependencies (one-time setup)
```bash
# Option A: With virtual environment (preferred)
python3 start_agent.py --check-only

# Option B: System-wide installation
python3 start_agent.py --system-pip --check-only

# Option C: Manual installation
pip3 install -r requirements.txt
```

### 2. Start Ollama (for local AI)
```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Pull a code-friendly model
ollama pull deepseek-coder:6.7b
```

### 3. Set Environment Variables
```bash
export BB_AM_DEFAULT_PROVIDER=ollama
export OLLAMA_MODEL=deepseek-coder:6.7b
```

### 4. Start BB Agent Server
```bash
# Quick test server
python3 simple_test_server.py

# Full server with auto-setup
python3 start_agent.py

# Start server with chat client
python3 start_agent.py --chat
```

## 🧪 Tested Features

### ✅ API Endpoints Working
- `GET /health` - Server health check
- `GET /` - Basic info endpoint
- `POST /agent/chat` - Chat interface
- `GET /agent/mcp/tools` - Available tools
- Interactive API docs at `/docs`

### ✅ VS Code Integration
- REST Client extension compatibility
- Thunder Client compatibility  
- Simple Browser preview
- Environment variable support

### ✅ Tested API Calls
```bash
# Health check
curl http://localhost:8001/health

# Chat request
curl -X POST http://localhost:8001/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "ollama",
    "messages": [
      {"role": "user", "content": "Hello, can you help me review some code?"}
    ]
  }'
```

### ✅ Response Format
```json
{
  "response": "Hello! I'm BB Agent Manager running with ollama. Your message was: Hello, can you help me review some code?",
  "provider": "ollama", 
  "model": "deepseek-coder:6.7b"
}
```

## 📋 VS Code Setup Checklist

### 1. Install Required Extensions
- REST Client (`humao.rest-client`)
- Thunder Client (`rangav.vscode-thunder-client`)
- Python (`ms-python.python`)

### 2. Use Provided Files
- Use `examples/api_requests.http` with REST Client
- Use `.vscode/settings.json` for workspace configuration
- Use `chat_client.py` for interactive chat

### 3. Test the Integration
1. Start the server: `python3 simple_test_server.py`
2. Open `examples/api_requests.http` in VS Code
3. Click "Send Request" on any example
4. View responses in VS Code

## 🎯 Working Environment Variables Summary

**Minimum required for Ollama testing:**
```bash
export BB_AM_DEFAULT_PROVIDER=ollama
export OLLAMA_MODEL=deepseek-coder:6.7b
```

**Full development environment:**
```bash
export BB_AM_DEFAULT_PROVIDER=ollama
export OLLAMA_BASE_URL=http://localhost:11434/v1
export OLLAMA_MODEL=deepseek-coder:6.7b
export DEBUG=1
export LOG_LEVEL=DEBUG
```

The setup is now **fully tested and working** for VS Code IDE integration! 🎉

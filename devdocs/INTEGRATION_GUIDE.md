# BB Agent Manager - Integration & Testing Guide

## Running as BabbleBeaver Plugin

### Option 1: Package Installation (Recommended)

1. **Install bb-agent-manager in BabbleBeaver's environment:**

```bash
# In BabbleBeaver directory
source venv/bin/activate
pip install git+https://github.com/Buildly-Labs/bb-agent-manager.git
```

2. **Modify BabbleBeaver's main.py to load plugins:**

Add this to BabbleBeaver's `main.py` after the FastAPI app creation:

```python
# main.py - Add after: app = FastAPI(debug=True)
import pkg_resources

# Load bb-agent-manager plugin
try:
    for ep in pkg_resources.iter_entry_points(group="babblebeaver.modules"):
        if ep.name == "bb_agent_manager":
            register_fn = ep.load()
            result = register_fn(app, {})
            print(f"[BB] Loaded plugin: {result}")
except Exception as e:
    print(f"[BB] Failed to load bb_agent_manager: {e}")
```

3. **Set environment variables in BabbleBeaver's .env:**

```bash
# Add to BabbleBeaver's .env file
LABS_BASE_URL=https://labs.buildly.io/api
LABS_API_TOKEN=your_labs_token
BB_AM_DEFAULT_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_key
GEMINI_MODEL=gemini-1.5-pro
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama3.1:8b
GITHUB_TOKEN=ghp_your_github_token
BB_AM_MOUNT_PATH=/agent
```

4. **Run BabbleBeaver:**

```bash
cd /path/to/babblebeaver
source venv/bin/activate
uvicorn main:app --reload
```

**Access Points:**
- BabbleBeaver: `http://localhost:8000`
- Agent Chat: `http://localhost:8000/agent/chat` (POST)
- Agent Tools: `http://localhost:8000/agent/mcp/tools` (GET)
- Tool Invoke: `http://localhost:8000/agent/mcp/invoke` (POST)

### Option 2: Direct Import

Modify BabbleBeaver's `main.py`:

```python
# Add after existing imports
from bb_agent_manager import register as register_bb_agent

# Add after app creation
register_bb_agent(app, {})
```

## Running Independently for Testing

### Standalone Server

Create `test_server.py` in your bb-agent-manager directory:

```python
#!/usr/bin/env python3
"""
Standalone test server for bb-agent-manager
"""
from fastapi import FastAPI
from bb_agent_manager.plugin import register
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="BB Agent Manager Test Server",
    description="Standalone test server for bb-agent-manager",
    version="0.1.0"
)

# Register the plugin
result = register(app, {})
print(f"Plugin registered: {result}")

if __name__ == "__main__":
    uvicorn.run(
        "test_server:app", 
        host="0.0.0.0", 
        port=8001, 
        reload=True
    )
```

**Run the test server:**

```bash
python test_server.py
```

**Access Points:**
- Test Server: `http://localhost:8001`
- Agent Chat: `http://localhost:8001/agent/chat`
- OpenAPI Docs: `http://localhost:8001/docs`
- Agent Tools: `http://localhost:8001/agent/mcp/tools`

### Docker Testing

Create `docker-compose.test.yml`:

```yaml
version: '3.8'

services:
  bb-agent-test:
    build: .
    ports:
      - "8001:8000"
    environment:
      - LABS_BASE_URL=https://labs.buildly.io/api
      - LABS_API_TOKEN=${LABS_API_TOKEN}
      - BB_AM_DEFAULT_PROVIDER=gemini
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - GEMINI_MODEL=gemini-1.5-pro
      - BB_AM_MOUNT_PATH=/agent
    volumes:
      - ./test_server.py:/app/main.py
    command: ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

volumes:
  ollama_data:
```

**Run with Docker:**

```bash
docker-compose -f docker-compose.test.yml up --build
```

## Testing Examples

### 1. Test Chat Endpoint

```bash
curl -X POST "http://localhost:8001/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "gemini",
    "messages": [
      {
        "role": "system",
        "content": "You are the Buildly Agent. Use tools to update devdocs and Labs."
      },
      {
        "role": "user", 
        "content": "Create a task in Labs for implementing user authentication"
      }
    ]
  }'
```

### 2. Test Tool Discovery

```bash
curl "http://localhost:8001/agent/mcp/tools"
```

### 3. Test Direct Tool Invocation

```bash
# Test devdocs update
curl -X POST "http://localhost:8001/agent/mcp/invoke" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "update_devdocs",
    "arguments": {
      "files": ["src/auth.py", "tests/test_auth.py"],
      "summary": "Implemented OAuth2 authentication with JWT tokens",
      "component_reuse_notes": "Auth middleware can be reused across projects"
    }
  }'

# Test Labs task creation
curl -X POST "http://localhost:8001/agent/mcp/invoke" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "labs_upsert_task",
    "arguments": {
      "product_uuid": "your-product-uuid",
      "title": "Implement user authentication",
      "description": "Add OAuth2 authentication with JWT tokens",
      "pr_url": "https://github.com/your-org/your-repo/pull/123",
      "labels": ["authentication", "security", "backend"]
    }
  }'
```

### 4. Test with Python

Create `test_client.py`:

```python
#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8001"

def test_chat():
    """Test the chat endpoint"""
    payload = {
        "provider": "gemini",
        "messages": [
            {
                "role": "system",
                "content": "You are the Buildly Agent. Use tools to update devdocs and Labs."
            },
            {
                "role": "user",
                "content": "Refactor user service and update documentation"
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/agent/chat", json=payload)
    print(f"Chat response: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_tools():
    """Test tool discovery"""
    response = requests.get(f"{BASE_URL}/agent/mcp/tools")
    print(f"Tools response: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_devdocs_tool():
    """Test devdocs tool directly"""
    payload = {
        "name": "update_devdocs",
        "arguments": {
            "files": ["src/user_service.py"],
            "summary": "Refactored user service with improved error handling",
            "component_reuse_notes": "Error handling patterns can be reused"
        }
    }
    
    response = requests.post(f"{BASE_URL}/agent/mcp/invoke", json=payload)
    print(f"DevDocs response: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    print("Testing BB Agent Manager...")
    test_tools()
    test_devdocs_tool()
    test_chat()
```

Run the test:

```bash
python test_client.py
```

## Debugging & Development

### Debug Mode

Set these environment variables for detailed logging:

```bash
export PYTHONPATH="/path/to/bb-agent-manager:$PYTHONPATH"
export DEBUG=1
export LOG_LEVEL=DEBUG
```

### Hot Reload Development

For rapid development, use the test server with file watching:

```bash
# Install watchdog for file monitoring
pip install watchdog

# Run with auto-reload
uvicorn test_server:app --reload --host 0.0.0.0 --port 8001
```

### Integration with BabbleBeaver Development

1. **Clone BabbleBeaver:**

```bash
git clone https://github.com/Buildly-Labs/BabbleBeaver.git
cd BabbleBeaver
```

2. **Install in development mode:**

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install BabbleBeaver dependencies
pip install -r requirements.txt

# Install bb-agent-manager in development mode
pip install -e /path/to/bb-agent-manager
```

3. **Modify main.py to load plugin:**

```python
# Add to BabbleBeaver's main.py
from bb_agent_manager import register as register_bb_agent

# After app creation
register_bb_agent(app, {})
```

4. **Run BabbleBeaver with agent:**

```bash
uvicorn main:app --reload
```

## Troubleshooting

### Common Issues

1. **Import Errors:**
   - Ensure bb-agent-manager is installed: `pip list | grep bb-agent`
   - Check PYTHONPATH: `echo $PYTHONPATH`

2. **Plugin Not Loading:**
   - Verify entry points: `pip show bb-agent-manager`
   - Check for import errors in BabbleBeaver logs

3. **API Key Issues:**
   - Verify environment variables: `env | grep -E "(GEMINI|LABS|GITHUB)"`
   - Test API keys independently

4. **Tool Execution Failures:**
   - Check file permissions for devdocs directory
   - Verify git repository is initialized
   - Ensure Labs API token has correct permissions

### Logs & Monitoring

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Monitor API calls:

```bash
# Watch logs in real-time
tail -f /var/log/babblebeaver.log

# Monitor HTTP requests
curl -X GET "http://localhost:8001/agent/mcp/tools" -v
```

This setup allows you to develop and test your bb-agent-manager both as a standalone service and integrated with BabbleBeaver!

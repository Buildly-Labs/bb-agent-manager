# Quick Start Guide - Run Locally with Docker + Copilot Chat

This guide helps you run BB Agent Manager in Docker and integrate with GitHub Copilot Chat **right now**.

## 🚀 5-Minute Setup

### Step 1: Set Environment Variables

```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your API keys (choose ONE provider to start)
nano .env
```

**Minimum Required (pick one):**

```bash
# Option A: Use Ollama (Free, Local)
OLLAMA_BASE_URL=http://host.docker.internal:11434/v1
OLLAMA_MODEL=deepseek-coder:6.7b
BB_AM_DEFAULT_PROVIDER=ollama

# Option B: Use Gemini (Free tier available)
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-1.5-pro
BB_AM_DEFAULT_PROVIDER=gemini

# Option C: Use Claude Sonnet (Premium)
ANTHROPIC_API_KEY=sk-ant-xxxxx
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
BB_AM_DEFAULT_PROVIDER=claude

# Option D: Use GPT-4 (Premium)
OPENAI_API_KEY=sk-xxxxx
OPENAI_MODEL=gpt-4o
BB_AM_DEFAULT_PROVIDER=openai
```

**Optional (for GitHub PR/issue features):**
```bash
GITHUB_TOKEN=ghp_xxxxx
GITHUB_REPO=YourOrg/your-repo
```

**Optional (for Buildly Labs task management):**
```bash
LABS_BASE_URL=https://labs.buildly.io/api
# Token is obtained via login, no need to set here
```

### Step 2: Build and Start Container

```bash
# Build the Docker image
docker-compose build

# Start the container
docker-compose up -d

# Check logs
docker-compose logs -f bb-agent
```

You should see:
```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Step 3: Test the API

```bash
# Health check
curl http://localhost:8001/health

# Test MCP tool listing
curl http://localhost:8001/agent/mcp/tools | jq

# Test a simple invocation (write to devdocs)
curl -X POST http://localhost:8001/agent/mcp/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "name": "devdocs_write",
    "arguments": {
      "filename": "test.md",
      "content": "# Test\n\nThis is a test from Docker!"
    }
  }'

# Verify file was created
ls -la devdocs/test.md
```

## 🤖 Integrate with GitHub Copilot Chat

### Method 1: REST Client in VS Code (Recommended for Testing)

1. **Install REST Client extension:**
   ```
   ext install humao.rest-client
   ```

2. **Create test file** `test_bb_agent.http`:

```http
### Test Health
GET http://localhost:8001/health

### List Available Tools
GET http://localhost:8001/agent/mcp/tools

### Write Documentation
POST http://localhost:8001/agent/mcp/invoke
Content-Type: application/json

{
  "name": "devdocs_write",
  "arguments": {
    "filename": "api_overview.md",
    "content": "# API Overview\n\n## Authentication\n\nUse Bearer tokens..."
  }
}

### Search DevDocs
POST http://localhost:8001/agent/mcp/invoke
Content-Type: application/json

{
  "name": "devdocs_search",
  "arguments": {
    "query": "authentication"
  }
}

### Chat with Agent (Claude)
POST http://localhost:8001/agent/chat
Content-Type: application/json

{
  "message": "What tools are available?",
  "provider_hint": "claude"
}

### Login to Buildly Labs
POST http://localhost:8001/agent/mcp/invoke
Content-Type: application/json

{
  "name": "buildly_login",
  "arguments": {
    "username": "your-email@example.com",
    "password": "your-password"
  }
}

### Get Prioritized Tasks
POST http://localhost:8001/agent/mcp/invoke
Content-Type: application/json

{
  "name": "buildly_get_tasks",
  "arguments": {}
}
```

3. **Click "Send Request"** above any request to test

### Method 2: Use with GitHub Copilot Chat

**In Copilot Chat, ask:**

```
@workspace I want to test the BB Agent Manager running at http://localhost:8001

Can you help me:
1. Write some documentation to devdocs
2. Search for existing documentation
3. Create a test file
```

**Example Copilot prompts:**

```
Use the BB Agent at http://localhost:8001 to write documentation 
about our authentication system to devdocs/auth.md

Search the devdocs for information about API endpoints using 
the agent at http://localhost:8001

List all available tools from the BB Agent Manager
```

### Method 3: Python Client Script

Create `test_copilot_integration.py`:

```python
#!/usr/bin/env python3
"""Test BB Agent Manager with Copilot-like workflow"""
import requests
import json

BASE_URL = "http://localhost:8001"

def invoke_tool(tool_name, arguments):
    """Invoke an MCP tool"""
    response = requests.post(
        f"{BASE_URL}/agent/mcp/invoke",
        json={"name": tool_name, "arguments": arguments}
    )
    return response.json()

def chat(message, provider="gemini"):
    """Chat with the agent"""
    response = requests.post(
        f"{BASE_URL}/agent/chat",
        json={"message": message, "provider_hint": provider}
    )
    return response.json()

# Test 1: Write documentation
print("1️⃣ Writing documentation...")
result = invoke_tool("devdocs_write", {
    "filename": "copilot_test.md",
    "content": "# Copilot Integration Test\n\nTesting from Python!"
})
print(f"✅ {result.get('message', result)}\n")

# Test 2: Search documentation
print("2️⃣ Searching documentation...")
result = invoke_tool("devdocs_search", {
    "query": "copilot"
})
print(f"✅ Found {len(result.get('results', []))} results\n")

# Test 3: Chat with agent
print("3️⃣ Chatting with agent...")
result = chat("What tools do you have available?")
print(f"✅ Agent says: {result.get('response', result)[:200]}...\n")

# Test 4: List tools
print("4️⃣ Listing available tools...")
response = requests.get(f"{BASE_URL}/agent/mcp/tools")
tools = response.json()
print(f"✅ Available tools: {len(tools.get('tools', []))}")
for tool in tools.get('tools', [])[:5]:
    print(f"   - {tool['name']}: {tool['description'][:60]}...")
```

Run it:
```bash
python3 test_copilot_integration.py
```

## 🔧 Using Different AI Providers

### Switch Provider on the Fly

```bash
# Stop current container
docker-compose down

# Change provider in .env
echo "BB_AM_DEFAULT_PROVIDER=claude" >> .env

# Restart
docker-compose up -d
```

Or override per request:

```bash
# Use Claude for this request
curl -X POST http://localhost:8001/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain this code",
    "provider_hint": "claude"
  }'

# Use GPT-4 for this request
curl -X POST http://localhost:8001/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Review this PR",
    "provider_hint": "openai"
  }'
```

### Test All Providers

```bash
#!/bin/bash
# test_all_providers.sh

for provider in ollama gemini claude openai; do
    echo "Testing $provider..."
    curl -X POST http://localhost:8001/agent/chat \
      -H "Content-Type: application/json" \
      -d "{\"message\": \"Hello from $provider\", \"provider_hint\": \"$provider\"}" | jq
done
```

## 🎯 Common Copilot Chat Workflows

### Workflow 1: Documentation Assistant

**In Copilot Chat:**
```
@workspace I need to document our new authentication system

Please use the BB Agent at http://localhost:8001 to:
1. Create devdocs/auth/overview.md with authentication flow
2. Create devdocs/auth/api.md with API endpoints
3. Search existing docs for related content
```

### Workflow 2: Code Review Assistant

**In Copilot Chat:**
```
@workspace Review the changes in src/auth.py

Use the BB Agent to:
1. Read the file and analyze it
2. Write a review summary to devdocs/reviews/auth_review.md
3. Create a GitHub PR with the review
```

### Workflow 3: Task Management with Buildly Labs

**In Copilot Chat:**
```
@workspace What should I work on next?

Use the BB Agent to:
1. Login to Buildly Labs
2. Get my prioritized tasks
3. Show me the top 3 features to implement
```

### Workflow 4: Git Operations

**In Copilot Chat:**
```
@workspace I finished feature #123

Use the BB Agent to:
1. Create a pull request for my changes
2. Link it to issue #123
3. Request review from the team
```

## 🐛 Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs bb-agent

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Can't connect to Ollama on host

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Fix: Make sure Ollama allows network connections
# In Ollama settings, enable "Allow network connections"

# Or use Docker network mode
docker run -d --network host --name ollama ollama/ollama
```

### API returns 500 errors

```bash
# Check environment variables are set
docker-compose exec bb-agent env | grep -E "(GEMINI|OLLAMA|ANTHROPIC|OPENAI)"

# Check logs for missing API keys
docker-compose logs bb-agent | grep -i "error\|warning"
```

### Copilot can't reach the agent

```bash
# Verify port is open
netstat -an | grep 8001

# Test from command line first
curl http://localhost:8001/health

# Check firewall
sudo ufw status
sudo ufw allow 8001/tcp
```

## 📊 Monitor Agent Activity

```bash
# Follow logs in real-time
docker-compose logs -f bb-agent

# See recent tool invocations
docker-compose logs bb-agent | grep "invoke"

# Check health
watch -n 5 'curl -s http://localhost:8001/health | jq'

# Monitor container stats
docker stats bb-agent-manager
```

## 🔄 Update to Latest Version

```bash
# Pull latest code
git pull origin main

# Rebuild container
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check version
curl http://localhost:8001/health | jq
```

## 🛑 Stop and Cleanup

```bash
# Stop container
docker-compose down

# Stop and remove volumes (WARNING: deletes devdocs)
docker-compose down -v

# Remove images
docker rmi bb-agent-bb-agent
```

## 🎉 Next Steps

1. ✅ **Test basic functionality** - Write and search devdocs
2. ✅ **Try different AI providers** - Compare Claude vs GPT-4 vs Gemini
3. ✅ **Integrate with Copilot** - Use in your daily workflow
4. ✅ **Setup GitHub integration** - Add GITHUB_TOKEN for PR creation
5. ✅ **Try Buildly Labs workflow** - Login and manage tasks
6. ✅ **Read full guides:**
   - [COPILOT_CURSOR_INTEGRATION.md](./COPILOT_CURSOR_INTEGRATION.md)
   - [BUILDLY_LABS_INTEGRATION.md](./BUILDLY_LABS_INTEGRATION.md)
   - [IDE_INTEGRATION_GUIDE.md](./IDE_INTEGRATION_GUIDE.md)

## 💡 Pro Tips

**Tip 1:** Use `jq` to format JSON responses
```bash
curl http://localhost:8001/agent/mcp/tools | jq '.tools[] | {name, description}'
```

**Tip 2:** Set up bash aliases
```bash
alias bb-invoke='curl -X POST http://localhost:8001/agent/mcp/invoke -H "Content-Type: application/json" -d'
alias bb-chat='curl -X POST http://localhost:8001/agent/chat -H "Content-Type: application/json" -d'

# Usage
bb-chat '{"message": "Hello!"}'
```

**Tip 3:** Create a Makefile
```makefile
.PHONY: start stop logs test

start:
	docker-compose up -d

stop:
	docker-compose down

logs:
	docker-compose logs -f bb-agent

test:
	python3 test_copilot_integration.py
```

Now you're ready to use BB Agent Manager with Copilot! 🚀

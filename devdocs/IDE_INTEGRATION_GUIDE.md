# IDE Integration Guide - VS Code Extension

## Overview

This guide shows how to integrate bb-agent-manager into VS Code as a chat assistant, similar to GitHub Copilot Chat. You can use either local Ollama models or hosted Gemini AI.

## Architecture

```
┌─────────────────┐    HTTP API    ┌─────────────────┐    LLM API    ┌─────────────────┐
│   VS Code       │ ◄────────────► │ BB Agent Manager│ ◄───────────► │ Ollama/Gemini   │
│   Extension     │                │   localhost:8001│               │ AI Provider     │
│   Chat Panel    │                │                 │               │                 │
└─────────────────┘                └─────────────────┘               └─────────────────┘
```

## Setup Instructions

### 1. Start BB Agent Manager Service

#### Option A: Standalone Development Server
```bash
cd bb-agent-manager
python test_server.py
# Service available at: http://localhost:8001
```

#### Option B: Docker Development
```bash
cd bb-agent-manager
docker-compose -f docker-compose.test.yml up -d
# Service available at: http://localhost:8001
```

### 2. Configure AI Provider

#### Local Ollama Setup
```bash
# Install and start Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve

# Pull a code-friendly model
ollama pull deepseek-coder:6.7b
# or
ollama pull codellama:7b
# or
ollama pull llama3.1:8b
```

Set environment variables:
```bash
export BB_AM_DEFAULT_PROVIDER=ollama
export OLLAMA_BASE_URL=http://localhost:11434/v1
export OLLAMA_MODEL=deepseek-coder:6.7b
```

#### Hosted Gemini Setup
```bash
# Get API key from: https://makersuite.google.com/app/apikey
export BB_AM_DEFAULT_PROVIDER=gemini
export GEMINI_API_KEY=your_gemini_api_key_here
export GEMINI_MODEL=gemini-1.5-pro
```

### 3. VS Code Extension Integration

#### Method 1: REST Client Extension

Install the "REST Client" extension and create `.http` files:

```http
### Test Agent Health
GET http://localhost:8001/health

### Test Tool Discovery
GET http://localhost:8001/agent/mcp/tools

### Chat with Agent - Code Review
POST http://localhost:8001/agent/chat
Content-Type: application/json

{
  "provider": "ollama",
  "messages": [
    {
      "role": "system",
      "content": "You are a Buildly development assistant. Help with code review, documentation, and development tasks. Use available tools when appropriate."
    },
    {
      "role": "user",
      "content": "Review this Python function and suggest improvements:\n\ndef process_data(data):\n    result = []\n    for item in data:\n        if item > 0:\n            result.append(item * 2)\n    return result"
    }
  ]
}

### Chat with Agent - Create Documentation
POST http://localhost:8001/agent/chat
Content-Type: application/json

{
  "provider": "gemini",
  "messages": [
    {
      "role": "system",
      "content": "You are a Buildly development assistant. When asked to document code changes, use the update_devdocs tool."
    },
    {
      "role": "user",
      "content": "I just implemented OAuth2 authentication in src/auth.py. Please document this change and note that the auth middleware can be reused in other projects."
    }
  ]
}

### Direct Tool Invocation - Update DevDocs
POST http://localhost:8001/agent/mcp/invoke
Content-Type: application/json

{
  "name": "update_devdocs",
  "arguments": {
    "files": ["src/auth.py", "tests/test_auth.py"],
    "summary": "Implemented OAuth2 authentication with JWT tokens and refresh token support",
    "component_reuse_notes": "Auth middleware, JWT utilities, and token validation decorators can be reused across projects. Consider extracting to shared auth library."
  }
}
```

#### Method 2: Thunder Client Extension

1. Install "Thunder Client" extension
2. Create a new collection: "BB Agent Manager"
3. Add requests:

**Health Check:**
- Method: GET
- URL: `http://localhost:8001/health`

**Chat Request:**
- Method: POST
- URL: `http://localhost:8001/agent/chat`
- Headers: `Content-Type: application/json`
- Body:
```json
{
  "provider": "{{provider}}",
  "messages": [
    {
      "role": "system",
      "content": "You are a Buildly development assistant specialized in Python, FastAPI, and documentation."
    },
    {
      "role": "user",
      "content": "{{prompt}}"
    }
  ]
}
```

**Environment Variables:**
- `provider`: `ollama` or `gemini`
- `prompt`: Your question/request

#### Method 3: Custom VS Code Extension

Create a simple VS Code extension for chat interface:

**package.json:**
```json
{
  "name": "bb-agent-chat",
  "displayName": "BB Agent Chat",
  "description": "Buildly Agent Chat Interface",
  "version": "0.1.0",
  "engines": {
    "vscode": "^1.74.0"
  },
  "categories": ["Other"],
  "activationEvents": [],
  "main": "./out/extension.js",
  "contributes": {
    "commands": [
      {
        "command": "bbAgent.openChat",
        "title": "Open BB Agent Chat",
        "category": "BB Agent"
      }
    ],
    "views": {
      "explorer": [
        {
          "id": "bbAgentChat",
          "name": "BB Agent Chat",
          "when": "true"
        }
      ]
    }
  },
  "scripts": {
    "compile": "tsc -p ./",
    "watch": "tsc -watch -p ./"
  },
  "devDependencies": {
    "@types/vscode": "^1.74.0",
    "@types/node": "16.x",
    "typescript": "^4.9.4"
  }
}
```

**src/extension.ts:**
```typescript
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    const provider = new BBAgentChatProvider(context.extensionUri);
    
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider('bbAgentChat', provider)
    );
    
    const openChatCommand = vscode.commands.registerCommand('bbAgent.openChat', () => {
        vscode.commands.executeCommand('bbAgentChat.focus');
    });
    
    context.subscriptions.push(openChatCommand);
}

class BBAgentChatProvider implements vscode.WebviewViewProvider {
    constructor(private readonly _extensionUri: vscode.Uri) {}
    
    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken,
    ) {
        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };
        
        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);
        
        webviewView.webview.onDidReceiveMessage(async data => {
            switch (data.type) {
                case 'sendMessage':
                    await this.sendMessageToAgent(data.message);
                    break;
            }
        });
    }
    
    private async sendMessageToAgent(message: string) {
        try {
            const response = await fetch('http://localhost:8001/agent/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    provider: 'ollama', // or 'gemini'
                    messages: [
                        {
                            role: 'system',
                            content: 'You are a Buildly development assistant.'
                        },
                        {
                            role: 'user',
                            content: message
                        }
                    ]
                })
            });
            
            const result = await response.json();
            // Send response back to webview
            // Implementation details...
        } catch (error) {
            vscode.window.showErrorMessage(`BB Agent error: ${error}`);
        }
    }
    
    private _getHtmlForWebview(webview: vscode.Webview): string {
        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>BB Agent Chat</title>
            <style>
                body { font-family: var(--vscode-font-family); }
                .chat-container { padding: 10px; }
                .message { margin-bottom: 10px; }
                .user-message { background: var(--vscode-editor-selectionBackground); padding: 8px; border-radius: 4px; }
                .agent-message { background: var(--vscode-editor-inactiveSelectionBackground); padding: 8px; border-radius: 4px; }
                .input-container { display: flex; margin-top: 10px; }
                #messageInput { flex: 1; padding: 6px; }
                #sendButton { margin-left: 5px; padding: 6px 12px; }
            </style>
        </head>
        <body>
            <div class="chat-container">
                <div id="chatMessages"></div>
                <div class="input-container">
                    <input type="text" id="messageInput" placeholder="Ask BB Agent...">
                    <button id="sendButton">Send</button>
                </div>
            </div>
            <script>
                const vscode = acquireVsCodeApi();
                const chatMessages = document.getElementById('chatMessages');
                const messageInput = document.getElementById('messageInput');
                const sendButton = document.getElementById('sendButton');
                
                sendButton.addEventListener('click', sendMessage);
                messageInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') sendMessage();
                });
                
                function sendMessage() {
                    const message = messageInput.value.trim();
                    if (!message) return;
                    
                    addMessage('user', message);
                    messageInput.value = '';
                    
                    vscode.postMessage({
                        type: 'sendMessage',
                        message: message
                    });
                }
                
                function addMessage(sender, content) {
                    const messageDiv = document.createElement('div');
                    messageDiv.className = 'message ' + sender + '-message';
                    messageDiv.textContent = content;
                    chatMessages.appendChild(messageDiv);
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                }
                
                window.addEventListener('message', event => {
                    const message = event.data;
                    if (message.type === 'agentResponse') {
                        addMessage('agent', message.content);
                    }
                });
            </script>
        </body>
        </html>`;
    }
}

export function deactivate() {}
```

## Testing Scenarios

### 1. Code Review Assistant
```http
POST http://localhost:8001/agent/chat
Content-Type: application/json

{
  "provider": "ollama",
  "messages": [
    {
      "role": "system",
      "content": "You are a senior Python developer. Review code for best practices, security, performance, and maintainability."
    },
    {
      "role": "user",
      "content": "Please review this FastAPI endpoint:\n\n@app.post('/users')\ndef create_user(user_data: dict):\n    # Save to database\n    db.save(user_data)\n    return {'status': 'success'}"
    }
  ]
}
```

### 2. Documentation Generator
```http
POST http://localhost:8001/agent/chat
Content-Type: application/json

{
  "provider": "gemini",
  "messages": [
    {
      "role": "system",
      "content": "You are a technical writer. When asked to document code, use the update_devdocs tool to create comprehensive documentation."
    },
    {
      "role": "user",
      "content": "Document the new user authentication system in src/auth/ including OAuth2 flow, JWT handling, and middleware components."
    }
  ]
}
```

### 3. Debugging Assistant
```http
POST http://localhost:8001/agent/chat
Content-Type: application/json

{
  "provider": "ollama",
  "messages": [
    {
      "role": "system",
      "content": "You are a debugging expert. Help identify and fix issues in code."
    },
    {
      "role": "user",
      "content": "I'm getting this error: 'TypeError: unsupported operand type(s) for +: 'NoneType' and 'str'' in my Python function. Here's the code:\n\ndef process_name(first, last):\n    return first + ' ' + last"
    }
  ]
}
```

### 4. Test Generation
```http
POST http://localhost:8001/agent/chat
Content-Type: application/json

{
  "provider": "gemini",
  "messages": [
    {
      "role": "system",
      "content": "You are a test automation expert. Generate comprehensive test cases for given code."
    },
    {
      "role": "user",
      "content": "Generate pytest test cases for this function:\n\ndef calculate_discount(price, discount_percent, min_price=10):\n    if price < min_price:\n        return price\n    return price * (1 - discount_percent / 100)"
    }
  ]
}
```

## Performance Optimization

### Local Ollama Optimization
```bash
# Use smaller, faster models for quick responses
ollama pull deepseek-coder:1.3b  # Faster, less accurate
ollama pull deepseek-coder:6.7b  # Balanced
ollama pull deepseek-coder:33b   # Slower, more accurate

# Configure model parameters
export OLLAMA_NUM_PARALLEL=4
export OLLAMA_MAX_LOADED_MODELS=2
export OLLAMA_FLASH_ATTENTION=1
```

### Gemini Optimization
```bash
# Use appropriate model for task
export GEMINI_MODEL=gemini-1.5-flash    # Faster, cheaper
export GEMINI_MODEL=gemini-1.5-pro      # More capable
```

## Keyboard Shortcuts

Add to VS Code `keybindings.json`:
```json
[
  {
    "key": "ctrl+shift+a",
    "command": "bbAgent.openChat",
    "when": "editorTextFocus"
  },
  {
    "key": "ctrl+shift+d",
    "command": "bbAgent.documentCode",
    "when": "editorHasSelection"
  }
]
```

## Troubleshooting

### Common Issues

1. **Agent service not responding:**
   ```bash
   curl http://localhost:8001/health
   # Should return: {"status": "healthy"}
   ```

2. **Ollama connection issues:**
   ```bash
   # Check Ollama status
   ollama list
   curl http://localhost:11434/api/tags
   ```

3. **Gemini API issues:**
   ```bash
   # Test API key
   curl -H "Authorization: Bearer $GEMINI_API_KEY" \
        https://generativelanguage.googleapis.com/v1/models
   ```

4. **VS Code extension issues:**
   - Check Developer Console: `Help > Toggle Developer Tools`
   - Reload window: `Ctrl+Shift+P` → "Developer: Reload Window"

### Debug Mode

Enable detailed logging:
```bash
export DEBUG=1
export LOG_LEVEL=DEBUG
python test_server.py
```

This setup gives you a GitHub Copilot-like experience with bb-agent-manager, supporting both local Ollama models for privacy and Gemini for enhanced capabilities! 🚀

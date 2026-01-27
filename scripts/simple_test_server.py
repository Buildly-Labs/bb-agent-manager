#!/usr/bin/env python3
"""
Simple test server for BB Agent Manager
"""
import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Add current directory to path so we can import bb_agent_manager
sys.path.insert(0, os.path.dirname(__file__))

app = FastAPI(
    title="BB Agent Manager Test Server",
    description="Test server for BB Agent Manager IDE integration",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "BB Agent Manager Test Server",
        "status": "running",
        "provider": os.environ.get("BB_AM_DEFAULT_PROVIDER", "ollama"),
        "model": os.environ.get("OLLAMA_MODEL", "not-set"),
        "docs": "/docs"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "provider": os.environ.get("BB_AM_DEFAULT_PROVIDER", "ollama"),
        "ollama_url": os.environ.get("OLLAMA_BASE_URL", "not-set"),
        "model": os.environ.get("OLLAMA_MODEL", "not-set")
    }

@app.post("/agent/chat")
def chat_endpoint(request: dict):
    """Simple chat endpoint for testing"""
    return {
        "response": f"Hello! I'm BB Agent Manager running with {os.environ.get('BB_AM_DEFAULT_PROVIDER', 'ollama')}. Your message was: {request.get('messages', [])[-1].get('content', 'no message') if request.get('messages') else 'no messages'}",
        "provider": os.environ.get("BB_AM_DEFAULT_PROVIDER", "ollama"),
        "model": os.environ.get("OLLAMA_MODEL", "not-set")
    }

@app.get("/agent/mcp/tools")
def list_tools():
    """Mock tools endpoint"""
    return {
        "tools": [
            {"name": "update_devdocs", "description": "Update developer documentation"},
            {"name": "git_status", "description": "Check git status"},
            {"name": "labs_sync", "description": "Sync with Buildly Labs"}
        ]
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    print(f"🚀 Starting BB Agent Manager Test Server on port {port}")
    print(f"🌐 Open http://localhost:{port} to test")
    print(f"📋 API docs at http://localhost:{port}/docs")
    print(f"🔧 Provider: {os.environ.get('BB_AM_DEFAULT_PROVIDER', 'ollama')}")
    print(f"🤖 Model: {os.environ.get('OLLAMA_MODEL', 'not-set')}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

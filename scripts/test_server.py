#!/usr/bin/env python3
"""
Standalone test server for bb-agent-manager
Run independently for testing and development
"""
from fastapi import FastAPI
from bb_agent_manager.plugin import register
import uvicorn
import os

# Create FastAPI app
app = FastAPI(
    title="BB Agent Manager Test Server",
    description="Standalone test server for bb-agent-manager development and testing",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add a simple health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "bb-agent-manager",
        "version": "0.1.0"
    }

# Register the bb-agent-manager plugin
try:
    result = register(app, {})
    print(f"✅ Plugin registered successfully: {result}")
except Exception as e:
    print(f"❌ Failed to register plugin: {e}")
    raise

if __name__ == "__main__":
    print("🚀 Starting BB Agent Manager Test Server...")
    print("📋 Available endpoints:")
    print("   • Health: http://localhost:8001/health")
    print("   • Chat: http://localhost:8001/agent/chat (POST)")
    print("   • Tools: http://localhost:8001/agent/mcp/tools (GET)")
    print("   • Invoke: http://localhost:8001/agent/mcp/invoke (POST)")
    print("   • Docs: http://localhost:8001/docs")
    print()
    
    # Check for required environment variables
    env_vars = {
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
        "LABS_API_TOKEN": os.getenv("LABS_API_TOKEN"),
        "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN")
    }
    
    print("🔧 Environment Configuration:")
    for var, value in env_vars.items():
        status = "✅ Set" if value else "❌ Missing"
        print(f"   • {var}: {status}")
    print()
    
    uvicorn.run(
        "test_server:app", 
        host="0.0.0.0", 
        port=8001, 
        reload=True,
        log_level="info"
    )

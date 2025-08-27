#!/usr/bin/env python3
"""
BB Agent Manager Test Server
===========================

Easy startup script for testing bb-agent-manager in different modes.

Usage:
    ./start_agent.py                    # Default: Ollama with deepseek-coder
    ./start_agent.py --gemini           # Use Gemini AI
    ./start_agent.py --ollama           # Use Ollama (explicit)
    ./start_agent.py --port 8002        # Custom port
    ./start_agent.py --debug            # Enable debug logging
    ./start_agent.py --chat             # Start with chat client
"""

import argparse
import asyncio
import os
import subprocess
import sys
from pathlib import Path

def setup_environment(provider: str, model: str = None, debug: bool = False):
    """Configure environment variables for the chosen provider."""
    
    if provider == "ollama":
        os.environ["BB_AM_DEFAULT_PROVIDER"] = "ollama"
        os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434/v1"
        os.environ["OLLAMA_MODEL"] = model or "deepseek-coder:6.7b"
        
        print(f"🤖 Configured for Ollama with model: {os.environ['OLLAMA_MODEL']}")
        print("📝 Make sure Ollama is running: ollama serve")
        
    elif provider == "gemini":
        os.environ["BB_AM_DEFAULT_PROVIDER"] = "gemini"
        os.environ["GEMINI_MODEL"] = model or "gemini-1.5-pro"
        
        if not os.environ.get("GEMINI_API_KEY"):
            print("❌ GEMINI_API_KEY environment variable is required for Gemini")
            print("   Get your key from: https://makersuite.google.com/app/apikey")
            print("   Set it with: export GEMINI_API_KEY=your_api_key_here")
            sys.exit(1)
            
        print(f"🌟 Configured for Gemini with model: {os.environ['GEMINI_MODEL']}")
        
    # Common settings
    if debug:
        os.environ["DEBUG"] = "1"
        os.environ["LOG_LEVEL"] = "DEBUG"
        print("🐛 Debug logging enabled")

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import fastapi
        import uvicorn
        import bb_agent_manager
        print("✅ Core dependencies found")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Install with: pip install -e .")
        sys.exit(1)

def check_ollama_connection():
    """Check if Ollama is running and has models."""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [m["name"] for m in models]
            
            if model_names:
                print(f"✅ Ollama connected with models: {', '.join(model_names[:3])}")
                
                # Check if recommended model exists
                recommended = ["deepseek-coder:6.7b", "codellama:7b", "llama3.1:8b"]
                available_recommended = [m for m in recommended if m in model_names]
                
                if not available_recommended:
                    print("💡 Consider pulling a code-friendly model:")
                    print("   ollama pull deepseek-coder:6.7b")
                    print("   ollama pull codellama:7b")
                    
            else:
                print("⚠️  Ollama running but no models found")
                print("💡 Pull a model with: ollama pull deepseek-coder:6.7b")
        else:
            print("❌ Ollama not responding")
            print("💡 Start Ollama with: ollama serve")
            
    except Exception as e:
        print("❌ Could not connect to Ollama")
        print("💡 Make sure Ollama is installed and running: ollama serve")

async def start_server(port: int = 8001):
    """Start the BB Agent Manager server."""
    print(f"🚀 Starting BB Agent Manager server on port {port}")
    
    # Import and start the server
    try:
        import uvicorn
        from bb_agent_manager.main import app
        
        config = uvicorn.Config(
            app=app,
            host="0.0.0.0", 
            port=port,
            log_level="debug" if os.environ.get("DEBUG") else "info",
            reload=True
        )
        
        server = uvicorn.Server(config)
        await server.serve()
        
    except ImportError:
        # Fallback to test_server.py
        print("📝 Using fallback test server...")
        import test_server
        test_server.main()

def start_chat_client(provider: str):
    """Start the interactive chat client."""
    try:
        import rich
        import aiohttp
        print("🗨️  Starting interactive chat client...")
        subprocess.run([
            sys.executable, "chat_client.py", 
            "--provider", provider
        ])
    except ImportError:
        print("❌ Chat client dependencies not installed")
        print("💡 Install with: pip install rich aiohttp")
    except FileNotFoundError:
        print("❌ chat_client.py not found")
        print("💡 Make sure you're in the bb-agent-manager directory")

def main():
    parser = argparse.ArgumentParser(description="BB Agent Manager Test Server")
    parser.add_argument("--provider", choices=["ollama", "gemini"], default="ollama",
                       help="AI provider to use")
    parser.add_argument("--model", help="Specific model to use")
    parser.add_argument("--port", type=int, default=8001, help="Server port")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--chat", action="store_true", help="Start chat client after server")
    parser.add_argument("--check-only", action="store_true", help="Only check dependencies")
    
    args = parser.parse_args()
    
    # Check dependencies
    check_dependencies()
    
    # Configure environment
    setup_environment(args.provider, args.model, args.debug)
    
    # Check provider-specific requirements
    if args.provider == "ollama":
        check_ollama_connection()
    
    if args.check_only:
        print("✅ All checks completed")
        return
    
    # Display startup info
    print("\n" + "="*50)
    print("🤖 BB Agent Manager - Test Server")
    print("="*50)
    print(f"Provider: {args.provider}")
    print(f"Port: {args.port}")
    print(f"API URL: http://localhost:{args.port}")
    print(f"Health Check: http://localhost:{args.port}/health")
    print(f"Tools: http://localhost:{args.port}/agent/mcp/tools")
    print("="*50)
    
    try:
        if args.chat:
            # Start server in background and then chat client
            print("🚀 Starting server in background...")
            
            # Start server process
            server_cmd = [
                sys.executable, "-c",
                f"""
import asyncio
import os
os.environ.update({dict(os.environ)!r})
from start_agent import start_server
asyncio.run(start_server({args.port}))
"""
            ]
            
            server_process = subprocess.Popen(server_cmd)
            
            # Wait a moment for server to start
            import time
            time.sleep(3)
            
            # Start chat client
            start_chat_client(args.provider)
            
            # Cleanup
            server_process.terminate()
            
        else:
            # Start server normally
            asyncio.run(start_server(args.port))
            
    except KeyboardInterrupt:
        print("\n👋 Shutting down BB Agent Manager")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

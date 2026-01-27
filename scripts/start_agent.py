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
import venv
from pathlib import Path

def setup_virtual_environment():
    """Set up virtual environment and install dependencies."""
    venv_path = Path("venv")
    
    if not venv_path.exists():
        print("🔧 Creating virtual environment...")
        try:
            venv.create(venv_path, with_pip=True)
            print("✅ Virtual environment created")
        except Exception as e:
            print(f"❌ Failed to create virtual environment: {e}")
            print("💡 On Ubuntu/Debian, run: sudo apt install python3-venv")
            print("💡 Continuing with system Python...")
            return sys.executable
    
    # Determine the correct python executable path
    if os.name == 'nt':  # Windows
        python_exe = venv_path / "Scripts" / "python.exe"
        pip_exe = venv_path / "Scripts" / "pip.exe"
    else:  # Unix/Linux/macOS
        python_exe = venv_path / "bin" / "python"
        pip_exe = venv_path / "bin" / "pip"
    
    # Check if python exists in venv
    if not python_exe.exists():
        print("❌ Virtual environment python not found, using system python")
        return sys.executable
    
    # Check if dependencies are installed
    try:
        result = subprocess.run([str(python_exe), "-c", "import fastapi"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Dependencies already installed")
            return str(python_exe)
    except FileNotFoundError:
        pass
    
    # Install dependencies
    print("📦 Installing dependencies...")
    requirements_file = Path("requirements.txt")
    
    if requirements_file.exists():
        try:
            subprocess.run([str(pip_exe), "install", "-r", "requirements.txt"], 
                         check=True, capture_output=True, text=True)
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            print("💡 Trying with system pip...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                             check=True)
                print("✅ Dependencies installed with system pip")
                return sys.executable
            except subprocess.CalledProcessError:
                print("❌ Failed to install dependencies with system pip")
                sys.exit(1)
    else:
        print("❌ requirements.txt not found")
        sys.exit(1)
    
    # Install the package in development mode
    try:
        subprocess.run([str(pip_exe), "install", "-e", "."], 
                     check=True, capture_output=True, text=True)
        print("✅ BB Agent Manager installed in development mode")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Could not install in development mode: {e}")
        # Continue anyway, might work without -e install
    
    return str(python_exe)

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

def check_dependencies(python_exe: str = None):
    """Check if required dependencies are installed."""
    if python_exe is None:
        python_exe = sys.executable
        
    try:
        result = subprocess.run([python_exe, "-c", "import fastapi, uvicorn"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Core dependencies found")
            return True
        else:
            return False
    except Exception as e:
        print(f"❌ Dependency check failed: {e}")
        return False

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

async def start_server(port: int = 8001, python_exe: str = None):
    """Start the BB Agent Manager server."""
    print(f"🚀 Starting BB Agent Manager server on port {port}")
    
    if python_exe is None:
        python_exe = sys.executable
    
    # Try to start with uvicorn directly
    try:
        # Use the virtual environment's python to run the server
        server_script = f"""
import sys
sys.path.insert(0, '.')
import uvicorn
from bb_agent_manager.main import app

if __name__ == '__main__':
    uvicorn.run(
        app,
        host='0.0.0.0',
        port={port},
        log_level='{"debug" if os.environ.get("DEBUG") else "info"}',
        reload=True
    )
"""
        
        with open("temp_server.py", "w") as f:
            f.write(server_script)
        
        subprocess.run([python_exe, "temp_server.py"])
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        print("💡 Trying fallback test server...")
        
        # Fallback to simple test server
        test_server_script = f"""
import sys
sys.path.insert(0, '.')
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="BB Agent Manager Test", version="0.1.0")

@app.get("/health")
def health():
    return {{"status": "healthy", "message": "BB Agent Manager is running"}}

@app.get("/")
def root():
    return {{"message": "BB Agent Manager Test Server", "docs": "/docs"}}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port={port})
"""
        
        with open("simple_test_server.py", "w") as f:
            f.write(test_server_script)
        
        subprocess.run([python_exe, "simple_test_server.py"])

def start_chat_client(provider: str, python_exe: str = None):
    """Start the interactive chat client."""
    if python_exe is None:
        python_exe = sys.executable
        
    try:
        # Check if chat client dependencies are available
        result = subprocess.run([python_exe, "-c", "import rich, aiohttp"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Chat client dependencies not installed")
            print("💡 Installing chat client dependencies...")
            pip_exe = python_exe.replace("python", "pip")
            subprocess.run([pip_exe, "install", "rich", "aiohttp"], check=True)
        
        print("🗨️  Starting interactive chat client...")
        subprocess.run([python_exe, "chat_client.py", "--provider", provider])
        
    except subprocess.CalledProcessError:
        print("❌ Failed to install chat client dependencies")
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
    parser.add_argument("--skip-venv", action="store_true", help="Skip virtual environment setup")
    parser.add_argument("--system-pip", action="store_true", help="Use system pip instead of virtual environment")
    
    args = parser.parse_args()
    
    # Set up virtual environment and install dependencies (unless skipped)
    if args.system_pip:
        print("🔧 Using system pip to install dependencies...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            print("✅ Dependencies installed with system pip")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            sys.exit(1)
        python_exe = sys.executable
    elif not args.skip_venv:
        python_exe = setup_virtual_environment()
    else:
        python_exe = sys.executable
    
    # Check dependencies
    if not check_dependencies(python_exe):
        if args.skip_venv:
            print("❌ Dependencies not found. Try running without --skip-venv")
            sys.exit(1)
        else:
            print("❌ Dependencies check failed after installation")
            sys.exit(1)
    
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
    print(f"Python: {python_exe}")
    print(f"API URL: http://localhost:{args.port}")
    print(f"Health Check: http://localhost:{args.port}/health")
    print(f"Tools: http://localhost:{args.port}/agent/mcp/tools")
    print("="*50)
    
    try:
        if args.chat:
            # Start server in background and then chat client
            print("🚀 Starting server in background...")
            
            # Start server process
            server_cmd = [python_exe, "-c", f"""
import sys
import os
sys.path.insert(0, '.')
os.environ.update({dict(os.environ)!r})

# Simple test server for chat testing
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="BB Agent Manager", version="0.1.0")

@app.get("/health")
def health():
    return {{"status": "healthy"}}

@app.get("/")
def root():
    return {{"message": "BB Agent Manager running", "provider": "{args.provider}"}}

uvicorn.run(app, host='0.0.0.0', port={args.port}, log_level='info')
"""]
            
            server_process = subprocess.Popen(server_cmd)
            
            # Wait a moment for server to start
            import time
            time.sleep(3)
            
            # Start chat client
            start_chat_client(args.provider, python_exe)
            
            # Cleanup
            server_process.terminate()
            
        else:
            # Start server normally
            asyncio.run(start_server(args.port, python_exe))
            
    except KeyboardInterrupt:
        print("\n👋 Shutting down BB Agent Manager")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("💡 Check that all required environment variables are set")
        sys.exit(1)

if __name__ == "__main__":
    main()

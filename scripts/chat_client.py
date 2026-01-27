#!/usr/bin/env python3
"""
Interactive BB Agent Manager Chat Client
=====================================

A simple command-line chat interface for testing bb-agent-manager
like GitHub Copilot Chat with either Ollama or Gemini.

Usage:
    python chat_client.py --provider ollama
    python chat_client.py --provider gemini
    python chat_client.py --provider gemini --model gemini-1.5-flash

Features:
- Interactive chat with syntax highlighting
- Code review assistance  
- Documentation generation
- Tool invocation (git, devdocs, testing)
- Session history
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any
import asyncio
import aiohttp
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.syntax import Syntax
from rich.table import Table

console = Console()

class BBAgentChatClient:
    def __init__(self, base_url: str = "http://localhost:8001", provider: str = "ollama"):
        self.base_url = base_url
        self.provider = provider
        self.session_history: List[Dict[str, Any]] = []
        self.system_prompt = """You are a Buildly development assistant specialized in:
- Code review and suggestions
- Documentation generation using available tools
- Test creation and debugging
- Git operations and workflow guidance
- Component reusability analysis

Use available tools when appropriate:
- update_devdocs: For documenting code changes
- git_status, git_add, git_commit: For git operations  
- run_tests: For test execution
- sync_labs_component: For component documentation

Be concise but thorough. Format code with proper syntax highlighting."""

    async def check_health(self) -> bool:
        """Check if the agent service is running."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("status") == "healthy"
        except Exception as e:
            console.print(f"[red]Health check failed: {e}[/red]")
        return False

    async def get_available_tools(self) -> List[str]:
        """Get list of available MCP tools."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/agent/mcp/tools") as response:
                    if response.status == 200:
                        data = await response.json()
                        return [tool["name"] for tool in data.get("tools", [])]
        except Exception as e:
            console.print(f"[yellow]Could not fetch tools: {e}[/yellow]")
        return []

    async def chat(self, message: str) -> str:
        """Send a chat message to the agent."""
        # Add user message to history
        self.session_history.append({
            "role": "user", 
            "content": message,
            "timestamp": datetime.now().isoformat()
        })

        # Prepare messages for API
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add recent history (last 10 exchanges)
        recent_history = self.session_history[-20:]  # Last 10 user+assistant pairs
        for msg in recent_history:
            if msg["role"] in ["user", "assistant"]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        payload = {
            "provider": self.provider,
            "messages": messages
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/agent/chat",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        assistant_message = data.get("response", "No response received")
                        
                        # Add assistant response to history
                        self.session_history.append({
                            "role": "assistant",
                            "content": assistant_message,
                            "timestamp": datetime.now().isoformat()
                        })
                        
                        return assistant_message
                    else:
                        error_text = await response.text()
                        return f"Error {response.status}: {error_text}"
        except Exception as e:
            return f"Request failed: {e}"

    def display_response(self, response: str):
        """Display the agent response with proper formatting."""
        # Check if response contains code blocks
        if "```" in response:
            parts = response.split("```")
            for i, part in enumerate(parts):
                if i % 2 == 0:  # Regular text
                    if part.strip():
                        console.print(Markdown(part))
                else:  # Code block
                    lines = part.split('\n')
                    if lines and lines[0].strip():  # First line might be language
                        language = lines[0].strip()
                        code = '\n'.join(lines[1:])
                    else:
                        language = "text"
                        code = part
                    
                    if code.strip():
                        syntax = Syntax(code, language, theme="monokai", line_numbers=True)
                        console.print(Panel(syntax, title=f"Code ({language})", expand=False))
        else:
            console.print(Markdown(response))

    def save_session(self, filename: str = None):
        """Save chat session to file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bb_agent_session_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump({
                "provider": self.provider,
                "base_url": self.base_url,
                "messages": self.session_history
            }, f, indent=2)
        
        console.print(f"[green]Session saved to {filename}[/green]")

    def load_session(self, filename: str):
        """Load chat session from file."""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                self.session_history = data.get("messages", [])
                console.print(f"[green]Session loaded from {filename}[/green]")
                console.print(f"[blue]Loaded {len(self.session_history)} messages[/blue]")
        except Exception as e:
            console.print(f"[red]Could not load session: {e}[/red]")

async def main():
    parser = argparse.ArgumentParser(description="BB Agent Manager Chat Client")
    parser.add_argument("--provider", choices=["ollama", "gemini"], default="ollama",
                      help="AI provider to use")
    parser.add_argument("--model", help="Specific model to use (optional)")
    parser.add_argument("--base-url", default="http://localhost:8001",
                      help="BB Agent Manager service URL")
    parser.add_argument("--load-session", help="Load previous chat session")
    
    args = parser.parse_args()

    # Create client
    client = BBAgentChatClient(base_url=args.base_url, provider=args.provider)

    # Load session if requested
    if args.load_session:
        client.load_session(args.load_session)

    # Check service health
    console.print("[blue]Checking BB Agent Manager service...[/blue]")
    if not await client.check_health():
        console.print("[red]BB Agent Manager service is not running![/red]")
        console.print("[yellow]Start the service with: python test_server.py[/yellow]")
        sys.exit(1)

    # Get available tools
    tools = await client.get_available_tools()
    
    # Display welcome banner
    welcome_table = Table(title="BB Agent Manager Chat Client")
    welcome_table.add_column("Setting", style="cyan")
    welcome_table.add_column("Value", style="green")
    
    welcome_table.add_row("Provider", args.provider)
    welcome_table.add_row("Service URL", args.base_url)
    welcome_table.add_row("Available Tools", ", ".join(tools) if tools else "None")
    welcome_table.add_row("Model", args.model or f"Default ({args.provider})")
    
    console.print(welcome_table)
    console.print()

    # Display usage examples
    examples_panel = Panel.fit("""
[bold]Example Commands:[/bold]

💡 Code Review:
   "Review this function: def process(data): return [x*2 for x in data if x > 0]"

📝 Documentation:
   "Document the authentication system in src/auth.py with OAuth2 flow details"

🔧 Git Operations:
   "Check git status and commit any pending changes with a descriptive message"

🧪 Testing:
   "Run tests for the user authentication module and analyze any failures"

📋 Component Analysis:
   "Analyze the payment gateway integration for reusability across projects"

💾 Session Commands:
   "/save [filename]" - Save chat session
   "/load filename" - Load chat session  
   "/tools" - List available tools
   "/help" - Show this help
   "/quit" - Exit chat
    """, title="Usage Guide", border_style="blue")
    
    console.print(examples_panel)
    console.print()

    # Main chat loop
    console.print("[bold green]BB Agent is ready! Type your message or /help for commands.[/bold green]")
    
    while True:
        try:
            # Get user input
            user_input = Prompt.ask("\n[bold blue]You[/bold blue]", default="")
            
            if not user_input.strip():
                continue
                
            # Handle special commands
            if user_input.startswith("/"):
                command_parts = user_input[1:].split()
                command = command_parts[0].lower()
                
                if command == "quit" or command == "exit":
                    break
                elif command == "help":
                    console.print(examples_panel)
                    continue
                elif command == "save":
                    filename = command_parts[1] if len(command_parts) > 1 else None
                    client.save_session(filename)
                    continue
                elif command == "load":
                    if len(command_parts) > 1:
                        client.load_session(command_parts[1])
                    else:
                        console.print("[red]Usage: /load filename[/red]")
                    continue
                elif command == "tools":
                    tools = await client.get_available_tools()
                    if tools:
                        tools_table = Table(title="Available Tools")
                        tools_table.add_column("Tool Name", style="cyan")
                        for tool in tools:
                            tools_table.add_row(tool)
                        console.print(tools_table)
                    else:
                        console.print("[yellow]No tools available[/yellow]")
                    continue
                elif command == "clear":
                    client.session_history = []
                    console.print("[green]Session history cleared[/green]")
                    continue
                else:
                    console.print(f"[red]Unknown command: {command}[/red]")
                    continue

            # Send message to agent
            console.print("\n[bold yellow]🤖 BB Agent is thinking...[/bold yellow]")
            
            response = await client.chat(user_input)
            
            console.print(f"\n[bold green]🤖 BB Agent[/bold green]:")
            client.display_response(response)
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Chat interrupted. Use /quit to exit properly.[/yellow]")
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")

    # Save session on exit
    if client.session_history:
        save_exit = Prompt.ask("\nSave this session before exiting?", choices=["y", "n"], default="y")
        if save_exit.lower() == "y":
            client.save_session()

    console.print("\n[bold blue]Thanks for using BB Agent Manager! 👋[/bold blue]")

if __name__ == "__main__":
    # Install required packages message
    try:
        import rich
        import aiohttp
    except ImportError:
        print("Required packages not installed. Run:")
        print("pip install rich aiohttp")
        sys.exit(1)
    
    asyncio.run(main())

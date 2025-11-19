#!/usr/bin/env python3
"""
Buildly Labs Workflow CLI
Interactive tool for logging in, selecting products, and working on tasks
"""
import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from bb_agent_manager.tools.buildly_auth import BuildlyLabsClient
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich import box
import json

console = Console()

async def interactive_login():
    """Interactive login flow"""
    console.print("\n[bold cyan]🔐 Buildly Labs Login[/bold cyan]\n")
    
    # Check for saved session
    client = BuildlyLabsClient()
    saved = await client.load_saved_session()
    
    if saved.get("success"):
        user = saved.get("user", {})
        console.print(f"[green]Found saved session for {user.get('name', 'user')}[/green]")
        
        if Confirm.ask("Use saved session?", default=True):
            return client
        else:
            await client.logout()
    
    # Get credentials
    username = Prompt.ask("Username or email")
    password = Prompt.ask("Password", password=True)
    
    # Login
    result = await client.login(username, password)
    
    if result.get("success"):
        console.print(f"\n[green]✅ {result['message']}[/green]")
        return client
    else:
        console.print(f"\n[red]❌ Login failed: {result.get('error')}[/red]")
        return None

async def select_organization(client: BuildlyLabsClient):
    """Interactive organization selection"""
    console.print("\n[bold cyan]🏢 Select Organization[/bold cyan]\n")
    
    # Get organizations
    result = await client.get_organizations()
    
    if not result.get("success"):
        console.print(f"[red]Error: {result.get('error')}[/red]")
        return False
    
    orgs = result.get("organizations", [])
    
    if not orgs:
        console.print("[yellow]No organizations found[/yellow]")
        return False
    
    # Auto-select if only one
    if len(orgs) == 1:
        org = orgs[0]
        console.print(f"[green]Auto-selected: {org.get('name')}[/green]")
        await client.select_organization(org["id"])
        return True
    
    # Display table
    table = Table(title="Your Organizations", box=box.ROUNDED)
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Role", style="yellow")
    
    for org in orgs:
        table.add_row(
            str(org.get("id")),
            org.get("name", "Unnamed"),
            org.get("role", "Member")
        )
    
    console.print(table)
    
    # Get selection
    org_id = Prompt.ask("\nSelect organization ID", choices=[str(o["id"]) for o in orgs])
    
    result = await client.select_organization(int(org_id))
    
    if result.get("success"):
        console.print(f"\n[green]✅ {result['message']}[/green]")
        return True
    else:
        console.print(f"\n[red]❌ {result.get('error')}[/red]")
        return False

async def select_product(client: BuildlyLabsClient):
    """Interactive product selection"""
    console.print("\n[bold cyan]📦 Select Product[/bold cyan]\n")
    
    if not client.selected_org:
        console.print("[red]No organization selected[/red]")
        return False
    
    # Get products
    result = await client.get_products()
    
    if not result.get("success"):
        console.print(f"[red]Error: {result.get('error')}[/red]")
        return False
    
    products = result.get("products", [])
    
    if not products:
        console.print("[yellow]No products found in this organization[/yellow]")
        return False
    
    # Auto-select if only one
    if len(products) == 1:
        product = products[0]
        console.print(f"[green]Auto-selected: {product.get('name')}[/green]")
        await client.select_product(product["id"])
        return True
    
    # Display table
    table = Table(title=f"Products in {client.selected_org.get('name')}", box=box.ROUNDED)
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Description", style="white")
    
    for product in products:
        table.add_row(
            str(product.get("id")),
            product.get("name", "Unnamed"),
            product.get("description", "")[:50]
        )
    
    console.print(table)
    
    # Get selection
    product_id = Prompt.ask("\nSelect product ID", choices=[str(p["id"]) for p in products])
    
    result = await client.select_product(int(product_id))
    
    if result.get("success"):
        console.print(f"\n[green]✅ {result['message']}[/green]")
        return True
    else:
        console.print(f"\n[red]❌ {result.get('error')}[/red]")
        return False

async def display_tasks(client: BuildlyLabsClient):
    """Display prioritized tasks"""
    console.print("\n[bold cyan]📋 Prioritized Tasks[/bold cyan]\n")
    
    result = await client.get_prioritized_tasks()
    
    if not result.get("success"):
        console.print(f"[red]Error: {result.get('error')}[/red]")
        return
    
    tasks = result.get("tasks", {})
    total = result.get("total", 0)
    
    if total == 0:
        console.print("[yellow]No tasks found for this product[/yellow]")
        return
    
    # Features
    if tasks.get("features"):
        table = Table(title="🚀 Features", box=box.ROUNDED, show_header=True)
        table.add_column("ID", style="cyan", width=8)
        table.add_column("Priority", style="yellow", width=10)
        table.add_column("Title", style="green")
        table.add_column("Status", style="blue", width=12)
        
        for feature in tasks["features"][:10]:  # Top 10
            table.add_row(
                str(feature.get("id")),
                str(feature.get("priority", "N/A")),
                feature.get("title", "Untitled"),
                feature.get("status", "Open")
            )
        
        console.print(table)
        console.print()
    
    # Issues
    if tasks.get("issues"):
        table = Table(title="🐛 Issues", box=box.ROUNDED, show_header=True)
        table.add_column("ID", style="cyan", width=8)
        table.add_column("Priority", style="red", width=10)
        table.add_column("Title", style="green")
        table.add_column("Status", style="blue", width=12)
        
        for issue in tasks["issues"][:10]:  # Top 10
            table.add_row(
                str(issue.get("id")),
                str(issue.get("priority", "N/A")),
                issue.get("title", "Untitled"),
                issue.get("status", "Open")
            )
        
        console.print(table)
        console.print()
    
    # Punchlist
    if tasks.get("punchlist"):
        table = Table(title="✅ Punchlist Items", box=box.ROUNDED, show_header=True)
        table.add_column("ID", style="cyan", width=8)
        table.add_column("Priority", style="yellow", width=10)
        table.add_column("Title", style="green")
        table.add_column("Status", style="blue", width=12)
        
        for item in tasks["punchlist"][:10]:  # Top 10
            table.add_row(
                str(item.get("id")),
                str(item.get("priority", "N/A")),
                item.get("title", "Untitled"),
                item.get("status", "Open")
            )
        
        console.print(table)
        console.print()
    
    console.print(f"[bold]Total: {total} tasks[/bold]")

async def main_menu(client: BuildlyLabsClient):
    """Main menu for workflow actions"""
    while True:
        console.print("\n[bold cyan]🤖 BB Agent Manager - Buildly Labs[/bold cyan]\n")
        
        # Display current context
        info_table = Table(box=box.SIMPLE)
        info_table.add_column("Context", style="cyan")
        info_table.add_column("Value", style="green")
        
        if client.user_info:
            info_table.add_row("User", client.user_info.get("name", "Unknown"))
        if client.selected_org:
            info_table.add_row("Organization", client.selected_org.get("name", "Unknown"))
        if client.selected_product:
            info_table.add_row("Product", client.selected_product.get("name", "Unknown"))
        
        console.print(info_table)
        console.print()
        
        # Menu options
        console.print("[1] View Tasks")
        console.print("[2] Change Product")
        console.print("[3] Change Organization")
        console.print("[4] Associate API with Product")
        console.print("[5] Export Configuration")
        console.print("[6] Logout")
        console.print("[7] Exit")
        
        choice = Prompt.ask("\nSelect action", choices=["1", "2", "3", "4", "5", "6", "7"])
        
        if choice == "1":
            await display_tasks(client)
        elif choice == "2":
            await select_product(client)
        elif choice == "3":
            await select_organization(client)
            await select_product(client)
        elif choice == "4":
            await associate_api_interactive(client)
        elif choice == "5":
            export_config(client)
        elif choice == "6":
            await client.logout()
            console.print("[green]Logged out successfully[/green]")
            break
        elif choice == "7":
            break

async def associate_api_interactive(client: BuildlyLabsClient):
    """Interactive API association"""
    if not client.selected_product:
        console.print("[red]No product selected[/red]")
        return
    
    console.print(f"\n[bold cyan]🔌 Associate API with {client.selected_product.get('name')}[/bold cyan]\n")
    
    api_name = Prompt.ask("API Name")
    api_url = Prompt.ask("API Base URL")
    api_description = Prompt.ask("API Description (optional)", default="")
    
    result = await client.associate_api_with_product(
        client.selected_product["id"],
        api_name,
        api_url,
        api_description if api_description else None
    )
    
    if result.get("success"):
        console.print(f"\n[green]✅ {result['message']}[/green]")
    else:
        console.print(f"\n[red]❌ {result.get('error')}[/red]")

def export_config(client: BuildlyLabsClient):
    """Export configuration for use with BB Agent"""
    console.print("\n[bold cyan]📄 Export Configuration[/bold cyan]\n")
    
    config = {
        "LABS_BASE_URL": client.base_url,
        "LABS_API_TOKEN": client.token,
        "BUILDLY_ORG_ID": client.selected_org.get("id") if client.selected_org else None,
        "BUILDLY_ORG_NAME": client.selected_org.get("name") if client.selected_org else None,
        "BUILDLY_PRODUCT_ID": client.selected_product.get("id") if client.selected_product else None,
        "BUILDLY_PRODUCT_NAME": client.selected_product.get("name") if client.selected_product else None,
    }
    
    # Display
    panel_content = "\n".join([f"export {k}='{v}'" for k, v in config.items() if v])
    console.print(Panel(panel_content, title="Environment Variables", border_style="green"))
    
    # Save to file
    if Confirm.ask("\nSave to .env file?", default=True):
        with open(".env", "a") as f:
            f.write("\n# Buildly Labs Configuration\n")
            for k, v in config.items():
                if v:
                    f.write(f"{k}={v}\n")
        console.print("[green]Configuration saved to .env[/green]")

async def main():
    """Main entry point"""
    console.print(Panel.fit(
        "[bold cyan]BB Agent Manager[/bold cyan]\n"
        "[white]Buildly Labs Workflow Integration[/white]",
        border_style="cyan"
    ))
    
    # Login
    client = await interactive_login()
    if not client:
        return
    
    # Select organization
    if not client.selected_org:
        if not await select_organization(client):
            return
    
    # Select product
    if not client.selected_product:
        if not await select_product(client):
            return
    
    # Main menu
    await main_menu(client)
    
    console.print("\n[bold cyan]👋 Thank you for using BB Agent Manager![/bold cyan]\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)

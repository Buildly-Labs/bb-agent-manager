#!/usr/bin/env python3
"""
BB Agent Manager - AI Work Coach
Integrated AI assistant for task management, prioritization, and work guidance

This is the main orchestrator that:
1. Authenticates with Buildly Labs
2. Fetches tasks from the selected product
3. Uses AI to analyze and prioritize work
4. Guides the developer through task execution
5. Updates task states and adds insights as work progresses

Usage:
    python scripts/ai_work_coach.py [--provider claude] [--product_id ID]
"""

import asyncio
import json
import sys
from typing import Dict, Any, Optional, List
from pathlib import Path
import argparse
from datetime import datetime
from enum import Enum

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from bb_agent_manager.tools.buildly_auth import get_buildly_client
from bb_agent_manager.config import AgentSettings
from bb_agent_manager.llm.router import get_provider


class WorkMode(str, Enum):
    """Work modes for the coach"""
    PLAN = "plan"  # Initial planning and prioritization
    EXECUTE = "execute"  # Active task execution
    REVIEW = "review"  # Review completed work
    REFLECT = "reflect"  # Retrospective analysis


class AIWorkCoach:
    """AI-powered work coach and task manager"""
    
    def __init__(self, provider_hint: str = "claude"):
        self.settings = AgentSettings()
        self.provider = get_provider(self.settings, provider_hint)
        self.client = get_buildly_client(self.settings.labs_base_url)
        self.provider_name = provider_hint
        
        # Work session state
        self.current_product: Optional[Dict] = None
        self.current_org: Optional[Dict] = None
        self.tasks: Dict[str, List[Dict]] = {}
        self.work_plan: Optional[str] = None
        self.current_task: Optional[Dict] = None
        self.session_log: List[Dict] = []
    
    async def login(self, use_saved: bool = True) -> bool:
        """Authenticate with Buildly Labs"""
        print("\n🔐 Authenticating with Buildly Labs...")
        
        if use_saved:
            result = await self.client.load_saved_session()
            if result.get("success"):
                user = result.get("user", {})
                print(f"✓ Logged in as {user.get('name', 'Unknown')}")
                return True
        
        print("❌ No saved session available")
        print("Please run: python scripts/test_buildly_integration.py")
        return False
    
    async def select_product(self, product_id: Optional[int] = None) -> bool:
        """Select a product to work on"""
        print("\n📦 Selecting Product")
        print("-" * 70)
        
        if product_id:
            result = await self.client.select_product(product_id)
            if result.get("success"):
                self.current_product = result.get("product")
                print(f"✓ Selected: {self.current_product.get('name')}")
                return True
        else:
            # List available products
            result = await self.client.get_products()
            if result.get("success"):
                products = result.get("products", [])
                if not products:
                    print("❌ No products available")
                    return False
                
                print(f"Found {len(products)} products:")
                for i, prod in enumerate(products, 1):
                    print(f"  {i}. {prod.get('name')} (ID: {prod.get('id')})")
                
                choice = input("\nSelect product (number): ").strip()
                try:
                    selected = products[int(choice) - 1]
                    result = await self.client.select_product(selected.get("id"))
                    if result.get("success"):
                        self.current_product = result.get("product")
                        print(f"✓ Selected: {self.current_product.get('name')}")
                        return True
                except (ValueError, IndexError):
                    print("❌ Invalid selection")
        
        return False
    
    async def fetch_tasks(self) -> bool:
        """Fetch all tasks for current product"""
        print("\n📋 Fetching Tasks")
        print("-" * 70)
        
        if not self.current_product:
            print("❌ No product selected")
            return False
        
        result = await self.client.get_prioritized_tasks()
        
        if result.get("success"):
            self.tasks = result.get("tasks", {})
            total = result.get("total", 0)
            
            print(f"✓ Retrieved {total} tasks:")
            for task_type, items in self.tasks.items():
                print(f"  • {task_type.capitalize()}: {len(items)}")
            
            return True
        else:
            print(f"❌ Failed to fetch tasks: {result.get('error')}")
            return False
    
    def _format_tasks_for_ai(self) -> str:
        """Format tasks for AI analysis"""
        formatted = "# Current Tasks\n\n"
        
        for task_type, items in self.tasks.items():
            if items:
                formatted += f"## {task_type.capitalize()} ({len(items)} items)\n\n"
                for task in items[:8]:  # Limit to top 8 per category
                    formatted += f"### {task.get('title')} (ID: {task.get('id')})\n"
                    formatted += f"- Priority: {task.get('priority', 'medium')}\n"
                    formatted += f"- Status: {task.get('status', 'open')}\n"
                    formatted += f"- Description: {task.get('description', 'N/A')[:150]}\n\n"
        
        return formatted
    
    async def create_work_plan(self) -> bool:
        """Use AI to create an optimized work plan"""
        print("\n🎯 Creating AI-Powered Work Plan")
        print("-" * 70)
        
        tasks_context = self._format_tasks_for_ai()
        
        prompt = f"""
You are an expert software engineering project manager. Analyze these tasks and create an optimal work plan:

{tasks_context}

Please provide:
1. **Priority-Ranked Execution Plan**: Order tasks by impact/effort ratio
2. **Dependencies**: Identify task dependencies and sequencing
3. **Risk Assessment**: Key risks and mitigation strategies
4. **Timeline**: Realistic estimates for completion
5. **Weekly Goals**: What should be done in the next week
6. **Quick Wins**: Fast tasks to build momentum
7. **Blockers**: Items preventing progress that need immediate attention

Format as actionable, prioritized steps. Be specific and practical.
"""
        
        try:
            messages = [{"role": "user", "content": prompt}]
            result = await self.provider.chat(messages=messages, tools=[], tool_callback=None)
            
            if result.get("content"):
                self.work_plan = result["content"]
                print("\n✓ Work plan created")
                return True
            else:
                print("❌ Failed to generate work plan")
                return False
        
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    async def display_work_plan(self):
        """Display the current work plan"""
        if not self.work_plan:
            print("❌ No work plan available")
            return
        
        print("\n" + "="*70)
        print("📋 YOUR PERSONALIZED WORK PLAN")
        print("="*70)
        print(self.work_plan)
        print("\n" + "="*70)
    
    async def start_task(self, task_id: int) -> bool:
        """Start working on a specific task"""
        print(f"\n🚀 Starting Task #{task_id}")
        print("-" * 70)
        
        # Find task
        for task_type, items in self.tasks.items():
            for task in items:
                if task.get("id") == task_id:
                    self.current_task = task
                    
                    print(f"Title: {task.get('title')}")
                    print(f"Type: {task_type.capitalize()}")
                    print(f"Priority: {task.get('priority', 'medium')}")
                    print(f"Description: {task.get('description', 'N/A')[:200]}")
                    
                    # Log session
                    self.session_log.append({
                        "timestamp": datetime.now().isoformat(),
                        "action": "start_task",
                        "task_id": task_id,
                        "task_title": task.get("title")
                    })
                    
                    return True
        
        print(f"❌ Task {task_id} not found")
        return False
    
    async def get_task_guidance(self) -> Optional[str]:
        """Get AI guidance for current task"""
        if not self.current_task:
            print("❌ No current task selected")
            return None
        
        print("\n💡 Getting Task Guidance")
        print("-" * 70)
        
        task = self.current_task
        prompt = f"""
You are a helpful coding coach. Provide practical guidance for working on this task:

**Task**: {task.get('title')}
**Type**: {task.get('type', 'feature')}
**Priority**: {task.get('priority', 'medium')}
**Description**: {task.get('description', 'N/A')}

Please provide:
1. **Approach**: How to break down this task into steps
2. **Key Considerations**: Important aspects to focus on
3. **Testing Strategy**: How to validate the work
4. **Potential Pitfalls**: Common mistakes to avoid
5. **Success Criteria**: How to know when it's done
6. **Resources**: Relevant documentation or patterns
7. **Time Estimate**: How long it should take

Be practical and specific to this task.
"""
        
        try:
            messages = [{"role": "user", "content": prompt}]
            result = await self.provider.chat(messages=messages, tools=[], tool_callback=None)
            
            if result.get("content"):
                return result["content"]
        except Exception as e:
            print(f"❌ Error: {e}")
        
        return None
    
    async def complete_task(self, summary: str, commit_hash: Optional[str] = None) -> bool:
        """Mark current task as complete"""
        if not self.current_task:
            print("❌ No current task")
            return False
        
        task_id = self.current_task.get("id")
        task_title = self.current_task.get("title")
        
        print(f"\n✅ Completing Task #{task_id}")
        print("-" * 70)
        print(f"Task: {task_title}")
        print(f"Summary: {summary[:100]}...")
        
        # Log completion
        self.session_log.append({
            "timestamp": datetime.now().isoformat(),
            "action": "complete_task",
            "task_id": task_id,
            "task_title": task_title,
            "summary": summary,
            "commit": commit_hash
        })
        
        # Reset current task
        self.current_task = None
        
        print("✓ Task logged as complete")
        return True
    
    async def save_session(self):
        """Save work session log"""
        session_file = Path(__file__).parent.parent / "work_session.json"
        
        session_data = {
            "timestamp": datetime.now().isoformat(),
            "product": self.current_product.get("name") if self.current_product else None,
            "organization": self.current_org.get("name") if self.current_org else None,
            "work_plan": self.work_plan,
            "log": self.session_log,
            "ai_provider": self.provider_name
        }
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        print(f"✓ Session saved to {session_file}")
    
    async def interactive_coaching_session(self):
        """Run interactive coaching session"""
        print("\n" + "="*70)
        print("🎯 AI WORK COACH - INTERACTIVE SESSION")
        print("="*70)
        
        # 1. Login
        if not await self.login():
            return
        
        # 2. Select product
        product_id = None
        try:
            product_id = int(input("\nEnter product ID (or press Enter to browse): ").strip() or "0")
            if product_id == 0:
                product_id = None
        except ValueError:
            product_id = None
        
        if not await self.select_product(product_id):
            return
        
        # 3. Fetch tasks
        if not await self.fetch_tasks():
            return
        
        # 4. Create work plan
        if input("\nCreate work plan? (y/n): ").lower() == 'y':
            if await self.create_work_plan():
                await self.display_work_plan()
        
        # 5. Interactive loop
        while True:
            print("\n" + "-"*70)
            print("Session Menu:")
            print("  1. View work plan")
            print("  2. Start a task")
            print("  3. Get guidance for current task")
            print("  4. Complete current task")
            print("  5. View all tasks")
            print("  6. Save session & exit")
            print("  7. Exit without saving")
            
            choice = input("\nSelect option (1-7): ").strip()
            
            if choice == "1":
                await self.display_work_plan()
            elif choice == "2":
                task_id = int(input("Enter task ID: ").strip())
                await self.start_task(task_id)
            elif choice == "3":
                guidance = await self.get_task_guidance()
                if guidance:
                    print("\n" + "="*70)
                    print("📚 TASK GUIDANCE")
                    print("="*70)
                    print(guidance)
            elif choice == "4":
                if self.current_task:
                    summary = input("Task summary: ").strip()
                    commit = input("Commit hash (optional): ").strip() or None
                    await self.complete_task(summary, commit)
                else:
                    print("❌ No current task")
            elif choice == "5":
                for task_type, items in self.tasks.items():
                    if items:
                        print(f"\n{task_type.upper()} ({len(items)}):")
                        for task in items[:5]:
                            status = "✓" if task.get("status") == "resolved" else "○"
                            print(f"  {status} #{task.get('id')}: {task.get('title')}")
            elif choice == "6":
                await self.save_session()
                print("Goodbye!")
                break
            elif choice == "7":
                print("Goodbye!")
                break


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="AI Work Coach - Task management & guidance")
    parser.add_argument("--provider", default="claude", help="LLM provider")
    parser.add_argument("--product_id", type=int, help="Product ID")
    parser.add_argument("--mode", default="interactive", help="Mode: interactive, plan, or execute")
    
    args = parser.parse_args()
    
    coach = AIWorkCoach(provider_hint=args.provider)
    
    await coach.interactive_coaching_session()


if __name__ == "__main__":
    asyncio.run(main())

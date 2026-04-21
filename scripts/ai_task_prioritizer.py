#!/usr/bin/env python3
"""
BB Agent Manager - AI-Powered Task Prioritization & Analysis
Analyzes Buildly Labs tasks and provides AI-driven prioritization and recommendations

Usage:
    python scripts/ai_task_prioritizer.py [--product_id ID] [--provider claude] [--analyze]

Example:
    python scripts/ai_task_prioritizer.py --product_id 123 --provider claude --analyze
"""

import asyncio
import json
import sys
from typing import Dict, Any, List, Optional
from pathlib import Path
import argparse
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from bb_agent_manager.tools.buildly_auth import get_buildly_client
from bb_agent_manager.config import AgentSettings
from bb_agent_manager.llm.router import get_provider


class AITaskPrioritizer:
    """AI-powered task prioritization and analysis"""
    
    def __init__(self, provider_hint: str = "claude"):
        self.settings = AgentSettings()
        self.provider = get_provider(self.settings, provider_hint)
        self.client = get_buildly_client(self.settings.labs_base_url)
        self.provider_name = provider_hint
    
    async def login(self, use_saved: bool = True) -> bool:
        """Login to Buildly Labs"""
        print("\n🔐 Buildly Labs Authentication")
        print("-" * 60)
        
        if use_saved:
            result = await self.client.load_saved_session()
            if result.get("success"):
                print(f"✓ Loaded saved session for {result.get('user', {}).get('name')}")
                return True
        
        print("No saved session found. Please login manually via test_buildly_integration.py")
        return False
    
    async def get_tasks_for_analysis(
        self,
        product_id: Optional[int] = None,
        org_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Fetch tasks for analysis"""
        print("\n📋 Fetching Tasks")
        print("-" * 60)
        
        # If no product selected, guide user to select one
        if not self.client.selected_product and product_id:
            # Select organization first if needed
            if org_id:
                await self.client.select_organization(org_id)
            await self.client.select_product(product_id)
        
        if not self.client.selected_product:
            print("❌ No product selected")
            return None
        
        product_name = self.client.selected_product.get("name")
        print(f"📦 Product: {product_name}")
        
        # Fetch all task types
        result = await self.client.get_prioritized_tasks()
        
        if result.get("success"):
            tasks = result.get("tasks", {})
            total = result.get("total", 0)
            
            print(f"✓ Retrieved {total} total tasks:")
            print(f"  • Features: {len(tasks.get('features', []))}")
            print(f"  • Issues: {len(tasks.get('issues', []))}")
            print(f"  • Punchlist: {len(tasks.get('punchlist', []))}")
            
            return tasks
        else:
            print(f"❌ Failed to fetch tasks: {result.get('error')}")
            return None
    
    def _format_tasks_for_analysis(self, tasks: Dict[str, List[Dict]]) -> str:
        """Format tasks for AI analysis"""
        formatted = "## Current Tasks in Buildly Labs\n\n"
        
        for category, items in tasks.items():
            category_name = category.capitalize()
            if items:
                formatted += f"### {category_name} ({len(items)} items)\n\n"
                for i, task in enumerate(items[:10], 1):  # Limit to top 10 per category
                    priority = task.get("priority", "medium")
                    status = task.get("status", "open")
                    title = task.get("title", "Untitled")
                    description = task.get("description", "No description")
                    
                    formatted += f"{i}. **{title}** (Priority: {priority}, Status: {status})\n"
                    formatted += f"   - Description: {description[:100]}...\n"
                    formatted += f"   - ID: {task.get('id')}\n\n"
        
        return formatted
    
    async def analyze_and_prioritize(self, tasks: Dict[str, List[Dict]]) -> Optional[str]:
        """Use AI to analyze and prioritize tasks"""
        print("\n🤖 AI Analysis & Prioritization")
        print("-" * 60)
        print(f"Using provider: {self.provider_name.upper()}")
        
        # Format tasks for analysis
        tasks_text = self._format_tasks_for_analysis(tasks)
        
        # Create analysis prompt
        analysis_prompt = f"""
You are an expert project manager and software engineer. Analyze the following Buildly Labs tasks and provide:

1. **Priority Ranking**: Reorder tasks by priority considering:
   - Business impact
   - Technical complexity
   - Dependencies between tasks
   - Risk mitigation
   - Team capacity

2. **Risk Assessment**: Identify potential blockers or risks

3. **Resource Recommendations**: Suggest which tasks should be assigned to which team members

4. **Timeline**: Suggest a realistic timeline for completion

5. **Next Steps**: What should be done immediately

Tasks to analyze:
{tasks_text}

Please provide a comprehensive analysis with actionable recommendations.
"""
        
        print("Sending tasks to AI for analysis...")
        
        try:
            # Call LLM for analysis
            messages = [
                {"role": "user", "content": analysis_prompt}
            ]
            
            result = await self.provider.chat(
                messages=messages,
                tools=[],  # No tools needed for analysis
                tool_callback=None
            )
            
            if result.get("content"):
                return result["content"]
            else:
                print("❌ No response from AI provider")
                return None
        except Exception as e:
            print(f"❌ Error calling AI provider: {e}")
            return None
    
    async def get_ai_recommendations(self, analysis: str) -> Optional[str]:
        """Get specific action recommendations from AI"""
        print("\n💡 Getting Specific Recommendations")
        print("-" * 60)
        
        recommendation_prompt = f"""
Based on the following task analysis and prioritization:

{analysis}

Please provide:
1. **Top 3 Actions for This Week**: Most impactful work to do now
2. **Quick Wins**: Tasks that can be completed quickly to build momentum
3. **Blockers to Address**: Critical items preventing other work
4. **Team Communication**: Key messages for stakeholders about timeline/status
5. **Optimization Opportunities**: Ways to improve workflow or reduce technical debt

Format as actionable items with estimated effort.
"""
        
        try:
            messages = [
                {"role": "user", "content": recommendation_prompt}
            ]
            
            result = await self.provider.chat(
                messages=messages,
                tools=[],
                tool_callback=None
            )
            
            if result.get("content"):
                return result["content"]
            else:
                return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    async def run_full_analysis(
        self,
        product_id: Optional[int] = None,
        org_id: Optional[int] = None,
        save_results: bool = True
    ):
        """Run complete analysis pipeline"""
        print("\n" + "="*70)
        print("🎯 BB AGENT MANAGER - AI-POWERED TASK ANALYSIS & PRIORITIZATION")
        print("="*70)
        
        # 1. Login
        if not await self.login():
            print("❌ Authentication failed")
            return
        
        # 2. Fetch tasks
        tasks = await self.get_tasks_for_analysis(product_id, org_id)
        if not tasks:
            print("❌ Could not retrieve tasks")
            return
        
        # 3. AI Analysis
        analysis = await self.analyze_and_prioritize(tasks)
        if not analysis:
            print("❌ AI analysis failed")
            return
        
        print("\n" + "="*70)
        print("📊 ANALYSIS RESULTS")
        print("="*70)
        print(analysis)
        
        # 4. Get recommendations
        print("\n" + "-"*70)
        recommendations = await self.get_ai_recommendations(analysis)
        
        if recommendations:
            print("\n" + "="*70)
            print("🎯 RECOMMENDATIONS")
            print("="*70)
            print(recommendations)
        
        # 5. Save results
        if save_results:
            results = {
                "timestamp": datetime.now().isoformat(),
                "product": self.client.selected_product.get("name") if self.client.selected_product else "Unknown",
                "organization": self.client.selected_org.get("name") if self.client.selected_org else "Unknown",
                "analysis": analysis,
                "recommendations": recommendations,
                "ai_provider": self.provider_name
            }
            
            results_file = Path(__file__).parent.parent / "ai_analysis_results.json"
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"\n✓ Results saved to: {results_file}")
    
    async def interactive_mode(self):
        """Interactive task management mode"""
        print("\n" + "="*70)
        print("🎯 INTERACTIVE TASK MANAGEMENT")
        print("="*70)
        
        if not await self.login():
            return
        
        while True:
            print("\n" + "-"*70)
            print("Options:")
            print("  1. Analyze tasks for current product")
            print("  2. View task details")
            print("  3. Change product")
            print("  4. Update task status")
            print("  5. Add comment to task")
            print("  6. Exit")
            
            choice = input("\nSelect option (1-6): ").strip()
            
            if choice == "1":
                tasks = await self.get_tasks_for_analysis()
                if tasks:
                    analysis = await self.analyze_and_prioritize(tasks)
                    if analysis:
                        print("\n" + analysis)
            
            elif choice == "2":
                await self._show_task_details(tasks)
            
            elif choice == "3":
                await self._change_product()
            
            elif choice == "4":
                await self._update_task_status()
            
            elif choice == "5":
                await self._add_task_comment()
            
            elif choice == "6":
                print("Goodbye!")
                break
            
            else:
                print("Invalid option")
    
    async def _show_task_details(self, tasks: Dict[str, List[Dict]]):
        """Show detailed task information"""
        print("\n📋 Task Details")
        for category, items in tasks.items():
            if items:
                print(f"\n{category.upper()}:")
                for task in items[:5]:
                    print(f"\n  ID: {task.get('id')}")
                    print(f"  Title: {task.get('title')}")
                    print(f"  Status: {task.get('status')}")
                    print(f"  Priority: {task.get('priority')}")
                    print(f"  Description: {task.get('description', 'N/A')[:100]}")
    
    async def _change_product(self):
        """Interactive product selection"""
        # Placeholder for product selection logic
        print("Product selection coming soon...")
    
    async def _update_task_status(self):
        """Interactive task status update"""
        # Placeholder for status update logic
        print("Task status update coming soon...")
    
    async def _add_task_comment(self):
        """Interactive comment addition"""
        # Placeholder for comment logic
        print("Task comments coming soon...")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="AI-powered task analysis and prioritization"
    )
    parser.add_argument("--product_id", type=int, help="Product ID")
    parser.add_argument("--org_id", type=int, help="Organization ID")
    parser.add_argument("--provider", default="claude", help="LLM provider (claude, openai, gemini, ollama)")
    parser.add_argument("--analyze", action="store_true", help="Run analysis")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    
    args = parser.parse_args()
    
    prioritizer = AITaskPrioritizer(provider_hint=args.provider)
    
    if args.interactive:
        await prioritizer.interactive_mode()
    else:
        await prioritizer.run_full_analysis(
            product_id=args.product_id,
            org_id=args.org_id,
            save_results=True
        )


if __name__ == "__main__":
    asyncio.run(main())

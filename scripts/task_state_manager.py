#!/usr/bin/env python3
"""
BB Agent Manager - Task State & Comment Manager
Manages task state transitions and adds comments to Buildly Labs tasks

Usage:
    python scripts/task_state_manager.py --task_id ID --action [status|comment]
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
from bb_agent_manager.tools.labs_sync import labs_upsert_task
from bb_agent_manager.config import AgentSettings
from bb_agent_manager.llm.router import get_provider


class TaskStatus(str, Enum):
    """Task status values"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    RESOLVED = "resolved"
    BLOCKED = "blocked"
    ON_HOLD = "on_hold"


class TaskStateManager:
    """Manage task states and comments"""
    
    def __init__(self):
        self.settings = AgentSettings()
        self.client = get_buildly_client(self.settings.labs_base_url)
        self.current_tasks: Dict[int, Dict] = {}
    
    async def login(self, use_saved: bool = True) -> bool:
        """Login to Buildly Labs"""
        if use_saved:
            result = await self.client.load_saved_session()
            if result.get("success"):
                return True
        return False
    
    async def get_task_details(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Get details of a specific task"""
        try:
            # Fetch tasks from current product
            result = await self.client.get_prioritized_tasks()
            
            if not result.get("success"):
                return None
            
            tasks_by_type = result.get("tasks", {})
            
            # Search across all task types
            for task_type, tasks in tasks_by_type.items():
                for task in tasks:
                    if task.get("id") == task_id:
                        self.current_tasks[task_id] = task
                        return task
            
            print(f"❌ Task {task_id} not found")
            return None
        
        except Exception as e:
            print(f"❌ Error fetching task details: {e}")
            return None
    
    async def update_task_status(
        self,
        task_id: int,
        new_status: TaskStatus,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update task status"""
        print(f"\n📝 Updating Task Status")
        print("-" * 60)
        
        # Get current task
        task = await self.get_task_details(task_id)
        if not task:
            print(f"❌ Could not find task {task_id}")
            return False
        
        print(f"Task: {task.get('title')}")
        print(f"Current Status: {task.get('status')}")
        print(f"New Status: {new_status.value}")
        
        # Validate status transition
        current_status = task.get("status")
        if not self._is_valid_transition(current_status, new_status.value):
            print(f"⚠️  Warning: Invalid transition from {current_status} to {new_status.value}")
        
        # Prepare update data
        update_data = {
            "id": task_id,
            "status": new_status.value,
            **task  # Preserve existing fields
        }
        
        if metadata:
            update_data.update(metadata)
        
        # Update via labs_sync
        try:
            result = await labs_upsert_task(update_data)
            
            if result.get("success"):
                print(f"✓ Task status updated successfully")
                return True
            else:
                print(f"❌ Failed to update task: {result.get('error')}")
                return False
        
        except Exception as e:
            print(f"❌ Error updating task: {e}")
            return False
    
    def _is_valid_transition(self, from_status: str, to_status: str) -> bool:
        """Validate status transitions"""
        # Define valid state transitions
        valid_transitions = {
            "open": ["in_progress", "blocked", "on_hold"],
            "in_progress": ["in_review", "blocked", "resolved", "on_hold"],
            "in_review": ["resolved", "in_progress", "blocked"],
            "resolved": ["open"],  # Can reopen if needed
            "blocked": ["in_progress", "open"],
            "on_hold": ["in_progress", "open", "blocked"]
        }
        
        allowed = valid_transitions.get(from_status, [])
        return to_status in allowed
    
    async def add_comment(
        self,
        task_id: int,
        comment_text: str,
        ai_generated: bool = False
    ) -> bool:
        """Add a comment to a task"""
        print(f"\n💬 Adding Comment to Task")
        print("-" * 60)
        
        # Get current task
        task = await self.get_task_details(task_id)
        if not task:
            print(f"❌ Could not find task {task_id}")
            return False
        
        print(f"Task: {task.get('title')}")
        print(f"Comment: {comment_text[:100]}...")
        
        # Prepare comment data
        timestamp = datetime.now().isoformat()
        
        comment_data = {
            "text": comment_text,
            "timestamp": timestamp,
            "ai_generated": ai_generated,
            "type": "ai_analysis" if ai_generated else "manual"
        }
        
        # Add to task's comments array
        comments = task.get("comments", [])
        if not isinstance(comments, list):
            comments = []
        
        comments.append(comment_data)
        
        # Update task with new comments
        update_data = {
            "id": task_id,
            "comments": comments,
            **task  # Preserve existing fields
        }
        
        try:
            result = await labs_upsert_task(update_data)
            
            if result.get("success"):
                print(f"✓ Comment added successfully")
                return True
            else:
                print(f"❌ Failed to add comment: {result.get('error')}")
                return False
        
        except Exception as e:
            print(f"❌ Error adding comment: {e}")
            return False
    
    async def add_ai_insights(
        self,
        task_id: int,
        insights: str,
        priority_recommendation: Optional[str] = None,
        effort_estimate: Optional[str] = None
    ) -> bool:
        """Add AI-generated insights and recommendations to a task"""
        print(f"\n🤖 Adding AI Insights to Task")
        print("-" * 60)
        
        comment_text = f"""
## AI Analysis & Insights

{insights}
"""
        
        if priority_recommendation:
            comment_text += f"\n### Priority Recommendation\n{priority_recommendation}"
        
        if effort_estimate:
            comment_text += f"\n### Effort Estimate\n{effort_estimate}"
        
        comment_text += f"\n\n_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_"
        
        return await self.add_comment(task_id, comment_text, ai_generated=True)
    
    async def bulk_update_statuses(
        self,
        task_updates: List[Dict[str, Any]]
    ) -> Dict[int, bool]:
        """Update multiple tasks at once"""
        print(f"\n📊 Bulk Update Tasks")
        print("-" * 60)
        print(f"Updating {len(task_updates)} tasks...")
        
        results = {}
        
        for update in task_updates:
            task_id = update.get("id")
            new_status = update.get("status")
            metadata = update.get("metadata", {})
            
            print(f"\nTask {task_id}: {new_status}")
            
            try:
                success = await self.update_task_status(
                    task_id,
                    TaskStatus(new_status),
                    metadata
                )
                results[task_id] = success
            except ValueError:
                print(f"❌ Invalid status: {new_status}")
                results[task_id] = False
        
        # Summary
        successful = sum(1 for v in results.values() if v)
        print(f"\n✓ Updated {successful}/{len(task_updates)} tasks")
        
        return results
    
    async def get_task_commit_info(
        self,
        task_id: int,
        commit_hash: str,
        branch: str = "main"
    ) -> Dict[str, Any]:
        """Prepare commit info for task resolution"""
        return {
            "commit_hash": commit_hash,
            "branch": branch,
            "resolved_at": datetime.now().isoformat(),
            "commit_url": f"https://github.com/buildly/bb-agent/commit/{commit_hash}"
        }
    
    async def resolve_task(
        self,
        task_id: int,
        commit_hash: str,
        branch: str = "main",
        summary: Optional[str] = None
    ) -> bool:
        """Resolve a task with commit information"""
        print(f"\n✅ Resolving Task")
        print("-" * 60)
        
        commit_info = await self.get_task_commit_info(task_id, commit_hash, branch)
        
        metadata = {
            "commit_info": commit_info
        }
        
        if summary:
            metadata["resolution_summary"] = summary
        
        success = await self.update_task_status(
            task_id,
            TaskStatus.RESOLVED,
            metadata
        )
        
        if success and summary:
            # Add resolution comment
            comment_text = f"""## Resolution Summary

{summary}

**Commit**: {commit_hash}
**Branch**: {branch}
**Resolved**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            await self.add_comment(task_id, comment_text)
        
        return success
    
    async def interactive_task_manager(self):
        """Interactive task management interface"""
        print("\n" + "="*70)
        print("🎯 INTERACTIVE TASK STATE MANAGER")
        print("="*70)
        
        if not await self.login():
            print("❌ Login failed")
            return
        
        while True:
            print("\n" + "-"*70)
            print("Task Management Options:")
            print("  1. Update task status")
            print("  2. Add comment to task")
            print("  3. Add AI insights to task")
            print("  4. Resolve task with commit")
            print("  5. View task details")
            print("  6. Exit")
            
            choice = input("\nSelect option (1-6): ").strip()
            
            if choice == "1":
                await self._interactive_status_update()
            elif choice == "2":
                await self._interactive_add_comment()
            elif choice == "3":
                await self._interactive_add_insights()
            elif choice == "4":
                await self._interactive_resolve_task()
            elif choice == "5":
                await self._interactive_view_task()
            elif choice == "6":
                print("Goodbye!")
                break
            else:
                print("Invalid option")
    
    async def _interactive_status_update(self):
        """Interactive status update workflow"""
        task_id = int(input("Enter task ID: ").strip())
        
        print("\nAvailable statuses:")
        for status in TaskStatus:
            print(f"  • {status.value}")
        
        new_status = input("Enter new status: ").strip()
        
        try:
            await self.update_task_status(task_id, TaskStatus(new_status))
        except ValueError:
            print("❌ Invalid status")
    
    async def _interactive_add_comment(self):
        """Interactive comment addition"""
        task_id = int(input("Enter task ID: ").strip())
        comment = input("Enter comment: ").strip()
        
        await self.add_comment(task_id, comment)
    
    async def _interactive_add_insights(self):
        """Interactive AI insights addition"""
        task_id = int(input("Enter task ID: ").strip())
        insights = input("Enter AI insights: ").strip()
        
        await self.add_ai_insights(task_id, insights)
    
    async def _interactive_resolve_task(self):
        """Interactive task resolution"""
        task_id = int(input("Enter task ID: ").strip())
        commit_hash = input("Enter commit hash: ").strip()
        branch = input("Enter branch (default: main): ").strip() or "main"
        summary = input("Enter resolution summary: ").strip()
        
        await self.resolve_task(task_id, commit_hash, branch, summary)
    
    async def _interactive_view_task(self):
        """Interactive task detail viewing"""
        task_id = int(input("Enter task ID: ").strip())
        
        task = await self.get_task_details(task_id)
        if task:
            print("\n" + json.dumps(task, indent=2))


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Task state and comment manager")
    parser.add_argument("--task_id", type=int, help="Task ID")
    parser.add_argument("--status", help="New status")
    parser.add_argument("--comment", help="Comment to add")
    parser.add_argument("--commit", help="Commit hash for resolution")
    parser.add_argument("--branch", default="main", help="Git branch")
    parser.add_argument("--summary", help="Resolution summary")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    
    args = parser.parse_args()
    
    manager = TaskStateManager()
    
    if not await manager.login():
        print("❌ Login failed")
        return
    
    if args.interactive:
        await manager.interactive_task_manager()
    elif args.task_id:
        if args.status:
            try:
                await manager.update_task_status(args.task_id, TaskStatus(args.status))
            except ValueError:
                print(f"❌ Invalid status: {args.status}")
        elif args.comment:
            await manager.add_comment(args.task_id, args.comment)
        elif args.commit:
            await manager.resolve_task(
                args.task_id,
                args.commit,
                args.branch,
                args.summary
            )
    else:
        await manager.interactive_task_manager()


if __name__ == "__main__":
    asyncio.run(main())

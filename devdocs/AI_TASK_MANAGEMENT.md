# AI-Powered Task Management Guide

## Overview

BB Agent Manager now includes three powerful AI-driven tools for managing work with Buildly Labs:

1. **AI Work Coach** (`ai_work_coach.py`) - Main orchestrator for guided work sessions
2. **AI Task Prioritizer** (`ai_task_prioritizer.py`) - Deep analysis and prioritization of tasks
3. **Task State Manager** (`task_state_manager.py`) - Update task status and add comments

## Prerequisites

### 1. Buildly Labs Authentication

First, authenticate with Buildly Labs:

```bash
# Run the integration test to authenticate
python scripts/test_buildly_integration.py

# This will:
# - Prompt for your Buildly Labs username and password
# - Test connectivity to https://labs-api.buildly.io
# - Save your session to ~/.bb_agent_config.json
# - Show available organizations and products
```

Once authenticated, all tools will use your saved session.

## 1. AI Work Coach (Main Tool)

**Best for**: Guided work sessions with AI assistance

The Work Coach is your personal AI assistant that:
- Creates optimized work plans based on your tasks
- Guides you through task execution
- Provides contextual advice
- Tracks your progress
- Saves work session logs

### Quick Start

```bash
python scripts/ai_work_coach.py
```

This launches an interactive session where you can:

1. **View your work plan** - AI-generated prioritization of all tasks
2. **Start a task** - Begin working on a specific task ID
3. **Get guidance** - Contextual advice for the current task
4. **Complete tasks** - Mark tasks done with a summary
5. **Save session** - Export your work log to JSON

### Example Session

```bash
$ python scripts/ai_work_coach.py

🎯 AI WORK COACH - INTERACTIVE SESSION
======================================================================

🔐 Authenticating with Buildly Labs...
✓ Logged in as glind

📦 Selecting Product
------
Found 3 products:
  1. BB Agent (ID: 123)
  2. Labs Dashboard (ID: 456)
  3. API Gateway (ID: 789)

Select product (number): 1
✓ Selected: BB Agent

📋 Fetching Tasks
------
✓ Retrieved 12 tasks:
  • Features: 4
  • Issues: 5
  • Punchlist: 3

🎯 Creating AI-Powered Work Plan
------
✓ Work plan created

======================================================================
📋 YOUR PERSONALIZED WORK PLAN
======================================================================

## 1. Priority-Ranked Execution Plan

### Week 1 (High Impact, Low Effort)
1. Fix authentication timeout (Issue #45) - 2 hours
2. Add rate limiting headers (Feature #78) - 3 hours
3. Update API documentation (Punchlist #12) - 1.5 hours

### Week 2 (Medium Impact, Medium Effort)
...

Session Menu:
  1. View work plan
  2. Start a task
  3. Get guidance for current task
  4. Complete current task
  5. View all tasks
  6. Save session & exit
  7. Exit without saving

Select option (1-7): 2
Enter task ID: 45

🚀 Starting Task #45
------
Title: Fix authentication timeout
Type: Issue
Priority: high
Description: Users are experiencing 30-second timeouts...

Session Menu:
  ...
  3. Get guidance for current task

Select option (1-7): 3

💡 Getting Task Guidance
------

🎯 YOUR TASK GUIDANCE
======================================================================

**Approach**: 
1. Check the current session timeout in config.py (line 45)
2. Review the timeout logic in llm/base.py
3. Implement exponential backoff retry strategy
4. Add configurable timeout values to environment
5. Write tests in tests/test_timeout.py
...
```

## 2. AI Task Prioritizer

**Best for**: Deep analysis of your task portfolio and prioritization recommendations

Analyzes all tasks in your product and uses AI to:
- Rank tasks by business impact and effort
- Identify dependencies and blockers
- Assess risks
- Recommend team allocation
- Suggest timeline

### Quick Start

```bash
# Analyze tasks for current product
python scripts/ai_task_prioritizer.py --provider claude

# Analyze specific product
python scripts/ai_task_prioritizer.py --product_id 123 --provider claude

# Interactive mode
python scripts/ai_task_prioritizer.py --interactive
```

### Output Example

```
🎯 BB AGENT MANAGER - AI-POWERED TASK ANALYSIS & PRIORITIZATION
======================================================================

🔐 Buildly Labs Authentication
✓ Loaded saved session for glind

📋 Fetching Tasks
------
📦 Product: BB Agent Manager
✓ Retrieved 12 total tasks:
  • Features: 4
  • Issues: 5
  • Punchlist: 3

🤖 AI Analysis & Prioritization
------
Using provider: CLAUDE

📊 ANALYSIS RESULTS
======================================================================

## 1. Priority Ranking

### Tier 1 (Critical Path - Do First)
1. **Authentication timeout fix** (Issue #45) - 2 hours, unblocks 3 others
2. **MCP tool definitions** (Feature #78) - 4 hours, needed for deployment
3. **Docker compose fix** (Issue #22) - 1 hour, blocks local testing

### Tier 2 (High Value - This Week)
...

## 2. Risk Assessment

**Critical Risks**:
- Docker configuration issues could delay deployment
- LLM provider rate limits need monitoring

...

💡 RECOMMENDATIONS
======================================================================

## Quick Wins (Do Today)
- Fix Docker compose (1 hour)
- Update README (30 min)

## This Week Priority
1. Authentication timeout fix (2 hours)
2. MCP tool definitions (4 hours)
3. Rate limit handling (3 hours)

✓ Results saved to: ai_analysis_results.json
```

## 3. Task State Manager

**Best for**: Updating task status and adding comments/insights

Manages task lifecycle:
- Update status (open → in_progress → in_review → resolved)
- Add comments with observations
- Add AI insights and recommendations
- Mark tasks resolved with commit information

### Quick Start

```bash
# Interactive mode
python scripts/task_state_manager.py --interactive

# Update specific task status
python scripts/task_state_manager.py --task_id 45 --status in_progress

# Add comment to task
python scripts/task_state_manager.py --task_id 45 --comment "Started implementation"

# Resolve task with commit
python scripts/task_state_manager.py \
  --task_id 45 \
  --commit abc123def456 \
  --branch feature/auth-timeout \
  --summary "Implemented exponential backoff retry strategy"
```

### Task Status Flow

```
┌─────────┐
│  OPEN   │ ← New task starts here
└────┬────┘
     │
     ├─→ IN_PROGRESS ─→ IN_REVIEW ─→ RESOLVED ✓
     │
     ├─→ BLOCKED (needs investigation/unblocking)
     │
     └─→ ON_HOLD (deprioritized or waiting)
```

### Interactive Mode Example

```bash
$ python scripts/task_state_manager.py --interactive

🎯 INTERACTIVE TASK STATE MANAGER
======================================================================

Task Management Options:
  1. Update task status
  2. Add comment to task
  3. Add AI insights to task
  4. Resolve task with commit
  5. View task details
  6. Exit

Select option (1-6): 3

Add AI Insights to Task
------
Enter task ID: 45

🤖 Adding AI Insights to Task
------
Task: Fix authentication timeout
Enter AI insights: This timeout issue affects 30% of requests.
Implementation should use exponential backoff with jitter.
Maximum wait time should be configurable via environment variable.

Enter priority recommendation: HIGH - Fix immediately, blocks other work

Enter effort estimate: 2-3 hours

✓ Comment added successfully
```

## Complete Workflow Example

Here's how to use all three tools together:

### Step 1: Initial Planning Session

```bash
# Run prioritizer to understand the full task landscape
python scripts/ai_task_prioritizer.py --provider claude

# Review the analysis to understand priority and effort
```

### Step 2: Start Your Work Coach Session

```bash
# Launch the main work coach
python scripts/ai_work_coach.py

# This creates an optimized work plan and guides you through tasks
```

### Step 3: During Task Execution

```bash
# If you want to add AI analysis to a task
python scripts/task_state_manager.py --task_id 45 --comment "Started work"

# Or update status as you progress
python scripts/task_state_manager.py --task_id 45 --status in_progress
```

### Step 4: After Completing Work

```bash
# Mark task resolved with commit info
python scripts/task_state_manager.py \
  --task_id 45 \
  --commit abc123def456 \
  --summary "Implemented exponential backoff retry with 3-second max wait"
```

## Configuration

### Environment Variables

All tools use these environment variables from `.env`:

```bash
# Buildly Labs API
LABS_BASE_URL=https://labs-api.buildly.io
LABS_API_TOKEN=<your-jwt-token>  # Auto-populated after login

# LLM Provider Selection
LLM_PROVIDER=claude  # or openai, gemini, ollama

# Claude (Anthropic)
CLAUDE_API_KEY=<your-key>

# OpenAI
OPENAI_API_KEY=<your-key>

# Google Gemini
GEMINI_API_KEY=<your-key>

# Ollama (local)
OLLAMA_BASE_URL=http://localhost:11434
```

### Session Persistence

Your Buildly Labs session is saved to:
```
~/.bb_agent_config.json
```

This includes:
- Your authentication token
- Selected organization and product
- User information

You can delete this file to force re-authentication.

## Output Files

All tools generate JSON results:

### 1. AI Work Coach
- **File**: `work_session.json`
- **Contents**: Work plan, task log, AI provider used
- **Use**: Track your work sessions and review progress

### 2. AI Task Prioritizer
- **File**: `ai_analysis_results.json`
- **Contents**: Full analysis, recommendations, product/org info
- **Use**: Share with team, document prioritization decisions

### 3. Task State Manager
- **Via API**: Updates task state directly in Buildly Labs
- **Logged**: Session activities logged in task comments

## Troubleshooting

### "No saved session found"

**Solution**: Run authentication first:
```bash
python scripts/test_buildly_integration.py
```

### "Task not found"

**Verify**:
1. Task ID is correct
2. Working with correct product
3. Task hasn't been deleted

```bash
# View available tasks
python scripts/ai_work_coach.py
# Then select option 5 to list tasks
```

### "AI provider error"

**Check**:
1. API key is set in `.env`
2. Network connectivity to provider
3. Provider is running (for Ollama)

### "API Token expired"

**Solution**: Re-authenticate:
```bash
rm ~/.bb_agent_config.json
python scripts/test_buildly_integration.py
```

## Advanced Usage

### Batch Task Updates

Use the Task State Manager in a Python script:

```python
from scripts.task_state_manager import TaskStateManager

async def update_tasks():
    manager = TaskStateManager()
    await manager.login()
    
    updates = [
        {"id": 45, "status": "resolved"},
        {"id": 46, "status": "in_progress"},
        {"id": 47, "status": "blocked"}
    ]
    
    results = await manager.bulk_update_statuses(updates)
    print(f"Updated {sum(results.values())}/{len(updates)} tasks")
```

### Custom AI Prompts

Integrate with the LLM provider directly:

```python
from bb_agent_manager.llm.router import get_provider
from bb_agent_manager.config import AgentSettings

settings = AgentSettings()
provider = get_provider(settings, "claude")

result = await provider.chat(
    messages=[{"role": "user", "content": "Your custom prompt"}],
    tools=[],
    tool_callback=None
)
```

## Integration with Development Workflow

### Recommended Process

1. **Morning**: Run AI Task Prioritizer to understand priority
2. **Throughout Day**: Use AI Work Coach for guidance
3. **During Development**: Update task status as you progress
4. **On Completion**: Mark task resolved with commit info
5. **Evening**: Review work session log

### With GitHub Integration

The system can automatically:
- Resolve tasks when PR is merged
- Add AI-generated commit summaries
- Link commits to tasks
- Post progress updates

See [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) for GitHub Actions setup.

## Support

For issues or questions:
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review task comments for AI insights
3. Check `work_session.json` for session logs
4. Run test suite: `python scripts/test_buildly_integration.py`

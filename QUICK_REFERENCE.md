# Quick Reference - All Commands

## Setup (One Time)

### 1. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 2. Authenticate with Buildly Labs
```bash
python scripts/test_buildly_integration.py
# Prompts for username/password
# Saves to ~/.bb_agent_config.json
```

---

## Daily Workflow

### Morning - Get Prioritized Work Plan

```bash
python scripts/ai_task_prioritizer.py
```

**Options:**
```bash
python scripts/ai_task_prioritizer.py --provider claude    # Use Claude
python scripts/ai_task_prioritizer.py --product_id 123     # Specific product
python scripts/ai_task_prioritizer.py --interactive        # Interactive mode
```

**Output:** AI-generated analysis and priorities saved to `ai_analysis_results.json`

---

### Throughout Day - Interactive Work Coach

```bash
python scripts/ai_work_coach.py
```

**Options:**
```bash
python scripts/ai_work_coach.py --provider claude          # Use Claude
python scripts/ai_work_coach.py --product_id 123           # Specific product
```

**Interactive Menu:**
```
1. View work plan
2. Start a task
3. Get guidance for current task
4. Complete current task
5. View all tasks
6. Save session & exit
```

---

### Update Task Status

**Interactive mode:**
```bash
python scripts/task_state_manager.py --interactive
```

**Direct commands:**
```bash
# Update status
python scripts/task_state_manager.py --task_id 45 --status in_progress

# Available statuses:
# - open
# - in_progress
# - in_review
# - resolved
# - blocked
# - on_hold
```

---

### Add Comments

```bash
python scripts/task_state_manager.py --task_id 45 --comment "Your comment here"
```

---

### Mark Task Resolved

```bash
python scripts/task_state_manager.py --task_id 45 \
  --commit abc123def456 \
  --branch feature/my-feature \
  --summary "What was done"
```

---

### Add AI Insights

```bash
python scripts/task_state_manager.py --task_id 45 --interactive
# Select option 3: Add AI insights
```

---

## System Management

### Check System Health

```bash
python verify_buildly_integration.py
```

**Checks:**
- Environment variables
- Dependencies
- Buildly Labs connection
- AI provider setup
- File structure
- Authentication

---

### Run Integration Tests

```bash
python scripts/test_buildly_integration.py
```

**With verbose output:**
```bash
python scripts/test_buildly_integration.py --verbose
```

**With specific credentials:**
```bash
python scripts/test_buildly_integration.py --username glind --password mypass
```

---

### List Available Tasks

```bash
python scripts/ai_work_coach.py
# Select option 5: View all tasks
```

---

## Configuration

### Set API Keys (Optional)

```bash
# Claude (Anthropic) - Recommended
export ANTHROPIC_API_KEY="sk-..."

# Or OpenAI
export OPENAI_API_KEY="sk-..."

# Or Google Gemini
export GEMINI_API_KEY="AIz..."

# Or use local Ollama (no key needed)
# Just ensure ollama serve is running
```

### Edit .env File

```bash
nano .env
# Edit these if needed:
# LABS_API_TOKEN
# LABS_BASE_URL
# BB_AM_DEFAULT_PROVIDER
```

---

## Help & Troubleshooting

### Get Help for Any Command

```bash
python scripts/ai_work_coach.py --help
python scripts/ai_task_prioritizer.py --help
python scripts/task_state_manager.py --help
```

---

### Clear Credentials (Force Re-login)

```bash
rm ~/.bb_agent_config.json
python scripts/test_buildly_integration.py
```

---

### Check Environment

```bash
# Verify Python version
python --version

# Check .env file
cat .env | grep -E "LABS_|PROVIDER"

# Verify API token
grep LABS_API_TOKEN .env

# Check credentials file
cat ~/.bb_agent_config.json
```

---

### Verify Dependencies

```bash
python -c "import httpx, pydantic, anthropic; print('✓ All dependencies OK')"
```

---

### Debug Issues

```bash
# Run tests with verbose output
python scripts/test_buildly_integration.py --verbose

# Check system health
python verify_buildly_integration.py

# Look at help
python scripts/ai_work_coach.py --help
```

---

## Advanced Usage

### Use Different AI Provider

```bash
# For all commands, use --provider flag:
python scripts/ai_task_prioritizer.py --provider openai
python scripts/ai_task_prioritizer.py --provider gemini
python scripts/ai_task_prioritizer.py --provider ollama
```

---

### Batch Update Tasks (Python Script)

```python
from scripts.task_state_manager import TaskStateManager
import asyncio

async def update_multiple():
    manager = TaskStateManager()
    await manager.login()
    
    updates = [
        {"id": 45, "status": "in_progress"},
        {"id": 46, "status": "blocked"},
        {"id": 47, "status": "open"}
    ]
    
    results = await manager.bulk_update_statuses(updates)
    print(f"Updated {sum(results.values())}/{len(updates)} tasks")

asyncio.run(update_multiple())
```

---

### Export Session Data

```bash
# Results are automatically saved to:
# - work_session.json (from ai_work_coach.py)
# - ai_analysis_results.json (from ai_task_prioritizer.py)
# - verification_results.json (from verify_buildly_integration.py)

# View them:
cat work_session.json | python -m json.tool
cat ai_analysis_results.json | python -m json.tool
```

---

## Scheduled Workflows

### Daily Automated Analysis

```bash
# Add to crontab (runs every morning at 9 AM)
0 9 * * * cd /path/to/bb-agent && .venv/bin/python scripts/ai_task_prioritizer.py

# Or use a workflow file (create script):
cat > daily_analysis.sh << 'EOF'
#!/bin/bash
cd /path/to/bb-agent
.venv/bin/python scripts/ai_task_prioritizer.py
EOF

chmod +x daily_analysis.sh
```

---

## Integration with Other Tools

### Pipe to Other Commands

```bash
# Export work plan to file
python scripts/ai_task_prioritizer.py > work_plan_$(date +%Y-%m-%d).txt

# Email results (requires mail command)
python scripts/ai_task_prioritizer.py | mail -s "Daily Work Plan" your@email.com

# Save to Markdown
python scripts/ai_task_prioritizer.py | tee devdocs/daily_plan.md
```

---

## Common Workflows

### Workflow 1: Daily Planning

```bash
# 1. Get prioritized tasks (5 min)
python scripts/ai_task_prioritizer.py

# 2. Start interactive session (10 min)
python scripts/ai_work_coach.py

# 3. Select first task and get guidance
# - Follow the AI advice
# - Mark status as in_progress
# - Save when done
```

### Workflow 2: Complete a Task

```bash
# 1. Start work
python scripts/task_state_manager.py --task_id 45 --status in_progress

# 2. During work: add comments
python scripts/task_state_manager.py --task_id 45 --comment "First part done"

# 3. When complete: mark resolved
python scripts/task_state_manager.py --task_id 45 \
  --commit abc123def456 \
  --summary "Feature complete with tests"

# 4. In evening: review session
cat work_session.json | python -m json.tool
```

### Workflow 3: Team Sync

```bash
# Get latest analysis
python scripts/ai_task_prioritizer.py

# Copy results
cp ai_analysis_results.json team_report_$(date +%Y-%m-%d).json

# Share with team (via email, Slack, etc.)
```

---

## File Locations

### Important Files

```bash
# Configuration
.env                                  # API keys and settings
~/.bb_agent_config.json              # Saved credentials

# Scripts
scripts/ai_work_coach.py             # Main tool
scripts/ai_task_prioritizer.py       # Analysis tool
scripts/task_state_manager.py        # Status tool
scripts/test_buildly_integration.py  # Tests

# Documentation
devdocs/AI_TASK_MANAGEMENT.md        # Complete guide
BUILDLY_INTEGRATION_READY.md         # Setup guide
BUILDLY_LABS_INTEGRATION_GUIDE.md    # Reference

# Output files
work_session.json                     # Session log
ai_analysis_results.json              # Analysis results
verification_results.json             # System check results
```

---

## Environment Variables

```bash
# Required
LABS_BASE_URL                  # Buildly API URL
LABS_API_TOKEN                 # JWT token (auto-set after login)

# Optional - Pick one LLM provider
ANTHROPIC_API_KEY             # For Claude
OPENAI_API_KEY                # For OpenAI
GEMINI_API_KEY                # For Google Gemini
OLLAMA_BASE_URL               # For local Ollama

# Settings
BB_AM_DEFAULT_PROVIDER        # Which provider to use
BB_AM_MOUNT_PATH             # MCP server path
```

---

## Keyboard Shortcuts

**In Interactive Mode:**
```
Ctrl+C      Exit
Ctrl+L      Clear screen
Up/Down     Navigate history (some terminals)
Tab         Auto-complete (some terminals)
```

---

## Quick Fixes

### Issue: "No saved session"
```bash
python scripts/test_buildly_integration.py
```

### Issue: "Task not found"
```bash
# View available tasks
python scripts/ai_work_coach.py
# Then select option 5
```

### Issue: "API error"
```bash
# Check token
grep LABS_API_TOKEN .env

# Re-authenticate
rm ~/.bb_agent_config.json
python scripts/test_buildly_integration.py
```

### Issue: "AI provider error"
```bash
# Check API key is set
echo $ANTHROPIC_API_KEY

# Try different provider
python scripts/ai_work_coach.py --provider ollama
```

---

## Support

- **Documentation**: See `/devdocs` folder
- **Quick Help**: `python scripts/<tool>.py --help`
- **Full Guide**: [BUILDLY_INTEGRATION_READY.md](BUILDLY_INTEGRATION_READY.md)
- **Health Check**: `python verify_buildly_integration.py`

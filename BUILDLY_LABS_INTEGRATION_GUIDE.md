# BB Agent Manager - Buildly Labs Integration

Complete AI-powered task management system integrated with Buildly Labs.

## 🎯 What You Can Do

✅ **Login to Buildly Labs** with your credentials  
✅ **Fetch your tasks** from your organization and products  
✅ **Get AI analysis** of your work items with prioritization  
✅ **Receive guidance** for each task from an AI coach  
✅ **Update task status** as you work (open → in_progress → resolved)  
✅ **Add AI insights** and comments to tasks  
✅ **Track progress** with automated work session logging  

## 🚀 Getting Started

### Step 1: Install Dependencies

```bash
# Install required Python packages
pip install -r requirements.txt

# For AI providers (pick at least one):
# Claude (Anthropic)
export CLAUDE_API_KEY="your-api-key"

# Or OpenAI
export OPENAI_API_KEY="your-api-key"

# Or Google Gemini
export GEMINI_API_KEY="your-api-key"

# Or use local Ollama (no API key needed)
ollama pull llama2  # or your preferred model
```

### Step 2: Authenticate with Buildly Labs

```bash
python scripts/test_buildly_integration.py

# This will:
# 1. Prompt for your Buildly Labs username and password
# 2. Test API connectivity
# 3. Show your organizations and products
# 4. Save your session to ~/.bb_agent_config.json
```

### Step 3: Start Your AI Work Coach

```bash
python scripts/ai_work_coach.py

# Interactive menu:
# 1. View work plan
# 2. Start a task
# 3. Get guidance
# 4. Complete task
# 5. Save session
```

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [AI_TASK_MANAGEMENT.md](devdocs/AI_TASK_MANAGEMENT.md) | Complete guide to all AI tools |
| [BUILDLY_LABS_INTEGRATION.md](devdocs/BUILDLY_LABS_INTEGRATION.md) | API details and configuration |
| [ENVIRONMENT_SETUP.md](devdocs/ENVIRONMENT_SETUP.md) | Initial environment setup |
| [QUICK_START.md](devdocs/QUICK_START.md) | 5-minute quick start |

## 🛠️ Main Tools

### 1. AI Work Coach
**Interactive personal AI assistant for guided work sessions**

```bash
python scripts/ai_work_coach.py
```

Features:
- AI-generated work plans
- Task execution guidance
- Progress tracking
- Session logging

[Full Documentation](devdocs/AI_TASK_MANAGEMENT.md#1-ai-work-coach-main-tool)

### 2. AI Task Prioritizer
**Deep analysis and prioritization of your entire task portfolio**

```bash
python scripts/ai_task_prioritizer.py --provider claude
```

Provides:
- Priority ranking by impact/effort
- Risk assessment
- Team recommendations
- Timeline estimates

[Full Documentation](devdocs/AI_TASK_MANAGEMENT.md#2-ai-task-prioritizer)

### 3. Task State Manager
**Update task status and add comments/insights**

```bash
python scripts/task_state_manager.py --interactive
```

Capabilities:
- Update task status
- Add comments
- Mark tasks resolved
- Add AI insights

[Full Documentation](devdocs/AI_TASK_MANAGEMENT.md#3-task-state-manager)

## 🔌 API Endpoints

The server exposes MCP (Model Context Protocol) endpoints for all Buildly Labs operations:

```bash
# Start the server
python start_agent.py --provider claude

# Login
curl -X POST http://localhost:8001/agent/mcp/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "name": "buildly_login",
    "arguments": {
      "username": "user@example.com",
      "password": "password"
    }
  }'

# Get tasks
curl -X POST http://localhost:8001/agent/mcp/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "name": "buildly_get_tasks",
    "arguments": {}
  }'
```

Available MCP tools:
- `buildly_login` - Login with credentials
- `buildly_select_org` - Choose organization
- `buildly_select_product` - Choose product
- `buildly_get_tasks` - Fetch tasks with priority sorting
- `buildly_resolve_task` - Mark task as resolved
- `buildly_associate_api` - Link API to product

## 📁 Project Structure

```
bb-agent/
├── scripts/
│   ├── ai_work_coach.py              # Main AI coach (interactive)
│   ├── ai_task_prioritizer.py        # Task analysis & prioritization
│   ├── task_state_manager.py         # Status & comment management
│   └── test_buildly_integration.py   # Integration test suite
│
├── bb_agent_manager/
│   ├── tools/
│   │   ├── buildly_auth.py           # Buildly API client (526 lines)
│   │   └── labs_sync.py              # Task sync utility
│   ├── llm/
│   │   ├── router.py                 # LLM provider selection
│   │   ├── claude.py                 # Anthropic integration
│   │   ├── openai_provider.py        # OpenAI integration
│   │   ├── gemini.py                 # Google Gemini integration
│   │   └── ollama.py                 # Local Ollama integration
│   └── mcp/
│       └── server.py                 # MCP JSON-RPC server
│
├── devdocs/
│   ├── AI_TASK_MANAGEMENT.md         # ← START HERE
│   ├── BUILDLY_LABS_INTEGRATION.md   # Technical details
│   ├── QUICK_START.md                # 5-minute setup
│   └── ... more documentation
│
├── .env                              # Configuration (includes API token)
└── requirements.txt                  # Python dependencies
```

## 🔐 Authentication

### First Login
```bash
python scripts/test_buildly_integration.py
# Prompts for username/password
```

### Saved Sessions
Credentials are automatically saved to `~/.bb_agent_config.json`
- Includes: JWT token, organization, product, user info
- Auto-loads on next run
- Delete file to force re-login

### Environment Variables
```bash
# In .env file (created after first login)
LABS_BASE_URL=https://labs-api.buildly.io
LABS_API_TOKEN=eyJhbGci...  # JWT token
```

## 💡 Example Workflow

### 1. First Thing (Morning)

Get an AI-powered analysis of your tasks:

```bash
python scripts/ai_task_prioritizer.py
```

This shows you:
- What's most important to work on
- Estimated effort for each task
- Potential blockers
- Risk assessment

### 2. Plan Your Day

Start an interactive work coach session:

```bash
python scripts/ai_work_coach.py
```

Get:
- Personalized work plan
- Task-by-task guidance
- Timeline estimates
- Progress tracking

### 3. During Development

Update task status as you work:

```bash
# When you start
python scripts/task_state_manager.py --task_id 45 --status in_progress

# Add progress notes
python scripts/task_state_manager.py --task_id 45 \
  --comment "Completed first phase of implementation"

# When done
python scripts/task_state_manager.py --task_id 45 \
  --commit abc123def456 \
  --summary "Implemented feature with comprehensive tests"
```

### 4. End of Day

Review your work session:

```bash
# Check the generated work_session.json
cat work_session.json

# Or review in Buildly Labs UI - all updates are synced
```

## 🧪 Testing

Run the full integration test suite:

```bash
python scripts/test_buildly_integration.py --verbose

# Test results saved to: test_results_buildly.json
```

Verify with tests:

```bash
# Run unit tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_buildly_integration.py -v
```

## ⚙️ Configuration

### LLM Provider Selection

Set via environment variable or argument:

```bash
# Via environment
export LLM_PROVIDER=claude

# Via command line
python scripts/ai_work_coach.py --provider claude

# Options: claude, openai, gemini, ollama
```

### API Keys

Add to `.env` file:

```bash
# Claude
CLAUDE_API_KEY=sk-...

# OpenAI
OPENAI_API_KEY=sk-...

# Google Gemini
GEMINI_API_KEY=AIz...

# Ollama (no key needed, runs locally)
OLLAMA_BASE_URL=http://localhost:11434
```

## 🚨 Troubleshooting

### Authentication Issues

```bash
# Clear saved session
rm ~/.bb_agent_config.json

# Re-authenticate
python scripts/test_buildly_integration.py
```

### No Tasks Appearing

```bash
# Check that product is selected
python scripts/ai_work_coach.py

# Select a product with tasks
```

### AI Provider Errors

```bash
# Verify API key is set
echo $CLAUDE_API_KEY

# Check network connectivity
curl https://api.anthropic.com/v1/models

# Try local Ollama instead
python scripts/ai_work_coach.py --provider ollama
```

## 📖 Learning Resources

1. **New to the system?** → Read [QUICK_START.md](devdocs/QUICK_START.md)
2. **Want deep dive?** → Read [AI_TASK_MANAGEMENT.md](devdocs/AI_TASK_MANAGEMENT.md)
3. **Need API details?** → See [BUILDLY_LABS_INTEGRATION.md](devdocs/BUILDLY_LABS_INTEGRATION.md)
4. **Integrating with code?** → Check [INTEGRATION_GUIDE.md](devdocs/INTEGRATION_GUIDE.md)

## 🎯 Key Features

### ✅ Buildly Labs Integration
- ✓ OAuth/JWT authentication
- ✓ Organization & product selection
- ✓ Task CRUD operations
- ✓ Priority sorting
- ✓ Session persistence

### ✅ AI-Powered Assistance
- ✓ Task prioritization by impact/effort
- ✓ Risk assessment
- ✓ Timeline estimation
- ✓ Contextual guidance
- ✓ Automated insights

### ✅ Task Management
- ✓ Status transitions (open → in_progress → resolved)
- ✓ Comments and notes
- ✓ Commit linking
- ✓ Bulk operations

### ✅ Reporting
- ✓ Work session logs (JSON)
- ✓ Analysis results
- ✓ Progress tracking
- ✓ Team dashboards

## 📞 Support

- **Documentation**: See `/devdocs` folder
- **Issues**: Create an issue on GitHub
- **Questions**: Check FAQ in [QUICK_START.md](devdocs/QUICK_START.md)

## 📜 License

Part of the BB Agent Manager project. See LICENSE file.

---

**Ready to get started?** → [Run ai_work_coach.py](devdocs/AI_TASK_MANAGEMENT.md#1-ai-work-coach-main-tool)

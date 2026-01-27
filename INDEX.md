# BB Agent Manager - Complete Index & Navigation

## 📍 Start Here

**New to the system?**
1. First read: [BUILDLY_INTEGRATION_READY.md](BUILDLY_INTEGRATION_READY.md)
2. Then see: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
3. Full guide: [devdocs/AI_TASK_MANAGEMENT.md](devdocs/AI_TASK_MANAGEMENT.md)

**Status check:**
- Run: `python verify_buildly_integration.py`
- See: [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)

---

## 🎯 Main Tools

### [AI Work Coach](scripts/ai_work_coach.py)
Personal AI assistant for guided work sessions
```bash
python scripts/ai_work_coach.py
```
See: [devdocs/AI_TASK_MANAGEMENT.md#1-ai-work-coach](devdocs/AI_TASK_MANAGEMENT.md)

### [AI Task Prioritizer](scripts/ai_task_prioritizer.py)
Analyze and prioritize your task portfolio
```bash
python scripts/ai_task_prioritizer.py --provider claude
```
See: [devdocs/AI_TASK_MANAGEMENT.md#2-ai-task-prioritizer](devdocs/AI_TASK_MANAGEMENT.md)

### [Task State Manager](scripts/task_state_manager.py)
Update task status and add comments
```bash
python scripts/task_state_manager.py --interactive
```
See: [devdocs/AI_TASK_MANAGEMENT.md#3-task-state-manager](devdocs/AI_TASK_MANAGEMENT.md)

---

## 📚 Documentation

### Getting Started
- [BUILDLY_INTEGRATION_READY.md](BUILDLY_INTEGRATION_READY.md) - Status & setup
- [devdocs/QUICK_START.md](devdocs/QUICK_START.md) - 5-minute quick start
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - All commands
- [README.md](README.md) - Project overview

### Complete Guides
- [devdocs/AI_TASK_MANAGEMENT.md](devdocs/AI_TASK_MANAGEMENT.md) - **Complete usage guide**
- [BUILDLY_LABS_INTEGRATION_GUIDE.md](BUILDLY_LABS_INTEGRATION_GUIDE.md) - Integration reference
- [devdocs/BUILDLY_LABS_INTEGRATION.md](devdocs/BUILDLY_LABS_INTEGRATION.md) - Technical details

### Reference
- [devdocs/ARCHITECTURE.md](devdocs/ARCHITECTURE.md) - System architecture
- [devdocs/ENVIRONMENT_SETUP.md](devdocs/ENVIRONMENT_SETUP.md) - Environment setup
- [devdocs/INTEGRATION_GUIDE.md](devdocs/INTEGRATION_GUIDE.md) - Integration patterns
- [REORGANIZATION_SUMMARY.md](REORGANIZATION_SUMMARY.md) - Project structure

### Status
- [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md) - What's been implemented
- [devdocs/TODO.md](devdocs/TODO.md) - Future work items
- [devdocs/TEST_RESULTS.md](devdocs/TEST_RESULTS.md) - Test results

---

## 🛠️ Utilities

### Health & Testing
- `python verify_buildly_integration.py` - System health check
- `python scripts/test_buildly_integration.py` - Integration tests
- `python -m pytest tests/ -v` - Unit tests

### Workflow
```bash
# 1. Login (first time only)
python scripts/test_buildly_integration.py

# 2. Get work plan
python scripts/ai_task_prioritizer.py

# 3. Start working
python scripts/ai_work_coach.py

# 4. Update status
python scripts/task_state_manager.py --task_id 45 --status in_progress

# 5. Mark complete
python scripts/task_state_manager.py --task_id 45 --commit abc123
```

---

## 📋 Command Reference

**Quick Commands:**
```bash
# See all commands
QUICK_REFERENCE.md

# View work plan
python scripts/ai_task_prioritizer.py

# Interactive work session
python scripts/ai_work_coach.py

# Update task
python scripts/task_state_manager.py --task_id 45 --status in_progress

# Health check
python verify_buildly_integration.py

# Login
python scripts/test_buildly_integration.py
```

See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for complete command reference.

---

## 🏗️ Project Structure

```
bb-agent/
├── INDEX.md                             # ← You are here
├── QUICK_REFERENCE.md                   # All commands
├── BUILDLY_INTEGRATION_READY.md         # Getting started
├── BUILDLY_LABS_INTEGRATION_GUIDE.md    # Reference
├── README.md                            # Project overview
├── IMPLEMENTATION_COMPLETE.md           # Implementation status
│
├── scripts/                             # User tools
│   ├── ai_work_coach.py
│   ├── ai_task_prioritizer.py
│   ├── task_state_manager.py
│   └── test_buildly_integration.py
│
├── bb_agent_manager/                    # Core library
│   ├── tools/buildly_auth.py           # Buildly API (complete)
│   ├── llm/                             # AI providers
│   ├── mcp/                             # MCP server
│   └── config.py                        # Configuration
│
├── devdocs/                             # Documentation
│   ├── AI_TASK_MANAGEMENT.md           # ← Complete guide
│   ├── BUILDLY_LABS_INTEGRATION.md
│   ├── QUICK_START.md
│   ├── ARCHITECTURE.md
│   ├── ENVIRONMENT_SETUP.md
│   ├── INTEGRATION_GUIDE.md
│   └── ... (10+ docs)
│
├── .env                                 # Configuration
├── requirements.txt                     # Dependencies
└── .venv/                               # Python environment
```

---

## ❓ Common Questions

**How do I get started?**
→ Read [BUILDLY_INTEGRATION_READY.md](BUILDLY_INTEGRATION_READY.md)

**What commands do I need?**
→ See [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

**How do I use the tools?**
→ See [devdocs/AI_TASK_MANAGEMENT.md](devdocs/AI_TASK_MANAGEMENT.md)

**How is the system structured?**
→ See [devdocs/ARCHITECTURE.md](devdocs/ARCHITECTURE.md)

**What's been implemented?**
→ See [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)

**How do I troubleshoot issues?**
→ See [devdocs/ENVIRONMENT_SETUP.md](devdocs/ENVIRONMENT_SETUP.md)

---

## 🚀 Quick Start

```bash
# 1. Login (first time only)
python scripts/test_buildly_integration.py

# 2. Get prioritized tasks
python scripts/ai_task_prioritizer.py

# 3. Start interactive session
python scripts/ai_work_coach.py

# 4. Follow the guidance!
```

---

## 📞 Support Resources

- **Quick Commands**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- **Complete Guide**: [devdocs/AI_TASK_MANAGEMENT.md](devdocs/AI_TASK_MANAGEMENT.md)
- **System Check**: `python verify_buildly_integration.py`
- **Help**: `python scripts/<tool>.py --help`

---

**Last Updated**: 2024
**Status**: Production Ready ✅

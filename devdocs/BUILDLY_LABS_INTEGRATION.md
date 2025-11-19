# Buildly Labs Integration Guide

## Overview

BB Agent Manager integrates directly with the Buildly Labs platform, allowing you to:
- **Login** with your Buildly Labs credentials
- **Select** your organization and product
- **View** prioritized features, issues, and punchlist items
- **Work** on tasks using AI assistance
- **Resolve** tasks automatically when commits are merged

## Quick Start

### 1. Interactive Workflow Tool

```bash
# Install required dependencies (if not already installed)
pip install rich httpx

# Run the interactive workflow
python3 buildly_workflow.py
```

This launches an interactive CLI that guides you through:
1. Login to Buildly Labs
2. Organization selection (if you have multiple)
3. Product selection
4. View prioritized tasks
5. Associate APIs with products
6. Export configuration

### 2. API-Based Workflow

```bash
# Start BB Agent server
python3 start_agent.py --provider claude

# Use the Buildly Labs tools via API
curl -X POST http://localhost:8001/agent/mcp/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "name": "buildly_login",
    "arguments": {
      "username": "your-email@example.com",
      "password": "your-password"
    }
  }'
```

## Features

### Authentication & Session Management

**Login with Credentials:**
```python
# Via API
POST /agent/mcp/invoke
{
  "name": "buildly_login",
  "arguments": {
    "username": "user@example.com",
    "password": "password"
  }
}

# Response includes:
{
  "success": true,
  "user": {"id": 123, "name": "John Doe", ...},
  "organizations": [...],  // If user has orgs
  "message": "Welcome, John Doe!"
}
```

**Saved Sessions:**
- Credentials are saved to `~/.bb_agent_config.json`
- Auto-loads on next run
- No need to re-login each time

### Organization & Product Selection

**Select Organization:**
```python
POST /agent/mcp/invoke
{
  "name": "buildly_select_org",
  "arguments": {
    "org_id": 1
  }
}

# Response includes products in that org
{
  "success": true,
  "organization": {"id": 1, "name": "My Company"},
  "products": [...],
  "message": "Selected organization: My Company\n\nFound 3 product(s)..."
}
```

**Select Product:**
```python
POST /agent/mcp/invoke
{
  "name": "buildly_select_product",
  "arguments": {
    "product_id": 5
  }
}

# Response includes task summary
{
  "success": true,
  "product": {"id": 5, "name": "Mobile App"},
  "tasks_summary": {
    "features": 12,
    "issues": 8,
    "punchlist": 24,
    "total": 44
  },
  "message": "Selected product: Mobile App\n\nFound 44 task(s) to work on."
}
```

### Task Management

**Get Prioritized Tasks:**
```python
POST /agent/mcp/invoke
{
  "name": "buildly_get_tasks",
  "arguments": {
    "task_types": ["feature", "issue", "punchlist"]  // Optional filter
  }
}

# Response organized by type and priority
{
  "success": true,
  "tasks": {
    "features": [
      {
        "id": 101,
        "title": "Add user authentication",
        "priority": 1,
        "status": "Open",
        "description": "Implement OAuth2 authentication...",
        "assigned_to": "John Doe"
      },
      ...
    ],
    "issues": [
      {
        "id": 202,
        "title": "Fix null pointer exception in payment",
        "priority": 1,
        "status": "In Progress",
        "severity": "High"
      },
      ...
    ],
    "punchlist": [
      {
        "id": 303,
        "title": "Update API documentation",
        "priority": 2,
        "status": "Open"
      },
      ...
    ]
  },
  "total": 44,
  "product": "Mobile App"
}
```

**Resolve Task After Commit:**
```python
POST /agent/mcp/invoke
{
  "name": "buildly_resolve_task",
  "arguments": {
    "task_id": 101,
    "commit_sha": "a1b2c3d4e5f6",
    "commit_message": "feat: Add OAuth2 authentication system",
    "pr_number": 42  // Optional
  }
}

# Response
{
  "success": true,
  "task": {
    "id": 101,
    "status": "Resolved",
    "resolved_at": "2025-11-19T10:30:00Z",
    "resolved_by": 123,
    "commit_sha": "a1b2c3d4e5f6"
  },
  "message": "Task #101 marked as resolved"
}
```

### API Association

**Associate API with Product:**
```python
POST /agent/mcp/invoke
{
  "name": "buildly_associate_api",
  "arguments": {
    "api_name": "Payment Gateway API",
    "api_url": "https://api.payment.example.com/v1",
    "api_description": "Stripe payment integration"  // Optional
  }
}

# Response
{
  "success": true,
  "api": {
    "id": 10,
    "name": "Payment Gateway API",
    "url": "https://api.payment.example.com/v1",
    "product_id": 5
  },
  "message": "API 'Payment Gateway API' associated with product"
}
```

## Complete Workflow Example

### End-to-End Development Workflow

```bash
# 1. Start interactive workflow
python3 buildly_workflow.py

# Login credentials: user@company.com / password
# Select: Organization "My Company" (ID: 1)
# Select: Product "Mobile App" (ID: 5)

# 2. View prioritized tasks
# Output shows:
# - Feature #101: Add user authentication (Priority: 1)
# - Issue #202: Fix payment bug (Priority: 1)
# - Punchlist #303: Update docs (Priority: 2)

# 3. Work on Feature #101 using Claude Sonnet
export BB_AM_DEFAULT_PROVIDER=claude
export ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
python3 chat_client.py --provider claude

# Chat: "I need to implement OAuth2 authentication for feature #101. 
#        Review the requirements and help me design the solution."

# 4. Generate code with Claude
# Chat: "Generate the OAuth2 authentication middleware and JWT handling"

# 5. Document changes
# Chat: "Document this authentication system in devdocs"

# 6. Create PR
# Chat: "Create a pull request for feature #101 with these changes"

# 7. After PR is merged, resolve the task
curl -X POST http://localhost:8001/agent/mcp/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "name": "buildly_resolve_task",
    "arguments": {
      "task_id": 101,
      "commit_sha": "'$(git rev-parse HEAD)'",
      "commit_message": "feat: Add OAuth2 authentication",
      "pr_number": 42
    }
  }'
```

## Integration with GitHub Copilot & Cursor

### Cursor Workflow

```bash
# 1. Login to Buildly Labs
python3 buildly_workflow.py
# Export configuration to .env

# 2. Start BB Agent
python3 start_agent.py --provider claude

# 3. In Cursor:
# - Open Composer (Cmd/Ctrl+K)
# - Ask: "What tasks should I work on?"

# 4. BB Agent responds with prioritized tasks from Buildly Labs

# 5. Select a task in Cursor
# - Cursor generates code
# - BB Agent handles documentation and PR creation
# - Commit and merge
# - BB Agent auto-resolves task in Buildly Labs
```

### GitHub Copilot Workflow

```bash
# 1. Setup
python3 buildly_workflow.py
export LABS_API_TOKEN=<your-token>

# 2. VS Code with Copilot
# - Open Copilot Chat
# - Ask: "Show me high priority features to work on"

# 3. BB Agent + Copilot collaboration:
# - Copilot suggests code
# - BB Agent documents changes
# - BB Agent creates PR
# - BB Agent resolves task after merge
```

## Environment Variables

```bash
# Buildly Labs Configuration
export LABS_BASE_URL=https://labs.buildly.io/api
export LABS_API_TOKEN=<token-from-login>

# Optional: Pre-configured org/product
export BUILDLY_ORG_ID=1
export BUILDLY_PRODUCT_ID=5

# AI Provider (for task work)
export BB_AM_DEFAULT_PROVIDER=claude
export ANTHROPIC_API_KEY=sk-ant-xxxxx
export ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# GitHub Integration (for PR/commit tracking)
export GITHUB_TOKEN=ghp_xxxxx
export GITHUB_REPO=owner/repo
```

## Automated Task Resolution

### Automatic Resolution on PR Merge

When enabled, tasks are automatically resolved when:
1. PR is created with reference to task (e.g., "Closes #101")
2. All CI checks pass
3. PR is reviewed and approved
4. PR is merged to main
5. BB Agent calls `buildly_resolve_task` automatically

### GitHub Actions Integration

Add to `.github/workflows/buildly-sync.yml`:

```yaml
name: Sync with Buildly Labs

on:
  pull_request:
    types: [closed]

jobs:
  resolve-tasks:
    if: github.event.pull_request.merged == true
    runs-on: ubuntu-latest
    steps:
      - name: Extract task IDs
        id: tasks
        run: |
          # Extract task IDs from PR body
          TASK_IDS=$(echo "${{ github.event.pull_request.body }}" | grep -oP '(?<=#)\d+' | tr '\n' ',')
          echo "task_ids=$TASK_IDS" >> $GITHUB_OUTPUT
      
      - name: Resolve tasks in Buildly Labs
        run: |
          for TASK_ID in $(echo "${{ steps.tasks.outputs.task_ids }}" | tr ',' '\n'); do
            curl -X POST ${{ secrets.BB_AGENT_URL }}/agent/mcp/invoke \
              -H "Content-Type: application/json" \
              -d "{
                \"name\": \"buildly_resolve_task\",
                \"arguments\": {
                  \"task_id\": $TASK_ID,
                  \"commit_sha\": \"${{ github.event.pull_request.merge_commit_sha }}\",
                  \"commit_message\": \"${{ github.event.pull_request.title }}\",
                  \"pr_number\": ${{ github.event.pull_request.number }}
                }
              }"
          done
```

## Security Considerations

### Credential Storage

- Passwords are **never** stored
- Only the API token is saved to `~/.bb_agent_config.json`
- Token is stored with user-only read/write permissions (600)
- Config file location: `~/.bb_agent_config.json`

### Token Management

```python
# Logout clears saved token
await client.logout()

# Token auto-refresh (if API supports it)
# BB Agent automatically refreshes expired tokens
```

### API Access Control

- All API calls require authentication
- Tokens expire after inactivity
- Rate limiting applied
- Audit logging enabled

## Troubleshooting

### Login Issues

```bash
# Check API connectivity
curl https://labs.buildly.io/api/health

# Verify credentials
python3 buildly_workflow.py
# Try login interactively

# Check saved session
cat ~/.bb_agent_config.json
```

### Task Sync Issues

```bash
# Verify product selection
python3 buildly_workflow.py
# Re-select product

# Force refresh tasks
curl -X POST http://localhost:8001/agent/mcp/invoke \
  -d '{"name": "buildly_get_tasks"}'
```

### Resolution Failures

```bash
# Check task exists
# Verify commit SHA is valid
git rev-parse HEAD

# Check PR is merged
gh pr view <number>

# Manual resolution via CLI
python3 buildly_workflow.py
# Select option: Resolve Task
```

## API Reference

### Available Tools

| Tool | Description |
|------|-------------|
| `buildly_login` | Authenticate with username/password |
| `buildly_select_org` | Select organization to work with |
| `buildly_select_product` | Select product to work on |
| `buildly_get_tasks` | Get prioritized tasks (features/issues/punchlist) |
| `buildly_resolve_task` | Mark task as resolved with commit info |
| `buildly_associate_api` | Associate API with current product |

### Tool Parameters

**buildly_login:**
- `username` (required): Username or email
- `password` (required): Password

**buildly_select_org:**
- `org_id` (required): Organization ID

**buildly_select_product:**
- `product_id` (required): Product ID

**buildly_get_tasks:**
- `task_types` (optional): Array of types to filter (feature, issue, punchlist)

**buildly_resolve_task:**
- `task_id` (required): Task ID to resolve
- `commit_sha` (required): Git commit SHA
- `commit_message` (required): Commit message
- `pr_number` (optional): Pull request number

**buildly_associate_api:**
- `api_name` (required): API name
- `api_url` (required): API base URL
- `api_description` (optional): API description

## Best Practices

### 1. Task Workflow
- Start with highest priority tasks
- Work on one task at a time
- Always link commits to tasks
- Resolve tasks only after PR merge

### 2. Organization
- Use consistent naming for APIs
- Document API associations
- Keep task descriptions updated
- Use labels for categorization

### 3. Automation
- Set up GitHub Actions for auto-resolution
- Use draft PRs for AI-generated code
- Require human review before merge
- Auto-close issues on successful resolution

### 4. Security
- Never commit credentials
- Use environment variables
- Rotate tokens regularly
- Enable 2FA on Buildly Labs account

## Summary

Buildly Labs integration provides:

✅ **Seamless Login**: Username/password authentication with session saving
✅ **Multi-Org Support**: Work across multiple organizations and products  
✅ **Prioritized Tasks**: Features, issues, and punchlist items sorted by priority
✅ **AI-Assisted Development**: Use Claude, GPT-4, or Gemini for task work
✅ **Automated Resolution**: Auto-resolve tasks when PRs merge
✅ **API Management**: Associate and track APIs for each product
✅ **GitHub Integration**: Full PR and commit tracking
✅ **Copilot/Cursor Compatible**: Works with all major AI coding assistants

Start managing your Buildly Labs tasks with AI assistance today! 🚀
# Buildly Coding Instructions for GitHub Copilot

You are working in a **Buildly project**. Follow these guidelines on every session.

## At the start of a session

1. Call `buildly_get_current_work_context` to understand what's active in Buildly Labs
2. Call `memory_get_project_summary` to load project context from `buildly_memory/`
3. Call `buildly_get_repo_context` to see current branch and recent commits
4. Do not make architectural decisions before reviewing the above context

## During development

### Before major work
- Check Buildly Labs for the relevant issue/feature
- Read `buildly_memory/current_focus.md` to confirm alignment
- If starting a new piece of work, update `buildly_memory/current_focus.md`

### While coding
- Prefer small, release-sized changes over large refactors
- One concern per PR — don't bundle unrelated fixes
- Reuse existing patterns from `buildly_memory/conventions.md`
- Ask before making destructive changes (dropping data, removing public APIs)
- Never commit secrets, credentials, or `.env` files

### After meaningful changes
- Call `buildly_create_devdocs_summary` with the files changed and what was done
- If a new pattern emerged, call `memory_capture_pattern`
- If a significant architecture decision was made, call `memory_capture_decision`

## Before shipping

Run the Definition of Done check:
```
buildly_definition_of_done_check({
  "task_description": "...",
  "files_changed": [...],
  "tests_run": true,
  "devdocs_updated": true
})
```

Then:
- Update the Buildly Labs issue status: `buildly_update_issue_status`
- Create a draft PR for human review — never force-push or merge without review

## Documentation rules

- All significant code changes get a devdocs entry
- `buildly_memory/` is the source of truth for project context
- `devdocs/` is the developer changelog
- Do not put implementation detail in commit messages — put it in devdocs

## Buildly workflow summary

```
start session
  → check Buildly Labs context
  → load memory summary
  → code change
  → update devdocs
  → capture decisions/patterns
  → DoD check
  → update Labs issue
  → draft PR
  → end session note
```

## What this MCP server does NOT do

- It does not select or switch AI models — that is Copilot's / the client's job
- It does not execute code or run tests directly (use terminal for that)
- It does not auto-merge PRs or close issues without human confirmation

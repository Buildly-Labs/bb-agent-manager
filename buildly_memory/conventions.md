# Conventions

## Code style

- **Python 3.11+** with full type hints on all function signatures
- **Ruff** for formatting and linting (line length 100)
- **Double quotes** for strings
- **Imports**: stdlib → third-party → local, sorted

## Naming conventions

| Type | Convention | Example |
|------|------------|---------|
| Variables | snake_case | `issue_id`, `memory_path` |
| Functions | snake_case | `get_token()`, `handle()` |
| Classes | PascalCase | `MarkdownMemory`, `BuildlySettings` |
| Constants | SCREAMING_SNAKE | `TOOL_NAMES`, `_ORG_MEMORY_ROOT` |
| Files | snake_case | `buildly_labs.py`, `memory_service.py` |

## Tool module pattern

Each tool module must export:
```python
TOOLS: list[Tool]          # MCP tool schemas
TOOL_NAMES: set[str]       # for routing in server.py
async def handle(name, arguments, settings) -> dict  # implementation
```

## Memory rules

- Permanent facts → markdown files in `buildly_memory/`
- Session notes → `buildly_memory/sessions/`
- Decisions → `buildly_memory/decisions/`
- Cross-project patterns → promoted to `~/.buildly/memory/`
- No free-form dumping — structured entries with date + title

## Buildly workflow

1. Check Buildly Labs context before major work (`buildly_get_current_work_context`)
2. Update devdocs after meaningful changes (`buildly_create_devdocs_summary`)
3. Capture decisions when architecture choices are made (`memory_capture_decision`)
4. Run DoD check before shipping (`buildly_definition_of_done_check`)
5. Update Buildly issue status when work starts/completes (`buildly_update_issue_status`)
6. Small, release-sized changes preferred over large refactors

## Testing

- pytest for all tests
- Async tests use `pytest-asyncio`
- Tests live in `tests/` folder
- Coverage target: 70% overall

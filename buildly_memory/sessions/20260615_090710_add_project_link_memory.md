# Add project link memory

_Session: 2026-06-15 09:07_

## Summary
- Added `buildly_remember_project_link` and `buildly_get_project_link` tools.
- Persisted repo-to-Buildly project links in `buildly_memory/project_links.md`.
- Surfaced remembered project links in `buildly_get_environment_context`.
- Documented the login/token -> choose product -> bind repo workflow in the README.

## Notes
- The new link registry is markdown-backed and created automatically by `MarkdownMemory`.
- The repo continues to use the stdio MCP server path.
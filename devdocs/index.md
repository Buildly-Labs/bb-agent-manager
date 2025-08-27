# DevDocs Index

This directory contains developer documentation for the BB Agent Manager project. All significant changes should be documented here with summaries and component reuse notes.

## Documentation Standards

When making changes to the codebase:

1. **Document Changes**: Add entries for significant modifications, new features, or architectural decisions
2. **Include Summary**: Provide clear, concise description of what was changed and why
3. **Component Reuse Notes**: Document any reusable components, patterns, or utilities created
4. **Link to Issues**: Reference related GitHub issues or Buildly Labs tasks when applicable

## Format

Each entry should follow this format:

```markdown
## [Date] - [Change Title]

**Files:** list, of, modified, files.py

**Summary:** Brief description of the change and its purpose.

**Component Reuse Notes:** Description of any reusable components, patterns, or utilities created that could benefit other projects.

**Related Issues:** Links to GitHub issues or Labs tasks

---
```

## Change Log

### 2025-08-27 - Initial Project Setup

**Files:** All project files

**Summary:** Created bb-agent-manager as a pluggable AI development assistant for BabbleBeaver platform. Includes LLM provider abstraction (Gemini/Ollama), development tools for documentation automation, Buildly Labs integration, and MCP-compatible tool server.

**Component Reuse Notes:** 
- `LLMProvider` base class can be extended for additional AI providers
- Tool definition pattern using TypedDict for schema validation
- FastAPI plugin registration pattern via entry points
- Async tool execution with callback dispatcher pattern

**Related Issues:** Initial development for Buildly Labs development workflow automation

---

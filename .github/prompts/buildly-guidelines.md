# Buildly Development Guidelines for AI Assistants

## About Buildly

Buildly is a platform that accelerates application development through modular, reusable components and intelligent automation. We focus on creating scalable, maintainable solutions that can be easily composed into larger applications.

## Core Development Philosophy

### 1. Component-First Architecture
- **Modularity**: Build small, focused components that do one thing well
- **Reusability**: Design components to be easily reused across projects
- **Composability**: Components should integrate seamlessly with each other
- **Loose Coupling**: Minimize dependencies between components

### 2. API-Driven Development
- **API First**: Design APIs before implementation
- **OpenAPI/Swagger**: All APIs must have comprehensive documentation
- **RESTful Principles**: Follow REST conventions for HTTP APIs
- **Versioning**: Use semantic versioning for API changes

### 3. Documentation Standards
- **DevDocs**: All changes documented in `/devdocs` with summaries and reuse notes
- **API Documentation**: Swagger/OpenAPI specs for all endpoints
- **Code Comments**: Meaningful comments explaining business logic
- **README**: Clear setup and usage instructions

## Coding Standards

### Python Projects
```python
# Use type hints consistently
from typing import List, Dict, Optional, Any
from pydantic import BaseModel

# Async/await for I/O operations
async def fetch_data(url: str) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# Pydantic models for data validation
class UserRequest(BaseModel):
    name: str
    email: str
    age: Optional[int] = None
```

### Project Structure
```
project-name/
├─ pyproject.toml          # Python packaging and dependencies
├─ README.md               # Project overview and setup
├─ devdocs/               # Developer documentation
│  └─ index.md            # Change log and architectural decisions
├─ .github/
│  ├─ workflows/          # CI/CD pipelines
│  └─ prompts/            # AI assistant guidelines
├─ src/
│  └─ project_name/       # Main application code
├─ tests/                 # Test files
└─ docs/                  # User-facing documentation
```

### FastAPI Applications
- Use dependency injection for configuration and services
- Implement proper error handling with custom exception classes
- Use Pydantic models for request/response validation
- Include comprehensive OpenAPI documentation

### Testing
- **Pytest**: Use pytest for all Python testing
- **Coverage**: Maintain >80% test coverage
- **Integration Tests**: Test API endpoints end-to-end
- **Unit Tests**: Test individual functions and classes

## Buildly Labs Integration

### Task Management
- All development work should be tracked in Buildly Labs
- Link GitHub PRs to Labs tasks when possible
- Update task status as work progresses

### Component Registry
- Document reusable components in Labs component registry
- Include usage examples and integration notes
- Tag components with relevant technologies and use cases

## Security & Best Practices

### Environment Configuration
- Use environment variables for all configuration
- Never commit secrets or API keys
- Use `.env` files for local development
- Implement proper secret management in production

### Authentication & Authorization
- Use OAuth 2.0/OpenID Connect where possible
- Implement proper RBAC (Role-Based Access Control)
- Use GitHub Apps instead of personal access tokens
- Validate all inputs and sanitize outputs

### Error Handling
- Implement comprehensive error handling
- Use structured logging with correlation IDs
- Provide meaningful error messages to users
- Log errors with sufficient context for debugging

## AI Assistant Guidelines

When working on Buildly projects:

1. **Follow Standards**: Always adhere to the coding and documentation standards outlined above
2. **Update DevDocs**: Document all significant changes in `/devdocs/index.md`
3. **Component Reuse**: Identify and document reusable patterns and components
4. **API Documentation**: Ensure all endpoints have proper OpenAPI documentation
5. **Testing**: Include appropriate tests for new functionality
6. **Security**: Follow security best practices and validate all inputs

## Common Patterns

### Plugin Architecture
```python
# Entry point registration
[project.entry-points."buildly.plugins"]
my_plugin = "my_package.plugin:register"

# Plugin registration function
def register(app: FastAPI, settings: dict = None):
    app.include_router(my_router, prefix="/my-plugin")
    return {"status": "registered", "version": "1.0.0"}
```

### Configuration Management
```python
from pydantic import BaseModel
import os

class Settings(BaseModel):
    api_key: str = os.getenv("API_KEY", "")
    base_url: str = os.getenv("BASE_URL", "http://localhost")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
```

### Tool Integration
```python
# Tool definition with JSON schema
TOOL_SPEC = {
    "name": "tool_name",
    "description": "What the tool does",
    "parameters": {
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "Parameter description"}
        },
        "required": ["param1"]
    }
}
```

Remember: The goal is to build maintainable, scalable applications that leverage Buildly's platform capabilities while following industry best practices.

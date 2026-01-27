# Tests Directory

This directory contains unit tests, integration tests, and test fixtures for the BB Agent Manager.

## Test Structure

```
tests/
├── README.md                 # This file
├── conftest.py              # Pytest configuration and shared fixtures
├── test_tools.py            # Tests for tools (devdocs, git_ops, etc)
├── test_providers.py        # Tests for LLM providers
├── test_integration.py      # Integration tests
├── test_api.py              # API endpoint tests
├── fixtures/
│   ├── mock_llm_responses.py
│   ├── test_config.py
│   └── sample_data.py
```

## Running Tests

### Run All Tests
```bash
pytest tests/
```

### Run with Coverage
```bash
pytest tests/ --cov=bb_agent_manager --cov-report=html
```

### Run Specific Test File
```bash
pytest tests/test_tools.py -v
```

### Run Specific Test
```bash
pytest tests/test_tools.py::test_update_devdocs -v
```

### Run with Markers
```bash
pytest -m "unit" tests/
pytest -m "integration" tests/
```

## Test Coverage Goals

Current target: **>80% coverage**

- **Unit Tests**: Individual functions and classes
- **Integration Tests**: Tool interactions with external APIs
- **API Tests**: Endpoint functionality and responses
- **Fixture Tests**: Mocked external services

## Writing Tests

### Example Unit Test
```python
import pytest
from bb_agent_manager.tools.devdocs import update_devdocs

@pytest.mark.asyncio
async def test_update_devdocs_creates_file(tmp_path):
    """Test that update_devdocs creates a file"""
    # Arrange
    test_file = tmp_path / "test.md"
    
    # Act
    result = await update_devdocs(
        files=["test.py"],
        summary="Test change"
    )
    
    # Assert
    assert result["status"] == "ok"
```

### Example Integration Test
```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_claude_provider_chat(settings):
    """Test Claude provider chat functionality"""
    from bb_agent_manager.llm.claude import ClaudeProvider
    
    provider = ClaudeProvider(settings)
    response = await provider.chat(
        messages=[{"role": "user", "content": "Hello"}],
        tools=[]
    )
    
    assert response.get("content") is not None
```

## Fixtures

Common fixtures are defined in `conftest.py`:
- `settings` - AgentSettings with test configuration
- `mock_llm_response` - Mock LLM provider response
- `github_token` - Test GitHub token
- `tmp_path` - Temporary directory for file operations

## CI/CD Integration

Tests run automatically on:
- Pull requests
- Push to main branch
- Manual trigger

See `.github/workflows/code-review.yml` for configuration.

## Mocking External Services

### Mock LLM Responses
```python
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_with_mocked_llm():
    with patch('bb_agent_manager.llm.claude.Anthropic') as mock:
        mock_instance = mock.return_value
        mock_instance.messages.create = AsyncMock(
            return_value={"content": [{"text": "mocked response"}]}
        )
        # Your test code
```

### Mock External APIs
```python
@pytest.mark.asyncio
async def test_with_mocked_github():
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": 123}
        # Your test code
```

## Test Markers

Available pytest markers:
- `@pytest.mark.unit` - Unit tests (fast, no external calls)
- `@pytest.mark.integration` - Integration tests (call real APIs in test mode)
- `@pytest.mark.slow` - Slow tests (skip in CI)
- `@pytest.mark.asyncio` - Async tests

## Performance Benchmarks

Target response times:
- Chat endpoint: <500ms average
- Tool execution: <2s average (depending on external API)
- Provider selection: <10ms
- Health check: <50ms

## See Also

- [Development Roadmap](../devdocs/TODO.md)
- [Architecture](../devdocs/ARCHITECTURE.md)
- [Contributing Guidelines](../.github/prompts/buildly-guidelines.md)

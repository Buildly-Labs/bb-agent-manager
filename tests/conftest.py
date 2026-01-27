"""
Pytest configuration and shared fixtures for BB Agent Manager tests
"""
import pytest
import os
from unittest.mock import AsyncMock, MagicMock
from bb_agent_manager.config import AgentSettings


@pytest.fixture
def settings():
    """Provide test configuration settings"""
    return AgentSettings(
        labs_base_url="https://test.buildly.io/api",
        labs_api_token="test-token-123",
        default_provider="ollama",
        anthropic_api_key="test-claude-key",
        anthropic_model="claude-3-5-sonnet-20241022",
        openai_api_key="test-openai-key",
        openai_model="gpt-4o",
        gemini_api_key="test-gemini-key",
        gemini_model="gemini-1.5-pro",
        ollama_base_url="http://localhost:11434/v1",
        ollama_model="llama3.1:8b",
        github_token="test-gh-token",
        github_repo="test/repo",
        require_human_review=True,
        auto_close_issues=True,
        create_draft_prs=True,
    )


@pytest.fixture
def mock_anthropic_response():
    """Mock Anthropic/Claude API response"""
    return {
        "id": "msg_test123",
        "type": "message",
        "role": "assistant",
        "content": [{"type": "text", "text": "Test response from Claude"}],
        "model": "claude-3-5-sonnet-20241022",
        "stop_reason": "end_turn",
        "usage": {"input_tokens": 10, "output_tokens": 20},
    }


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    return {
        "id": "chatcmpl-test123",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "gpt-4o",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": "Test response from GPT"},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
    }


@pytest.fixture
def mock_gemini_response():
    """Mock Google Gemini API response"""
    return {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": "Test response from Gemini"}],
                    "role": "model",
                },
                "finish_reason": "STOP",
                "index": 0,
            }
        ],
        "usage_metadata": {
            "prompt_token_count": 10,
            "candidates_token_count": 20,
            "total_token_count": 30,
        },
    }


@pytest.fixture
def mock_github_pr_response():
    """Mock GitHub API PR creation response"""
    return {
        "id": 1,
        "number": 123,
        "title": "Test PR",
        "body": "Test PR body",
        "state": "open",
        "draft": True,
        "html_url": "https://github.com/test/repo/pull/123",
        "user": {"login": "test-user"},
        "created_at": "2026-01-27T00:00:00Z",
        "updated_at": "2026-01-27T00:00:00Z",
    }


@pytest.fixture
def mock_github_issue_response():
    """Mock GitHub API issue response"""
    return {
        "id": 1,
        "number": 42,
        "title": "Test Issue",
        "body": "Test issue body",
        "state": "open",
        "html_url": "https://github.com/test/repo/issues/42",
        "user": {"login": "test-user"},
        "created_at": "2026-01-27T00:00:00Z",
        "updated_at": "2026-01-27T00:00:00Z",
    }


@pytest.fixture
def mock_buildly_response():
    """Mock Buildly Labs API response"""
    return {
        "id": "task-123",
        "title": "Test Task",
        "description": "Test task description",
        "status": "open",
        "priority": "high",
        "created_at": "2026-01-27T00:00:00Z",
        "updated_at": "2026-01-27T00:00:00Z",
    }


@pytest.fixture
async def mock_llm_provider(mock_anthropic_response):
    """Mock LLM Provider"""
    provider = AsyncMock()
    provider.chat = AsyncMock(return_value={"content": "Test response"})
    return provider


@pytest.fixture
def mock_httpx_client():
    """Mock httpx AsyncClient"""
    client = AsyncMock()
    return client


@pytest.fixture
def github_token():
    """Test GitHub token"""
    return "ghp_test1234567890abcdefghijklmnop"


@pytest.fixture
def buildly_token():
    """Test Buildly token"""
    return "labs_test_1234567890abcdefghijklmnop"


@pytest.fixture
def api_key_claude():
    """Test Claude API key"""
    return "sk-ant-v0-test1234567890abcdefghijklmnopqrstuvwxyz"


@pytest.fixture
def api_key_openai():
    """Test OpenAI API key"""
    return "sk-proj-test1234567890abcdefghijklmnopqrstuvwxyz"


@pytest.fixture
def api_key_gemini():
    """Test Gemini API key"""
    return "AIzaSyDtest1234567890abcdefghijklmnopqrstuvwxyz"


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "slow: mark test as slow")
    config.addinivalue_line("markers", "asyncio: mark test as async")


@pytest.fixture(scope="session")
def event_loop_policy():
    """Configure event loop for async tests"""
    import asyncio

    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    return asyncio.get_event_loop_policy()

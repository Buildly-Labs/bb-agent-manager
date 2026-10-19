"""Tests for the experimental Buildly Labs create tools.

HTTP is mocked — no live Labs calls. Verifies tool registration, auth gating,
endpoint/payload construction, and required-field handling.
"""

import pytest

import bb_agent_manager.tools.buildly_labs as labs
from bb_agent_manager.config import BuildlySettings


@pytest.fixture
def settings():
    return BuildlySettings(
        labs_base_url="https://test.buildly.io",
        labs_api_token="test-token-123",
    )


@pytest.fixture
def capture_send(monkeypatch):
    """Capture calls to _send instead of hitting the network."""
    calls = []

    async def fake_send(url, method, token, payload=None):
        calls.append({"url": url, "method": method, "token": token, "payload": payload})
        return {"status": "ok", "data": {"uuid": "new-uuid", "echo": payload}}

    monkeypatch.setattr(labs, "_send", fake_send)
    return calls


def test_create_tools_registered():
    names = {t.name for t in labs.TOOLS}
    assert {"buildly_create_issue", "buildly_create_task", "buildly_create_product"} <= names
    # And dispatchable.
    assert {"buildly_create_issue", "buildly_create_task",
            "buildly_create_product"} <= labs.TOOL_NAMES


@pytest.mark.asyncio
async def test_create_issue_posts_to_backlog(settings, capture_send):
    res = await labs.handle(
        "buildly_create_issue",
        {"product_id": "prod-1", "name": "Fix login", "description": "500 on submit"},
        settings,
    )
    assert res["status"] == "ok"
    call = capture_send[0]
    assert call["method"] == "POST"
    assert call["url"].endswith("/api/v1/backlog")
    assert call["payload"]["type"] == "issue"
    assert call["payload"]["name"] == "Fix login"
    assert call["payload"]["product_id"] == "prod-1"


@pytest.mark.asyncio
async def test_create_task_posts_to_backlog_with_parent(settings, capture_send):
    res = await labs.handle(
        "buildly_create_task",
        {"product_id": "prod-1", "name": "Write test", "parent_uuid": "iss-9"},
        settings,
    )
    assert res["status"] == "ok"
    call = capture_send[0]
    assert call["payload"]["type"] == "task"
    assert call["payload"]["parent_uuid"] == "iss-9"


@pytest.mark.asyncio
async def test_create_product_posts_to_products(settings, capture_send):
    res = await labs.handle(
        "buildly_create_product", {"name": "New Product", "description": "d"}, settings,
    )
    assert res["status"] == "ok"
    call = capture_send[0]
    assert call["url"].endswith("/api/v1/products")
    assert call["payload"]["name"] == "New Product"


@pytest.mark.asyncio
async def test_create_issue_requires_product(settings, capture_send):
    # No product_id and no BUILDLY_PRODUCT_UUID → error, no HTTP call.
    res = await labs.handle("buildly_create_issue", {"name": "x"}, settings)
    assert "error" in res
    assert not capture_send


@pytest.mark.asyncio
async def test_create_requires_auth(capture_send, monkeypatch):
    # Force "no token resolvable" regardless of env / ~/.buildly/token.
    monkeypatch.setattr(labs, "_get_token", lambda settings, arguments: None)
    unauth = BuildlySettings(labs_base_url="https://test.buildly.io", labs_api_token="")
    res = await labs.handle("buildly_create_product", {"name": "x"}, unauth)
    assert "error" in res and "authenticat" in res["error"].lower()
    assert not capture_send

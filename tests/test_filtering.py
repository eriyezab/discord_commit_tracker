"""Tests for event filtering and branch filtering on the webhook endpoint."""

import json
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from discord_commit_tracker.db import Database
from discord_commit_tracker.server import app
from tests.helpers import sign_payload

FIXTURES = Path(__file__).parent / "fixtures"
TEST_SECRET = "testsecret"
TRACKED_REPO = "octocat/hello-world"


@pytest.fixture
async def client(tmp_path):
    db = Database(str(tmp_path / "test.db"))
    await db.init()
    await db.add_repo(TRACKED_REPO, TEST_SECRET)

    app.state.db = db
    app.state.channel = AsyncMock()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

    await db.close()


@pytest.mark.asyncio
async def test_non_push_event_ignored(client):
    payload = json.loads((FIXTURES / "push_single_commit.json").read_text())
    body = json.dumps(payload).encode()

    response = await client.post(
        "/github/webhook",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": sign_payload(body, TEST_SECRET),
            "X-GitHub-Event": "pull_request",
        },
    )
    assert response.status_code == 200
    assert response.json() == {"status": "ignored"}
    app.state.channel.send.assert_not_called()


@pytest.mark.asyncio
async def test_push_to_non_default_branch_ignored(client):
    payload = json.loads((FIXTURES / "push_non_default_branch.json").read_text())
    body = json.dumps(payload).encode()

    response = await client.post(
        "/github/webhook",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": sign_payload(body, TEST_SECRET),
            "X-GitHub-Event": "push",
        },
    )
    assert response.status_code == 200
    assert response.json() == {"status": "ignored"}
    app.state.channel.send.assert_not_called()


@pytest.mark.asyncio
async def test_multi_commit_push_posts_single_embed(client):
    payload = json.loads((FIXTURES / "push_multi_commit.json").read_text())
    body = json.dumps(payload).encode()

    await client.post(
        "/github/webhook",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": sign_payload(body, TEST_SECRET),
            "X-GitHub-Event": "push",
        },
    )
    app.state.channel.send.assert_called_once()
    _, kwargs = app.state.channel.send.call_args
    assert "embed" in kwargs

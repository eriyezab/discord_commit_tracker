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


@pytest.fixture
def push_payload():
    return json.loads((FIXTURES / "push_single_commit.json").read_text())


@pytest.mark.asyncio
async def test_webhook_returns_200(client, push_payload):
    body = json.dumps(push_payload).encode()
    response = await client.post(
        "/github/webhook",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": sign_payload(body, TEST_SECRET),
        },
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_webhook_posts_embed_to_channel(client, push_payload):
    body = json.dumps(push_payload).encode()
    await client.post(
        "/github/webhook",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": sign_payload(body, TEST_SECRET),
        },
    )
    channel = app.state.channel
    channel.send.assert_called_once()
    _, kwargs = channel.send.call_args
    assert "embed" in kwargs


@pytest.mark.asyncio
async def test_webhook_empty_commits_does_not_post(client, push_payload):
    push_payload["commits"] = []
    body = json.dumps(push_payload).encode()
    await client.post(
        "/github/webhook",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": sign_payload(body, TEST_SECRET),
        },
    )
    app.state.channel.send.assert_not_called()

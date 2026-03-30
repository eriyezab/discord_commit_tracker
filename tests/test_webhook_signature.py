import json
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from discord_commit_tracker.db import Database
from discord_commit_tracker.server import app
from tests.helpers import sign_payload


@pytest.fixture
async def client(tmp_path):
    db = Database(str(tmp_path / "test.db"))
    await db.init()

    app.state.db = db
    app.state.channel = AsyncMock()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

    await db.close()


PAYLOAD = {
    "repository": {
        "full_name": "owner/repo",
        "html_url": "https://github.com/owner/repo",
        "private": False,
    },
    "commits": [
        {
            "id": "abc123",
            "message": "fix: something",
            "author": {"name": "Alice"},
            "url": "https://github.com/owner/repo/commit/abc123",
            "timestamp": "2026-03-30T00:00:00Z",
        }
    ],
}


@pytest.mark.asyncio
async def test_valid_signature_accepted(client):
    secret = "supersecret"
    db: Database = app.state.db
    await db.add_repo("owner/repo", secret)

    body = json.dumps(PAYLOAD).encode()
    sig = sign_payload(body, secret)

    response = await client.post(
        "/github/webhook",
        content=body,
        headers={"Content-Type": "application/json", "X-Hub-Signature-256": sig},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_invalid_signature_rejected(client):
    secret = "supersecret"
    db: Database = app.state.db
    await db.add_repo("owner/repo", secret)

    body = json.dumps(PAYLOAD).encode()
    bad_sig = sign_payload(body, "wrongsecret")

    response = await client.post(
        "/github/webhook",
        content=body,
        headers={"Content-Type": "application/json", "X-Hub-Signature-256": bad_sig},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_unknown_repo_silently_ignored(client):
    body = json.dumps(PAYLOAD).encode()
    sig = sign_payload(body, "doesntmatter")

    response = await client.post(
        "/github/webhook",
        content=body,
        headers={"Content-Type": "application/json", "X-Hub-Signature-256": sig},
    )
    assert response.status_code == 200
    assert response.json() == {"status": "ignored"}


@pytest.mark.asyncio
async def test_missing_signature_header_rejected(client):
    secret = "supersecret"
    db: Database = app.state.db
    await db.add_repo("owner/repo", secret)

    body = json.dumps(PAYLOAD).encode()

    response = await client.post(
        "/github/webhook",
        content=body,
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 401

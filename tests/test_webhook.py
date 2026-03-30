import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from discord_commit_tracker.server import app

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def mock_channel():
    channel = MagicMock()
    channel.send = AsyncMock()
    return channel


@pytest.fixture
def client(mock_channel):
    app.state.channel = mock_channel
    return TestClient(app)


@pytest.fixture
def push_payload():
    return json.loads((FIXTURES / "push_single_commit.json").read_text())


def test_webhook_returns_200(client, push_payload):
    response = client.post("/github/webhook", json=push_payload)
    assert response.status_code == 200


def test_webhook_posts_embed_to_channel(client, mock_channel, push_payload):
    client.post("/github/webhook", json=push_payload)
    mock_channel.send.assert_called_once()
    _, kwargs = mock_channel.send.call_args
    assert "embed" in kwargs


def test_webhook_empty_commits_does_not_post(client, mock_channel, push_payload):
    push_payload["commits"] = []
    client.post("/github/webhook", json=push_payload)
    mock_channel.send.assert_not_called()

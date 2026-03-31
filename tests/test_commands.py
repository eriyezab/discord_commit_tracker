import pytest

from discord_commit_tracker.commands import (
    InvalidRepoFormat,
    list_repos,
    track_repo,
    untrack_repo,
    validate_repo_format,
)
from discord_commit_tracker.db import Database


@pytest.fixture
async def db():
    database = Database(":memory:")
    await database.init()
    yield database
    await database.close()


# ---------------------------------------------------------------------------
# validate_repo_format
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "repo",
    [
        "owner/repo",
        "my-org/my-repo",
        "user123/repo.name",
        "a/b",
    ],
)
def test_valid_repo_formats(repo):
    validate_repo_format(repo)  # should not raise


@pytest.mark.parametrize(
    "repo",
    [
        "nodash",
        "owner/repo/extra",
        "owner/",
        "/repo",
        "",
        "owner repo",
        "owner/repo name",
    ],
)
def test_invalid_repo_formats(repo):
    with pytest.raises(InvalidRepoFormat):
        validate_repo_format(repo)


# ---------------------------------------------------------------------------
# track_repo
# ---------------------------------------------------------------------------


async def test_track_repo_saves_to_db(db):
    await track_repo(db, "octocat/hello-world", webhook_base_url="https://example.com")
    repo = await db.get_repo("octocat/hello-world")
    assert repo is not None
    assert repo["full_name"] == "octocat/hello-world"


async def test_track_repo_returns_webhook_url(db):
    result = await track_repo(db, "octocat/hello-world", webhook_base_url="https://example.com")
    assert result["webhook_url"] == "https://example.com/github/webhook"


async def test_track_repo_returns_secret(db):
    result = await track_repo(db, "octocat/hello-world", webhook_base_url="https://example.com")
    assert len(result["secret"]) == 64  # secrets.token_hex(32) → 64 hex chars


async def test_track_repo_already_tracked_raises(db):
    await track_repo(db, "octocat/hello-world", webhook_base_url="https://example.com")
    with pytest.raises(Exception, match="already tracked"):
        await track_repo(db, "octocat/hello-world", webhook_base_url="https://example.com")


# ---------------------------------------------------------------------------
# untrack_repo
# ---------------------------------------------------------------------------


async def test_untrack_repo_removes_from_db(db):
    await track_repo(db, "octocat/hello-world", webhook_base_url="https://example.com")
    await untrack_repo(db, "octocat/hello-world")
    assert await db.get_repo("octocat/hello-world") is None


async def test_untrack_repo_not_found_raises(db):
    with pytest.raises(Exception, match="not tracked"):
        await untrack_repo(db, "octocat/hello-world")


# ---------------------------------------------------------------------------
# list_repos
# ---------------------------------------------------------------------------


async def test_list_repos_empty(db):
    result = await list_repos(db)
    assert result == []


async def test_list_repos_returns_full_names(db):
    await track_repo(db, "owner/repo-a", webhook_base_url="https://example.com")
    await track_repo(db, "owner/repo-b", webhook_base_url="https://example.com")
    result = await list_repos(db)
    assert "owner/repo-a" in result
    assert "owner/repo-b" in result

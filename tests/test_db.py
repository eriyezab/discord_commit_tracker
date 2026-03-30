import sqlite3

import pytest

from discord_commit_tracker.db import Database


@pytest.fixture
async def db():
    database = Database(":memory:")
    await database.init()
    yield database
    await database.close()


async def test_init_creates_table(db):
    repos = await db.list_repos()
    assert repos == []


async def test_add_repo(db):
    await db.add_repo("octocat/hello-world", "secret123")
    repos = await db.list_repos()
    assert len(repos) == 1
    assert repos[0]["full_name"] == "octocat/hello-world"
    assert repos[0]["webhook_secret"] == "secret123"


async def test_get_repo_returns_row(db):
    await db.add_repo("octocat/hello-world", "secret123")
    repo = await db.get_repo("octocat/hello-world")
    assert repo is not None
    assert repo["full_name"] == "octocat/hello-world"
    assert repo["webhook_secret"] == "secret123"


async def test_get_repo_missing_returns_none(db):
    repo = await db.get_repo("octocat/nonexistent")
    assert repo is None


async def test_add_duplicate_repo_raises(db):
    await db.add_repo("octocat/hello-world", "secret123")
    with pytest.raises(sqlite3.IntegrityError):
        await db.add_repo("octocat/hello-world", "other-secret")


async def test_remove_repo(db):
    await db.add_repo("octocat/hello-world", "secret123")
    await db.remove_repo("octocat/hello-world")
    assert await db.get_repo("octocat/hello-world") is None


async def test_remove_nonexistent_repo_is_noop(db):
    await db.remove_repo("octocat/nonexistent")


async def test_list_repos_multiple(db):
    await db.add_repo("owner/repo-a", "secret-a")
    await db.add_repo("owner/repo-b", "secret-b")
    repos = await db.list_repos()
    full_names = [r["full_name"] for r in repos]
    assert "owner/repo-a" in full_names
    assert "owner/repo-b" in full_names

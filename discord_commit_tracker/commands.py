import re
import secrets

from discord_commit_tracker.db import Database

_REPO_RE = re.compile(r"^[\w.\-]+/[\w.\-]+$")


class InvalidRepoFormat(ValueError):
    pass


class AlreadyTracked(Exception):
    pass


class NotTracked(Exception):
    pass


def validate_repo_format(repo: str) -> None:
    if not _REPO_RE.match(repo):
        raise InvalidRepoFormat(f"Invalid repo format: {repo!r}. Expected 'owner/repo'.")


async def track_repo(db: Database, full_name: str, *, webhook_base_url: str) -> dict[str, str]:
    existing = await db.get_repo(full_name)
    if existing is not None:
        raise AlreadyTracked(f"{full_name!r} is already tracked.")

    secret = secrets.token_hex(32)
    await db.add_repo(full_name, secret)

    return {
        "webhook_url": f"{webhook_base_url}/github/webhook",
        "secret": secret,
    }


async def untrack_repo(db: Database, full_name: str) -> None:
    existing = await db.get_repo(full_name)
    if existing is None:
        raise NotTracked(f"{full_name!r} is not tracked.")

    await db.remove_repo(full_name)


async def list_repos(db: Database) -> list[str]:
    rows = await db.list_repos()
    return [row["full_name"] for row in rows]

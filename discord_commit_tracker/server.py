import logging

from fastapi import FastAPI, Request

from discord_commit_tracker.embeds import build_commit_embed

logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/github/webhook")
async def github_webhook(request: Request) -> dict[str, str]:
    payload = await request.json()

    repo = payload.get("repository", {})
    repo_name = repo.get("full_name", "unknown")
    commits = payload.get("commits", [])

    logger.info("Received webhook for %s (%d commit(s))", repo_name, len(commits))

    if not commits:
        logger.info("No commits in payload for %s — ignoring", repo_name)
        return {"status": "ignored"}

    channel = request.app.state.channel

    for commit in commits:
        logger.info("Posting embed for commit %s by %s", commit["id"], commit["author"]["name"])
        embed = build_commit_embed(
            author=commit["author"]["name"],
            message=commit["message"],
            repo_full_name=repo["full_name"],
            repo_url=repo["html_url"],
            commit_url=commit["url"],
            timestamp=commit["timestamp"],
            private=repo["private"],
        )
        await channel.send(embed=embed)

    return {"status": "ok"}

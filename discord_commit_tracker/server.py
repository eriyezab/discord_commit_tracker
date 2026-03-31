import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from discord_commit_tracker.embeds import build_commit_embed
from discord_commit_tracker.security import verify_signature

logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/github/webhook")
async def github_webhook(request: Request) -> dict[str, str]:
    body = await request.body()
    payload = await request.json()

    repo = payload.get("repository", {})
    repo_name = repo.get("full_name", "unknown")

    db = request.app.state.db
    tracked = await db.get_repo(repo_name)

    if tracked is None:
        logger.info("Received webhook for untracked repo %s — ignoring", repo_name)
        return {"status": "ignored"}

    sig_header = request.headers.get("X-Hub-Signature-256")
    if not verify_signature(body, tracked["webhook_secret"], sig_header):
        logger.warning("Invalid signature for %s", repo_name)
        return JSONResponse(status_code=401, content={"detail": "Invalid signature"})

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

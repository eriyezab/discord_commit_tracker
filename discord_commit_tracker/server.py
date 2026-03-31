import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from discord_commit_tracker.embeds import build_push_embed
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

    event = request.headers.get("X-GitHub-Event", "push")
    if event != "push":
        logger.info("Ignoring non-push event '%s' for %s", event, repo_name)
        return {"status": "ignored"}

    ref = payload.get("ref", "")
    default_branch = repo.get("default_branch", "main")
    if ref != f"refs/heads/{default_branch}":
        logger.info("Ignoring push to non-default branch '%s' for %s", ref, repo_name)
        return {"status": "ignored"}

    commits = payload.get("commits", [])
    if not commits:
        logger.info("No commits in payload for %s — ignoring", repo_name)
        return {"status": "ignored"}

    logger.info("Posting push embed for %s (%d commit(s))", repo_name, len(commits))

    branch = ref.removeprefix("refs/heads/")
    embed = build_push_embed(
        repo_full_name=repo["full_name"],
        repo_url=repo["html_url"],
        compare_url=payload["compare"],
        branch=branch,
        commits=commits,
        latest_timestamp=commits[-1]["timestamp"],
        private=repo["private"],
    )
    await request.app.state.channel.send(embed=embed)

    return {"status": "ok"}

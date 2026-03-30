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

    commits = payload.get("commits", [])
    if not commits:
        return {"status": "ignored"}

    repo = payload["repository"]
    channel = request.app.state.channel

    for commit in commits:
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

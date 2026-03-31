from datetime import datetime

import discord

_MSG_MAX = 72


def build_push_embed(
    *,
    repo_full_name: str,
    repo_url: str,
    compare_url: str,
    branch: str,
    commits: list[dict],
    latest_timestamp: str,
    private: bool,
) -> discord.Embed:
    count = len(commits)
    title = f"{count} commit{'s' if count != 1 else ''} to {repo_full_name}"

    lines = []
    for commit in commits:
        short_sha = commit["id"][:7]
        first_line = commit["message"].splitlines()[0]
        msg = first_line if len(first_line) <= _MSG_MAX else first_line[:69] + "..."
        author = commit["author"]["name"]
        lines.append(f"• `{short_sha}` {msg} — {author}")

    embed = discord.Embed(
        title=title,
        url=compare_url,
        description="\n".join(lines),
        timestamp=datetime.fromisoformat(latest_timestamp.replace("Z", "+00:00")),
        color=discord.Color.blurple(),
    )
    embed.add_field(name="Branch", value=branch, inline=True)
    embed.add_field(
        name="Repository",
        value=f"[{repo_full_name}]({repo_url})",
        inline=True,
    )

    if private:
        embed.set_footer(text="🔒 Private repo — links may not be accessible.")

    return embed

from datetime import datetime

import discord

_TITLE_MAX = 80


def build_commit_embed(
    *,
    author: str,
    message: str,
    repo_full_name: str,
    repo_url: str,
    commit_url: str,
    timestamp: str,
    private: bool,
) -> discord.Embed:
    first_line = message.splitlines()[0]
    title = first_line if len(first_line) <= _TITLE_MAX else first_line[:77] + "..."

    embed = discord.Embed(
        title=title,
        url=commit_url,
        timestamp=datetime.fromisoformat(timestamp.replace("Z", "+00:00")),
        color=discord.Color.blurple(),
    )
    embed.set_author(name=author)
    embed.add_field(
        name="Repository",
        value=f"[{repo_full_name}]({repo_url})",
        inline=False,
    )

    if private:
        embed.set_footer(text="🔒 Private repo — link may not be accessible.")

    return embed

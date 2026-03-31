import logging

import discord
from discord import app_commands
from discord.ext import commands

from discord_commit_tracker.commands import (
    AlreadyTracked,
    InvalidRepoFormat,
    NotTracked,
    list_repos,
    track_repo,
    untrack_repo,
    validate_repo_format,
)
from discord_commit_tracker.config import Config
from discord_commit_tracker.db import Database
from discord_commit_tracker.server import app

logger = logging.getLogger(__name__)


class CodeTrackerBot(commands.Bot):
    def __init__(self, config: Config, db: Database) -> None:
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix="/", intents=intents)
        self.config = config
        self.db = db

    async def on_ready(self) -> None:
        logger.info("Logged in as %s (id=%s)", self.user, self.user.id if self.user else "?")
        logger.info("Channel ID: %s", self.config.discord_channel_id)

        await self.tree.sync(guild=discord.Object(id=int(self.config.discord_guild_id)))

        channel = self.get_channel(int(self.config.discord_channel_id))
        if isinstance(channel, discord.TextChannel):
            app.state.channel = channel
            repos = await list_repos(self.db)
            await channel.send(f"✅ Online — tracking {len(repos)} repo(s)")
        else:
            logger.warning("Could not find channel %s", self.config.discord_channel_id)

    async def on_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        logger.exception("Unexpected error in command", exc_info=error)
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "Something went wrong. Check the bot logs.", ephemeral=True
            )

    @app_commands.command(name="track", description="Track a GitHub repository")
    @app_commands.describe(repo="Repository in owner/repo format")
    async def cmd_track(self, interaction: discord.Interaction, repo: str) -> None:
        try:
            validate_repo_format(repo)
            result = await track_repo(self.db, repo, webhook_base_url=self.config.webhook_base_url)
        except InvalidRepoFormat as e:
            await interaction.response.send_message(str(e), ephemeral=True)
            return
        except AlreadyTracked as e:
            await interaction.response.send_message(str(e), ephemeral=True)
            return

        await interaction.response.send_message(
            f"✅ Now tracking **{repo}**\n\n"
            f"**Webhook URL:** `{result['webhook_url']}`\n"
            f"**Secret:** `{result['secret']}`\n\n"
            f"In your GitHub repo go to **Settings → Webhooks → Add webhook** and set:\n"
            f"- Payload URL: `{result['webhook_url']}`\n"
            f"- Content type: `application/json`\n"
            f"- Secret: `{result['secret']}`\n"
            f"- Events: **Just the push event**",
            ephemeral=True,
        )
        logger.info("Now tracking %s", repo)

    @app_commands.command(name="untrack", description="Stop tracking a GitHub repository")
    @app_commands.describe(repo="Repository in owner/repo format")
    async def cmd_untrack(self, interaction: discord.Interaction, repo: str) -> None:
        try:
            validate_repo_format(repo)
            await untrack_repo(self.db, repo)
        except InvalidRepoFormat as e:
            await interaction.response.send_message(str(e), ephemeral=True)
            return
        except NotTracked as e:
            await interaction.response.send_message(str(e), ephemeral=True)
            return

        await interaction.response.send_message(
            f"✅ Stopped tracking **{repo}**\n"
            f"Remember to delete the webhook from your GitHub repo settings.",
            ephemeral=True,
        )
        logger.info("Stopped tracking %s", repo)

    @app_commands.command(name="list", description="List all tracked repositories")
    async def cmd_list(self, interaction: discord.Interaction) -> None:
        repos = await list_repos(self.db)
        if not repos:
            await interaction.response.send_message(
                "No repositories are currently being tracked.", ephemeral=True
            )
            return

        repo_list = "\n".join(f"• `{r}`" for r in repos)
        await interaction.response.send_message(
            f"**Tracked repositories ({len(repos)}):**\n{repo_list}",
            ephemeral=True,
        )


def create_bot(config: Config, db: Database) -> CodeTrackerBot:
    return CodeTrackerBot(config, db)

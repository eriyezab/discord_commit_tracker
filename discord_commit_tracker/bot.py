import logging

import discord
from discord.ext import commands

from discord_commit_tracker.config import Config
from discord_commit_tracker.server import app

logger = logging.getLogger(__name__)


class CodeTrackerBot(commands.Bot):
    def __init__(self, config: Config) -> None:
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix="/", intents=intents)
        self.config = config

    async def on_ready(self) -> None:
        logger.info("Logged in as %s (id=%s)", self.user, self.user.id if self.user else "?")
        logger.info("Channel ID: %s", self.config.discord_channel_id)

        await self.tree.sync(guild=discord.Object(id=int(self.config.discord_guild_id)))

        channel = self.get_channel(int(self.config.discord_channel_id))
        if isinstance(channel, discord.TextChannel):
            app.state.channel = channel
            await channel.send("✅ Online — tracking 0 repos")
        else:
            logger.warning("Could not find channel %s", self.config.discord_channel_id)


def create_bot(config: Config) -> CodeTrackerBot:
    return CodeTrackerBot(config)

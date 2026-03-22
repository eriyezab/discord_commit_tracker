import os
from dataclasses import dataclass


class ConfigError(Exception):
    pass


@dataclass
class Config:
    discord_token: str
    discord_channel_id: str
    discord_guild_id: str
    port: int
    database_path: str
    webhook_base_url: str

    @classmethod
    def from_env(cls) -> "Config":
        required = ("DISCORD_TOKEN", "DISCORD_CHANNEL_ID", "DISCORD_GUILD_ID")
        missing = [var for var in required if not os.environ.get(var)]
        if missing:
            raise ConfigError(f"Missing required environment variables: {', '.join(missing)}")

        return cls(
            discord_token=os.environ["DISCORD_TOKEN"],
            discord_channel_id=os.environ["DISCORD_CHANNEL_ID"],
            discord_guild_id=os.environ["DISCORD_GUILD_ID"],
            port=int(os.environ.get("PORT", "8000")),
            database_path=os.environ.get("DATABASE_PATH", "db.sqlite3"),
            webhook_base_url=os.environ.get("WEBHOOK_BASE_URL", ""),
        )

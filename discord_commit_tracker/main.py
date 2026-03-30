import asyncio
import logging

import uvicorn

from discord_commit_tracker.bot import create_bot
from discord_commit_tracker.config import Config, ConfigError
from discord_commit_tracker.db import Database
from discord_commit_tracker.server import app

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


async def main() -> None:
    try:
        config = Config.from_env()
    except ConfigError as e:
        logger.error("Configuration error: %s", e)
        raise SystemExit(1) from e

    db = Database(config.database_path)
    await db.init()
    logger.info("Database ready at %s", config.database_path)

    bot = create_bot(config)

    server = uvicorn.Server(uvicorn.Config(app, host="0.0.0.0", port=config.port, log_level="info"))

    try:
        await asyncio.gather(
            bot.start(config.discord_token),
            server.serve(),
        )
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())

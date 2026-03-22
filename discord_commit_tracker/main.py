import asyncio
import logging

import uvicorn

from discord_commit_tracker.bot import create_bot
from discord_commit_tracker.config import Config, ConfigError
from discord_commit_tracker.server import app

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


async def main() -> None:
    try:
        config = Config.from_env()
    except ConfigError as e:
        logger.error("Configuration error: %s", e)
        raise SystemExit(1) from e

    bot = create_bot(config)

    server = uvicorn.Server(uvicorn.Config(app, host="0.0.0.0", port=config.port, log_level="info"))

    await asyncio.gather(
        bot.start(config.discord_token),
        server.serve(),
    )


if __name__ == "__main__":
    asyncio.run(main())

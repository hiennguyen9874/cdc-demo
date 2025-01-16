import asyncio

from loguru import logger
from tenacity import retry
from tenacity.after import after_log
from tenacity.before import before_log
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_fixed

from app.core.custom_logging import make_customize_logger
from app.core.es_connection import async_es_connection
from app.core.settings import settings
from app.es_models.item import create_index_if_not_exists

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1

make_customize_logger(settings.APP.CONFIG_DIR / "logging.json")


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, "INFO"),  # type: ignore
    after=after_log(logger, "WARNING"),  # type: ignore
)
@logger.catch
async def init() -> None:
    async_es_connection.init(connections_per_node=settings.ES.CONNECTIONS_PER_NODE)

    async with async_es_connection.session() as es:
        await create_index_if_not_exists(es=es)

    await async_es_connection.close()


def main() -> None:
    logger.info("Pre start, Initializing service")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(init())
    loop.close()

    logger.info("Pre start, Service finished initializing")


if __name__ == "__main__":
    main()

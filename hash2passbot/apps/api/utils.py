import logging
import sys

from loguru import logger

from hash2passbot.config.config import LOG_DIR
from hash2passbot.config.logg_settings import init_logging
from hash2passbot.db import init_db, init_hash_db
from hash2passbot.db.models import Password


def init_loggings():
    logger.configure(
        **dict(
            handlers=[
                {"sink": sys.stdout, "level": "TRACE", "enqueue": True, "diagnose": True},
                {
                    "sink": LOG_DIR / "api.log",
                    "level": "TRACE",
                    "enqueue": True,
                    "diagnose": True,
                    "encoding": "utf-8",
                    "rotation": "5MB",
                    "compression": "zip",
                },
            ]
        )
    )


async def initialize():
    # init_logging()
    init_logging(
        old_logger=True,
        level="TRACE",
        # old_level=logging.DEBUG,
        old_level=logging.INFO,
        steaming=True,
        write=True,
    )
    await init_db()
    Password.connection = await init_hash_db()

    # temp.STATS, _create = await Statistic.get_or_create(pk=1)
    # scheduler.add_job(save_statistics, "interval", minutes=10)
    # scheduler.start()
    logger.info(f'API сервер запущен')

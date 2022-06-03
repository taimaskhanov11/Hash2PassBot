import asyncio
import logging

import asyncpg
from asyncpg import Connection
from loguru import logger
from tortoise import Tortoise

__all__ = (
    "MODELS_DIR",
    "init_db",
    "models",
    "utils"
)

from hash2passbot.config.config import Database, config
from hash2passbot.config.logg_settings import init_logging

MODELS_DIR = "hash2passbot.db.models"


async def init_db(db: Database = config.db):
    logger.debug(f"Initializing Database {db.database}[{db.host}]...")
    data = {
        "db_url": db.postgres_url,
        "modules": {"models": [MODELS_DIR]},
    }
    try:
        await Tortoise.init(**data)
        logger.info("Try generate schemas...")
        await Tortoise.generate_schemas()
    except asyncpg.exceptions.ConnectionDoesNotExistError as e:
        logger.warning(e)
        logger.info("Creating a new database...")
        await Tortoise.init(**data, _create_db=True)
        logger.success(f"New database {db.database} created")
    logger.debug(f"Database {db.database}[{db.host}] initialized")


async def init_hash_db(db: Database = config.hash_db):
    logger.debug(f"Initializing Database {db.database}[{db.host}]...")
    conn: Connection = await asyncpg.connect(**db.dict())
    return conn


if __name__ == '__main__':
    init_logging(
        old_logger=True,
        level="TRACE",
        old_level=logging.DEBUG,
        # old_level=logging.INFO,
        steaming=True,
        write=False,
    )
    # asyncio.run(init_db(Database(username="postgres",
    #                              password="DpKeUf.0",
    #                              host="188.130.139.157",
    #                              port=5432,
    #                              db_name="hashdb")))
    asyncio.run(init_db())

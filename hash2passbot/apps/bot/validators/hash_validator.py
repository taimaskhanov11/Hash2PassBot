import contextlib
import re

import hashid
from loguru import logger

alphabet = re.compile("[a-zA-Z]")


async def hash_is_valid(_hash: str) -> bool | str:
    hashID = hashid.HashID()
    logger.debug(f"Попытка определить тип хеша {_hash}")

    if len(_hash) < 20:
        return False

    with contextlib.suppress(StopIteration):
        hash_type: hashid.HashInfo = next(hashID.identifyHash(_hash))
        logger.info(f"Возможный тип хеша {_hash} -> {hash_type.name}")

        if len(_hash) == 32:
            return "md5"
        elif len(_hash) == 40:
            return "sha1"
        else:
            return hash_type.name.lower()
    logger.debug(f"Не удалось определить тип хеша {_hash}")
    return False
    # if len(_hash) == 32:
    #     return "md5"
    # elif len(_hash) == 40:
    #     return "sha1"
    #
    # elif _hash.isdigit():
    #     return True
    # elif not re.findall(alphabet, _hash):
    #     return False
    # return True

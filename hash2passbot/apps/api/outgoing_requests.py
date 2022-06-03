# todo 6/3/2022 2:31 PM taima:
import asyncio


import aiohttp
import typing

from hash2passbot.config.config import config
from hash2passbot.db import init_db

if typing.TYPE_CHECKING:
    from hash2passbot.db.models import User


async def update_unlimited_subscription(user: "User", duration: int):
    url = "http://localhost:8000/api/v1/sub/"
    data = {
        "user_id": user.user_id,
        "username": user.username,
        "locale": user.locale,
        "duration": duration,
        "token": config.main_api_token
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as res:
            result = await res.json()
            return result


async def main():
    await init_db()
    user = await User.first()
    print(await update_unlimited_subscription(user, 30))
if __name__ == '__main__':
    asyncio.run(main())

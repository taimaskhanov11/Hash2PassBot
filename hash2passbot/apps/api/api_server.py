import asyncio
import re

from fastapi import FastAPI, status
from loguru import logger
from starlette.responses import JSONResponse

from hash2passbot.apps.api.schema import Item, UpdateRequest, get_or_create_from_api
from hash2passbot.apps.api.utils import initialize
from hash2passbot.db.models import SubscriptionTemplate

app = FastAPI()


@app.get("/api/v1/hash")
# async def get_hash(request: Request):
async def get_hash(item: Item):
    # info = await request.json()
    logger.debug(f"Запрос на расшифровку хеша по api. {item}")
    # print(hash)
    # print(hashs)
    res = await item.get_password()
    logger.debug(f"Результат {res}")
    return res


@app.post("/api/v1/limit")
async def update_limit(update: UpdateRequest):
    # info = await request.json()
    logger.debug(update)
    try:
        user = await get_or_create_from_api(update.trans_user)

        subs = await SubscriptionTemplate.all()
        for sub in subs:
            res = re.match(f".+{update.month} мес.+", sub.title)
            if res:
                await user.subscription.add_limit(sub.limit)
                logger.success(
                    f"Лимит пользователю {update.trans_user.user_id} успешно добавлен через api на: {sub.limit}")
                break

        # print(PydanticUser.schema())
        # pydantic_user = await PydanticUser.from_tortoise_orm(user)
        # pydantic_subscription = PydanticSubscription.from_orm(user.subscription)
        return {"limit": user.subscription.limit}
    except Exception as e:
        logger.warning(e)
        return JSONResponse(
            content={"ERROR": "Не удалось обновить лимиты"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, )


asyncio.create_task(initialize())

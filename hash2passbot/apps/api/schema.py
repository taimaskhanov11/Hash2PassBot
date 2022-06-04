import re

from loguru import logger
from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

from hash2passbot.apps.bot import temp
from hash2passbot.apps.bot.handlers.common.checking_password import search
from hash2passbot.db.models import User, Statistic

PydanticUser = pydantic_model_creator(User)


# PydanticSubscription = pydantic_model_creator(Subscription)


class TransUser(BaseModel):
    user_id: int
    username: str | None
    locale: str | None


class UpdateRequest(BaseModel):
    trans_user: TransUser
    month: int


class Hash(BaseModel):
    hash: str
    hash_type: str


class MockMessage(BaseModel):
    answer_text: str = ""

    async def answer(self, text):
        self.answer_text += f"\n{text}"


class Item(BaseModel):
    user: TransUser
    hashs: list[Hash]

    async def get_password(self):
        temp.STATS = await Statistic.first()
        user = await get_or_create_from_api(self.user)
        message = MockMessage()
        if user.subscription.limit:
            if user.subscription.limit < len(self.hashs):
                return f"Запросов может не хватить для расшифровки всех хешей, " \
                       f"перед расшифровкой нужно докупить запросы в партнерском боте @Hash2PassBot"

            for _hash in self.hashs:
                await search(user, _hash.hash, _hash.hash_type, message, sub=True)

        # Для пользователей без подписки
        else:
            for _hash in self.hashs:
                await search(user, _hash.hash, _hash.hash_type, message, sub=False)
        await temp.STATS.save()
        return self.prepare(
            message.answer_text) + f"\n\nКоличество оставшихся запросов в @Hash2PassBot: {user.subscription.limit}"
        # return message.answer_text

    def prepare(self, text) -> str:
        # return re.sub(r"Количество оставшихся запросов: \d", text, "")
        new_text = re.sub(r"Количество оставшихся запросов: \d+", "", text)

        return new_text.replace("Чтобы увидеть пароль приобретите запросы через меню.",
                         "Чтобы увидеть пароль приобретите запросы в боте @Hash2PassBot")


async def get_or_create_from_api(trans_user: TransUser) -> User:
    user, is_new = await User.get_or_create(
        user_id=trans_user.user_id,
        defaults=trans_user.dict(exclude={"user_id", "locale"}),
    )
    if is_new:
        logger.info(f"Новый пользователь {user.user_id=}")
    await user.fetch_related("subscription")
    return user

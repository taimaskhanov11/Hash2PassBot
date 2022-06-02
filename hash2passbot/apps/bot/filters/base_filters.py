from aiogram import types
from aiogram.dispatcher.filters import BaseFilter
from loguru import logger

from hash2passbot.apps.bot.markups.common import common_markups
from hash2passbot.apps.bot.temp import SUBSCRIPTION_CHANNELS
from hash2passbot.apps.bot.utils import channel_status_check
from hash2passbot.db.models import User
from hash2passbot.loader import _


class UserFilter(BaseFilter):
    async def __call__(self, update: types.CallbackQuery | types.Message) -> dict[str, User]:
        user = update.from_user
        user, is_new = await User.get_or_create(
            user_id=user.id,
            defaults={
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "language": user.language_code,
            },
        )
        if is_new:
            logger.info(f"Новый пользователь {user.first_name=}")
        await user.fetch_related("subscription")
        return {"user": user}


class ChannelSubscriptionFilter(BaseFilter):
    async def __call__(self, message: types.Message | types.CallbackQuery, user: User) -> bool:
        if isinstance(message, types.CallbackQuery):
            message = message.message
        if await channel_status_check(message.from_user.id):
            return True
            # return {"is_sub": True}
        await message.answer(_(f"📍 Для того, чтобы пользоваться ботом, нужно подписаться на каналы:"),
                             reply_markup=common_markups.channel_status_check(SUBSCRIPTION_CHANNELS))
        # return {"is_sub": False}
        return False


class HashFilter(BaseFilter):
    async def __call__(self, message: types.Message, user: User) -> bool:
        if len(message.text) < 32:
            await message.answer(_("Некорретный ввод"))
            return

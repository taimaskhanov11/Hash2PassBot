from aiogram import Dispatcher, Router, F

from hash2passbot.config.config import config
from .admin_menu import register_admin
from .bot_settings import register_bot_settings
from .change_menu import register_change_menu
from .channel_menu import register_channel
from .data_menu import register_data
from .send_mail_handers import register_send_mail
from .statistics_menu import register_statistics
from .subscription_menu import register_subscriptions

router = Router()


def register_admin_handlers(dp: Dispatcher):
    router.message.filter(F.from_user.id.in_(config.bot.admins))
    router.callback_query.filter(F.from_user.id.in_(config.bot.admins))
    register_admin(router)
    register_change_menu(router)
    register_data(router)
    register_channel(router)
    register_send_mail(router)
    register_bot_settings(router)
    register_statistics(router)
    register_subscriptions(router)
    dp.include_router(router)

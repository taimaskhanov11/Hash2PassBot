import asyncio
import logging

from aiogram import Bot, F
from aiogram.types import BotCommand

from hash2passbot.apps.bot import temp
from hash2passbot.apps.bot.handlers.admin import register_admin_handlers
from hash2passbot.apps.bot.handlers.common import register_common
from hash2passbot.apps.bot.handlers.common.checking_password import register_check_password
from hash2passbot.apps.bot.handlers.common.make_subscription import register_make_subscriptions
from hash2passbot.apps.bot.handlers.errors.errors_handlers import register_error
from hash2passbot.apps.bot.middleware.bot_middleware import BotMiddleware
from hash2passbot.apps.bot.utils import start_up_message, checking_purchases
from hash2passbot.apps.bot.utils.export import save_statistics
from hash2passbot.config.logg_settings import init_logging
from hash2passbot.db import init_db
from hash2passbot.db.models import Statistic, User
from hash2passbot.db.utils.backup import making_backup
from hash2passbot.loader import bot, dp, scheduler


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Главное меню"),
        BotCommand(command="/admin", description="Админ меню"),
    ]
    await bot.set_my_commands(commands)


async def start():
    # Настройка логирования
    init_logging(
        old_logger=True,
        level="TRACE",
        # old_level=logging.DEBUG,
        old_level=logging.INFO,
        steaming=True,
        write=True,
    )

    dp.startup.register(start_up_message)
    # dp.shutdown.register(on_shutdown)

    # Установка команд бота
    await set_commands(bot)
    dp.message.filter(F.chat.type == "private")
    # Инициализация бд
    await init_db()

    # Меню админа
    register_admin_handlers(dp)

    # Регистрация хэндлеров
    register_common(dp)
    register_make_subscriptions(dp)
    register_check_password(dp)
    register_error(dp)

    # Регистрация middleware
    middleware = BotMiddleware()
    dp.message.outer_middleware(middleware)
    dp.callback_query.outer_middleware(middleware)

    # Регистрация фильтров

    temp.STATS, _create = await Statistic.get_or_create(pk=1)

    scheduler.add_job(making_backup, "interval", hours=1)
    scheduler.add_job(save_statistics, "interval", minutes=10)
    scheduler.add_job(User.reset_search, "interval", minutes=5)
    scheduler.add_job(checking_purchases, "interval", minutes=1)
    scheduler.start()
    await dp.start_polling(bot, skip_updates=True)


def main():
    asyncio.run(start())
    asyncio.get_event_loop()


if __name__ == "__main__":
    main()

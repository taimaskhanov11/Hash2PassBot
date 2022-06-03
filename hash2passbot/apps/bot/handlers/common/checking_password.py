from aiogram import Dispatcher, Router, types
from aiogram.dispatcher.fsm.context import FSMContext
from loguru import logger

from hash2passbot.apps.bot import temp
from hash2passbot.apps.bot.filters.base_filters import ChannelSubscriptionFilter
from hash2passbot.apps.bot.validators.hash_validator import hash_is_valid
from hash2passbot.db.models import User, Password, ApiPassword, Statistic
from hash2passbot.loader import _

router = Router()


def blur_password(password) -> str:
    return (f"{password[0]}"
            f"{'*' * (len(password) - 2)}"
            f"{password[-1]}")


async def _password_found(user, _hash, found_password, message, sub):
    logger.success(f"Пароль найден {_hash} -> {found_password.password}")

    if sub:
        await user.subscription.decr()
        # _hash = markdown.hbold(_hash)
        # password = markdown.hbold(found_password.password)
        password = found_password.password
        answer = _("Хеш:\n{}\nсоответствует строке пароля:\n{}").format(_hash, password)
        answer = _("{}\n\nКоличество оставшихся запросов: {}").format(answer, user.subscription.limit)
        # answer.format(found_password.password)
        # answer.format(markdown.hbold(found_password.password))
    else:
        # _hash = markdown.hbold(_hash)
        # password = markdown.hbold(found_password.password)
        password = blur_password(found_password.password)
        answer = _("Хеш:\n{}\nсоответствует строке пароля:\n{}").format(_hash, password)
        answer = _("{}\nЧтобы увидеть пароль приобретите запросы через меню.").format(answer, _hash)
    await message.answer(answer)


async def search(user, _hash, hash_type, message, sub):
    if sub:
        temp.STATS.total_requests_count += 1

    logger.debug(f"{user.username}[{user.user_id}] Поиск хеша")

    if found_password := await Password.search_in_local(_hash, hash_type):
        logger.success(f"Хеш {_hash} [{hash_type}] найден в локальной базе")
        await _password_found(user, _hash, found_password, message, sub)
        if sub:
            temp.STATS.found_local_count += 1

    elif found_password := await ApiPassword.search_in_saved(_hash, hash_type):
        logger.success(f"Хеш {_hash} [{hash_type}] найден в сохраненной базе")
        await _password_found(user, _hash, found_password, message, sub)
        if sub:
            temp.STATS.found_in_saved_count += 1

    elif sub:
        if found_password := await Password.search_in_api(_hash, hash_type):
            temp.STATS.found_via_api_count += 1
            logger.success(f"Хеш {_hash} [{hash_type}] найден через API и сохранен в базе")
            await _password_found(user, _hash, found_password, message, sub)
        else:
            temp.STATS.not_found_count += 1
            logger.info(f"Пароль к хешу {_hash} [{hash_type}] не найден")
            # _hash = markdown.hbold(_hash)
            await message.answer(_("Не удалось найти пароль по хешу {}").format(_hash))

    else:
        logger.info(f"Пароль к хешу: {_hash} [{hash_type}] не найден")
        # _hash = markdown.hbold(_hash)
        await message.answer(_("Пароль для хеша {} не найден в ограниченной базе. "
                               "Для поиска в расширенной базе приобретите запросы через меню бота.").format(_hash))


async def get_password_hash(message: types.Message, user: User, state: FSMContext):
    await state.clear()
    _hash = message.text.strip()

    if user.is_search:
        await message.answer(_("Ожидайте завершения предыдущего поиска"))
        return
    try:
        if hash_type := await hash_is_valid(_hash):
            async with user:
                temp.STATS = await Statistic.first()
                # Для пользователей с подпиской
                if user.subscription.limit:
                    await search(user, _hash, hash_type, message, sub=True)

                # Для пользователей без подписки
                else:
                    await search(user, _hash, hash_type, message, sub=False)
                await temp.STATS.save()
            return
    except Exception as e:
        logger.warning(e)
    await message.answer(_("Некорректный hash"))


def register_check_password(dp: Dispatcher):
    dp.include_router(router)

    callback = router.callback_query.register
    message = router.message.register

    message(get_password_hash,
            # UserFilter(),
            ChannelSubscriptionFilter(),
            # HashFilter(),
            state="*"
            )

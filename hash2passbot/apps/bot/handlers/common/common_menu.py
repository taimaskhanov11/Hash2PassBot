from aiogram import Dispatcher, Router, types
from aiogram.dispatcher.fsm.context import FSMContext

from hash2passbot.apps.bot.const import menu
from hash2passbot.apps.bot.markups.common import common_markups
from hash2passbot.apps.bot.utils import channel_status_check, stop
from hash2passbot.db.models import User
from hash2passbot.loader import _

router = Router()


async def check_subscribe(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    if await channel_status_check(call.from_user.id):
        await call.message.answer(menu.check_subscribe_find())
        return True
    await call.answer(menu.check_subscribe_find(), show_alert=True)
    return False


async def start(message: types.Message | types.CallbackQuery, user: User, is_new: bool, state: FSMContext):
    await state.clear()
    if isinstance(message, types.CallbackQuery):
        message = message.message

    if is_new:
        await message.answer("🇷🇺 Выберите язык\n"
                             "🇺🇸 Select a language", reply_markup=common_markups.lang_choice())
        return
    await message.answer(menu.start(),
                         reply_markup=common_markups.start())

    # await message.answer(b"asd")


async def profile(message: types.Message, user: User, state: FSMContext):
    await state.clear()
    answer = menu.profile().format(
        user.user_id,
        user.username,
        user.subscription.limit
    )
    await message.answer(answer, reply_markup=common_markups.profile())


async def description(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(menu.description(),
                         reply_markup=common_markups.description()
                         )


async def support(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(menu.support(), reply_markup=common_markups.support())


async def locale_choice(call: types.CallbackQuery, user: User, state: FSMContext):
    if call.data == "ru":
        user.locale = "ru"
    else:
        user.locale = "en"
    await user.save(update_fields=["locale"])
    await call.message.answer(_("✅ Язык успешно выбран, введите /start чтобы продолжить", locale=user.locale))


def register_common(dp: Dispatcher):
    dp.include_router(router)

    callback = router.callback_query.register
    message = router.message.register

    message(start, commands="start", state="*")
    message(stop, commands="stop", state="*")
    callback(start, text="start", state="*")
    callback(locale_choice, text="ru", state="*")
    callback(locale_choice, text="en", state="*")

    message(profile, text_startswith="👤", state="*")
    message(description, text_startswith="📄", state="*")
    message(support, text_startswith="🙋‍♂", state="*")
    callback(check_subscribe, text="check_subscribe", state="*")

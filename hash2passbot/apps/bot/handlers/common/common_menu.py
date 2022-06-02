from aiogram import Dispatcher, Router, types
from aiogram.dispatcher.fsm.context import FSMContext

from hash2passbot.apps.bot.markups.common import common_markups
from hash2passbot.apps.bot.utils import channel_status_check, stop
from hash2passbot.db.models import User
from hash2passbot.loader import _

router = Router()


async def check_subscribe(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    if await channel_status_check(call.from_user.id):
        await call.message.answer(_("✅ Подписки найдены, введите /start чтобы продолжить"))
        return True
    await call.answer(_("❌ Ты подписался не на все каналы"), show_alert=True)
    return False


async def start(message: types.Message | types.CallbackQuery, user: User, state: FSMContext):
    await state.clear()
    if isinstance(message, types.CallbackQuery):
        message = message.message
    await message.answer(_("Главное меню!"), reply_markup=common_markups.start())

    # await message.answer(b"asd")


async def profile(message: types.Message, user: User, state: FSMContext):
    answer = _("🔑 ID: {}\n"
               "👤 Логин: @{}\n"
               "📄 Оставшиеся успешные запросы - {}").format(
        user.user_id,
        user.username,
        user.subscription.limit
    )
    await message.answer(answer, reply_markup=common_markups.profile())


async def description(message: types.Message, state: FSMContext):
    await message.answer(_("Профиль"), reply_markup=common_markups.description())


async def support(message: types.Message, state: FSMContext):
    await message.answer(_("По всем вопросам писать @chief_MailLeaks!"), reply_markup=common_markups.support())


def register_common(dp: Dispatcher):
    dp.include_router(router)

    callback = router.callback_query.register
    message = router.message.register

    message(start, commands="start", state="*")
    message(stop, commands="stop", state="*")
    callback(start, text="start", state="*")

    message(profile, text_startswith="👤")
    message(description, text_startswith="🗒")
    message(support, text_startswith="🙋‍♂")
    callback(check_subscribe, text="check_subscribe", state="*")

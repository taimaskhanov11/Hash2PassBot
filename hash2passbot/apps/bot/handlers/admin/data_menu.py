from aiogram import Router, types, F
from aiogram.dispatcher.fsm.context import FSMContext
# from aiogram.dispatcher.filters
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.utils import markdown
from loguru import logger

from hash2passbot.apps.bot.callback_data.base_callback import SubscriptionCallback, Action, UserCallback
from hash2passbot.apps.bot.markups.admin import data_markups
from hash2passbot.db.models import User, Subscription

router = Router()


class GetUser(StatesGroup):
    get = State()


class EditSubscription(StatesGroup):
    edit = State()


async def getting_user(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.answer()
    await call.message.answer("Введите имя пользователя или id")
    await state.set_state(GetUser.get)


async def _getter_user(message: types.Message | types.CallbackQuery, state: FSMContext,
                       callback_data: UserCallback = None):
    if isinstance(message, types.CallbackQuery):
        await message.answer()
        search_field = {"pk": callback_data.pk}
        message = message.message
    else:
        search_field = {
            "user_id": message.text} if message.text.isdigit() else {
            "username": message.text.replace("@", "")
        }

    user = await User.get_or_none(**search_field)
    if user:
        # payments made
        payments = await user.get_payments()
        answer = (
            f"🔑 ID: {user.user_id}\n"
            f"👤 Username: {user.username}\n"
            f"Количество оставшихся запросов: {user.subscription.limit}\n"
            f"Совершенные платежи: \n"
        )
        for p in payments:
            pay_title = markdown.hcode(p.__class__.__name__[7:])
            date = markdown.hcode(p.created_at.replace(microsecond=0))
            amount = markdown.hcode(round(p.amount, 1))
            answer += f"    ✓[{pay_title}] {date} -> {amount}р\n"

        await state.update_data(user_pk=user.pk)
        await message.answer(answer, "html", reply_markup=data_markups.get_user(user.subscription))
        await state.set_state()

        # await part_sending()
    else:
        await message.answer("Пользователь не найден")


async def get_user(message: types.Message, state: FSMContext):
    await _getter_user(message, state)


async def get_user_callback(call: types.CallbackQuery, callback_data: UserCallback, state: FSMContext):
    await _getter_user(call, state, callback_data)


async def edit_subscription(call: types.CallbackQuery, callback_data: SubscriptionCallback, state: FSMContext):
    await call.answer()
    await state.update_data(subscription_pk=callback_data.pk)
    await call.message.answer("Введите новое количество запросов", reply_markup=data_markups.edit_subscription())
    await state.set_state(EditSubscription.edit)


@logger.catch
async def edit_subscription_finish(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        data = await state.get_data()
        subscription = await Subscription.get(pk=data["subscription_pk"])
        await subscription.set_limit(message.text)
        await message.answer("✅ Количество запросов успешно обновлено",
                             reply_markup=data_markups.edit_subscription_finish(data.get("user_pk")) if data.get(
                                 "user_pk") else None)
        await state.set_state()
    else:
        await message.answer("Некорректный ввод")


def register_data(dp: Router):
    dp.include_router(router)

    callback = router.callback_query.register
    message = router.message.register

    callback(getting_user, text="getting_user", state="*")
    message(get_user, state=GetUser.get)
    callback(get_user_callback, UserCallback.filter(F.action == Action.view))

    callback(edit_subscription, SubscriptionCallback.filter(F.action == Action.edit))
    message(edit_subscription_finish, state=EditSubscription.edit)

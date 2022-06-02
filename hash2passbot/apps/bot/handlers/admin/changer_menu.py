from aiogram import Router, types, F
from aiogram.dispatcher.fsm.context import FSMContext
# from aiogram.dispatcher.filters
from aiogram.dispatcher.fsm.state import StatesGroup, State

from hash2passbot.apps.bot.callback_data.base_callback import SubscriptionCallback, Action
from hash2passbot.apps.bot.markups.admin import changer_markups
from hash2passbot.apps.bot.utils import part_sending
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


async def get_user(message: types.Message, state: FSMContext):
    search_field = {
        "user_id": message.text} if message.text.isdigit() else {
        "username": message.text.replace("@", "")
    }

    user = await User.get_or_none(**search_field)
    if user:
        invoice_cryptos = await user.invoice_cryptos.filter(is_paid=True)
        invoice_qiwis = await user.invoice_qiwis.filter(is_paid=True)
        await user.fetch_related("subscription")
        answer = (
            f"🔑 ID: {user.user_id}\n"
            f"👤 Username: {user.username}\n"
            f"Количество оставшихся запросов: {user.subscription.limit}\n"
            f"Совершенные платежи: "
        )
        await message.answer(answer, reply_markup=changer_markups.get_user(user.subscription))
        await part_sending()
    else:
        await message.answer("Пользователь не найден")


async def edit_subscription(call: types.CallbackQuery, callback_data: SubscriptionCallback, state: FSMContext):
    await call.answer()
    await state.update_data(subscription_pk=callback_data.pk)
    await call.message.answer("Введите новое количество запросов", reply_markup=changer_markups.edit_subscription())
    await state.set_state(EditSubscription.edit)


async def edit_subscription_finish(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        subscription = await Subscription.get(pk=message.text)
        await subscription.set_limit(message.text)
        await message.answer("✅ Количество запросов успешно обновлено",
                             reply_markup=changer_markups.edit_subscription_finish())
        await state.clear()
    else:
        await message.answer("Некорректный ввод")


def register_changer(dp: Router):
    dp.include_router(router)

    callback = router.callback_query.register
    message = router.message.register

    callback(getting_user, text="getting_user", state="*")
    message(get_user, state=GetUser.get)

    callback(edit_subscription, SubscriptionCallback.filter(F.action == Action.edit))
    message(edit_subscription_finish, state=EditSubscription.edit)

from aiogram import Router, types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State

from hash2passbot.apps.bot.const import menu
from hash2passbot.apps.bot.markups.admin import changer_menu_markups

# from aiogram.dispatcher.filters

router = Router()


class ChangeStart(StatesGroup):
    choice = State()
    finish = State()


async def change_start(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    answer = ""
    # for num, data in enumerate(menu.dict().items()):
    for num, key in enumerate(menu.method_list()):
        func = getattr(menu, key)
        value = func()
        answer += f"#{num}\n{key}\n{value}\n\n"
    await call.message.answer(f"Выберите поле для изменения:\n{answer}",
                              reply_markup=changer_menu_markups.change_start())
    await state.set_state(ChangeStart.choice)


async def change_choice(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(change_field=call.data)
    await call.message.answer(f"Введите новое значение для поля {call.data}",
                              reply_markup=changer_menu_markups.change_choice())
    await state.set_state(ChangeStart.finish)


async def change_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    setattr(menu, data["change_field"], lambda: message.text)
    await message.answer("Поле успешно изменено")
    await state.clear()


def register_change_menu(dp: Router):
    dp.include_router(router)

    callback = router.callback_query.register
    message = router.message.register

    callback(change_start, text="change_menu", state="*")
    callback(change_choice, state=ChangeStart.choice)
    message(change_finish, state=ChangeStart.finish)

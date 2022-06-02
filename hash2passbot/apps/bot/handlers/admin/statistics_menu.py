from aiogram import Router, types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State

from hash2passbot.apps.bot import temp
from hash2passbot.apps.bot.markups.admin import statistics_markups, admin_markups
from hash2passbot.db.models import User, Subscription

router = Router()


class SendMail(StatesGroup):
    preview = State()
    select = State()

    button = State()
    send = State()


async def statistics_start(call: types.CallbackQuery, state: FSMContext):
    """
    Сколько запросов сделано пользователями, сколько найдено в локальной базе,
     сколько найдено через API сайта. Так же вывести в %.
     Общее количество сделанных запросов = 100%. Нужно считать процент найденных в локальной БД,
     найденных через API и не найденных нигде.
     """
    await state.clear()
    all_count = await User.count_all()
    today_count = await User.count_new_today()
    all_limits = await Subscription.all_limits()
    answer = (f"📊 Общее число пользователей: {all_count}\n"
              f"📊 Новых пользователей за сегодня: {today_count}\n"
              f"📊 Общее число выданных всем пользователям запросов: {all_limits}\n\n"
              f"📊 Всего запросов сделано пользователями: {temp.STATS.total_requests_count} (100%)\n"
              )
    if temp.STATS.total_requests_count:
        answer += (
            f"   📊 Найдено  в локальной базе: {temp.STATS.found_local_count} ({100 * (temp.STATS.found_local_count / temp.STATS.total_requests_count)}%)\n"
            f"   📊 Найдено  в сохраненной базе: {temp.STATS.found_in_saved_count} ({100 * (temp.STATS.found_in_saved_count / temp.STATS.total_requests_count)}%)\n"
            f"   📊 Найдено  через API: {temp.STATS.found_via_api_count} ({100 * (temp.STATS.found_via_api_count / temp.STATS.total_requests_count)}%)\n"
            f"   📊 НЕ Найдено: {temp.STATS.not_found_count} ({100 * (temp.STATS.not_found_count / temp.STATS.total_requests_count)})%")

    await call.message.answer(answer, reply_markup=admin_markups.back())


async def users_count(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    count = await User.count_all()
    await call.message.answer(f"В боте зарегистрировано: {count} 👥",
                              reply_markup=statistics_markups.back())


async def users_count_new(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    count = await User.count_new_today()
    await call.message.answer(f"Новых пользователей за сегодня: {count} 👥",
                              reply_markup=statistics_markups.back())


def register_statistics(dp: Router):
    dp.include_router(router)

    callback = router.callback_query.register
    message = router.message.register

    callback(statistics_start, text="statistics", state="*")
    callback(users_count, text="users_count", state="*")
    callback(users_count_new, text="users_count_new", state="*")

import datetime

from aiogram import Router, types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.utils import markdown

from hash2passbot.apps.bot import temp
from hash2passbot.apps.bot.markups.admin import statistics_markups, admin_markups
from hash2passbot.db.models import User, Subscription, Statistic, InvoiceQiwi, InvoiceCrypto

router = Router()


class SendMail(StatesGroup):
    preview = State()
    select = State()

    button = State()
    send = State()


async def get_last_payments() -> list[InvoiceCrypto, InvoiceQiwi]:
    date = datetime.date.today()
    invoice_cryptos = await InvoiceCrypto.filter(
        created_at__year=date.year,
        created_at__month=date.month,
        created_at__day=date.day,
        is_paid=True
    ).select_related("user")
    invoice_qiwis = await InvoiceQiwi.filter(
        created_at__year=date.year,
        created_at__month=date.month,
        created_at__day=date.day,
        is_paid=True
    ).select_related("user")
    invoice_cryptos.extend(invoice_qiwis)
    invoice_cryptos.sort(key=lambda x: x.created_at)
    return invoice_cryptos


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
    last_payments = await get_last_payments()

    # await save_statistics()
    temp.STATS = await Statistic.first()

    bold = markdown.hbold
    answer = (f"📊 Общее число пользователей: {bold(all_count)}\n"
              f"📊 Новых пользователей за сегодня: {bold(today_count)}\n"
              f"📊 Общее число выданных всем пользователям запросов: {bold(all_limits)}\n\n"
              f"📊 Всего запросов сделано пользователями: {bold(temp.STATS.total_requests_count)} (100%)\n"
              )

    if temp.STATS.total_requests_count:
        found_local_count = bold(round(100 * (temp.STATS.found_local_count / temp.STATS.total_requests_count), 2))
        found_in_saved_count = bold(round(100 * (temp.STATS.found_in_saved_count / temp.STATS.total_requests_count), 2))
        found_via_api_count = bold(round(100 * (temp.STATS.found_via_api_count / temp.STATS.total_requests_count), 2))
        not_found_count = bold(round(100 * (temp.STATS.not_found_count / temp.STATS.total_requests_count), 2))
        answer += (
            f"   📊 Найдено  в локальной базе: {bold(temp.STATS.found_local_count)} ({found_local_count}%)\n"
            f"   📊 Найдено  в сохраненной базе: {bold(temp.STATS.found_in_saved_count)} ({found_in_saved_count}%)\n"
            f"   📊 Найдено  через API: {bold(temp.STATS.found_via_api_count)} ({found_via_api_count}%)\n"
            f"   📊 НЕ Найдено: {bold(temp.STATS.not_found_count)} ({not_found_count})%\n")

    answer += f"\n📊Совершенные платежи за сегодня:\n"

    for p in last_payments:
        pay_title = markdown.hcode(p.__class__.__name__[7:])
        date:datetime.datetime = p.created_at
        date = date.strftime("%d.%m.%Y %H:%M")
        # date:datetime.datetime = p.created_at.replace(microsecond=0)
        # date.strftime()
        date = markdown.hcode(date)
        amount = markdown.hcode(round(p.amount, 1))
        username = markdown.hcode(p.user.username)
        answer += f"    ✓[{pay_title}] @{username}[{p.user.user_id}] {date} -> {amount}р\n"

    await call.message.answer(answer, "html", reply_markup=admin_markups.back())


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

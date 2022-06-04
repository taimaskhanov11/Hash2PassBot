from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from hash2passbot.loader import _


def start():
    builder = ReplyKeyboardBuilder()
    _menu = [_("👤 Профиль"), _("💳 Приобрести запросы"), _("📄 Описание"), _("🙋‍♂ Поддержка")]
    for i in _menu:
        builder.add(types.KeyboardButton(text=i))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def channel_status_check(channels: list[tuple[str, str]]):
    builder = ReplyKeyboardBuilder()
    for num, skin in enumerate(channels, 1):
        builder.button(text=f"Канал #{num}", url=f"https://t.me/{skin[1][1:]}")
    builder.button(text=_("✅ Я подписался"), callback_data="check_subscribe")
    builder.adjust(1)
    return builder.as_markup()


def lang_choice():
    builder = InlineKeyboardBuilder()
    builder.button(text="Русский", callback_data="ru")
    builder.button(text="English", callback_data="en")
    return builder.as_markup()


def profile():
    builder = InlineKeyboardBuilder()
    # builder.button(text=_("⬅️ Назад"), callback_data="start")
    return builder.as_markup()


def description():
    builder = InlineKeyboardBuilder()
    # builder.button(text=_("⬅️ Назад"), callback_data="start")
    return builder.as_markup()


def support():
    builder = InlineKeyboardBuilder()
    # builder.button(text=_("⬅️ Назад"), callback_data="start")
    return builder.as_markup()

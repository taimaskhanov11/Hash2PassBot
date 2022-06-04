from aiogram.utils.keyboard import InlineKeyboardBuilder

from hash2passbot.apps.bot.const import menu
from hash2passbot.apps.bot.markups.admin.admin_markups import back_to_admin


def change_start():
    builder = InlineKeyboardBuilder()
    for num, key in enumerate(menu.method_list()):
        builder.button(text=str(num), callback_data=key)
    builder.row(back_to_admin)
    return builder.as_markup()


def change_choice():
    builder = InlineKeyboardBuilder()
    builder.row(back_to_admin)
    return builder.as_markup()

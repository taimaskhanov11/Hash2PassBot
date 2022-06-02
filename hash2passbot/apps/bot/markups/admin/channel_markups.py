from aiogram.utils.keyboard import InlineKeyboardBuilder

from hash2passbot.apps.bot.callback_data.base_callback import ChannelCallback, Action
from hash2passbot.apps.bot.markups.admin.admin_markups import admin_back_buttons
from hash2passbot.apps.bot.markups.utils import get_inline_keyboard
from hash2passbot.db.models import Channel


def view_channels(channels: list[Channel]):
    builder = InlineKeyboardBuilder()
    for c in channels:
        builder.button(
            str(c),
            callback_data=ChannelCallback(pk=c.pk, action=Action.view)
        )
    return builder.as_markup()


def touch_channel(channel):
    keyboard = [[("✍ Удалить.", ChannelCallback(pk=channel.pk, action=Action.delete).pack())], [admin_back_buttons]]
    return get_inline_keyboard(keyboard)

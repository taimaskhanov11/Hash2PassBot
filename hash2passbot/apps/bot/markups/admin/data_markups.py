from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from hash2passbot.apps.bot.callback_data.base_callback import SubscriptionCallback, Action, UserCallback
from hash2passbot.apps.bot.markups.admin.admin_markups import back_to_admin
from hash2passbot.db.models import Subscription


def get_user(subscription: Subscription) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✍️ Изменить количество оставшихся запросов",
                   callback_data=SubscriptionCallback(pk=subscription.pk, action=Action.edit))
    builder.row(back_to_admin)
    return builder.as_markup()


def edit_subscription() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="10")
    builder.button(text="20")
    builder.button(text="50")
    builder.button(text="100")
    # builder.row(back_to_admin)
    return builder.as_markup(resize_keyboard=True, input_field_placeholder="Введите нужно количество")


def edit_subscription_finish(user_pk) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    # builder.row(back_to_admin)
    builder.button(text="⬅️ Назад", callback_data=UserCallback(pk=user_pk, action=Action.view))
    return builder.as_markup()
